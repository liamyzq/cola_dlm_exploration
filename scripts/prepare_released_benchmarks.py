"""Recover fixed capability inputs from pinned official evaluation artifacts.

Only IDs, prompts, and gold answers enter selection. Released predictions are
not used. This is a release-fixture subset, not the full original benchmark.
"""
import argparse
import json
from pathlib import Path
import subprocess
from tokenizers import Tokenizer
from cola_dlm.inference import apply_prompt_template


def recover_inputs(upstream, task, count=128):
    path=Path(upstream)/'eval_output/tasks_default'/f'{task}.jsonl'
    # Discard released predictions before sorting or selecting records.
    source=[]
    for line in path.read_text().splitlines():
        x=json.loads(line)
        source.append(dict(id=x['id'],prompt=x.get('few_shot_prefix','')+x['prompt'],answer=x['ground_truth']))
    source.sort(key=lambda x:x['id'])
    selected=source[:count]
    assert len(selected)==count and len({x['id'] for x in selected})==count
    for x in selected:
        full=x.pop('prompt')
        if task=='lambada':
            x.update(question=full,context='')
        else:
            current=full.rsplit('\n\nContext: ',1)[1]
            context,question=current.rsplit('\nQuestion: ',1)
            assert question.endswith('\nAnswer:')
            x.update(context=context,question=question[:-len('\nAnswer:')])
        rebuilt=apply_prompt_template(task,x['context'],x['question'],x['answer'],None)
        assert rebuilt==full, ('Official prompt reconstruction differs',task,x['id'])
        x.update(task=task,prompt=full,source_file=str(path))
    return selected


def main(a):
    out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    tok=Tokenizer.from_file(a.tokenizer)
    summary=dict(source_revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=a.upstream,text=True).strip(),
                 input_origin='Pinned released evaluation fixtures; original generated predictions excluded',
                 selection='First 128 IDs in sorted order within each task; no accuracy filtering',tasks={})
    for task in ('lambada','squad'):
        rows=recover_inputs(a.upstream,task)
        metadata=[]
        for x in rows:
            p=tok.encode(x['prompt']).ids
            whole=tok.encode(x['prompt']+' '+x['answer']).ids
            assert whole[:len(p)]==p, ('Gold suffix retokenizes prompt boundary',task,x['id'])
            answer=whole[len(p):]
            m=len(p)%16;k=16-m if m else 16
            metadata.append(dict(id=x['id'],prompt_tokens=len(p),answer_tokens=len(answer),
                prompt_remainder=m,mixed_generated_positions=k if m else None,
                gold_answer_crosses_mixed=bool(m and len(answer)>k),
                official_allocated_total_positions=len(p)-m+32))
        with (out/f'{task}.jsonl').open('w') as f:
            for x in rows:f.write(json.dumps(x)+'\n')
        (out/f'{task}_positions.json').write_text(json.dumps(metadata,indent=2)+'\n')
        summary['tasks'][task]=dict(items=len(rows),ids=[x['id'] for x in rows],
            gold_answers_crossing_mixed=sum(x['gold_answer_crosses_mixed'] for x in metadata),
            prompt_tokens_range=[min(x['prompt_tokens'] for x in metadata),max(x['prompt_tokens'] for x in metadata)],
            official_total_above_512=sum(x['official_allocated_total_positions']>512 for x in metadata))
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:{m:v for m,v in x.items() if m!='ids'} for k,x in summary['tasks'].items()},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--upstream',required=True);p.add_argument('--tokenizer',required=True);p.add_argument('--output',required=True)
    main(p.parse_args())
