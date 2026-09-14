from pathlib import Path
from collections import Counter
import json,shutil
b=Path('/home/mlw0719/cola_dlm_exploration_storage');run=b/'runs/002_task_consequence_basin';repo=b/'worktrees/002-development';f=run/'rescored-v2/002-control-source_recoverability-v1/measurements/records.jsonl';rows=[json.loads(x) for x in f.read_text().splitlines()]
summary=dict(source=str(f),scorer_commit='52244c9c04a2e4628bd2a4b7678e5a55b0d6d812',worlds=len({r['world_id'] for r in rows}),records=len(rows),conditions={})
for kind in ['zero','high_noise']:
 rs=[r for r in rows if r['kind']==kind];counts=Counter(s for r in rs for s in r['status']);summary['conditions'][kind]=dict(records=len(rs),fields=2*len(rs),correct_fields=counts['correct'],valid_wrong_fields=counts['valid_wrong'],unparseable_fields=counts['unparseable'],by_domain={d:dict(records=len([r for r in rs if r['domain']==d]),correct_fields=sum(s=='correct' for r in rs if r['domain']==d for s in r['status'])) for d in ['number','entity']})
out=run/'analysis-v2/source_recoverability_v2.json';out.write_text(json.dumps(summary,indent=2)+'\n');dest=repo/'experiments/002_task_consequence_basin/results/final_v2';shutil.copy2(out,dest/out.name)
shutil.copy2(Path(__file__),dest/'summarize_source_recoverability.py')
f=repo/'experiments/002_task_consequence_basin/results/FINAL_REPORT.md';t=f.read_text().replace('This diagnostic provides no source-only decoder-repair evidence.','The [corrected source-recovery summary](final_v2/source_recoverability_v2.json) provides no source-only decoder-repair evidence.');f.write_text(t)
f=repo/'experiments/002_task_consequence_basin/reviews/CORE_COMPLETION_AUDIT.md';t=f.read_text().replace('Final control JSONs plus original `interpretation_controls_v1.json`','Final control JSONs including corrected `source_recoverability_v2.json`');t+='\nThe bounded subagent coverage review found every required execution group complete. Its sole reporting finding, the missing corrected compact source-recoverability summary, was resolved from the retained v2 records; no new model run or scientific setting was needed.\n';f.write_text(t)
print(json.dumps(summary))
