"""Full-readout encoded-reference interface using the pinned official CoLa models."""
from contextlib import nullcontext
from pathlib import Path
import torch
from tokenizers import Tokenizer
from cola_dlm import ColaDiTModel, ColaTextVAEModel


class ColaBasin:
    def __init__(self,checkpoint,device='cuda:0',load_dit=False):
        self.device=torch.device(device); self.checkpoint=Path(checkpoint)
        self.vae=ColaTextVAEModel.from_pretrained(self.checkpoint/'cola_dlm/cola_vae').to(self.device).eval().requires_grad_(False)
        self.tokenizer=Tokenizer.from_file(str(self.checkpoint/'tokenizer.json'))
        self.dit=None
        if load_dit:
            self.load_dit()
        assert self.vae.latent_dim==16 and self.vae.patch_size==1 and self.vae.block_size==1
        self.counts=dict(encode=0,decode=0,dit_cond=0,dit_uncond=0,dit_history=0)
        self.timesteps=torch.linspace(1000,0,17)

    def load_dit(self):
        if self.dit is None:
            self.dit=ColaDiTModel.from_pretrained(self.checkpoint/'cola_dlm/cola_dit').to(self.device).eval().requires_grad_(False)
            assert self.dit.block_size==16

    def shape(self,n):
        return torch.tensor([[n]],device=self.device,dtype=torch.long)

    def precision(self,fp32=False):
        return nullcontext() if fp32 else torch.autocast('cuda',dtype=torch.bfloat16)

    @torch.no_grad()
    def encode(self,ids):
        self.vae.set_kv_cache(False)
        with self.precision():
            enc=self.vae.encode([torch.tensor(ids,device=self.device)])
            mode=enc.latents_list[0]
            if enc.latent_dists is not None:
                assert torch.equal(mode,enc.latent_dists[0].mode())
            z=((mode-self.vae.shifting_factor)*self.vae.scaling_factor).float()
        self.counts['encode']+=1
        return z

    def decode(self,z,start=0,length=None,fp32=False):
        self.vae.set_kv_cache(False)
        shape=self.shape(len(z))
        with self.precision(fp32):
            logits=self.vae.decode(z=z,txt_shape=shape,txt_q_shape=shape,update_kv=False)[0]
        self.counts['decode']+=1
        return logits[start:start+length if length is not None else None].float()

    def decode_cached(self,z,start,length):
        self.vae.set_kv_cache(False)
        with self.precision():
            self.vae.decode(z=z[:start],txt_shape=self.shape(start),txt_q_shape=self.shape(start),update_kv=True)
            logits=self.vae.decode(z=z[start:],txt_shape=self.shape(len(z)),txt_q_shape=self.shape(len(z)-start),update_kv=False)[0,:length]
        self.counts['decode']+=2
        self.vae.set_kv_cache(False)
        return logits.float()

    def read(self,z,layout):
        logits=self.decode(z,layout['prefix_length'],layout['answer_length'])
        ids=logits.argmax(-1).tolist()
        text=self.tokenizer.decode(ids,skip_special_tokens=False)
        return ids,text,logits

    def gaussian(self,shape,seed):
        return torch.randn(shape,device=self.device,generator=torch.Generator(device=self.device).manual_seed(seed))

    def rotation(self,seed):
        matrix=self.gaussian((16,16),seed)
        q,r=torch.linalg.qr(matrix)
        return q*torch.where(torch.diag(r)>=0,1.,-1.)[None,:]

    @torch.no_grad()
    def recover(self,clean,start,noise,restart_index,cfg=1.):
        """Recover answer+trailer, rebuilding each block's teacher-clean history."""
        assert len(clean)%16==0 and noise.shape==clean[start:].shape
        result=clean.clone()
        lam=float(self.timesteps[restart_index])/1000
        for begin in range(start//16*16,len(clean),16):
            for block in self.dit.blocks:
                block.set_kv_cache(True)
            if begin:
                with self.precision():
                    self.dit(txt=clean[:begin].to(torch.bfloat16),txt_shape=self.shape(begin),txt_q_shape=self.shape(begin),
                        timestep=torch.zeros(begin,device=self.device,dtype=torch.bfloat16),update_kv=True,use_kv_cache=True)
                self.counts['dit_history']+=1
            known=max(0,start-begin)
            txt=clean[begin:begin+16].clone()
            n=16-known
            noise_start=max(begin,start)-start
            txt[known:]=(1-lam)*txt[known:]+lam*noise[noise_start:noise_start+n]
            for t,tn in zip(self.timesteps[restart_index:-1],self.timesteps[restart_index+1:]):
                txt[:known]=clean[begin:begin+known]
                ts=torch.full((16,),float(t),device=self.device)
                ts[:known]=0
                with self.precision():
                    args=dict(txt=txt.to(torch.bfloat16),txt_q_shape=self.shape(16),timestep=ts.to(torch.bfloat16),update_kv=False)
                    cond=self.dit(**args,txt_shape=self.shape(begin+16),use_kv_cache=True).txt_sample
                    self.counts['dit_cond']+=1
                    uncond=self.dit(**args,txt_shape=self.shape(16),use_kv_cache=False).txt_sample
                    self.counts['dit_uncond']+=1
                    scale=cfg if begin else 1.
                    drift=scale*(cond-uncond)+uncond
                txt=txt-drift*((float(t)-float(tn))/1000)
                txt[:known]=clean[begin:begin+known]
            result[begin:begin+16]=txt
        assert torch.equal(result[:start],clean[:start])
        return result
