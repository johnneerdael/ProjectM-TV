"""Validate worker roles from pinned inputs and reconstructed source trees."""
from __future__ import annotations

from dataclasses import asdict
import difflib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/preset-lab/src'))
from preset_lab.build_worker import prepare_engine
from preset_lab.identity import digest


def sha(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): sha(path)
            for path in sorted(root.rglob('*')) if path.is_file()}


def _supported_roles() -> set[str]:
    return {'upstream', 'patched'} | {f'without-{number:04d}' for number in range(2, 14)}


def _validate_git_pins(inputs: Path, series: dict) -> None:
    engine = inputs / 'third_party/projectm'
    engine_commit = subprocess.check_output(
        ['git', '-C', str(engine), 'rev-parse', 'HEAD'], text=True).strip()
    evaluator_gitlink = subprocess.check_output(
        ['git', '-C', str(engine), 'ls-tree', 'HEAD', 'vendor/projectm-eval'],
        text=True).split()
    evaluator = engine / 'vendor/projectm-eval'
    evaluator_commit = subprocess.check_output(
        ['git', '-C', str(evaluator), 'rev-parse', 'HEAD'], text=True).strip()
    if (engine_commit != series['engine_commit'] or len(evaluator_gitlink) != 4 or
            evaluator_gitlink[2] != series['evaluator_commit'] or
            evaluator_commit != series['evaluator_commit']):
        raise ValueError('Prepared source git pins differ from the documented series')


def _validate_patch_inputs(role: str, inputs: Path, series: dict) -> None:
    patch_dir = inputs / 'tools/projectm-patches'
    if not patch_dir.is_dir():
        raise ValueError('Prepared patch input directory is missing')
    expected = [] if role == 'upstream' else series['patches']
    actual_names = sorted(path.name for path in patch_dir.glob('*.patch'))
    expected_names = sorted(entry['filename'] for entry in expected)
    if actual_names != expected_names:
        raise ValueError('Prepared patch input inventory differs: ' + role)
    for entry in expected:
        patch = patch_dir / entry['filename']
        if sha(patch) != entry['sha256']:
            raise ValueError('Prepared patch bytes differ: ' + entry['filename'])


def _replace(path: Path, old: str, new: str, relative: str) -> str:
    before = path.read_text()
    if before.count(old) != 1:
        raise ValueError(f'Capture adjustment anchor differs: {relative}')
    after = before.replace(old, new)
    path.write_text(after)
    return ''.join(difflib.unified_diff(
        before.splitlines(True), after.splitlines(True),
        fromfile=relative, tofile=relative, n=0))


def _apply_role_source(role: str, source: Path, patch_dir: Path, series: dict) -> str:
    adjustments = []
    if role == 'upstream':
        path = source / 'src/libprojectM/Renderer/Platform/GladLoader.cpp'
        relative = path.relative_to(source).as_posix()
        adjustments.append(_replace(path, '.WithMinimumVersion(3, 2)',
                                    '.WithMinimumVersion(3, 0)', relative))
        adjustments.append(_replace(path, '.WithMinimumShaderLanguageVersion(3, 20)',
                                    '.WithMinimumShaderLanguageVersion(3, 0)', relative))
        return ''.join(adjustments)

    if role.startswith('without-'):
        number = int(role[8:])
        patch = patch_dir / next(entry['filename'] for entry in series['patches']
                                 if int(entry['number']) == number)
        environment = dict(os.environ, GIT_CEILING_DIRECTORIES=str(source.parent))
        subprocess.run(['git', 'apply', '--reverse', str(patch)], cwd=source,
                       check=True, env=environment, capture_output=True)
    path = source / 'src/libprojectM/Renderer/Shader.cpp'
    relative = path.relative_to(source).as_posix()
    adjustments.append(_replace(
        path, '        ProgramCache::Instance().Store(m_shaderProgram, cacheKey);',
        '        // Proof capture: API36 binary export is outside image validation.', relative))
    return ''.join(adjustments)


def _normalise_adjustments(value: str) -> str:
    normalized = []
    for line in value.splitlines(keepends=True):
        if line.startswith(('--- ', '+++ ')):
            prefix, path = line[:4], line[4:].rstrip('\r\n')
            marker = '/engine/'
            if marker in path:
                path = path.rsplit(marker, 1)[1]
            elif path.startswith('engine/'):
                path = path[len('engine/'):]
            elif Path(path).is_absolute():
                raise ValueError('Capture adjustment path is outside the worker engine')
            normalized.append(prefix + path + line[len(line.rstrip('\r\n')):])
        else:
            normalized.append(line)
    return ''.join(normalized)


def validate_prepared_source(role: str, identity: dict, series: dict) -> None:
    """Rebuild the prepared source recipe and reject role claims that disagree."""
    if role not in _supported_roles():
        raise ValueError('Unsupported worker role: ' + role)
    removed = int(role[8:]) if role.startswith('without-') else None
    expected_patches = [] if role == 'upstream' else series['patches']
    if ('patch_removed' not in identity or identity.get('role') != role or
            identity.get('patch_removed') != removed or
            type(identity.get('patch_removed')) is not type(removed) or
            identity.get('ordered_patches') != expected_patches):
        raise ValueError('Worker role metadata differs from the requested source role: ' + role)
    source_commit = identity.get('source_commit')
    if (not isinstance(source_commit, str) or len(source_commit) != 40 or
            any(char not in '0123456789abcdef' for char in source_commit.lower()) or
            identity.get('engine_commit') != series['engine_commit'] or
            identity.get('evaluator_commit') != series['evaluator_commit']):
        raise ValueError('Worker source pins differ from the documented series: ' + role)

    source_manifest = Path(identity['source_hashes'])
    role_dir = source_manifest.parent
    inputs = role_dir / 'inputs'
    source = role_dir / 'engine'
    patch_dir = inputs / 'tools/projectm-patches'
    _validate_patch_inputs(role, inputs, series)
    _validate_git_pins(inputs, series)

    with tempfile.TemporaryDirectory(prefix='patch-proof-source-') as temporary:
        rebuilt, parent = prepare_engine(inputs, Path(temporary) / 'prepared')
        parent_data = asdict(parent)
        if identity.get('parent') != parent_data:
            raise ValueError('Prepared source identity differs from rebuilt pins: ' + role)
        if json.loads((rebuilt / 'preset-lab-identity.json').read_text()) != parent_data:
            raise ValueError('Rebuilt preset-lab identity differs: ' + role)

        saved_snapshot = role_dir / 'snapshot' / 'engines' / digest(parent_data)
        if file_hashes(saved_snapshot) != file_hashes(rebuilt):
            raise ValueError('Retained prepared snapshot differs from pinned inputs: ' + role)

        expected_source = Path(temporary) / 'expected-engine'
        shutil.copytree(rebuilt, expected_source)
        expected_adjustments = _apply_role_source(role, expected_source, patch_dir, series)

        if file_hashes(source) != file_hashes(expected_source):
            raise ValueError('Compiled engine does not match its prepared source role: ' + role)
        actual_source_hashes = json.loads(source_manifest.read_text())
        if actual_source_hashes != file_hashes(source):
            raise ValueError('Compiled source inventory changed: ' + role)

        adjustments_path = role_dir / 'capture-adjustments.diff'
        actual_adjustments = _normalise_adjustments(adjustments_path.read_text())
        if actual_adjustments != expected_adjustments:
            raise ValueError('Capture adjustments differ from the prepared source role: ' + role)
        if sha(adjustments_path) != identity.get('adjustments_sha256'):
            raise ValueError('Capture adjustment identity changed: ' + role)
