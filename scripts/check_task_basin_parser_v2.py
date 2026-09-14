import json
from pathlib import Path
from scripts.check_task_basin import parser_cases
from src.tasks.task_basin_data import normalize
from scripts.rescore_task_basin import rescore
assert len(parser_cases())==80
for value in ['Emma and','Bob and','Oscar and',"Alice's",'of','Alice or Bob']:assert normalize(value,'entity') is None,value
for value,expected in [('Will','will'),('Nora','nora'),('Anderson','anderson'),("O'Neil","o'neil")]:assert normalize(value,'entity')==expected,value
base=Path('/home/mlw0719/cola_dlm_exploration_storage/runs/002_task_consequence_basin/analysis-v1/blind_audit_v1')
worlds={w['world_id']:w for w in map(json.loads,Path('/home/mlw0719/cola_dlm_exploration_storage/datasets/002_task_consequence_basin/v1/worlds.jsonl').read_text().splitlines())}
key={r['audit_id']:r for r in map(json.loads,(base/'audit_key.jsonl').read_text().splitlines())}
labels={r['audit_id']:r for r in map(json.loads,Path('experiments/002_task_consequence_basin/reviews/blind_labels_v1.jsonl').read_text().splitlines())}
checked=[]
for item in map(json.loads,(base/'blind_items.jsonl').read_text().splitlines()):
 k=key[item['audit_id']];new=rescore(dict(text=item['output']),worlds[k['world_id']],'sentence' if k['cohort']=='sentence' else 'record')
 assert new['status']==labels[item['audit_id']]['expected_field_status'],dict(item=item,new=new,expected=labels[item['audit_id']])
 checked.append(dict(audit_id=item['audit_id'],original_status=k['parser_status'],corrected_status=new['status'],expected_status=labels[item['audit_id']]['expected_field_status']))
result=dict(original_parser_cases=80,additional_entity_cases=10,blind_items=100,blind_field_agreements=200,items=checked)
(base/'comparison_after_correction.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:80 original cases,10 incomplete/complete-name cases,100 blinded items /200 fields agree after correction.')
