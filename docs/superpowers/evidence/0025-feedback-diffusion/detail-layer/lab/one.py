"""one.py IDX LABEL W H RW RH [ENV=VAL ...]: render one broad-list preset, keep captures + stderr in runs/b<IDX>-<LABEL>."""
import json, os, subprocess, sys
from pathlib import Path
D = Path(__file__).resolve().parent
WT = Path('/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-4k-phase-aware-diffusion')
i, label, w, h, rw, rh = int(sys.argv[1]), sys.argv[2], *map(int, sys.argv[3:7])
env = dict(a.split('=', 1) for a in sys.argv[7:])
preset = json.loads((D / 'broad-list.json').read_text())[i]
out = D / 'runs' / f'b{i}-{label}'; (out / 'captures').mkdir(parents=True, exist_ok=True)
job = {'schema_version': 1, 'config': {'width': w, 'height': h, 'fps': 30, 'warmup_seconds': 4, 'measurement_seconds': 12,
       'line_reference_width': rw, 'line_reference_height': rh, 'seed': 12345}, 'pcm_path': str(D / 'pcm-480.f32'),
       'preset_path': str(WT / 'core/src/main/assets/presets' / preset), 'texture_root': str(WT / 'core/src/main/assets/textures'),
       'bands_path': str(out / 'bands.jsonl'), 'manifest_path': str(out / 'manifest.json'), 'identity': {'preset': preset, 'config': label},
       'capture_dir': str(out / 'captures')}
(out / 'job.json').write_text(json.dumps(job))
r = subprocess.run([os.environ.get('WORKER', str(D / 'wb-detail/preset-lab-worker')), '--job', str(out / 'job.json')],
                   env=dict(os.environ, PRESET_LAB_SEED='12345', **env), capture_output=True, text=True)
(out / 'stderr.txt').write_text(r.stderr); print(label, 'rc', r.returncode, preset)
