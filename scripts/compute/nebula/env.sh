#!/usr/bin/env bash
# Source from a checkout or frozen worktree on nebula.
export COLA_STORAGE=/home/mlw0719/cola_dlm_exploration_storage
export COLA_CHECKPOINT="$COLA_STORAGE/checkpoints/Cola-DLM-c1eafdd"
export COLA_UPSTREAM="$COLA_STORAGE/upstream/Cola-DLM"
export PYTHONPATH="$PWD:$COLA_UPSTREAM${PYTHONPATH:+:$PYTHONPATH}"
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
export PYTHONUNBUFFERED=1
export COLA_PYTHON="$COLA_STORAGE/venv/bin/python"
