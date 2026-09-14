"""World-clustered calibration and core effects for idea 002."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import numpy as np


def read_records(paths,filename='records.jsonl'):
    rows=[]
    for path in paths:
        rows.extend(json.loads(line) for line in (Path(path)/filename).read_text().splitlines())
    return rows


def calibration(rows,stage):
    key='sigma' if stage=='noise' else 'noise_fraction'
    grouped=defaultdict(list)
    for row in rows:
        if row['paired_clean'] and (stage=='noise' or row['kind']=='real'):
            grouped[row[key]].append(row)
    values=[]
    for point,rs in sorted(grouped.items()):
        values.append(dict(point=point,lexical_disagreement=float(np.mean([r['token_disagreement'] for r in rs])),
            any_field_damage=float(np.mean([r['any_fact_changed'] for r in rs])),
            unparseable_fraction=float(np.mean([s=='unparseable' for r in rs for s in r['status']])),
            worlds=len({r['world_id'] for r in rs}),records=len(rs)))
    if not values:
        raise ValueError('No paired-clean development worlds')
    best=min(values,key=lambda r:(abs(r['lexical_disagreement']-.10),r['point']))
    nondegenerate=any(.03<=r['lexical_disagreement']<=.25 for r in values) if stage=='noise' else any(r['any_field_damage']>0 and r['unparseable_fraction']<.95 for r in values)
    return dict(stage=stage,selection='paired-clean lexical disagreement closest to 0.10; smaller point breaks ties',
                chosen_point=best['point'],measurement_range_valid=nondegenerate,grid=values,
                role_effects_used_for_selection=False)


def clustered(rows,draws=5000,seed=20260914):
    """Rows are one scalar per independent world; preserve domain/template strata."""
    if not rows:
        return dict(mean=None,ci95=None,worlds=0)
    rng=np.random.default_rng(seed)
    domains={}; boot_domains=[]
    for domain in ('number','entity'):
        rs=[r for r in rows if r['domain']==domain]
        if not rs:
            domains[domain]=dict(mean=None,ci95=None,worlds=0);continue
        samples=np.zeros(draws)
        for template in sorted({r['template'] for r in rs}):
            x=np.array([r['value'] for r in rs if r['template']==template])
            samples+=x[rng.integers(0,len(x),size=(draws,len(x)))].sum(-1)/len(rs)
        mean=float(np.mean([r['value'] for r in rs])); boot_domains.append(samples)
        domains[domain]=dict(mean=mean,ci95=np.quantile(samples,[.025,.975]).tolist(),worlds=len(rs))
    if len(boot_domains)!=2:
        return dict(mean=None,ci95=None,worlds=len(rows),domains=domains)
    boot=np.mean(boot_domains,axis=0)
    mean=float(np.mean([v['mean'] for v in domains.values()]))
    centered=boot-mean
    p=float((1+np.sum(np.abs(centered)>=abs(mean)))/(len(centered)+1))
    return dict(mean=mean,ci95=np.quantile(boot,[.025,.975]).tolist(),worlds=len(rows),domains=domains,
                centered_bootstrap_two_sided_p=p,nondegenerate_bootstrap=bool(np.std(boot)>0))


def effects(rows,stage):
    key='sigma' if stage=='noise' else 'noise_fraction'
    result=[]
    for point in sorted({r[key] for r in rows}):
        all_rows=[r for r in rows if r[key]==point]
        rs=[r for r in all_rows if r['paired_clean']]
        metrics=defaultdict(list)
        if stage=='noise':
            for r in rs:
                q=r['query']; s=r['status']
                for label,fn in [('protection',lambda t:t!='correct'),('value_protection',lambda t:t=='valid_wrong'),('unparseable_protection',lambda t:t=='unparseable')]:
                    metrics[(r['world_id'],label)].append(float(fn(s[1-q]))-float(fn(s[q])))
        else:
            groups=defaultdict(list)
            for r in rs:groups[(r['world_id'],r['query'],r['seed_id'])].append(r)
            for (world,q,seed),group in groups.items():
                real=next(r for r in group if r['kind']=='real');rot=[r for r in group if r['kind']=='rotated']
                assert len(rot)==4
                for suffix,fn in [('',lambda s:s!='correct'),('_valid_wrong',lambda s:s=='valid_wrong'),('_unparseable',lambda s:s=='unparseable')]:
                    crit=np.mean([fn(r['status'][q]) for r in rot])-float(fn(real['status'][q]))
                    non=np.mean([fn(r['status'][1-q]) for r in rot])-float(fn(real['status'][1-q]))
                    metrics[(world,'G_critical'+suffix)].append(crit);metrics[(world,'G_noncritical'+suffix)].append(non)
                    metrics[(world,'G_selective'+suffix)].append(crit-non)
        meta={r['world_id']:r for r in rs}
        estimates={}
        for label in sorted({label for world,label in metrics}):
            wr=[dict(world_id=w,domain=meta[w]['domain'],template=meta[w]['template'],value=float(np.mean(v))) for (w,k),v in metrics.items() if k==label]
            est=clustered(wr)
            est['leave_one_template_out']={str(t):clustered([r for r in wr if r['template']!=t],draws=1000)['mean'] for t in sorted({r['template'] for r in wr})}
            est['world_values']=wr;estimates[label]=est
        descriptives={}
        for population,pop in [('all_fixed',all_rows),('paired_clean',rs)]:
            for kind in sorted({r['kind'] for r in pop}):
                subset=[r for r in pop if r['kind']==kind]
                descriptives[population+'/'+kind]=dict(records=len(subset),
                    queried_damage=float(np.mean([r['status'][r['query']]!='correct' for r in subset])),
                    nonqueried_damage=float(np.mean([r['status'][1-r['query']]!='correct' for r in subset])),
                    valid_wrong=float(np.mean([s=='valid_wrong' for r in subset for s in r['status']])),
                    unparseable=float(np.mean([s=='unparseable' for r in subset for s in r['status']])),
                    full_fact_failure=float(np.mean([r['any_fact_changed'] for r in subset])),
                    token_disagreement=float(np.mean([r['token_disagreement'] for r in subset])))
        result.append(dict(point=point,estimates=estimates,descriptive=descriptives,
            fixed_worlds=len({r['world_id'] for r in all_rows}),paired_clean_worlds=len(meta)))
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--mode',choices=['calibrate','effects'],required=True)
    p.add_argument('--stage',choices=['noise','recovery'],required=True);p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--output',required=True)
    args=p.parse_args();rows=read_records(args.inputs)
    answer=calibration(rows,args.stage) if args.mode=='calibrate' else effects(rows,args.stage)
    Path(args.output).write_text(json.dumps(answer,indent=2)+'\n');print(json.dumps(answer if args.mode=='calibrate' else dict(points=len(answer))))

if __name__=='__main__':main()
