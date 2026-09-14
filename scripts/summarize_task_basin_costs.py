"""Observed job artifacts and instrumented calls for all idea-002 formal runs."""
import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser();p.add_argument('--ledger',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();events=list(map(json.loads,Path(a.ledger).read_text().splitlines()))
    jobs={r['job_id']:r for r in events if r.get('event')=='submitted' and r['experiment'].startswith('002-')}
    runs=[];groups=defaultdict(list)
    for job in jobs.values():
        folder=Path(job['artifact_dir']);terminal=folder/'exit.txt'
        assert terminal.exists(),f'Job still pending: {job["job_id"]}'
        candidates=list(folder.glob('*/summary.json'));assert len(candidates)<=1,str(folder)
        summary=json.loads(candidates[0].read_text()) if candidates else {}
        counts=dict(summary.get('counts',summary.get('recovery',{}).get('counts',{})))
        row=dict(experiment=job['experiment'],job_id=job['job_id'],commit=job['commit'],config=job['config'],gpu=job['gpu'],
            artifact_dir=str(folder),exit_code=int(terminal.read_text()),instrumented_calls=counts,
            source_count_adjustments={'dit_history':1} if job['experiment']=='002-p0-v1' else {},
            reported_elapsed_seconds=summary.get('elapsed_seconds'),peak_memory_gb=summary.get('peak_memory_gb'),
            launch_to_exit_seconds=terminal.stat().st_mtime-datetime.fromisoformat(job['recorded_at']).timestamp(),
            units={k:summary[k] for k in ['worlds','records','features','targets','backward_steps','native_verifications'] if k in summary})
        runs.append(row);groups[job['experiment']].append(row)
    aggregated=[]
    for name,rs in groups.items():
        totals=defaultdict(int);units=defaultdict(int);adjustments=defaultdict(int)
        for r in rs:
            for k,v in r['instrumented_calls'].items():totals[k]+=v
            for k,v in r['units'].items():units[k]+=v
            for k,v in r['source_count_adjustments'].items():adjustments[k]+=v
        aggregated.append(dict(experiment=name,jobs=len(rs),successful_jobs=sum(r['exit_code']==0 for r in rs),instrumented_calls=dict(totals),source_count_adjustments=dict(adjustments),
            accounted_calls={k:totals[k]+adjustments[k] for k in set(totals)|set(adjustments)},units=dict(units),
            summed_worker_wall_hours=sum(r['launch_to_exit_seconds'] for r in rs)/3600,
            reported_elapsed_seconds_sum=sum(r['reported_elapsed_seconds'] or 0 for r in rs)))
    result=dict(scope='All idea-002 formal submissions retained in the job ledger, including calibration and controls.',
        accounting='Worker wall time is launch timestamp to observed exit-file timestamp. Concurrent workers share GPUs; summed worker hours are not dedicated GPU-hours. Reported measurement timers can omit model loading. Call totals cover the instrumented model interfaces.',
        p0_count_note='The P0 native-parity path makes one additional direct clean-history DiT call outside its counter; other native sample-block calls use the shared counter. Scientific run workers use the instrumented recovery path.',
        jobs=len(runs),groups=aggregated,runs=runs)
    Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(jobs=len(runs),groups=len(aggregated))))

if __name__=='__main__':main()
