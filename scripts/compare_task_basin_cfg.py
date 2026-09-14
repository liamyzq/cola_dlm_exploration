"""Supplementary CFG comparison restricted to the same predefined worlds."""
import argparse
import json
from pathlib import Path
from scripts.analyze_task_basin import effects,clustered,read_records


def compare(main_rows,control_rows):
    control_worlds={r['world_id'] for r in control_rows}
    main_rows=[r for r in main_rows if r['world_id'] in control_worlds]
    assert len(control_worlds)==64 and len(main_rows)==len(control_rows)==20480
    key=lambda r:(r['world_id'],r['query'],r['noise_fraction'],r['seed_id'],r['kind'],r['rotation_id'])
    main_keys={key(r):r for r in main_rows};assert set(main_keys)=={key(r) for r in control_rows}
    assert all(main_keys[key(r)]['noise_seed']==r['noise_seed'] and main_keys[key(r)]['rotation_seed']==r['rotation_seed'] for r in control_rows)
    baseline=effects(main_rows,'recovery');control=effects(control_rows,'recovery');contrasts=[]
    for b,c in zip(baseline,control):
        assert b['point']==c['point'];est={}
        for name in ['G_critical','G_noncritical','G_selective']:
            br={r['world_id']:r for r in b['estimates'][name]['world_values']}
            values=[dict(r,value=r['value']-br[r['world_id']]['value']) for r in c['estimates'][name]['world_values'] if r['world_id'] in br]
            est[name]=clustered(values)
        contrasts.append(dict(point=b['point'],cfg7_minus_cfg1=est))
    return dict(scope='Supplementary paired comparison on the 64 prespecified control worlds; no new confirmatory endpoint.',cfg1_matched=baseline,cfg7=control,contrasts=contrasts)


def main():
    p=argparse.ArgumentParser();p.add_argument('--main-inputs',nargs='+',required=True);p.add_argument('--control-inputs',nargs='+',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();result=compare(read_records(a.main_inputs),read_records(a.control_inputs));Path(a.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(control_worlds=64,points=len(result['contrasts']))))

if __name__=='__main__':main()
