"""Reward-blind native proposals for completed full or mixed generated blocks."""
from dataclasses import dataclass
import math
import time
import torch
from src.models.cola_state import accepted


@dataclass
class Candidate:
    index: int
    latent: torch.Tensor
    ids: tuple
    logits: torch.Tensor
    state: object
    proposal_index: int
    kl_sum: float
    kl_max: float


def same_computed_history(engine, state):
    """Compare new-block caches after commits from an identical single-root prefix."""
    for blocks,caches in ((engine.dit_blocks,state.dit_cache),
                          (engine.decoder_blocks,state.decoder_cache)):
        for block,(ks,vs) in zip(blocks,caches):
            if not torch.equal(block._k_cache[0][-16:],ks[0][-16:]):
                return False
            if not torch.equal(block._v_cache[0][-16:],vs[0][-16:]):
                return False
    return True


@torch.inference_mode()
def native_candidates(engine, pre, original_latent, original_noise, eta, epsilon,
                      proposal_seed, count=2, max_proposals=32):
    """No future reward or continuation randomness enters candidate generation."""
    mixed = pre.step == 0 and pre.trim > 0
    known = pre.first_mask if mixed else torch.zeros(16,device=engine.device,dtype=torch.bool)
    free = ~known
    if mixed:
        assert torch.equal(original_latent[known],pre.first_latent[known])
    cohort = 'M' if mixed else 'F'
    engine.restore(pre)
    ref_ids,ref_logits=engine.commit(original_latent)
    ref_state=engine.snapshot()
    candidates=[Candidate(0,original_latent.clone(),ref_ids,ref_logits,ref_state,-1,0.0,0.0)]
    proposals=[]
    for attempt in range(max_proposals):
        if len(candidates)>=count:
            break
        torch.cuda.synchronize()
        start=time.perf_counter()
        prior_calls=engine.calls.copy()
        noise=math.sqrt(1-eta*eta)*original_noise+eta*engine.noise(proposal_seed+attempt)[0]
        noise[known] = original_noise[known]
        engine.restore(pre)
        latent=engine.sample_block(noise)
        known_equal = torch.equal(latent[known],original_latent[known])
        assert known_equal, 'Mixed proposal changed a known prompt latent'
        ids,logits=engine.commit(latent)
        ok,kl=accepted(ref_ids,ids,ref_logits,logits,epsilon)
        duplicate=any(torch.equal(latent,c.latent) for c in candidates)
        # Cache lists index batch members, and each tensor concatenates time.
        # Earlier positions came from the common snapshot; only the last 16
        # positions can differ. Check actual computed state, not just fp32 z.
        effective_duplicate = None
        if ok and not duplicate:
            effective_duplicate = any(same_computed_history(engine,c.state) for c in candidates)
        ok=ok and not duplicate and not effective_duplicate
        if ok:
            assert engine.generated_ids==ref_state.generated_ids
            candidates.append(Candidate(len(candidates),latent.clone(),ids,logits,engine.snapshot(),
                                        attempt,kl.sum().item(),kl.max().item()))
        torch.cuda.synchronize()
        proposals.append(dict(attempt=attempt,seed=proposal_seed+attempt,accepted=ok,
                              same_tokens=ids==ref_ids,duplicate=duplicate,
                              effective_cache_duplicate=effective_duplicate,cohort=cohort,
                              free_positions=int(free.sum()),known_latents_equal=known_equal,
                              kl_sum=kl.sum().item(),kl_max=kl.max().item(),
                              delta_norm=(latent-original_latent).norm().item(),
                              dit_input_bf16_delta_norm=(latent[free].bfloat16().float()-original_latent[free].bfloat16().float()).norm().item(),
                              elapsed_seconds=time.perf_counter()-start,
                              calls={k:engine.calls[k]-prior_calls[k] for k in prior_calls}))
    engine.restore(ref_state)
    return candidates,proposals
