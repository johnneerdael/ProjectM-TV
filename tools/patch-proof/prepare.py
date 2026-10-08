#!/usr/bin/env python3
"""Rebuild source-bound Android proof roles without changing the checkout."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / 'docs/superpowers/evidence/current-patch-proof'
sys.path.insert(0, str(ROOT / 'tools/preset-lab/src'))
sys.path.insert(0, str(ROOT / 'tools/core-corpus'))
from preset_lab.build_worker import prepare_engine
from build_core_aars import checkout_pinned_engine
from source_identity import build_patch_worker, prepare_harness, DEFAULT_SERIES, digest, _supported_roles


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + '\n')


def run(args: list[str], **kwargs) -> None:
    subprocess.run(args, check=True, **kwargs)


def change(path: Path, old: str, new: str) -> str:
    before = path.read_text()
    if before.count(old) != 1:
        raise ValueError(f'Missing or ambiguous capture anchor in {path}')
    after = before.replace(old, new)
    path.write_text(after)
    return ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                       fromfile=str(path), tofile=str(path), n=0))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--series', type=Path, default=DEFAULT_SERIES,
                        help='Explicit series manifest; default preserves the frozen 13-patch checkpoint')
    parser.add_argument('--cache-repo', type=Path, required=True,
                        help='Checkout containing the initialized projectM/evaluator git caches')
    parser.add_argument('--source', help='Must match the selected series source commit')
    parser.add_argument('--ndk', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--roles', nargs='+', default=['upstream', 'patched'],
                        help='upstream, patched, or without-NNNN (one current patch removed)')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    series = json.loads(args.series.read_text())
    if args.jobs < 1:
        parser.error('--jobs must be positive')
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    cache = args.cache_repo.resolve()
    source = subprocess.check_output(['git', '-C', str(cache), 'rev-parse', args.source or series['source_commit']],
                                     text=True).strip()
    if source != series['source_commit']:
        raise ValueError('Source commit differs from the selected snapshot')
    patches = []
    for entry in series['patches']:
        data = subprocess.check_output(['git', '-C', str(cache), 'show',
                                        source + ':tools/projectm-patches/' + entry['filename']])
        if hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('This reproducer requires the documented patch series')
        patches.append((entry, data))
    engine, pin, evaluator = checkout_pinned_engine(cache, source, work / 'engine-checkout')
    if (pin, evaluator) != (series['engine_commit'], series['evaluator_commit']):
        raise ValueError('Source pins differ from the documented comparison')
    harness = prepare_harness(work / 'harness')
    identities = {}
    for role in args.roles:
        number = int(role[8:]) if role.startswith('without-') else None
        if role not in _supported_roles(series):
            raise ValueError('Use upstream, patched, or an ablation in the selected series')
        dest = work / role
        repo = dest / 'inputs'
        (repo / 'third_party').mkdir(parents=True)
        (repo / 'third_party/projectm').symlink_to(engine, target_is_directory=True)
        patch_dir = repo / 'tools/projectm-patches'
        patch_dir.mkdir(parents=True)
        if role != 'upstream':
            for entry, data in patches:
                (patch_dir / entry['filename']).write_bytes(data)
        snapshot, identity = prepare_engine(repo, dest / 'snapshot')
        compiled_source = dest / 'engine'
        shutil.copytree(snapshot, compiled_source)
        transforms = []
        if role == 'upstream':
            path = compiled_source / 'src/libprojectM/Renderer/Platform/GladLoader.cpp'
            transforms.append(change(path, '.WithMinimumVersion(3, 2)', '.WithMinimumVersion(3, 0)'))
            transforms.append(change(path, '.WithMinimumShaderLanguageVersion(3, 20)',
                                     '.WithMinimumShaderLanguageVersion(3, 0)'))
        else:
            if number is not None:
                patch = patch_dir / patches[number - 1][0]['filename']
                run(['git', 'apply', '--reverse', str(patch)], cwd=compiled_source,
                    env=dict(os.environ, GIT_CEILING_DIRECTORIES=str(compiled_source.parent)))
            transforms.append(change(compiled_source / 'src/libprojectM/Renderer/Shader.cpp',
                                     '        ProgramCache::Instance().Store(m_shaderProgram, cacheKey);',
                                     '        // Proof capture: API36 binary export is outside image validation.'))
        binary = build_patch_worker(harness, dest / 'ndk-build', compiled_source,
                                    args.ndk.resolve(), role, args.jobs)
        sources = {p.relative_to(compiled_source).as_posix(): sha(p)
                   for p in sorted(compiled_source.rglob('*')) if p.is_file()}
        write(dest / 'source-hashes.json', sources)
        (dest / 'capture-adjustments.diff').write_text(''.join(transforms))
        identities[role] = {'role': role, 'series_sha256': digest(series),
                            'source_commit': source, 'engine_commit': pin,
                            'evaluator_commit': evaluator, 'parent': asdict(identity),
                            'patch_removed': number, 'ordered_patches': [p[0] for p in patches]
                            if role != 'upstream' else [], 'binary': str(binary),
                            'binary_sha256': sha(binary), 'source_hashes': str(dest / 'source-hashes.json'),
                            'harness_sha256': {p.relative_to(harness).as_posix(): sha(p)
                                              for p in sorted(harness.rglob('*')) if p.is_file()},
                            'adjustments_sha256': sha(dest / 'capture-adjustments.diff'),
                            'prepare_sha256': sha(Path(__file__)), 'shipping_binary': False}
        write(dest / 'identity.json', identities[role])
        print(role + ': built', flush=True)
    write(work / 'workers.json', identities)


if __name__ == '__main__':
    main()
