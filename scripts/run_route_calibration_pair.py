"""Execute the two predefined P0 difficulties on one assigned graph shard."""
import argparse
from pathlib import Path
import subprocess
import sys

p=argparse.ArgumentParser()
p.add_argument('--shard',type=int,required=True)
p.add_argument('--shards',type=int,default=4)
p.add_argument('--output',required=True,type=Path)
args=p.parse_args()
for difficulty in ['easy','hard']:
    command=[sys.executable,'-m','src.tasks.route_calibration','--config',
             f'configs/001_same_prefix_state/p0_calibration_{difficulty}.json',
             '--shard',str(args.shard),'--shards',str(args.shards),
             '--output',str(args.output/difficulty)]
    subprocess.run(command,check=True)
