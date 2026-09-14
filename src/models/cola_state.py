"""Resumable single-root inference using the pinned official CoLa modules.

The Euler, CFG, prompt pinning, autocast, and commit order follow ByteDance's
Apache-2.0 inference implementation at 7d1daee. Model modules remain upstream.
"""
from dataclasses import dataclass
from pathlib import Path
import math
import time
import torch
from tokenizers import Tokenizer
from cola_dlm import ColaDiTModel, ColaTextVAEModel


@dataclass
class State:
    dit_cache: list
    decoder_cache: list
    history: tuple
    prompt_ids: tuple
    generated_ids: tuple
    position: int
    step: int
    first_latent: torch.Tensor
    first_mask: torch.Tensor
    trim: int
    decoder_ids: tuple


def clone_cache(blocks):
    return [(None if b._k_cache is None else [x.clone() for x in b._k_cache],
             None if b._v_cache is None else [x.clone() for x in b._v_cache]) for b in blocks]


def restore_cache(blocks, cache):
    for b, (k, v) in zip(blocks, cache):
        b._k_cache = None if k is None else [x.clone() for x in k]
        b._v_cache = None if v is None else [x.clone() for x in v]


class ColaStateEngine:
    def __init__(self, checkpoint, device='cuda:0', steps=16, cfg=7.0, repetition_penalty=1.0):
        self.device = torch.device(device)
        self.steps, self.cfg = steps, cfg
        self.repetition_penalty = repetition_penalty
        checkpoint = Path(checkpoint)
        self.dit = ColaDiTModel.from_pretrained(checkpoint / 'cola_dlm/cola_dit').to(self.device).eval()
        self.vae = ColaTextVAEModel.from_pretrained(checkpoint / 'cola_dlm/cola_vae').to(self.device).eval()
        self.dit.requires_grad_(False)
        self.vae.requires_grad_(False)
        self.tokenizer = Tokenizer.from_file(str(checkpoint / 'tokenizer.json'))
        assert self.dit.block_size == 16 and self.vae.patch_size == 1 and self.vae.latent_dim == 16
        self.dit_blocks = [b.msa for b in self.dit.blocks]
        self.decoder_blocks = list(self.vae.decoder.blocks)
        self.calls = {'dit_cond': 0, 'dit_uncond': 0, 'dit_commit': 0, 'decoder': 0, 'encode': 0}
        self.timesteps = torch.linspace(1000, 0, steps + 1)
        self.qshape = self.shape(16)

    def shape(self, length):
        return torch.tensor([[length]], dtype=torch.long, device=self.device)

    def clear(self):
        for b in self.dit.blocks:
            b.set_kv_cache(True)
        self.vae.set_kv_cache(True)

    @torch.inference_mode()
    def begin(self, prompt):
        self.clear()
        self.prompt_ids = tuple(self.tokenizer.encode(prompt).ids)
        pad = (-len(self.prompt_ids)) % 16
        ids = torch.tensor(self.prompt_ids + (100277,) * pad, device=self.device)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            enc = self.vae.encode([ids])
            lat = ((enc.latents_list[0] - self.vae.shifting_factor) * self.vae.scaling_factor).float()
        self.calls['encode'] += 1
        self.trim = len(self.prompt_ids) % 16
        prefix_len = len(self.prompt_ids) - self.trim
        self.first_latent = lat[prefix_len:prefix_len+16] if self.trim else lat[-16:].clone()
        self.first_mask = torch.arange(16, device=self.device) < self.trim
        self.generated_ids = ()
        self.decoder_ids = ()
        self.step = 0
        self.position = 0
        self.history = ()
        if prefix_len:
            prefix = lat[:prefix_len].clone()
            self._prefill(prefix)
            self.history = (prefix,)
        return self.snapshot()

    @torch.inference_mode()
    def _prefill(self, latent):
        # The official prefix path commits DiT before decoder.
        shape = self.shape(latent.shape[0])
        with torch.autocast('cuda', dtype=torch.bfloat16):
            self.dit(txt=latent.to(torch.bfloat16), txt_shape=shape, txt_q_shape=shape,
                     timestep=torch.zeros(len(latent), device=self.device, dtype=torch.bfloat16),
                     update_kv=True, use_kv_cache=True)
            self.vae.decode(z=latent, txt_shape=shape, txt_q_shape=shape, update_kv=True)
        self.calls['dit_commit'] += 1
        self.calls['decoder'] += 1
        self.position = len(latent)

    @torch.inference_mode()
    def snapshot(self):
        return State(clone_cache(self.dit_blocks), clone_cache(self.decoder_blocks),
                     self.history, self.prompt_ids, self.generated_ids, self.position,
                     self.step, self.first_latent.clone(), self.first_mask.clone(), self.trim, self.decoder_ids)

    @torch.inference_mode()
    def restore(self, state):
        restore_cache(self.dit_blocks, state.dit_cache)
        restore_cache(self.decoder_blocks, state.decoder_cache)
        self.history = state.history
        self.prompt_ids, self.generated_ids = state.prompt_ids, state.generated_ids
        self.decoder_ids = state.decoder_ids
        self.position, self.step = state.position, state.step
        self.first_latent, self.first_mask, self.trim = state.first_latent, state.first_mask, state.trim

    @torch.inference_mode()
    def rebuild(self, state):
        """Reconstruct caches by replaying their original chronological commits."""
        self.restore(state)
        self.clear()
        self.position = 0
        self.generated_ids = ()
        self.decoder_ids = ()
        self.step = 0
        self.history = ()
        prefix_len = len(state.prompt_ids) - state.trim
        history = list(state.history)
        if prefix_len:
            prefix = history.pop(0)
            self._prefill(prefix)
            self.history = (prefix,)
        for latent in history:
            self.commit(latent)
        assert self.generated_ids == state.generated_ids
        assert self.decoder_ids == state.decoder_ids
        assert self.position == state.position and self.step == state.step

    def noise(self, seed, blocks=1):
        g = torch.Generator(device=self.device).manual_seed(int(seed))
        # Draw individual block tensors exactly as the official single-root loop.
        return torch.stack([torch.randn(16, 16, device=self.device, generator=g) for _ in range(blocks)])

    @torch.inference_mode()
    def sample_block(self, noise):
        txt = noise.clone()
        shape = self.shape(self.position + 16)
        for t, tn in zip(self.timesteps[:-1], self.timesteps[1:]):
            ts = torch.full((16,), t, device=self.device)
            if self.step == 0:
                ts[self.first_mask] = 0
                txt[self.first_mask] = self.first_latent[self.first_mask]
            with torch.autocast('cuda', dtype=torch.bfloat16):
                args = dict(txt=txt.to(torch.bfloat16), txt_q_shape=self.qshape,
                            timestep=ts.to(torch.bfloat16), update_kv=False)
                cond = self.dit(**args, txt_shape=shape, use_kv_cache=True).txt_sample
                uncond = self.dit(**args, txt_shape=self.qshape, use_kv_cache=False).txt_sample
            self.calls['dit_cond'] += 1
            self.calls['dit_uncond'] += 1
            if self.step == 0:
                scale = torch.full((16, 1), self.cfg if self.position else 1.0,
                                   device=self.device, dtype=torch.bfloat16)
            else:
                scale = self.cfg
            drift = scale * (cond - uncond) + uncond
            txt = txt - drift * ((float(t) - float(tn)) / 1000.0)
            if self.step == 0:
                txt[self.first_mask] = self.first_latent[self.first_mask]
        return txt

    @torch.inference_mode()
    def commit(self, latent, dit_latent=None):
        """Commit decoder latent and (normally identical) prior latent from restored state."""
        shape = self.shape(self.position + 16)
        with torch.autocast('cuda', dtype=torch.bfloat16):
            logits = self.vae.decode(z=latent, txt_shape=shape, txt_q_shape=self.qshape, update_kv=True)[0]
            prior = latent if dit_latent is None else dit_latent
            self.dit(txt=prior.to(torch.bfloat16), txt_shape=shape, txt_q_shape=self.qshape,
                     timestep=torch.zeros(16, device=self.device, dtype=torch.bfloat16),
                     update_kv=True, use_kv_cache=True)
        self.calls['decoder'] += 1
        self.calls['dit_commit'] += 1
        if self.repetition_penalty == 1.0:
            ids = tuple(logits.argmax(-1).tolist())
        else:
            from cola_dlm.inference import sample_with_strategies
            context = (torch.tensor([self.decoder_ids],device=self.device)
                       if self.decoder_ids else None)
            # The official processor mutates logits. Keep the raw decoder
            # readout for KL; history includes the first block's prompt slice.
            processed = sample_with_strategies(logits.clone().unsqueeze(0),
                generated_ids=context,temperature=0.0,
                repetition_penalty=self.repetition_penalty)
            ids = tuple(processed[0].tolist())
        self.decoder_ids += ids
        self.generated_ids += ids[self.trim:] if self.step == 0 else ids
        self.position += 16
        self.step += 1
        self.history += (latent.clone(),)
        return ids, logits.float()

    @torch.inference_mode()
    def advance(self, noise):
        latent = self.sample_block(noise)
        ids, logits = self.commit(latent)
        return latent, ids, logits

    @torch.inference_mode()
    def continue_from(self, state, noises):
        self.restore(state)
        for noise in noises:
            self.advance(noise)
        return tuple(self.generated_ids)

    def text(self, ids=None):
        return self.tokenizer.decode(list(self.generated_ids if ids is None else ids), skip_special_tokens=False)


def symmetric_kl(reference_logits, candidate_logits):
    """Full-vocabulary per-position symmetric KL, evaluated in fp64."""
    a = reference_logits.double().log_softmax(-1)
    b = candidate_logits.double().log_softmax(-1)
    return 0.5 * ((a.exp() - b.exp()) * (a - b)).sum(-1)


def accepted(reference_ids, candidate_ids, reference_logits, candidate_logits, epsilon):
    kl = symmetric_kl(reference_logits, candidate_logits)
    return (reference_ids == candidate_ids and kl.sum().item() <= epsilon and
            kl.max().item() <= epsilon / 4), kl
