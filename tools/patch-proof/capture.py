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
import shutil
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/core-corpus'))
from run_corpus import session_lock
from PIL import Image, ImageDraw
from source_identity import validate_prepared_source, DEFAULT_SERIES, digest, _supported_roles
from rgb_payload import inspect_rgb, compress_rgb


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
    adb('shell', 'rm', '-rf', path)
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
    parser.add_argument('--series', type=Path, default=DEFAULT_SERIES,
                        help='Series manifest used to prepare these workers')
    parser.add_argument('--workers', type=Path, required=True, help='prepare.py workers.json')
    parser.add_argument('--preset', type=Path, required=True)
    parser.add_argument('--textures', type=Path, required=True)
    parser.add_argument('--device', required=True)
    parser.add_argument('--user', required=True, type=int)
    parser.add_argument('--ndk', type=Path, required=True,
                        help='Android NDK 27.3.13750724 used to reproduce worker binaries')
    parser.add_argument('--adb', default='adb')
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--width', type=int, choices=(256, 512, 1280, 1920, 2560, 3840), default=512)
    parser.add_argument('--line-reference-height', type=int, default=0,
                        help='16:9 quad-line reference height for the patched library; 0 uses classic lines')
    parser.add_argument('--line-antialiasing', action='store_true')
    parser.add_argument('--compress-streams', action='store_true',
                        help='Retain complete lossless gzip RGB streams after checking decompressed hashes')
    parser.add_argument('--shader-failure-probe', action='store_true',
                        help='Observe sixteen intentional fragment rejections and a valid shader retry before rendering')
    parser.add_argument('--texture-history-probe', action='store_true',
                        help='Observe controlled fresh/recreated colour attachment pixels, caller state and pooling')
    parser.add_argument('--evaluator-control', action='store_true')
    parser.add_argument('--texture-journey', action='store_true',
                        help='Use texture roots a/b, switch at20, soft-cut at21, reset at40')
    args = parser.parse_args()
    if not args.device.startswith('emulator-') or args.user < 0:
        parser.error('Select an emulator serial and a nonnegative Android user')
    if args.line_reference_height < 0:
        parser.error('--line-reference-height must be nonnegative')
    if args.shader_failure_probe and args.texture_history_probe:
        parser.error('Select one resource diagnostic per capture')
    if (args.shader_failure_probe or args.texture_history_probe) and (args.evaluator_control or args.texture_journey):
        parser.error('Resource diagnostics require a plain image capture')
    preset, textures = args.preset.resolve(), args.textures.resolve()
    if not preset.is_file() or not textures.is_dir():
        parser.error('Preset or texture directory is unavailable')
    if args.texture_journey and (not (textures / 'a').is_dir() or not (textures / 'b').is_dir()):
        parser.error('--texture-journey requires a and b directories under --textures')
    workers = json.loads(args.workers.read_text())
    series = json.loads(args.series.read_text())
    supported_roles = _supported_roles(series)
    for role in workers:
        if role not in supported_roles:
            raise ValueError('Unsupported worker role: ' + role)
        identity = workers[role]
        if 'series_sha256' in identity and identity['series_sha256'] != digest(series):
            raise ValueError('Worker snapshot differs from the selected series: ' + role)
        if identity.get('role') != role:
            raise ValueError('Worker role identity differs: ' + role)
        removed = int(role[8:]) if role.startswith('without-') else None
        if ('patch_removed' not in identity or identity['patch_removed'] != removed or
                type(identity['patch_removed']) is not type(removed)):
            raise ValueError('Worker patch removal differs: ' + role)
        if identity.get('ordered_patches') != ([] if role == 'upstream' else series['patches']):
            raise ValueError('Worker patch inventory differs: ' + role)
        validate_prepared_source(role, identity, series, args.ndk.resolve())
    for identity in workers.values():
        if sha(Path(identity['binary']).read_bytes()) != identity['binary_sha256']:
            raise ValueError('Worker binary identity changed')
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    preset_name = preset.name
    inputs = work / 'inputs'
    inputs.mkdir()
    shutil.copyfile(preset, inputs / 'witness.milk')
    shutil.copytree(textures, inputs / 'textures')
    preset, textures = inputs / 'witness.milk', inputs / 'textures'
    preset_hash = sha(preset.read_bytes())
    texture_hashes = {p.relative_to(textures).as_posix(): sha(p.read_bytes())
                      for p in sorted(textures.rglob('*')) if p.is_file()}

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
            report = {'series_sha256': digest(series),
                      'capture_sha256': sha(Path(__file__).read_bytes()), 'capture_kind': 'evaluator' if args.evaluator_control else
                      'texture-journey' if args.texture_journey else 'image', 'device': args.device, 'user': args.user, 'features': features,
                      'fingerprint': adb('shell', 'getprop', 'ro.build.fingerprint').stdout.strip(),
                      'preset': preset_name, 'preset_sha256': preset_hash,
                      'textures': texture_hashes,
                      'pcm_sha256': sha(signal), 'clock': 'frame/30.0', 'frames': 120,
                      'host_controls': {'line_reference_height': args.line_reference_height,
                                        'line_antialiasing': args.line_antialiasing},
                      'frame_payload': 'lossless-gzip' if args.compress_streams else 'raw-rgb',
                      'rgb_payload_sha256': sha(Path(__file__).with_name('rgb_payload.py').read_bytes()),
                      'dimensions': [width, height], 'alpha_excluded': True, 'roles': {}}
            if args.shader_failure_probe:
                report['diagnostic_kind'] = 'shader-fragment-failure'
            if args.texture_history_probe:
                report['diagnostic_kind'] = 'texture-history'
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
                           'seed': 12345, 'line_reference_height': args.line_reference_height,
                           'line_antialiasing': args.line_antialiasing},
                           'pcm_path': remote + '/audio.f32', 'preset_path': remote + '/witness.milk',
                           'texture_root': remote + ('/textures/a' if args.texture_journey else '/textures'),
                           'bands_path': remote + '/bands.jsonl',
                           'manifest_path': remote + '/manifest.json',
                           'identity': {'role': role, 'repeat': repeat}}
                    if args.shader_failure_probe:
                        job['config']['shader_failure_probe'] = True
                    if args.texture_history_probe:
                        job['config']['texture_history_probe'] = True
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
                    if result.returncode:
                        failed = {'status': 'failed', 'exit': result.returncode,
                                  'pull_errors': {}, 'retained_artifacts': {}}
                        for name in ('render.log', 'manifest.json', 'frames.rgb'):
                            path = directory / name
                            try:
                                pulled = adb('pull', remote + '/' + name, str(path), check=False)
                            except (subprocess.SubprocessError, OSError) as error:
                                failed['pull_errors'][name] = str(error)
                                continue
                            if pulled.returncode:
                                failed['pull_errors'][name] = {
                                    'exit': pulled.returncode, 'output': pulled.stdout + pulled.stderr}
                                continue
                            data = path.read_bytes()
                            failed['retained_artifacts'][name] = {'sha256': sha(data), 'bytes': len(data)}
                            if name == 'render.log':
                                failed['log'] = data.decode('utf-8', errors='replace')
                            elif name == 'manifest.json':
                                try:
                                    failed['manifest'] = json.loads(data)
                                except (ValueError, UnicodeError) as error:
                                    failed['manifest_parse_error'] = str(error)
                        runs.append(failed)
                        continue
                    adb('pull', remote + '/render.log', str(directory / 'render.log'))
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
                    snapshots = (29, 40, 59, 119) if args.texture_journey else (29, 59, 119)
                    payload = inspect_rgb(directory / 'frames.rgb', width, height, snapshots=snapshots)
                    for frame in snapshots:
                        Image.frombytes('RGB', (width, height),
                                        payload['snapshots'][frame]).save(directory / f'{frame}.png')
                    if args.compress_streams:
                        compress_rgb(directory, width, height, payload)
                    runs.append({'status': 'success', 'manifest': manifest, 'frame_hashes': payload['frame_hashes'],
                                 'stream_sha256': payload['stream_sha256']})
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
