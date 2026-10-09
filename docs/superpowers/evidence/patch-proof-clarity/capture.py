"""Capture selected final RGB frames from an exact one-patch comparison twice."""
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from PIL import Image


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--work', type=Path, required=True)
    p.add_argument('--name', required=True)
    p.add_argument('--patch', required=True)
    p.add_argument('--preset', type=Path, required=True)
    p.add_argument('--selected', default='0,1,2,5,29,59,93,94,95,119,239')
    p.add_argument('--frames', type=int, default=240, choices=(240,480))
    args = p.parse_args()
    args.repo=args.repo.resolve();args.work=args.work.resolve();args.preset=args.preset.resolve()
    selected = sorted(set(int(i) for i in args.selected.split(',')))
    if min(selected) < 0 or max(selected) >= args.frames:
        raise ValueError('selected frame out of bounds')
    target = args.work / 'captures' / args.name
    target.mkdir(parents=True, exist_ok=False)
    pcm = args.repo / f'docs/superpowers/evidence/patch-visual-catalog/audio/frozen-{args.frames}-frames.f32'
    textures = args.repo / 'core/src/main/assets/textures'
    texture_hashes = {i.relative_to(textures).as_posix(): sha(i.read_bytes())
                      for i in sorted(textures.rglob('*')) if i.is_file()}
    inputs = {'preset_sha256': sha(args.preset.read_bytes()), 'pcm_sha256': sha(pcm.read_bytes()),
              'texture_inventory': texture_hashes}
    receipt = {'name': args.name, 'patch': args.patch, 'inputs': inputs, 'roles': {}}
    for role in ('without-' + args.patch, 'full'):
        identity = json.loads((args.work / role / 'identity.json').read_text())
        if sha(Path(identity['worker']).read_bytes()) != identity['worker_sha256']:
            raise ValueError('worker mismatch')
        repeats = []
        for repeat in range(2):
            run = target / f'{role}-{repeat}'
            run.mkdir()
            job = {'schema_version': 1, 'config': {'width': 3840, 'height': 2160, 'fps': 30,
                   'warmup_seconds': 0, 'measurement_seconds': args.frames / 30,
                   'seed': 12345, 'line_reference_width': 1280, 'line_reference_height': 720,
                   'line_antialiasing': True, 'feedback_detail': 0, 'selected_frames': selected},
                   'pcm_path': str(pcm), 'preset_path': str(args.preset), 'texture_root': str(textures),
                   'manifest_path': str(run / 'manifest.json'), 'identity': identity}
            path = run / 'job.json'
            path.write_text(json.dumps(job, indent=2) + '\n')
            hashes = {}
            with (run / 'diagnostics.txt').open('wb') as log:
                proc = subprocess.Popen([identity['worker'], '--job', str(path)], stdout=subprocess.PIPE,
                    stderr=log, env=dict(os.environ, PRESET_LAB_SEED='12345'))
                for frame in selected:
                    payload = proc.stdout.read(3840 * 2160 * 3)
                    if len(payload) != 3840 * 2160 * 3:
                        raise ValueError('incomplete RGB frame: ' + str(run))
                    hashes[str(frame)] = sha(payload)
                    if repeat == 0:
                        Image.frombytes('RGB', (3840,2160), payload).save(run / f'frame-{frame:03d}.png')
                if proc.wait():
                    raise ValueError((run / 'diagnostics.txt').read_text())
            manifest = json.loads((run / 'manifest.json').read_text())
            if manifest['status'] != 'success' or manifest['gl_error_frames']:
                raise ValueError('renderer failure')
            (run / 'result.json').write_text(json.dumps({'rgb_sha256': hashes, 'manifest': manifest}, indent=2) + '\n')
            repeats.append(hashes)
            print(args.name, role, repeat, manifest['gl_renderer'], flush=True)
        if repeats[0] != repeats[1]:
            raise ValueError('nonrepeatable pixels')
        receipt['roles'][role] = {'identity': identity, 'rgb_sha256': repeats[0], 'repeat_equal': True}
    if sha(args.preset.read_bytes()) != inputs['preset_sha256'] or sha(pcm.read_bytes()) != inputs['pcm_sha256']:
        raise ValueError('inputs changed')
    (target / 'comparison.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
