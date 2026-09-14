"""Uniform parser-v2 view of every saved idea-002 output, preserving raw scores."""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil
import subprocess
import time
from src.tasks.task_basin_data import normalize,parse_record,parse_sentence

SCORER_VERSION='task_basin_parser_v2'


def rescore(row,world,variant):
    parsed,repetition=parse_sentence(row['text'],world) if variant=='sentence' else parse_record(row['text'],world['keys'],world['domain'])
    status=['unparseable' if parsed[k] is None else 'correct' if parsed[k]==normalize(v,world['domain']) else 'valid_wrong' for k,v in zip(world['keys'],world['values'])]
    return dict(row,parsed=parsed,repetition=repetition,status=status,any_fact_changed=any(s!='correct' for s in status),scorer_version=SCORER_VERSION)


def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--worlds',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();started=time.monotonic();out=Path(a.output);out.mkdir(parents=True,exist_ok=False)
    worlds={w['world_id']:w for w in map(json.loads,Path(a.worlds).read_text().splitlines())}
    events=list(map(json.loads,Path(a.ledger).read_text().splitlines()));jobs={r['job_id']:r for r in events if r.get('event')=='submitted' and r['experiment'].startswith('002-')}
    reports=[]
    for job in jobs.values():
        source=Path(job['artifact_dir']);target=out/source.name;measure=source/'measurements'
        assert (source/'exit.txt').read_text().strip()=='0',str(source)
        if not (measure/'records.jsonl').exists():
            target.symlink_to(source,target_is_directory=True)
            reports.append(dict(source=str(source),view=str(target),action='unchanged reference: no parser-scored record table'))
            continue
        target.mkdir();dest=target/'measurements';dest.mkdir()
        for filename in ['launch.json','exit.txt']:
            if (source/filename).exists():shutil.copy2(source/filename,target/filename)
        for filename in ['config.json','summary.json']:shutil.copy2(measure/filename,dest/filename)
        if (measure/'latents').exists():(dest/'latents').symlink_to(measure/'latents',target_is_directory=True)
        config=json.loads((measure/'config.json').read_text());variant=config.get('variant','record');tables=[]
        for filename in ['records.jsonl','anchors.jsonl']:
            if not (measure/filename).exists():continue
            transitions=Counter();changed_rows=0;total_damage_changes=0;count=0
            with (dest/filename).open('w') as stream:
                for line in (measure/filename).open():
                    old=json.loads(line);new=rescore(old,worlds[old['world_id']],variant);count+=1
                    changed_rows+=old['status']!=new['status']
                    for before,after in zip(old['status'],new['status']):
                        if before!=after:transitions[before+' -> '+after]+=1
                        total_damage_changes+=(before!='correct')!=(after!='correct')
                    if filename=='anchors.jsonl' and old['paired_clean']:assert new['status']==['correct','correct']
                    stream.write(json.dumps(new)+'\n')
            if filename=='records.jsonl':assert count==json.loads((measure/'summary.json').read_text())['records']
            tables.append(dict(table=filename,rows=count,changed_rows=changed_rows,field_transitions=dict(transitions),total_damage_changes=total_damage_changes))
        reports.append(dict(source=str(source),view=str(target),action='rescored all rows',original_model_commit=job['commit'],tables=tables))
    manifest=dict(scorer_version=SCORER_VERSION,scorer_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        rule_change='Reject standalone of, coordinating and/or, and dangling apostrophe-s entity values. Other lexical entity labels remain literal parsed labels, not evidence of plausible person identity.',
        raw_outputs_preserved=True,model_generations_repeated=False,elapsed_seconds=time.monotonic()-started,runs=reports)
    (out/'rescore_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(dict(runs=len(reports),record_rows=sum(t['rows'] for r in reports for t in r.get('tables',[]) if t['table']=='records.jsonl'),changed_fields=sum(sum(t['field_transitions'].values()) for r in reports for t in r.get('tables',[])),total_damage_changes=sum(t['total_damage_changes'] for r in reports for t in r.get('tables',[])),elapsed_seconds=manifest['elapsed_seconds'])))

if __name__=='__main__':main()
