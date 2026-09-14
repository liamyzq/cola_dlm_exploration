"""Decision-relevant P0 checks required by the idea 002 protocol."""
import argparse
import json
from pathlib import Path
import time
import torch
from src.models.cola_basin import ColaBasin
from src.tasks.task_basin_data import normalize, parse_record, named_seed, text_parts


def parser_cases():
    # Twenty explicit cases per domain, repeated with a second registered key pair.
    numbers=[
      ('Red: 7; Blue: 9.',('7','9')),(' blue=09\nRED : 07.0 ',('7','9')),
      ('Red: +7; Blue: 9.0',('7','9')),('Red: -7; Blue: 9',('-7','9')),
      ('Red: 7.5; Blue: 9',('7.5','9')),('Red: .7; Blue: 9',('0.7','9')),
      ('Red: 8; Blue: 6',('8','6')),('Red: 7; Red: 07; Blue: 9',('7','9')),
      ('Red: 7; Red: 8; Blue: 9',(None,'9')),('Red: 7',('7',None)),
      ('Blue: 9',(None,'9')),('',(None,None)),('7; 9',(None,None)),
      ('Red: not 7; Blue: 9',(None,'9')),('Not Red: 7; Blue: 9',(None,'9')),
      ('Red: 7 points; Blue: 9',(None,'9')),('Red: 7<|endoftext|>; Blue: 9',(None,'9')),
      ('Red: 7,5; Blue: 9',(None,'9')),('Red: 7; Blue: -9',('7','-9')),
      ('The red team scored 7 points. Blue: 9.',(None,None))]
    names=[
      ('Red: Alice; Blue: Bob.',('alice','bob')),(' blue=BOB\nRED : alice ',('alice','bob')),
      ('Red: "Alice"; Blue: Bob',('alice','bob')),('Red: Alicia; Blue: Bob',('alicia','bob')),
      ('Red: Carol; Blue: David',('carol','david')),('Red: Alice; Red: ALICE; Blue: Bob',('alice','bob')),
      ('Red: Alice; Red: Carol; Blue: Bob',(None,'bob')),('Red: Alice',('alice',None)),
      ('Blue: Bob',(None,'bob')),('',(None,None)),('Alice; Bob',(None,None)),
      ('Red: not Alice; Blue: Bob',(None,'bob')),('Not Red: Alice; Blue: Bob',(None,'bob')),
      ('Red: 7; Blue: Bob',(None,'bob')),('Red: Alice<|endoftext|>; Blue: Bob',(None,'bob')),
      ('Red: Alice; Blue: Bob; Blue: Carol',('alice',None)),('Red: (Alice); Blue: Bob',('alice','bob')),
      ('Red: Alice; Blue: B0b',('alice',None)),('Red: Alice; Blue:   Bob  ',('alice','bob')),
      ('Alice captains the red team. Bob captains the blue team.',(None,None))]
    result=[]
    for domain,cases in [('number',numbers),('entity',names)]:
        for keys in [('red','blue'),('east','west')]:
            for text,expected in cases:
                text=text.replace('Red',keys[0].capitalize()).replace('RED',keys[0].upper()).replace('red',keys[0])
                text=text.replace('Blue',keys[1].capitalize()).replace('BLUE',keys[1].upper()).replace('blue',keys[1])
                actual,repeat=parse_record(text,keys,domain)
                row=dict(domain=domain,text=text,expected=expected,actual=[actual[k] for k in keys],repetition=repeat)
                assert tuple(row['actual'])==expected,row
                result.append(row)
    assert len(result)==80
    return result


