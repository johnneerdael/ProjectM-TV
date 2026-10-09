"""Check published lossless frames against captured RGB and role identities."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from guide_bindings import verify_guide
from frozen_protocol import FROZEN_PCM, UPSTREAM_SOURCE_TREE_SHA256


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inventory_digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False).encode('utf-8'))


def verify_request(record, capture, canonical, case):
    """Bind the original complete request to inputs, outputs and the frozen protocol.

    Do not resolve historical absolute paths on another checkout. The preserved
    relative inputs are checked separately against the actual committed bytes.
    """
    role, repeat = record['role'], record['repeat']
    request = record['request']
    assert set(request) == {'schema_version', 'config', 'pcm_path', 'preset_path',
                            'texture_root', 'bands_path', 'manifest_path', 'identity'}, f'request fields: {case}/{role}'
    assert type(request['schema_version']) is int and request['schema_version'] == 1, f'request schema: {case}'
    assert request['identity'] == canonical[role], f'request worker: {case}/{role}'
    config = request['config']
    expected = {'width': capture['width'], 'height': capture['height'], 'fps': 30,
                'warmup_seconds': 0, 'measurement_seconds': capture['frames']/30,
                'seed': 12345, 'line_reference_height': 0, 'line_antialiasing': False}
    assert set(config) == set(expected), f'request config fields: {case}/{role}'
    for key, value in expected.items():
        assert type(config[key]) is type(value) and config[key] == value, f'request config {key}: {case}/{role}'
    # The frozen worker derives absent line_reference_width from height, thus0/0.
    # Its hash binds the fixed48×32 mesh, (frame+1)/fps clock and TV feedback-off
    # setup. Requests cannot add an override that the protocol did not admit.
    assert request['identity']['harness']['worker.cpp'] == 'b4e39678acbfd70c386101425854666bf057bccd075a803c7fd6ba42737e260f', f'request clock harness: {case}'
    worker = Path(canonical[role]['worker'])
    host = worker.parents[2]
    run = host / 'captures' / case / f'{role}-{repeat}'
    assert request['pcm_path'] == str(host / 'captures' / case / 'audio.f32'), f'request PCM path: {case}/{role}'
    assert request['preset_path'] == capture['preset_path'], f'request preset path: {case}/{role}'
    assert request['texture_root'] == str(host.parent.parent / 'core/src/main/assets/textures'), f'request texture path: {case}/{role}'
    assert request['bands_path'] == str(run / 'bands.jsonl'), f'request bands path: {case}/{role}/{repeat}'
    assert request['manifest_path'] == str(run / 'manifest.json'), f'request manifest path: {case}/{role}/{repeat}'
    assert (Path(request['preset_path']).name == Path(capture['preset_relative_path']).name), f'request preset name: {case}'


def verify(repo):
    evidence = repo / 'docs/superpowers/evidence/patch-visual-catalog'
    images = json.loads((evidence / 'images.json').read_text())
    gallery = json.loads((evidence / 'gallery.json').read_text())
    assert len(gallery) == 18 and len({e['issue'] for e in gallery}) == 18
    assert len(images) == 46, 'expected 23 complete pairs'
    expected = set()
    selected_frames = {}
    for entry in gallery:
        for pair in [entry, *entry['extras']]:
            expected.update(f"{pair['case']}-{role}.png" for role in ('upstream', 'patched'))
            assert pair['case'] not in selected_frames, 'duplicate gallery case'
            selected_frames[pair['case']] = pair['frame']
    assert set(images) == expected
    assets = repo / 'docs/user-guide/images/patches/audit'
    assert {p.name for p in assets.glob('*.png')} == expected
    cases = set()
    for name, info in images.items():
        assert name == f"{info['case']}-{info['role']}.png", f'filename identity: {name}'
        assert info['frame'] == selected_frames[info['case']], f'gallery frame: {name}'
        path = assets / name
        assert sha(path.read_bytes()) == info['png_sha256'], name
        with Image.open(path) as image:
            assert image.mode == 'RGB' and image.size == (info['width'], info['height']), name
            assert sha(image.tobytes()) == info['raw_rgb_sha256'], name
        record = json.loads((evidence / 'captures' / f"{info['case']}.json").read_text())
        assert (info['width'], info['height']) == (record['width'], record['height']), f'image dimensions: {name}'
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
    workers = json.loads((evidence / 'workers.json').read_text())
    textures = json.loads((evidence / 'textures.json').read_text())
    texture_digest = inventory_digest(textures)
    texture_root = repo / 'core/src/main/assets/textures'
    actual_textures = {path.relative_to(texture_root).as_posix(): sha(path.read_bytes())
                       for path in texture_root.rglob('*') if path.is_file()}
    assert actual_textures == textures, 'preserved texture bytes differ from inventory'
    assert set(workers) == {'upstream', 'patched'}
    canonical = {}
    supplementary = {'source_tree_sha256', 'texture_inventory_sha256',
                     'evaluator_commit', 'ordered_patches'}
    for role, worker in workers.items():
        source_tree = json.loads((evidence / f'{role}-source-tree.json').read_text())
        assert inventory_digest(source_tree) == worker['source_tree_sha256'], f'source inventory: {role}'
        if role == 'upstream':
            assert inventory_digest(source_tree) == UPSTREAM_SOURCE_TREE_SHA256, 'frozen upstream source anchor'
        assert texture_digest == worker['texture_inventory_sha256'], 'texture inventory mismatch'
        assert worker['evaluator_commit'] == '22fb0cfd8f2dfbcd2b68f2443e7f44e19b32c09a'
        patches = [(p['filename'], p['sha256']) for p in worker['ordered_patches']]
        assert inventory_digest(patches) == worker['engine']['patches_sha256'], f'patch inventory: {role}'
        canonical[role] = {key: value for key, value in worker.items() if key not in supplementary}
    inputs = json.loads((evidence / 'cases.json').read_text())
    indexed = {entry['name']: entry for entry in inputs}
    assert len(indexed) == len(inputs) == 26
    assert set(runs) == set(captures) == set(indexed), 'run/capture/input case sets differ'
    for case, records in runs.items():
        capture = captures[case]
        assert capture['name'] == case
        assert all(capture[key] == value for key, value in indexed[case].items()), case
        preset_file = repo / capture['preset_relative_path']
        assert preset_file.is_file(), f'preset file missing: {case}'
        assert sha(preset_file.read_bytes()) == capture['preset_sha256'], f'preset bytes: {case}'
        pcm_file = repo / capture['pcm_relative_path']
        assert pcm_file.is_file(), f'PCM file missing: {case}'
        assert sha(pcm_file.read_bytes()) == capture['pcm_sha256'], f'PCM bytes: {case}'
        assert capture['frames'] in FROZEN_PCM and capture['pcm_sha256'] == FROZEN_PCM[capture['frames']], f'frozen PCM anchor: {case}'
        assert pcm_file.stat().st_size == capture['frames'] * 1470 * 4, f'PCM frame length: {case}'
        assert capture['texture_inventory_sha256'] == texture_digest, f'textures: {case}'
        assert set(capture['roles']) == set(canonical)
        for role in canonical:
            assert capture['roles'][role]['identity'] == canonical[role], f'canonical worker: {case}/{role}'
        observed = set()
        for record in records:
            manifest = record['manifest']
            role, repeat = record['role'], record['repeat']
            assert role in ('upstream', 'patched') and repeat in (0, 1)
            assert (role, repeat) not in observed, f'duplicate run: {case}/{role}/{repeat}'
            observed.add((role, repeat))
            verify_request(record, capture, canonical, case)
            assert record['exit'] == 0 and record['frames'] == manifest['frames'] == capture['frames']
            assert (manifest['width'], manifest['height']) == (capture['width'], capture['height']), case
            assert manifest['fps'] == 30 and manifest['seed'] == capture['seed'] == 12345
            assert manifest['identity'] == capture['roles'][role]['identity'], f'worker mismatch: {case}/{role}'
            assert len(record['frame_sha256']) == capture['frames'], f'frame count: {case}/{role}/{repeat}'
            assert record['frame_sha256'] == capture['roles'][role]['frame_sha256'], f'repeat frame hashes: {case}/{role}/{repeat}'
            assert record['inputs'] == {key: capture[key] for key in
                                       ('preset_sha256', 'pcm_sha256', 'texture_inventory_sha256')}, case
            assert manifest['status'] == 'success' and manifest['gl_error_frames'] == 0
            assert manifest['gl_renderer'] == 'Apple M4 Pro'
        assert observed == {(role, repeat) for role in ('upstream', 'patched') for repeat in (0, 1)}, case
        assert len(records) == 4, case
    assert cases <= set(runs)
    verify_guide((repo / 'docs/user-guide/engine/patches.md').read_text(), gallery, captures)
    print(f'PASS: 18 repairs, {len(images)//2} pairs, {len(runs)} cases, '
          f'{sum(len(r) for r in runs.values())} successful runs; PNG/RGB hashes and pins match')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    verify(parser.parse_args().repo.resolve())
