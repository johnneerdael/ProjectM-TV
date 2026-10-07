#!/usr/bin/env python3
"""Capture two hash-verified library runs on an explicitly selected GPU TV emulator."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
import shlex
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/core-corpus'))
from run_corpus import session_lock
from PIL import Image, ImageDraw


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + '\n')


def pcm() -> bytes:
    samples = bytearray()
    for i in range(120 * 1470):
        t = i / 44100
        envelope = .4 + .3 * math.sin(2 * math.pi * 1.7 * t) ** 2
        value = envelope * (.45 * math.sin(2 * math.pi * 80 * t)
                            + .15 * math.sin(2 * math.pi * 440 * t)
                            + .10 * math.sin(2 * math.pi * 1600 * t))
        samples.extend(struct.pack('<f', value))
    return bytes(samples)


@contextmanager
def remote_workspace(adb, path):
    """Remove only this capture's hashed directory; retain pulled local evidence."""
    adb('shell', 'mkdir', '-p', path)
    try:
        yield
    finally:
        try:
            result = adb('shell', 'rm', '-rf', path, check=False)
            if result.returncode:
                print('Remote cleanup failed for ' + path, file=sys.stderr)
        except (subprocess.SubprocessError, OSError) as error:
            print('Remote cleanup failed for ' + path + ': ' + str(error), file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=Path, required=True, help='prepare.py workers.json')
    parser.add_argument('--preset', type=Path, required=True)
    parser.add_argument('--textures', type=Path, required=True)
    parser.add_argument('--device', required=True)
    parser.add_argument('--user', required=True, type=int)
    parser.add_argument('--adb', default='adb')
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--width', type=int, choices=(256, 512), default=512)
    parser.add_argument('--evaluator-control', action='store_true')
    parser.add_argument('--texture-journey', action='store_true',
                        help='Use texture roots a/b, switch at20, soft-cut at21, reset at40')
    args = parser.parse_args()
    if not args.device.startswith('emulator-') or args.user < 0:
        parser.error('Select an emulator serial and a nonnegative Android user')
    preset, textures = args.preset.resolve(), args.textures.resolve()
    if not preset.is_file() or not textures.is_dir():
        parser.error('Preset or texture directory is unavailable')
    if args.texture_journey and (not (textures / 'a').is_dir() or not (textures / 'b').is_dir()):
        parser.error('--texture-journey requires a and b directories under --textures')
    workers = json.loads(args.workers.read_text())
    for identity in workers.values():
        if sha(Path(identity['binary']).read_bytes()) != identity['binary_sha256']:
            raise ValueError('Worker binary identity changed')
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)

    def adb(*arguments: str, check: bool = True) -> subprocess.CompletedProcess:
        return subprocess.run([args.adb, '-s', args.device, *arguments],
                              capture_output=True, text=True, check=check, timeout=180)

    def user() -> None:
        observed = adb('shell', 'am', 'get-current-user').stdout.strip()
        if observed != str(args.user):
            raise ValueError('Android user changed or query is malformed')

    with session_lock(args.device, 5037):
        user()
        if adb('shell', 'getprop', 'ro.kernel.qemu').stdout.strip() != '1':
            raise ValueError('Selected device does not report an emulator')
        features = adb('shell', 'pm', 'list', 'features').stdout.splitlines()
        if not {'feature:android.software.leanback',
                'feature:android.hardware.type.television'} <= set(features):
            raise ValueError('Selected emulator is not an Android TV image')
        remote = '/data/local/tmp/projectmtv-patch-proof-' + sha(str(work).encode())[:16]
        with remote_workspace(adb, remote):
            adb('push', str(preset), remote + '/witness.milk')
            adb('push', str(textures), remote + '/textures')
            signal = pcm()
            (work / 'audio.f32').write_bytes(signal)
            adb('push', str(work / 'audio.f32'), remote + '/audio.f32')
            width, height = args.width, args.width * 9 // 16
            report = {'capture_sha256': sha(Path(__file__).read_bytes()), 'capture_kind': 'evaluator' if args.evaluator_control else
                      'texture-journey' if args.texture_journey else 'image', 'device': args.device, 'user': args.user, 'features': features,
                      'fingerprint': adb('shell', 'getprop', 'ro.build.fingerprint').stdout.strip(),
                      'preset': preset.name, 'preset_sha256': sha(preset.read_bytes()),
                      'textures': {p.relative_to(textures).as_posix(): sha(p.read_bytes())
                                   for p in sorted(textures.rglob('*')) if p.is_file()},
                      'pcm_sha256': sha(signal), 'clock': 'frame/30.0', 'frames': 120,
                      'dimensions': [width, height], 'alpha_excluded': True, 'roles': {}}
            backend = None
            for role, identity in workers.items():
                adb('push', identity['binary'], remote + '/worker')
                adb('shell', 'chmod', '755', remote + '/worker')
                runs = []
                for repeat in range(2):
                    user()
                    directory = work / role / str(repeat)
                    directory.mkdir(parents=True)
                    if args.evaluator_control:
                        command = shlex.join(['env', 'PRESET_LAB_SEED=12345', remote + '/worker',
                                              '--evaluator-control'])
                        result = adb('shell', command, check=False)
                        (directory / 'output.txt').write_text(result.stdout + result.stderr)
                        runs.append({'exit': result.returncode, 'control': json.loads(result.stdout)})
                        continue
                    job = {'schema_version': 1, 'config': {'width': width, 'height': height,
                           'fps': 30, 'warmup_seconds': 0, 'measurement_seconds': 4,
                           'seed': 12345, 'line_reference_height': 0},
                           'pcm_path': remote + '/audio.f32', 'preset_path': remote + '/witness.milk',
                           'texture_root': remote + ('/textures/a' if args.texture_journey else '/textures'),
                           'bands_path': remote + '/bands.jsonl',
                           'manifest_path': remote + '/manifest.json',
                           'identity': {'role': role, 'repeat': repeat}}
                    if args.texture_journey:
                        job['events'] = [
                            {'frame': 20, 'texture_root': remote + '/textures/b'},
                            {'frame': 21, 'load_preset': remote + '/witness.milk', 'smooth': True},
                            {'frame': 40, 'reset_textures': True}]
                    write(directory / 'job.json', job)
                    adb('push', str(directory / 'job.json'), remote + '/job.json')
                    command = shlex.join(['env', 'PRESET_LAB_SEED=12345', remote + '/worker',
                                          '--job', remote + '/job.json'])
                    command += ' > ' + shlex.quote(remote + '/frames.rgb')
                    command += ' 2> ' + shlex.quote(remote + '/render.log')
                    adb('shell', 'rm', '-f', remote + '/manifest.json')
                    result = adb('shell', command, check=False)
                    adb('pull', remote + '/render.log', str(directory / 'render.log'))
                    if result.returncode:
                        runs.append({'status': 'failed', 'exit': result.returncode,
                                     'log': (directory / 'render.log').read_text()})
                        continue
                    adb('pull', remote + '/manifest.json', str(directory / 'manifest.json'))
                    manifest = json.loads((directory / 'manifest.json').read_text())
                    renderer = manifest['gl_renderer']
                    if any(x in renderer.lower() for x in ('swiftshader', 'llvmpipe', 'softpipe',
                                                           'lavapipe', 'software rasterizer')):
                        raise ValueError('Software renderer is outside GPU proof scope')
                    observed = [manifest[k] for k in ('gl_vendor', 'gl_renderer', 'gl_version', 'glsl_version')]
                    if backend is not None and backend != observed:
                        raise ValueError('GPU backend changed between roles or repeats')
                    backend = observed
                    if manifest['status'] != 'success' or manifest['gl_error_frames'] != 0:
                        raise ValueError('Worker did not complete strict GL validation')
                    adb('pull', remote + '/frames.rgb', str(directory / 'frames.rgb'))
                    data = (directory / 'frames.rgb').read_bytes()
                    size = width * height * 3
                    if len(data) != size * 120:
                        raise ValueError('RGB stream length is not the declared frame count')
                    hashes = [sha(data[i * size:(i + 1) * size]) for i in range(120)]
                    for frame in ([29, 40, 59, 119] if args.texture_journey else [29, 59, 119]):
                        Image.frombytes('RGB', (width, height),
                                        data[frame * size:(frame + 1) * size]).save(directory / f'{frame}.png')
                    (directory / 'frames.rgb').unlink()
                    runs.append({'status': 'success', 'manifest': manifest, 'frame_hashes': hashes,
                                 'stream_sha256': sha(data)})
                if args.evaluator_control:
                    repeat_equal = runs[0]['control'] == runs[1]['control']
                else:
                    repeat_equal = all(r['status'] == 'success' for r in runs) and (
                        runs[0]['frame_hashes'] == runs[1]['frame_hashes'])
                report['roles'][role] = {'worker': identity, 'runs': runs, 'repeat_equal': repeat_equal}
                write(work / 'results.json', report)
                print(role, 'repeat_equal=' + str(repeat_equal), flush=True)
            report['backend'] = backend
            if not args.evaluator_control:
                image = Image.new('RGB', (width * len(workers), height + 32), '#171717')
                draw = ImageDraw.Draw(image)
                for col, (role, value) in enumerate(report['roles'].items()):
                    draw.text((col * width + 4, 8), role, fill='white')
                    if value['repeat_equal']:
                        image.paste(Image.open(work / role / '0/119.png'), (col * width, 32))
                    else:
                        draw.text((col * width + 8, 80), 'Rejected or unstable\nNo verified framebuffer', fill='#ffb4ab')
                image.save(work / 'comparison.png')
            write(work / 'results.json', report)


if __name__ == '__main__':
    main()
