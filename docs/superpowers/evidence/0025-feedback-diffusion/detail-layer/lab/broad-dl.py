"""Host broad screen: per preset, classic 1182 (stored), then configs compared on the fly; captures deleted."""
import json, os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cv2, numpy as np
D = Path(__file__).resolve().parent
WT = Path('/Users/jneerdael/Scripts/Projectm-TV/.worktrees/native-4k-phase-aware-diffusion')
OUT = D / sys.argv[1]; OUT.mkdir(exist_ok=True)
WORKER = Path(os.environ.get('WORKER', D / 'worker-build/preset-lab-worker'))
PICKS = [120, 150, 180, 210, 239, 300, 390, 479]
LUMA = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
CONFIGS = json.loads(os.environ.get('CONFIGS', json.dumps({
    'classic': [1182, 665, 0, 0, {}], 'c1280': [1280, 720, 0, 0, {}],
    'v0': [3840, 2160, 1024, 768, {'PM_DIFFUSION_VARIANCE_SCALE': '0'}],
    'v1': [3840, 2160, 1024, 768, {}],
    'emuc': [3840, 2160, 1024, 768, {'PM_DIFFUSION_VARIANCE_SCALE': '0', 'PM_PHASE_MODE': 'emuc'}]})))
presets = json.loads((D / 'broad-list.json').read_text())

def render(i, preset, label, cfg):
    w, h, rw, rh, env = cfg[:5]
    worker = Path(cfg[5]) if len(cfg) > 5 else WORKER
    out = OUT / 'tmp' / f'{i}-{label}'
    shutil.rmtree(out, ignore_errors=True); (out / 'captures').mkdir(parents=True)
    job = {'schema_version': 1, 'config': {'width': w, 'height': h, 'fps': 30, 'warmup_seconds': 4, 'measurement_seconds': 12,
           'line_reference_width': rw, 'line_reference_height': rh, 'seed': 12345},
           'pcm_path': str(D / 'pcm-480.f32'), 'preset_path': str(WT / 'core/src/main/assets/presets' / preset),
           'texture_root': str(WT / 'core/src/main/assets/textures'), 'bands_path': str(out / 'bands.jsonl'),
           'manifest_path': str(out / 'manifest.json'), 'identity': {'preset': preset, 'config': label}, 'capture_dir': str(out / 'captures')}
    (out / 'job.json').write_text(json.dumps(job))
    r = subprocess.run([str(worker), '--job', str(out / 'job.json')], env=dict(os.environ, PRESET_LAB_SEED='12345', **env),
                       capture_output=True, text=True, timeout=600)
    frames = []
    for f in PICKS:
        p = out / 'captures' / f'frame-{f}.rgb'
        if not p.exists(): return None, r.returncode, r.stderr[-400:]
        img = np.fromfile(p, dtype=np.uint8).reshape(h, w, 3).astype(np.float32) / 255
        if w != 1182: img = cv2.resize(img, (1182, 665), interpolation=cv2.INTER_AREA if w > 1182 else cv2.INTER_LINEAR)
        frames.append(img)
    shutil.rmtree(out, ignore_errors=True)
    return np.stack(frames), r.returncode, ''

def one(i):
    res_path = OUT / f'{i}.json'
    if res_path.exists(): return
    preset = presets[i]
    cl, rc, err = render(i, preset, 'classic', CONFIGS['classic'])
    rec = {'preset': preset}
    if cl is None:
        rec['error'] = f'classic failed {rc} {err}'; res_path.write_text(json.dumps(rec)); return
    cll = float((cl @ LUMA).mean()); rec['classic'] = {'luma': cll, 'contrast': float((cl @ LUMA).std(axis=(1, 2)).mean())}
    refs = {'classic': cl}
    if 'c1280' in CONFIGS:
        c2, rc, err = render(i, preset, 'c1280', CONFIGS['c1280'])
        if c2 is not None:
            refs['c1280'] = c2; l2 = float((c2 @ LUMA).mean())
            rec['c1280'] = {'luma': l2, 'luma_ratio': l2 / cll if cll > 1e-6 else None, 'mae': float(np.abs(c2 - cl).mean()), 'contrast': float((c2 @ LUMA).std(axis=(1, 2)).mean())}
    for label, cfg in CONFIGS.items():
        if label in ('classic', 'c1280'): continue
        refname = cfg[6] if len(cfg) > 6 else 'classic'
        if refname not in refs: rec[label] = {'error': 'no ref ' + refname}; continue
        ref = refs[refname]; cll_ = float((ref @ LUMA).mean())
        im, rc, err = render(i, preset, label, cfg)
        if im is None: rec[label] = {'error': f'{rc} {err}'}; continue
        l = float((im @ LUMA).mean())
        rec[label] = {'ref': refname, 'luma': l, 'luma_ratio': l / cll_ if cll_ > 1e-6 else None, 'mae': float(np.abs(im - ref).mean()),
                      'luma_abs_err': abs(l - cll_), 'contrast': float((im @ LUMA).std(axis=(1, 2)).mean()),
                      'digest': float(im[:, ::37, ::41].sum())}
    res_path.write_text(json.dumps(rec, indent=1))
    print(i, preset[:50], {k: round(v.get('mae', -1), 4) for k, v in rec.items() if isinstance(v, dict) and 'mae' in v}, flush=True)

with ThreadPoolExecutor(int(os.environ.get('JOBS', 3))) as ex:
    list(ex.map(one, range(len(presets))))
