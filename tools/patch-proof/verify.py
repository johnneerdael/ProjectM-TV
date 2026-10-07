#!/usr/bin/env python3
"""Verify retained image payloads, repeats, backend and source-bound worker identities."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw
from source_identity import validate_prepared_source


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(work: Path) -> dict:
    result = json.loads((work / 'results.json').read_text())
    series = json.loads((Path(__file__).resolve().parents[2] /
                         'docs/superpowers/evidence/current-patch-proof/series.json').read_text())
    width, height = result['dimensions']
    kind = result.get('capture_kind')
    if kind not in ('image', 'texture-journey', 'evaluator'):
        raise ValueError('Missing capture kind; reproduce with the current capture tool')
    verified, rejected, comparisons = [], [], {}
    previous = None
    for role, value in result['roles'].items():
        identity = value['worker']
        validate_prepared_source(role, identity, series)
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
        for repeat, run in enumerate(runs):
            manifest = run['manifest']
            if manifest['frames'] != 120 or manifest['status'] != 'success' or manifest['gl_error_frames']:
                raise ValueError('Incomplete or GL-failed render')
            if [manifest['width'], manifest['height']] != [width, height]:
                raise ValueError('Manifest dimensions differ')
            backend = [manifest[k] for k in ('gl_vendor', 'gl_renderer', 'gl_version', 'glsl_version')]
            if backend != result['backend'] or len(run['frame_hashes']) != 120:
                raise ValueError('Backend or frame count differs')
            stream = (work / role / str(repeat) / 'frames.rgb').read_bytes()
            frame_size = width * height * 3
            if len(stream) != frame_size * 120:
                raise ValueError('RGB stream length differs')
            if sha(stream) != run['stream_sha256']:
                raise ValueError('RGB stream hash differs')
            actual_hashes = [sha(stream[index * frame_size:(index + 1) * frame_size])
                             for index in range(120)]
            if actual_hashes != run['frame_hashes']:
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
    return {'status': 'verified', 'successful_roles': verified, 'rejected_roles': rejected,
            'different_frames_between_adjacent_successful_roles': comparisons,
            'scope': 'retained full RGB streams/images/repeats/reconstructed source/binary identities; load rejection remains a rejection'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.work.resolve())
    report['verifier_sha256'] = sha(Path(__file__).read_bytes())
    report['source_identity_sha256'] = sha(Path(__file__).with_name('source_identity.py').read_bytes())
    (args.work / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
