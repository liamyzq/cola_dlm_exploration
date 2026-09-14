"""Reward-blind native proposals for the last complete generated block."""
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


@torch.inference_mode()
def native_candidates(engine, pre, original_latent, original_noise, eta, epsilon,
                      proposal_seed, count=4, max_proposals=32):
    """No future reward or continuation randomness enters candidate generation."""
    if pre.step == 0 and pre.trim:
        raise ValueError('Intervention requires a complete generated block, without prompt positions.')
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
        engine.restore(pre)
        latent=engine.sample_block(noise)
        ids,logits=engine.commit(latent)
        ok,kl=accepted(ref_ids,ids,ref_logits,logits,epsilon)
        duplicate=any(torch.equal(latent,c.latent) for c in candidates)
        ok=ok and not duplicate
        if ok:
            assert engine.generated_ids==ref_state.generated_ids
            candidates.append(Candidate(len(candidates),latent.clone(),ids,logits,engine.snapshot(),
                                        attempt,kl.sum().item(),kl.max().item()))
        torch.cuda.synchronize()
        proposals.append(dict(attempt=attempt,seed=proposal_seed+attempt,accepted=ok,
                              same_tokens=ids==ref_ids,duplicate=duplicate,
                              kl_sum=kl.sum().item(),kl_max=kl.max().item(),
                              delta_norm=(latent-original_latent).norm().item(),
                              elapsed_seconds=time.perf_counter()-start,
                              calls={k:engine.calls[k]-prior_calls[k] for k in prior_calls}))
    engine.restore(ref_state)
    return candidates,proposals
