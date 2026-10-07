#!/usr/bin/env python3
"""Verify retained image payloads, repeats, backend and source-bound worker identities."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify(work: Path) -> dict:
    result = json.loads((work / 'results.json').read_text())
    width, height = result['dimensions']
    verified, rejected, comparisons = [], [], {}
    previous = None
    for role, value in result['roles'].items():
        identity = value['worker']
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
        if 'control' in runs[0]:
            if any(r['exit'] != 0 or r['control']['compiled'] != [True, True] for r in runs):
                raise ValueError('Evaluator control failed to compile')
            if runs[0]['control'] != runs[1]['control'] or not value['repeat_equal']:
                raise ValueError('Evaluator control does not repeat')
            verified.append(role)
            continue
        if any(r['status'] != 'success' for r in runs):
            if any(r['status'] == 'success' for r in runs):
                raise ValueError('Mixed success/failure repeats: ' + role)
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
            frames = [29, 59, 119]
            if (work / role / str(repeat) / "40.png").exists():
                frames.append(40)
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
    if (work / 'comparison.png').is_file():
        image = Image.open(work / 'comparison.png').convert('RGB')
        if image.size != (width * len(result['roles']), height + 32):
            raise ValueError('Comparison dimensions differ')
        for col, (role, value) in enumerate(result['roles'].items()):
            if role not in verified:
                continue
            frame = Image.open(work / role / '0/119.png').convert('RGB')
            if image.crop((col * width, 32, (col + 1) * width, height + 32)).tobytes() != frame.tobytes():
                raise ValueError('Comparison changed framebuffer pixels')
    return {'status': 'verified', 'successful_roles': verified, 'rejected_roles': rejected,
            'different_frames_between_adjacent_successful_roles': comparisons,
            'scope': 'retained images/repeats/source/binary identities; load rejection remains a rejection'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.work.resolve())
    (args.work / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
