"""Validate the real A/B runner's independent splits and identity null."""
import argparse,json,os
from pathlib import Path
from unittest.mock import patch
import torch
from src.models.cola_state import ColaStateEngine
from src.tasks.natural_state_study import measure_pair

@torch.inference_mode()
def run(out):
    out.mkdir(parents=True,exist_ok=False)
    path=Path('/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state/001-r3-payload-smoke-v1/checks/M.pt')
    payload=torch.load(path,map_location='cpu',weights_only=True)
    cfg=dict(samples_a=2,samples_b=2,noise_seed_a=310000000,noise_seed_b=410000000,future_tokens=32)
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT']);calls=[];original=engine.continue_from
    def capture(state,noise):
        calls.append(noise.cpu().clone());return original(state,noise)
    with patch.object(engine,'continue_from',capture):
        result=measure_pair(engine,payload,cfg,out)
    assert len(calls)==8
    assert torch.equal(calls[0],calls[2]) and torch.equal(calls[1],calls[3])
    assert torch.equal(calls[4],calls[6]) and torch.equal(calls[5],calls[7])
    assert not torch.equal(calls[0],calls[4]) and not torch.equal(calls[0],calls[1])
    identity=dict(payload,candidate_latents=payload['candidate_latents'][[0,0]])
    identity_out=out/'identity';identity_out.mkdir()
    null=measure_pair(engine,identity,dict(cfg,samples_a=1,samples_b=1),identity_out)
    assert null['h_token']==0.
    report=dict(status='pass',paired_noise_within_splits=True,independent_split_noise=True,identity_h_token=0.,real_pair=result)
    (out/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);run(Path(p.parse_args().output))
