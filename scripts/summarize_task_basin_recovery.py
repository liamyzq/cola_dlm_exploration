"""Completed recovery pairing, support diagnostics, and primary-test accounting."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from scripts.analyze_task_basin import effects,read_records


def summarize(rows,expected_worlds):
    keys=[(r['world_id'],r['query'],r['noise_fraction'],r['seed_id'],r['kind'],r['rotation_id']) for r in rows]
    assert len(keys)==len(set(keys))==expected_worlds*2*4*8*5
    worlds={r['world_id'] for r in rows};assert len(worlds)==expected_worlds
    grouped=defaultdict(list)
    for r in rows:grouped[(r['world_id'],r['noise_fraction'],r['seed_id'])].append(r)
    max_rms_difference=0.
    for key,group in grouped.items():
        assert len(group)==10 and len({r['noise_seed'] for r in group})==1
        for q in (0,1):
            rs=[r for r in group if r['query']==q];real=[r for r in rs if r['kind']=='real'];rot=[r for r in rs if r['kind']=='rotated']
            assert len(real)==1 and {r['rotation_id'] for r in rot}=={0,1,2,3}
            for r in rot:
                difference=abs(r['rms']-real[0]['rms']);max_rms_difference=max(max_rms_difference,difference)
                assert difference<=1e-5*max(1.,real[0]['rms'])
        for rot_id in range(4):
            assert len({r['rotation_seed'] for r in group if r['rotation_id']==rot_id})==1
    support=[]
    for point in sorted({r['noise_fraction'] for r in rows}):
        for kind in ('real','rotated'):
            rs=[r for r in rows if r['noise_fraction']==point and r['kind']==kind]
            support.append(dict(point=point,kind=kind,records=len(rs),
                **{field:dict(mean=float(np.mean([r[field] for r in rs])),quantiles=np.quantile([r[field] for r in rs],[0,.25,.5,.75,1]).tolist()) for field in ['rms','max_channel_abs','mean_decoder_entropy']}))
    return dict(integrity=dict(worlds=len(worlds),records=len(rows),unique_complete_keys=True,paired_noise_and_rotation_seeds=True,max_real_rotated_rms_difference=max_rms_difference),support=support)


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--expected-worlds',type=int,required=True);p.add_argument('--output',required=True)
    a=p.parse_args();result=summarize(read_records(a.inputs),a.expected_worlds)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['integrity']))

if __name__=='__main__':main()
