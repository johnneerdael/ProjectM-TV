#!/bin/bash
# sweep.sh PRESETS : classic + sym alpha 0/0.25/1 (+ emu) for diag presets
cd "$(dirname "$0")"
P=$1
python3 run.py classic --size 1182x665 --presets $P
for a in 0 0.25 0.5; do python3 run.py sym$a PM_PHASE_MODE=sym PM_PHASE_ALPHA=$a PM_DIFFUSION_VARIANCE_SCALE=0 --presets $P; done
python3 run.py sym PM_PHASE_MODE=sym PM_DIFFUSION_VARIANCE_SCALE=0 --presets $P
python3 run.py v1 --presets $P
