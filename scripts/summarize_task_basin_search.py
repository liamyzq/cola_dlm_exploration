"""Aggregate fixed-search success curves without imputing failed distances."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np
from scripts.analyze_task_basin import clustered, read_records


def summarize(rows,sigma):
    result=[]
    for mode,key in [('ray','ray_minimum_found_rms'),('combined','minimum_found_rms')]:
        for radius in [sigma,2*sigma,4*sigma]:
            for population in ['paired_clean','all_fixed']:
                groups=defaultdict(list)
                selected=[r for r in rows if population=='all_fixed' or r['paired_clean']]
                for r in selected:
                    success=r[key] is not None and r[key]<=radius
                    groups[r['world_id']].append((r,success))
                values=[];critical=[];noncritical=[]
                for w,group in groups.items():
                    crit=[int(s) for r,s in group if r['query']==r['field']]
                    non=[int(s) for r,s in group if r['query']!=r['field']]
                    assert len(crit)==len(non)==2
                    m=group[0][0];values.append(dict(world_id=w,domain=m['domain'],template=m['template'],value=float(np.mean(non)-np.mean(crit))))
                    critical.extend(crit);noncritical.extend(non)
                result.append(dict(mode=mode,radius=radius,population=population,estimate=clustered(values),
                    critical_success=float(np.mean(critical)) if critical else None,noncritical_success=float(np.mean(noncritical)) if noncritical else None))
    paired=[]
    groups=defaultdict(dict)
    for r in rows:
        if r['paired_clean']:groups[(r['world_id'],r['field'])][r['query']]=r
    for (w,field),group in groups.items():
        a,b=group[field]['minimum_found_rms'],group[1-field]['minimum_found_rms']
        if a is not None and b is not None and a>0 and b>0:
            paired.append(np.log(a)-np.log(b))
    return dict(curves=result,targets=len(rows),paired_both_success_edits=len(paired),
        eligible_paired_edits=len(groups),median_log_critical_over_noncritical=float(np.median(paired)) if paired else None,
        failed_searches=sum(r['minimum_found_rms'] is None for r in rows),
        endpoint_exact=sum(r['endpoint_exact'] for r in rows),
        backward_steps=sum(r['backward_steps'] for r in rows),
        native_verifications=sum(r['native_verifications'] for r in rows))


def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--sigma',type=float,required=True);p.add_argument('--output',required=True)
    a=p.parse_args();summary=summarize(read_records(a.inputs,'search_summary.jsonl'),a.sigma)
    Path(a.output).write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='curves'}))

if __name__=='__main__':main()