def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',required=True); p.add_argument('--output',required=True)
    args=p.parse_args(); config=json.loads(Path(args.config).read_text()); out=Path(args.output); out.mkdir(parents=True,exist_ok=True)
    (out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    cases=parser_cases(); (out/'parser_cases.json').write_text(json.dumps(cases,indent=2)+'\n')
    worlds=[json.loads(line) for line in Path(config['worlds']).read_text().splitlines() if json.loads(line)['split']=='smoke']
    started=time.monotonic(); model=ColaBasin(config['checkpoint'])
    rows=[]; strict=True
    with (out/'checks.jsonl').open('w') as stream:
        for world in worlds:
            for query in (0,1):
                layout=world['layouts'][query]; start=layout['prefix_length']; length=layout['answer_length']
                clean=model.encode(layout['full_ids'])
                with torch.no_grad():
                    full=model.decode(clean)
                    raw=full[start:start+length]
                    cached=model.decode_cached(clean,start,length)
                    repeated=model.decode(clean,start,length)
                    noise=model.gaussian((length,16),named_seed(world,1,0))
                    changed=clean.clone(); changed[start:start+length]+=0.1*noise
                    after=model.decode(changed)
                if query==0:
                    first_clean=clean.clone(); first_logits=raw.clone()
                else:
                    with torch.no_grad():
                        abba=model.decode(first_clean,world['layouts'][0]['prefix_length'],world['layouts'][0]['answer_length'])
                    strict &= torch.equal(abba,first_logits)
                record=dict(world_id=world['world_id'],domain=world['domain'],query=query,
                    clean_exact=raw.argmax(-1).tolist()==layout['answer_ids'],
                    repeat_exact=torch.equal(raw,repeated),
                    cached_max_abs=float((raw-cached).abs().max()),
                    cached_ids_exact=torch.equal(raw.argmax(-1),cached.argmax(-1)),
                    prefix_logits_exact=torch.equal(full[:start],after[:start]),endpoints=[])
                for field in (0,1):
                    ids=layout['prefix_ids']+layout['target_ids'][field]+layout['full_ids'][start+length:]
                    target=model.encode(ids)
                    with torch.no_grad():
                        hybrid=clean.clone(); hybrid[start:start+length]=target[start:start+length]
                        target_logits=model.decode(hybrid,start,length)
                    record['endpoints'].append(dict(field=field,prefix_latents_exact=torch.equal(target[:start],clean[:start]),
                        target_exact=target_logits.argmax(-1).tolist()==layout['target_ids'][field]))
                # Full-precision derivative avoids BF16 quantization hiding small finite differences.
                if query==0:
                    z=clean.detach().clone().requires_grad_(True)
                    pos=layout['field_positions'][0]; original=layout['answer_ids'][pos]; alternative=layout['target_ids'][0][pos]
                    logits=model.decode(z,start,length,fp32=True)
                    margin=logits[pos,original]-logits[pos,alternative]
                    grad=torch.autograd.grad(margin,z)[0]
                    direction=torch.zeros_like(z); g=grad[start:start+length]; direction[start:start+length]=g/g.norm()
                    derivative=float((grad*direction).sum()); eps=0.01
                    with torch.no_grad():
                        plus=model.decode(clean+eps*direction,start,length,fp32=True)
                        minus=model.decode(clean-eps*direction,start,length,fp32=True)
                        finite=float(((plus[pos,original]-plus[pos,alternative])-(minus[pos,original]-minus[pos,alternative]))/(2*eps))
                    record['gradient']=dict(norm=float(g.norm()),finite_difference=finite,autograd_direction=derivative,
                        relative_error=abs(finite-derivative)/max(abs(derivative),1e-12),parameters_frozen=all(not x.requires_grad for x in model.vae.parameters()))
                    strict &= bool(torch.isfinite(grad).all() and derivative>0 and abs(finite-derivative)/derivative<0.15)
                    del logits,z,grad
                strict &= record['repeat_exact'] and record['cached_ids_exact'] and record['prefix_logits_exact']
                strict &= all(r['prefix_latents_exact'] for r in record['endpoints'])
                rows.append(record); stream.write(json.dumps(record)+'\n'); stream.flush()
                print(json.dumps(record),flush=True)
        model.load_dit()
        w=worlds[0]; layout=w['layouts'][0]; clean=model.encode(layout['full_ids']); start=layout['prefix_length']; length=layout['answer_length']
        noise=model.gaussian(clean[start:].shape,named_seed(w,2,0))
        recovered=model.recover(clean,start,noise,12,1.)
        identity=model.recover(clean,start,noise,16,1.)
        e=recovered[start:start+length]-clean[start:start+length]
        rot=model.rotation(named_seed(w,3,0)); er=e@rot
        gram_error=float((e@e.T-er@er.T).abs().max()); gram_scale=max(float((e@e.T).abs().max()),1.)
        # Compare the first recovered full-noise block with the established native engine.
        from types import SimpleNamespace
        from src.models.cola_state import ColaStateEngine
        native_result=model.recover(clean,start,noise,0,7.)
        begin=start//16*16; known=start-begin
        for block in model.dit.blocks:
            block.set_kv_cache(True)
        if begin:
            with torch.no_grad(), model.precision():
                model.dit(txt=clean[:begin].to(torch.bfloat16),txt_shape=model.shape(begin),txt_q_shape=model.shape(begin),timestep=torch.zeros(begin,device=model.device,dtype=torch.bfloat16),update_kv=True,use_kv_cache=True)
        proxy=SimpleNamespace(device=model.device,position=begin,step=0,first_mask=torch.arange(16,device=model.device)<known,first_latent=clean[begin:begin+16],timesteps=model.timesteps,dit=model.dit,cfg=7.,qshape=model.shape(16),shape=model.shape,calls=model.counts)
        initial=torch.zeros((16,16),device=model.device); initial[known:]=noise[:16-known]
        native_block=ColaStateEngine.sample_block(proxy,initial)
        parity=torch.equal(native_block,native_result[begin:begin+16])
        strict &= parity
        recovery=dict(native_euler_first_block_exact=parity,prefix_exact=torch.equal(recovered[:start],clean[:start]),zero_time_exact=torch.equal(identity,clean),
            gram_relative_error=gram_error/gram_scale,orthogonal_error=float((rot.T@rot-torch.eye(16,device=model.device)).abs().max()),
            timestamps=model.timesteps.tolist(),residual_rms=float(e.square().mean().sqrt()),counts=model.counts)
        strict &= recovery['prefix_exact'] and recovery['zero_time_exact'] and recovery['gram_relative_error']<1e-5
        summary=dict(checks_passed=bool(strict),worlds=len(worlds),parser_cases=len(cases),clean_anchors=sum(r['clean_exact'] for r in rows),
            paired_clean_worlds=sum(all(r['clean_exact'] for r in rows if r['world_id']==w['world_id']) for w in worlds),
            target_endpoints=sum(e['target_exact'] for r in rows for e in r['endpoints']),recovery=recovery,
            elapsed_seconds=time.monotonic()-started,peak_memory_gb=torch.cuda.max_memory_allocated()/1e9)
        (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary),flush=True)
        assert strict,'P0 measurement checks failed; see checks.jsonl and summary.json'

if __name__=='__main__':
    main()
