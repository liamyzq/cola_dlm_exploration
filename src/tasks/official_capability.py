"""Pinned official capability generation, extraction, and paired engine checks."""
import argparse
import importlib.util
import json
import os
import subprocess
from pathlib import Path
import time
from unittest.mock import patch
import torch
import cola_dlm.inference as native
from src.models.cola_state import ColaStateEngine


def load_scorer():
    path=Path(os.environ['COLA_UPSTREAM'])/'scripts/acc_calc.py'
    spec=importlib.util.spec_from_file_location('pinned_cola_scorer',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def score_output(scorer,task,text,gold):
    processed=scorer.process_line({'generate':text})['generate']
    if task=='lambada':
        pred=scorer.get_first_word(processed);answer=scorer.get_first_word(gold)
        reward=int(pred==answer)
    else:
        pred=scorer.normalize_text(processed);answer=scorer.normalize_text(gold)
        reward=int(scorer.calculate_similarity(processed,gold)>=1.0)
    return dict(reward=reward,extracted_answer=pred,normalized_gold=answer,answer_line=processed)


@torch.inference_mode()
def native_sample(engine,item,cfg,paired=False):
    ids=[];noises=[]
    sample_fn=native.sample_with_strategies
    randn=torch.randn
    def capture_ids(*args,**kwargs):
        result=sample_fn(*args,**kwargs);ids.extend(result[0].tolist());return result
    def capture_noise(*args,**kwargs):
        result=randn(*args,**kwargs)
        if args==(16,16):noises.append(result.clone())
        return result
    os.environ['COLA_INFER_PER_SAMPLE_NOISE_SEED']=str(cfg['noise_seed'])
    torch.cuda.synchronize();start=time.perf_counter()
    with patch.object(native,'sample_with_strategies',capture_ids):
        if paired:
            with patch.object(torch,'randn',capture_noise):
                result=native.generate_task_repaint_inference(engine.dit,engine.vae,engine.tokenizer,
                    [item],task_name=item['task'],device=engine.device,
                    timestep_num=cfg['euler_steps'],guidance_scale=cfg['cfg'],
                    max_new_tokens=cfg['max_new_tokens'],temperature=cfg['temperature'],top_k=cfg['top_k'],top_p=cfg['top_p'],
                    repetition_penalty=cfg['repetition_penalty'],pad_token_id=cfg['pad_token_id'],
                    eos_token_id=cfg['eos_token_id'],im_end_token_id=cfg['im_end_token_id'])[0]
        else:
            result=native.generate_task_repaint_inference(engine.dit,engine.vae,engine.tokenizer,
                [item],task_name=item['task'],device=engine.device,
                timestep_num=cfg['euler_steps'],guidance_scale=cfg['cfg'],
                max_new_tokens=cfg['max_new_tokens'],temperature=cfg['temperature'],top_k=cfg['top_k'],top_p=cfg['top_p'],
                repetition_penalty=cfg['repetition_penalty'],pad_token_id=cfg['pad_token_id'],
                eos_token_id=cfg['eos_token_id'],im_end_token_id=cfg['im_end_token_id'])[0]
    torch.cuda.synchronize();seconds=time.perf_counter()-start
    assert result['prompt']==item['prompt']
    trim=len(engine.tokenizer.encode(item['prompt']).ids)%16
    generated=tuple(ids[trim:])
    assert engine.text(generated)==result['generate']
    blocks=len(ids)//16
    assert blocks in (1,2)
    if paired:assert len(noises)==blocks, 'Native initial-noise capture mismatch'
    return result,generated,noises,seconds,blocks


@torch.inference_mode()
def paired_wrapper(engine,item,cfg,expected_ids,noises):
    engine.repetition_penalty=cfg['repetition_penalty']
    engine.begin(item['prompt'])
    torch.cuda.synchronize();start=time.perf_counter();before=engine.calls.copy()
    first=None
    for noise in noises:
        engine.advance(noise)
        if first is None:first=engine.snapshot()
    torch.cuda.synchronize();seconds=time.perf_counter()-start
    assert engine.generated_ids==expected_ids, ('Native/wrapper token mismatch',item['task'],item['id'])
    final=engine.snapshot()
    if len(noises)>1:
        resumed=engine.continue_from(first,torch.stack(noises[1:]))
        assert resumed==expected_ids,'Penalty-aware resume mismatch'
        engine.rebuild(first)
        assert engine.decoder_ids==first.decoder_ids,'Penalty context reconstruction mismatch'
        assert engine.continue_from(engine.snapshot(),torch.stack(noises[1:]))==expected_ids
    engine.restore(final)
    return dict(exact_token_parity=True,resume_and_rebuild=True,
                penalty_context_tokens=len(final.decoder_ids),wrapper_seconds=seconds,
                wrapper_calls_including_replay={k:engine.calls[k]-before[k] for k in before})


def run(a):
    cfg=json.loads(Path(a.config).read_text())
    assert cfg['temperature']==0.0, 'Wrapper supports greedy decoding only'
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=os.environ['COLA_UPSTREAM'],text=True).strip()==cfg['source_revision']
    assert json.loads((Path(cfg['data_dir'])/'summary.json').read_text())['source_revision']==cfg['source_revision']
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    scorer=load_scorer()
    reused={}
    if not a.smoke:
        for line in Path(cfg['reuse_native_records']).read_text().splitlines():
            record=json.loads(line)
            reused[(record['task'],record['index'])]=record
        assert len(reused)==8
    engine=ColaStateEngine(os.environ['COLA_CHECKPOINT'],steps=cfg['euler_steps'],
                          cfg=cfg['cfg'],repetition_penalty=cfg['repetition_penalty'])
    with (out/'samples.jsonl').open('w') as f:
        for task in ('lambada','squad'):
            items=[json.loads(x) for x in (Path(cfg['data_dir'])/f'{task}.jsonl').read_text().splitlines()]
            assert len(items)==128
            for index,item in enumerate(items):
                if a.smoke and index not in cfg['paired_indices'][task]:continue
                if not a.smoke and index%a.shards!=a.shard:continue
                if not a.smoke and (task,index) in reused:
                    result=dict(reused[(task,index)],reused_from=cfg['reuse_native_records'],
                                native_implementation_commit=cfg['reuse_implementation_commit'])
                    assert result['id']==item['id']
                    f.write(json.dumps(result)+'\n');f.flush()
                    continue
                paired=a.smoke
                native_result,ids,noises,seconds,blocks=native_sample(engine,item,cfg,paired)
                result=dict(task=task,index=index,id=item['id'],generated_ids=ids,
                    text=native_result['generate'],native_seconds=seconds,blocks=blocks,
                    prompt_tokens=len(engine.tokenizer.encode(item['prompt']).ids),
                    **score_output(scorer,task,native_result['generate'],item['answer']))
                if paired:
                    torch.save(torch.stack(noises).cpu(),out/f'noise-{task}-{index}.pt')
                    try:
                        result['parity']=paired_wrapper(engine,item,cfg,ids,noises)
                    except AssertionError as error:
                        (out/'parity_failure.json').write_text(json.dumps(dict(native=result,
                            wrapper_ids=engine.generated_ids,error=str(error)),indent=2)+'\n')
                        raise
                f.write(json.dumps(result)+'\n');f.flush()
                print(json.dumps({k:result[k] for k in ('task','index','reward','native_seconds','blocks')}),flush=True)
        if a.smoke:
            # One unchanged default-setting control for the newly added history.
            control=dict(cfg,repetition_penalty=1.0)
            item=json.loads((Path(cfg['data_dir'])/'lambada.jsonl').read_text().splitlines()[0])
            _,ids,noises,_,_=native_sample(engine,item,control,True)
            check=paired_wrapper(engine,item,control,ids,noises)
            (out/'default_penalty_control.json').write_text(json.dumps(check,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--output',required=True)
    p.add_argument('--smoke',action='store_true');p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    run(p.parse_args())
