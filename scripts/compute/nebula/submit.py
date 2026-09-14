"""Start one detached nebula worker and record its actual PID and provenance."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--gpu',required=True,type=int,choices=[5,6,7,8])
    p.add_argument('--experiment',required=True)
    p.add_argument('--config',default='')
    p.add_argument('--output',required=True)
    p.add_argument('--ledger',required=True)
    p.add_argument('command',nargs=argparse.REMAINDER)
    args=p.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(['git','status','--porcelain'],text=True).strip()
    if dirty:
        raise SystemExit('Launch from the committed frozen worktree.')
    out=Path(args.output)
    out.mkdir(parents=True,exist_ok=False)
    argv=['bash','scripts/compute/nebula/run.sh',str(args.gpu)]+command
    record=dict(event='submitted',experiment=args.experiment,machine='nebula',scheduler='direct',
                commit=commit,config=args.config,command=shlex.join(argv),recorded_at=now(),
                artifact_dir=str(out),gpu=args.gpu,working_directory=os.getcwd())
    (out/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
    # The wrapper writes terminal evidence even when the Python worker fails.
    shell=shlex.join(argv)+'; result=$?; printf "%s\\n" "$result" > '+shlex.quote(str(out/'exit.txt'))+'; exit "$result"'
    with (out/'log.txt').open('w') as log:
        proc=subprocess.Popen(['bash','-c',shell],stdout=log,stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL,start_new_session=True)
    record['job_id']=str(proc.pid)
    (out/'launch.json').write_text(json.dumps(record,indent=2)+'\n')
    with Path(args.ledger).open('a') as f:
        f.write(json.dumps(record)+'\n')
    print(json.dumps(record))


if __name__=='__main__':
    main()
