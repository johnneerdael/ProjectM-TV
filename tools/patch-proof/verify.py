#!/usr/bin/env python3
"""Verify retained image payloads, repeats, backend and source-bound worker identities."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw
from source_identity import validate_prepared_source, DEFAULT_SERIES, digest
from rgb_payload import inspect_rgb, payload_path


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_run_protocol(work: Path, result: dict, role: str, repeat: int, manifest: dict) -> dict:
    identity = {'role': role, 'repeat': repeat}
    actual_identity = manifest.get('identity')
    if (actual_identity != identity or not isinstance(actual_identity, dict) or
            type(actual_identity.get('repeat')) is not int):
        raise ValueError('Rendered run identity differs from its role/repeat')
    if (type(manifest.get('seed')) is not int or manifest['seed'] != 12345 or
            type(manifest.get('fps')) is not int or manifest['fps'] != 30):
        raise ValueError('Rendered run protocol differs from frozen seed/FPS')
    directory = work / role / str(repeat)
    if json.loads((directory / 'manifest.json').read_text()) != manifest:
        raise ValueError('Retained manifest differs from inline run record')
    job = json.loads((directory / 'job.json').read_text())
    if (job.get('identity') != identity or
            type(job.get('identity', {}).get('repeat')) is not int):
        raise ValueError('Retained job identity differs from its role/repeat')
    controls = result.get('host_controls', {})
    width, height = result['dimensions']
    expected = {'width': width, 'height': height, 'fps': 30, 'seed': 12345,
                'warmup_seconds': 0, 'measurement_seconds': 4,
                'line_reference_height': controls.get('line_reference_height', 0),
                'line_antialiasing': controls.get('line_antialiasing', False)}
    cfg = job.get('config', {})
    if (job.get('schema_version') != 1 or any(cfg.get(key) != value for key, value in expected.items()) or
            type(cfg.get('seed')) is not int or type(cfg.get('fps')) is not int or
            cfg.get('feedback_detail', -1) != controls.get('feedback_detail', -1) or
            cfg.get('soft_cut_seconds', 2) != 2 or
            cfg.get('shader_failure_probe', False) != (result.get('diagnostic_kind') == 'shader-fragment-failure') or
            cfg.get('texture_history_probe', False) != (result.get('diagnostic_kind') == 'texture-history')):
        raise ValueError('Retained job protocol differs from capture settings')
    if 'line_reference_width' in cfg and cfg['line_reference_width'] != controls.get('line_reference_width', 0):
        raise ValueError('Retained job protocol differs from reference width')
    events = []
    if result['capture_kind'] == 'texture-journey':
        texture_root = job.get('texture_root', '')
        if not texture_root.endswith('/a'):
            raise ValueError('Retained host events have no initial pack-a root')
        events = [{'frame': 20, 'texture_root': texture_root[:-1] + 'b'},
                  {'frame': 21, 'load_preset': job.get('preset_path'), 'smooth': True},
                  {'frame': 40, 'reset_textures': True}]
    if job.get('events', []) != events:
        raise ValueError('Retained host events differ from the capture sequence')
    return {key: value for key, value in job.items() if key != 'identity'}


def verify_shader_lifetime(role: str, runs: list[dict]) -> None:
    observations = [run['manifest'].get('diagnostics') for run in runs]
    if observations[0] != observations[1] or not isinstance(observations[0], dict):
        raise ValueError('Shader lifetime diagnostic does not repeat')
    value = observations[0]
    expected_live = list(range(1, 17)) if role == 'upstream' else [0] * 16
    expected_final = 16 if role == 'upstream' else 0
    messages = value.get('rejection_messages', [])
    if (value.get('kind') != 'shader-fragment-failure' or value.get('attempts') != 16 or
            value.get('created_shader_objects') != 34 or
            value.get('live_vertex_after_each_failure') != expected_live or
            value.get('live_vertex_before_cleanup') != expected_final or
            value.get('retry_linked') is not True or value.get('observer_gl_error') != 0 or
            value.get('diagnostic_cleanup_complete') is not True or len(messages) != 16 or
            any(not isinstance(message, str) or 'fragment shader' not in message for message in messages)):
        raise ValueError('Shader lifetime diagnostic contradicts its observer/role contract')


def verify_texture_history(role: str, runs: list[dict]) -> None:
    values = [run['manifest'].get('diagnostics') for run in runs]
    if values[0] != values[1] or not isinstance(values[0], dict):
        raise ValueError('Texture history diagnostic does not repeat')
    value = values[0]
    upstream = role == 'upstream'
    expected_pixels = ([0, 160, 80, 255] if upstream else [0, 0, 0, 0]) * (64 * 48)
    if (value.get('kind') != 'texture-history' or [value.get('width'), value.get('height')] != [64, 48] or
            value.get('controlled_poison_rgba') != [0, 160, 80, 255] or
            value.get('poison_control_passed') is not True or
            value.get('fresh_rgba') != expected_pixels or value.get('recreated_rgba') != expected_pixels or
            value.get('driver_allocations') != (2 if upstream else 1) or
            value.get('pool_available') is not (not upstream) or
            value.get('pool_bytes_after_retire') != (0 if upstream else 64 * 48 * 4) or
            value.get('caller_state_preserved') != [True, True] or value.get('observer_gl_error') != 0):
        raise ValueError('Texture history diagnostic contradicts its pixel/state/allocation contract')


def verify_inputs(work: Path, result: dict, preset: Path | None, textures: Path | None) -> dict:
    inputs = work / 'inputs'
    if inputs.exists():
        preset, textures = inputs / 'witness.milk', inputs / 'textures'
        if not preset.is_file() or not textures.is_dir():
            raise ValueError('Retained capture inputs are incomplete')
        source = 'retained'
    else:
        if preset is None or textures is None:
            raise ValueError('Historical capture has no retained inputs; supply both --preset and --textures '
                             '(verify(..., preset=..., textures=...))')
        if not preset.is_file() or not textures.is_dir():
            raise ValueError('Explicit historical preset or texture directory is unavailable')
        source = 'explicit-external'
    if sha(preset.read_bytes()) != result.get('preset_sha256'):
        raise ValueError('Preset input hash differs')
    actual = {p.relative_to(textures).as_posix(): sha(p.read_bytes())
              for p in sorted(textures.rglob('*')) if p.is_file()}
    if actual != result.get('textures'):
        raise ValueError('Texture input inventory differs')
    return {'source': source, 'preset': str(preset.resolve()), 'textures': str(textures.resolve())}


def verify(work: Path, ndk: Path | None = None, series_path: Path = DEFAULT_SERIES, *,
           preset: Path | None = None, textures: Path | None = None) -> dict:
    if ndk is None:
        raise ValueError('NDK is required for executable-to-source verification')
    result = json.loads((work / 'results.json').read_text())
    series = json.loads(series_path.read_text())
    snapshot = result.get('series_sha256')
    legacy = snapshot is None and series == json.loads(DEFAULT_SERIES.read_text())
    if not legacy and snapshot != digest(series):
        raise ValueError('Capture snapshot differs from the selected series')
    width, height = result['dimensions']
    kind = result.get('capture_kind')
    if kind not in ('image', 'texture-journey', 'evaluator'):
        raise ValueError('Missing capture kind; reproduce with the current capture tool')
    audio = (work / 'audio.f32').read_bytes()
    if len(audio) != 120 * 1470 * 4 or sha(audio) != result.get('pcm_sha256'):
        raise ValueError('Retained PCM differs from frozen capture input')
    if result.get('clock') != 'frame/30.0' or result.get('frames') != 120:
        raise ValueError('Capture frame/clock protocol differs')
    input_verification = verify_inputs(work, result, preset, textures)
    verified, rejected, comparisons = [], [], {}
    previous = None
    common_job = None
    for role, value in result['roles'].items():
        identity = value['worker']
        validate_prepared_source(role, identity, series, ndk)
        if sha(Path(identity['binary']).read_bytes()) != identity['binary_sha256']:
            raise ValueError('Worker binary changed: ' + role)
        source_manifest = Path(identity['source_hashes'])
        source = source_manifest.parent / 'engine'
        expected = json.loads(source_manifest.read_text())
        actual = {p.relative_to(source).as_posix(): sha(p.read_bytes())
                  for p in sorted(source.rglob('*')) if p.is_file()}
        if expected != actual:
            raise ValueError('Compiled source inventory changed: ' + role)
        runs = value['runs']
        if len(runs) != 2:
            raise ValueError('Expected exactly two repeats')
        if kind == 'evaluator':
            if any(r['exit'] != 0 or r['control']['compiled'] != [True, True] for r in runs):
                raise ValueError('Evaluator control failed to compile')
            if runs[0]['control'] != runs[1]['control'] or not value['repeat_equal']:
                raise ValueError('Evaluator control does not repeat')
            if role not in ('upstream', 'patched', 'without-0003'):
                raise ValueError('Unsupported evaluator-control role: ' + role)
            expected_contract = role == 'patched'
            control = runs[0]['control']
            streams = control['streams']
            if len(streams) != 2 or any(len(s) != 128 for s in streams):
                raise ValueError('Evaluator stream lengths differ')
            for stream in streams:
                if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v < 1000000 for v in stream):
                    raise ValueError('Evaluator random samples are invalid')
                if len(set(stream)) < 2:
                    raise ValueError('Evaluator random stream is constant')
            observed_equal = streams[0] == streams[1]
            if observed_equal != expected_contract or control['fresh_thread_streams_equal'] != observed_equal:
                raise ValueError('Evaluator thread-isolation contract failed: ' + role)
            if control['lone_dot_is_zero'] != expected_contract:
                raise ValueError('Evaluator lone-dot contract failed: ' + role)
            for repeat, run in enumerate(runs):
                try:
                    output = (work / role / str(repeat) / 'output.txt').read_text()
                    # Capture appends stderr after the single stdout JSON value.
                    retained, _ = json.JSONDecoder().raw_decode(output.lstrip())
                except (OSError, ValueError) as error:
                    raise ValueError('Retained evaluator output is unavailable or invalid') from error
                if retained != run['control']:
                    raise ValueError('Retained evaluator output differs from inline control')
            verified.append(role)
            continue
        if any(r.get('status') != 'success' for r in runs):
            if any(r.get('status') == 'success' for r in runs):
                raise ValueError('Mixed success/failure repeats: ' + role)
            if any(r.get('status') != 'failed' or type(r.get('exit')) is not int or r['exit'] == 0
                   for r in runs):
                raise ValueError('Invalid failure record: ' + role)
            if value['repeat_equal'] is not False:
                raise ValueError('Failed repeats cannot be claimed equal: ' + role)
            rejected.append(role)
            continue
        if not value['repeat_equal'] or runs[0]['frame_hashes'] != runs[1]['frame_hashes']:
            raise ValueError('Unstable repeats: ' + role)
        if result.get('diagnostic_kind') == 'shader-fragment-failure':
            verify_shader_lifetime(role, runs)
        if result.get('diagnostic_kind') == 'texture-history':
            verify_texture_history(role, runs)
        for repeat, run in enumerate(runs):
            manifest = run['manifest']
            job = verify_run_protocol(work, result, role, repeat, manifest)
            if common_job is not None and job != common_job:
                raise ValueError('Retained jobs differ across roles/repeats')
            common_job = job
            if manifest['frames'] != 120 or manifest['status'] != 'success' or manifest['gl_error_frames']:
                raise ValueError('Incomplete or GL-failed render')
            if [manifest['width'], manifest['height']] != [width, height]:
                raise ValueError('Manifest dimensions differ')
            backend = [manifest[k] for k in ('gl_vendor', 'gl_renderer', 'gl_version', 'glsl_version')]
            if any(value in manifest['gl_renderer'].lower() for value in
                   ('swiftshader', 'llvmpipe', 'softpipe', 'lavapipe', 'software rasterizer')):
                raise ValueError('Software renderer is outside GPU proof scope')
            if backend != result['backend'] or len(run['frame_hashes']) != 120:
                raise ValueError('Backend or frame count differs')
            payload = inspect_rgb(payload_path(work / role / str(repeat)), width, height)
            if payload['stream_sha256'] != run['stream_sha256']:
                raise ValueError('RGB stream hash differs')
            if payload['frame_hashes'] != run['frame_hashes']:
                raise ValueError('RGB stream frame hashes differ')
            frames = [29, 40, 59, 119] if kind == 'texture-journey' else [29, 59, 119]
            for frame in frames:
                image = Image.open(work / role / str(repeat) / f'{frame}.png').convert('RGB')
                if image.size != (width, height) or sha(image.tobytes()) != run['frame_hashes'][frame]:
                    raise ValueError('PNG payload is not the recorded frame')
        if previous is not None:
            comparisons[previous[0] + ':' + role] = sum(a != b for a, b in zip(
                previous[1], runs[0]['frame_hashes']))
        previous = role, runs[0]['frame_hashes']
        verified.append(role)
    if not verified:
        raise ValueError('No successful verified role')
    if kind != 'evaluator':
        if not (work / 'comparison.png').is_file():
            raise ValueError('Missing comparison image')
        image = Image.open(work / 'comparison.png').convert('RGB')
        if image.size != (width * len(result['roles']), height + 32):
            raise ValueError('Comparison dimensions differ')
        expected_image = Image.new('RGB', image.size, '#171717')
        draw = ImageDraw.Draw(expected_image)
        for col, (role, value) in enumerate(result['roles'].items()):
            draw.text((col * width + 4, 8), role, fill='white')
            if role in verified:
                frame = Image.open(work / role / '0/119.png').convert('RGB')
                expected_image.paste(frame, (col * width, 32))
            else:
                draw.text((col * width + 8, 80), 'Rejected or unstable\nNo verified framebuffer', fill='#ffb4ab')
        if image.tobytes() != expected_image.tobytes():
            raise ValueError('Comparison changed framebuffer pixels, labels or rejection panels')
    scope = ('retained evaluator output/repeats/reconstructed source/binary identities' if kind == 'evaluator'
             else 'retained full RGB streams/images/repeats/reconstructed source/binary identities; '
                  'load rejection remains a rejection')
    scope += '; preset and texture bytes match recorded hashes'
    if input_verification['source'] == 'explicit-external':
        scope += '; historical inputs supplied explicitly, original uploaded bytes were not retained'
    return {'status': 'verified', 'successful_roles': verified, 'rejected_roles': rejected,
            'different_frames_between_adjacent_successful_roles': comparisons,
            'input_verification': input_verification, 'scope': scope}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--series', type=Path, default=DEFAULT_SERIES,
                        help='Same series manifest selected for preparation/capture')
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--ndk', type=Path, required=True,
                        help='Android NDK 27.3.13750724 for independent worker rebuilds')
    parser.add_argument('--preset', type=Path,
                        help='Exact preset for historical captures without retained inputs')
    parser.add_argument('--textures', type=Path,
                        help='Exact texture inventory for historical captures without retained inputs')
    args = parser.parse_args()
    report = verify(args.work.resolve(), args.ndk.resolve(), args.series.resolve(),
                    preset=args.preset, textures=args.textures)
    report['verifier_sha256'] = sha(Path(__file__).read_bytes())
    report['source_identity_sha256'] = sha(Path(__file__).with_name('source_identity.py').read_bytes())
    report['rgb_payload_sha256'] = sha(Path(__file__).with_name('rgb_payload.py').read_bytes())
    (args.work / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
