"""Reproduce the bounded idea-002 final analyses from completed immutable runs."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--run-base',required=True);p.add_argument('--worlds',required=True);p.add_argument('--output',required=True);p.add_argument('--ledger',required=True)
    a=p.parse_args();base=Path(a.run_base);out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    def shards(group):return [str(base/f'{group}-gpu{g}'/'measurements') for g in (5,6,7,8)]
    noise=shards('002-p1-test-noise-v1');recovery=shards('002-p2-test-recovery-v1');cfg7=shards('002-p2-cfg7-control-v1');search=shards('002-p1-test-search-v1')
    # Partial recovery files must never become the final study denominator.
    for paths in (noise,recovery,cfg7,search):
        for path in paths:
            folder=Path(path);assert (folder.parent/'exit.txt').read_text().strip()=='0',str(folder)
            assert (folder/'summary.json').exists(),str(folder)
    commands=[]
    def run(module,*args):
        command=[sys.executable,'-m',module,*map(str,args)];commands.append(command)
        (out/'analysis_commands.json').write_text(json.dumps(commands,indent=2)+'\n')
        subprocess.run(command,check=True)
    for label,paths,n in [('h2',recovery,256),('h2_cfg7',cfg7,64)]:
        run('scripts.summarize_task_basin_recovery','--inputs',*paths,'--expected-worlds',n,'--output',out/f'{label}_support_v1.json')
        run('scripts.analyze_task_basin','--mode','effects','--stage','recovery','--inputs',*paths,'--output',out/f'{label}_effects_v1.json')
    run('scripts.analyze_task_basin','--mode','effects','--stage','noise','--inputs',*noise,'--output',out/'h1_noise_v1.json')
    run('scripts.summarize_task_basin_search','--inputs',*search,'--sigma','.4','--output',out/'h1_search_v1.json')
    run('scripts.compare_task_basin_cfg','--main-inputs',*recovery,'--control-inputs',*cfg7,'--output',out/'cfg_matched_v1.json')
    run('scripts.task_basin_confidence','--inputs',*noise,'--sigma','.4','--worlds',a.worlds,'--output',out/'h1_confidence_v2.json')
    run('scripts.summarize_task_basin_costs','--ledger',a.ledger,'--output',out/'study_costs_v1.json')
    run('scripts.task_basin_geometry_prediction','--recovery',*recovery,'--search',*search,'--features',base/'002-geometry-features-v1/measurements/features.jsonl','--sigma','.4','--output',out/'geometry_prediction_v1.json')
    run('scripts.plot_task_basin','--noise',out/'h1_noise_v1.json','--recovery',out/'h2_effects_v1.json','--search',out/'h1_search_v1.json','--geometry',out/'geometry_prediction_v1.json','--output',out/'figures')
    tests={}
    for name,file,point,metric in [('H1','h1_noise_v1.json',.4,'protection'),('H2','h2_effects_v1.json',.5,'G_selective')]:
        e=next(r for r in json.loads((out/file).read_text()) if r['point']==point)['estimates'][metric]
        tests[name]=dict(point=point,metric=metric,estimate=e['mean'],ci95=e['ci95'],raw_p=e.get('centered_bootstrap_two_sided_p'),nondegenerate=e.get('nondegenerate_bootstrap'))
    ordered=sorted(tests,key=lambda k:tests[k]['raw_p']);previous=0.
    for i,key in enumerate(ordered):
        value=min(1.,max(previous,(2-i)*tests[key]['raw_p']));tests[key]['holm_p']=value;previous=value
    (out/'primary_tests_v1.json').write_text(json.dumps(tests,indent=2)+'\n')
    audit=out/'blind_audit_v1'
    if not audit.exists():
        run('scripts.prepare_task_basin_audit','--noise',*noise,'--recovery',*recovery,'--sentence',base/'002-control-sentence-v1/measurements','--worlds',a.worlds,'--output',audit)
    (out/'analysis_provenance.json').write_text(json.dumps(dict(analysis_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),run_base=str(base),primary_tests=tests,audit_requires_independent_labels=True),indent=2)+'\n')
    print(json.dumps(tests))

if __name__=='__main__':main()
