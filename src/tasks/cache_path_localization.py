"""Bounded cache-path counterfactuals on eight fixed development pairs."""
import argparse,json,os,time
from pathlib import Path
import torch
from src.models.cola_state import ColaStateEngine,symmetric_kl
from src.methods.token_distribution import token_heterogeneity,aggregate_distribution


def equal_cache(a,b):
    for layer_a,layer_b in zip(a,b):
        for xs,ys in zip(layer_a,layer_b):
            if (xs is None)!=(ys is None):return False
            if xs is not None and not all(torch.equal(x,y) for x,y in zip(xs,ys)):return False
    return True


@torch.inference_mode()
def run(a):
    cfg=json.loads(Path(a.config).read_text());out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    pairs=json.loads(Path(cfg['pair_manifest']).read_text())[:8]
    assert [x['root_id'] for x in pairs]==cfg['root_ids']
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    records=[]
    with (out/'roots.jsonl').open('w') as f:
        for entry in pairs:
            index=entry['root_id']
            if index%a.shards!=a.shard:continue
            payload=torch.load(entry['pair_file'],map_location='cpu',weights_only=True)
            pilot=Path(cfg['pilot_measurement']);raw=json.loads((pilot/f'future-root-{index}.json').read_text())
            noises=torch.load(pilot/f'noise-root-{index}.pt',map_location='cpu',weights_only=True)
            assert all(len(raw[s])==2 and len(raw[s][0])==cfg[f'samples_{s.lower()}'] for s in ('A','B'))
            assert all(noises[s].shape[:2]==(cfg[f'samples_{s.lower()}'],cfg['future_tokens']//16) for s in ('A','B'))
            torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
            engine.begin(payload['prompt'])
            for latent in payload['pre_generated_latents']:engine.commit(latent.to(engine.device))
            pre=engine.snapshot();zs=payload['candidate_latents'].to(engine.device)
            states={};logits={}
            # First label is the DiT input; second is the decoder input.
            for label,dit_index,decoder_index in [('reference',0,0),('native',1,1),('dit_only',1,0),('decoder_only',0,1)]:
                engine.restore(pre)
                _,q=engine.commit(zs[decoder_index],dit_latent=zs[dit_index])
                assert engine.generated_ids==tuple(payload['reference_generated_ids'])
                states[label]=engine.snapshot();logits[label]=q
            assert equal_cache(states['dit_only'].dit_cache,states['native'].dit_cache)
            assert equal_cache(states['dit_only'].decoder_cache,states['reference'].decoder_cache)
            assert equal_cache(states['decoder_only'].dit_cache,states['reference'].dit_cache)
            assert equal_cache(states['decoder_only'].decoder_cache,states['native'].decoder_cache)
            kl=symmetric_kl(logits['reference'],logits['native'])
            assert kl.sum().item()<=cfg['epsilon'] and kl.max().item()<=cfg['epsilon']/4
            anchor=len(payload['reference_generated_ids']);hybrids={};effects={}
            effects['native']=token_heterogeneity(raw['A'],raw['B'])
            for label in ('dit_only','decoder_only'):
                samples={}
                for split in ('A','B'):
                    samples[split]=[]
                    for noise in noises[split]:
                        ids=engine.continue_from(states[label],noise.to(engine.device))
                        assert ids[:anchor]==tuple(payload['reference_generated_ids'])
                        samples[split].append(ids[anchor:])
                effects[label]=token_heterogeneity([raw['A'][0],samples['A']],[raw['B'][0],samples['B']])
                hybrids[label]=samples
            torch.cuda.synchronize()
            record=dict(root_id=index,source_id=entry['source_id'],h_token=effects,
                changed_path_checks='pass',prefix_ids=payload['reference_generated_ids'],
                new_futures=16,reused_futures=16,seconds=time.perf_counter()-start,
                calls={k:engine.calls[k]-before[k] for k in before},pilot_measurement=str(pilot))
            (out/f'hybrid-future-root-{index}.json').write_text(json.dumps(hybrids)+'\n')
            records.append(record);f.write(json.dumps(record)+'\n');f.flush();print(json.dumps(record),flush=True)
    summary={label:aggregate_distribution([dict(source_id=x['source_id'],h_token=x['h_token'][label]) for x in records]) for label in ('native','dit_only','decoder_only')}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);run(p.parse_args())
