"""Host matrix: run.py LABEL [KEY=VAL env ...] [--presets 0,1,2] [--size 3840x2160] -> runs/p{i}-LABEL"""
import json, os, subprocess, sys
from pathlib import Path
D = Path(__file__).resolve().parent
WT = Path('/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-4k-phase-aware-diffusion')
PRESETS = ['$$$ Royal - Mashup (191).milk', 'Fed - quadratrail.milk', 'astral spinorgentics encrustcore nz+.milk',
           'Fumbling_Foo + En D & Martin - Mandelverse.milk', 'Fumbling_Foo & Flexi, Martin, Orb - Acid Mandala v1c.milk',
           '$$$ Royal - Mashup (255).milk', 'DIAG:FedNoBlur.milk', 'DIAG:FedNoWave.milk', 'DIAG:R191a.milk', 'DIAG:R191b.milk']
args = sys.argv[1:]
label = args.pop(0)
env_over, sel, size = {}, list(range(5)), (3840, 2160, 1024, 768)
while args:
    a = args.pop(0)
    if a == '--presets': sel = [int(x) for x in args.pop(0).split(',')]
    elif a == '--noref': size = (size[0], size[1], 0, 0)
    elif a == '--size':
        w, h = args.pop(0).split('x'); size = (int(w), int(h), 1024, 768) if int(w) != 1182 else (1182, 665, 0, 0)
    else: k, v = a.split('=', 1); env_over[k] = v
worker = Path(os.environ.get('WORKER', D / 'worker-build/preset-lab-worker'))
for i in sel:
    preset = PRESETS[i]
    out = D / 'runs' / f'p{i}-{label}'
    if (out / 'manifest.json').exists(): continue
    (out / 'captures').mkdir(parents=True, exist_ok=True)
    w, h, rw, rh = size
    job = {'schema_version': 1,
           'config': {'width': w, 'height': h, 'fps': 30, 'warmup_seconds': 4, 'measurement_seconds': 12,
                      'line_reference_width': rw, 'line_reference_height': rh, 'seed': 12345},
           'pcm_path': str(D / 'pcm-480.f32'), 'preset_path': str(D / 'diagpresets' / preset[5:]) if preset.startswith('DIAG:') else str(WT / 'core/src/main/assets/presets' / preset),
           'texture_root': str(WT / 'core/src/main/assets/textures'), 'bands_path': str(out / 'bands.jsonl'),
           'manifest_path': str(out / 'manifest.json'), 'identity': {'preset': preset, 'config': label},
           'capture_dir': str(out / 'captures')}
    (out / 'job.json').write_text(json.dumps(job, indent=1))
    env = dict(os.environ, PRESET_LAB_SEED='12345', **env_over)
    for k in ('PM_DUMP_GLSL_DIR',):
        if k in env_over: Path(env_over[k]).mkdir(parents=True, exist_ok=True)
    r = subprocess.run([str(worker), '--job', str(out / 'job.json')], env=env, capture_output=True, text=True)
    (out / 'stderr.txt').write_text(r.stderr)
    print(f'p{i}-{label}', preset[:34], 'exit', r.returncode, flush=True)
