#!/usr/bin/env bash
set -euo pipefail
# Usage: bash scripts/compute/nebula/run.sh PHYSICAL_GPU PYTHON_ARGUMENTS...
gpu="$1"
shift
case "$gpu" in 5|6|7|8) ;; *) echo 'This study is allocated physical GPUs 5-8 only.' >&2; exit 2;; esac
source scripts/compute/nebula/env.sh
export CUDA_VISIBLE_DEVICES="$gpu"
exec "$COLA_PYTHON" "$@"
