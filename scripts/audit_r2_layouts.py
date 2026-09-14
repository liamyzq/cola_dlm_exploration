from pathlib import Path
import json,os
from tokenizers import Tokenizer
from src.tasks.route_diagnostics import trunk_prefix_status
r=Path('/home/mlw0719/cola_dlm_exploration');base=Path('/home/mlw0719/cola_dlm_exploration_storage/runs/001_same_prefix_state');tok=Tokenizer.from_file(os.environ['COLA_CHECKPOINT']+'/tokenizer.json');out=[]
for cell in ('copy','chain','branch','matched-full'):
 tasks=json.loads((base/f'001-r2-{cell}-v1/evaluation/tasks.json').read_text());records=[]
 for task in tasks:
  trim=task['prompt_tokens']%16;first=16-trim if trim else 16
  first_full=first+(16 if trim else 0);ids=tok.encode(' '+' -> '.join(task['solution'])+'.').ids
  def status(n):return 'answer_ends_before_boundary' if len(ids)<n else trunk_prefix_status(task,tok.decode(ids[:n],skip_special_tokens=False))
  records.append(dict(task_id=task['id'],prompt_remainder=trim,canonical_answer_tokens=len(ids),trunk_tokens=len(tok.encode(' '+' -> '.join(task['trunk'])).ids),first_full_boundary=first_full,canonical_full_status=status(first_full),canonical_mixed_status=status(first) if trim else 'aligned_prompt_no_mixed'))
 summary=dict(cell=cell,tasks=len(tasks),canonical_full_eligible=sum(x['canonical_full_status']=='eligible' for x in records),canonical_mixed_eligible=sum(x['canonical_mixed_status']=='eligible' for x in records),trunk_tokens_range=[min(x['trunk_tokens'] for x in records),max(x['trunk_tokens'] for x in records)],answer_tokens_range=[min(x['canonical_answer_tokens'] for x in records),max(x['canonical_answer_tokens'] for x in records)],records=records)
 out.append(summary)
(r/'experiments/001_same_prefix_state/results/r2_canonical_layouts_v1.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps([{k:v for k,v in x.items() if k!='records'} for x in out],indent=2))
