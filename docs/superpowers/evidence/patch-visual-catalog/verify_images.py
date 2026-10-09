"""Check published lossless frames against captured RGB and role identities."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(repo):
    evidence = repo / 'docs/superpowers/evidence/patch-visual-catalog'
    images = json.loads((evidence / 'images.json').read_text())
    gallery = json.loads((evidence / 'gallery.json').read_text())
    assert len(gallery) == 18 and len({e['issue'] for e in gallery}) == 18
    assert len(images) == 46, 'expected 23 complete pairs'
    expected = set()
    for entry in gallery:
        for pair in [entry, *entry['extras']]:
            expected.update(f"{pair['case']}-{role}.png" for role in ('upstream', 'patched'))
    assert set(images) == expected
    assets = repo / 'docs/user-guide/images/patches/audit'
    assert {p.name for p in assets.glob('*.png')} == expected
    cases = set()
    for name, info in images.items():
        path = assets / name
        assert sha(path.read_bytes()) == info['png_sha256'], name
        with Image.open(path) as image:
            assert image.mode == 'RGB' and image.size == (info['width'], info['height']), name
            assert sha(image.tobytes()) == info['raw_rgb_sha256'], name
        record = json.loads((evidence / 'captures' / f"{info['case']}.json").read_text())
        role = record['roles'][info['role']]
        assert role['repeat_equal'] is True
        assert len(role['frame_sha256']) == record['frames']
        assert role['frame_sha256'][info['frame']] == info['raw_rgb_sha256'], name
        expected_engine = ('e98fca85e57802d27a6d11499642de2a1d5e994e' if info['role'] == 'upstream'
                           else '6f64807467e312034883a4389e6aa80a675458bc')
        assert role['identity']['engine']['commit'] == expected_engine
        assert role['identity']['source_commit'] == '8a15996e8510533113a44e26feaddc3a7d6e85f5'
        cases.add(info['case'])
    runs = json.loads((evidence / 'run-manifests.json').read_text())
    captures = {p.stem: json.loads(p.read_text()) for p in (evidence / 'captures').glob('*.json')}
    inputs = json.loads((evidence / 'cases.json').read_text())
    indexed = {entry['name']: entry for entry in inputs}
    assert len(indexed) == len(inputs) == 26
    assert set(runs) == set(captures) == set(indexed), 'run/capture/input case sets differ'
    for case, records in runs.items():
        capture = captures[case]
        assert capture['name'] == case
        assert all(capture[key] == value for key, value in indexed[case].items()), case
        observed = set()
        for record in records:
            manifest = record['manifest']
            role, repeat = record['role'], record['repeat']
            assert role in ('upstream', 'patched') and repeat in (0, 1)
            assert (role, repeat) not in observed, f'duplicate run: {case}/{role}/{repeat}'
            observed.add((role, repeat))
            assert record['exit'] == 0 and record['frames'] == manifest['frames'] == capture['frames']
            assert (manifest['width'], manifest['height']) == (capture['width'], capture['height']), case
            assert manifest['fps'] == 30 and manifest['seed'] == capture['seed'] == 12345
            assert manifest['identity'] == capture['roles'][role]['identity'], f'worker mismatch: {case}/{role}'
            assert record['inputs'] == {key: capture[key] for key in ('preset_sha256', 'pcm_sha256')}, case
            assert manifest['status'] == 'success' and manifest['gl_error_frames'] == 0
            assert manifest['gl_renderer'] == 'Apple M4 Pro'
        assert observed == {(role, repeat) for role in ('upstream', 'patched') for repeat in (0, 1)}, case
        assert len(records) == 4, case
    assert cases <= set(runs)
    print(f'PASS: 18 repairs, {len(images)//2} pairs, {len(runs)} cases, '
          f'{sum(len(r) for r in runs.values())} successful runs; PNG/RGB hashes and pins match')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    verify(parser.parse_args().repo.resolve())
