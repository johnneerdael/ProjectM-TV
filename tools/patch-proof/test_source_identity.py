"""Source-derived roles reject metadata that contradicts the prepared tree."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import importlib.util

SPEC = importlib.util.spec_from_file_location(
    'patch_proof_source_identity', Path(__file__).with_name('source_identity.py'))
SOURCE_IDENTITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SOURCE_IDENTITY)


@dataclass(frozen=True)
class EngineIdentity:
    commit: str
    patches_sha256: str
    instrumentation_sha256: str


class PreparedSourceDisposition(unittest.TestCase):
    def make_fixture(self, root, prepared_role):
        role_dir = root / 'patched'
        inputs = role_dir / 'inputs'
        patch_dir = inputs / 'tools/projectm-patches'
        patch_dir.mkdir(parents=True)
        (inputs / 'third_party/projectm').mkdir(parents=True)

        patch_text = '''diff --git a/renderer.cpp b/renderer.cpp
index 1111111..2222222 100644
--- a/renderer.cpp
+++ b/renderer.cpp
@@ -1 +1 @@
-value = base;
+value = patched;
'''
        patch_path = patch_dir / '0010.patch'
        patch_path.write_text(patch_text)
        patch_hash = hashlib.sha256(patch_path.read_bytes()).hexdigest()
        series = {
            'source_commit': 'a' * 40,
            'engine_commit': 'engine-pin',
            'evaluator_commit': 'evaluator-pin',
            'patches': [{'number': '0010', 'filename': '0010.patch', 'sha256': patch_hash}],
        }
        patch_digest = SOURCE_IDENTITY.digest([('0010.patch', patch_hash)])
        parent = EngineIdentity('engine-pin', patch_digest, 'instrumentation-digest')

        fresh_snapshot = root / 'fresh-snapshot'
        fresh_snapshot.mkdir()
        (fresh_snapshot / 'renderer.cpp').write_text('value = patched;\n')
        shader = fresh_snapshot / 'src/libprojectM/Renderer/Shader.cpp'
        shader.parent.mkdir(parents=True)
        shader.write_text('        ProgramCache::Instance().Store(m_shaderProgram, cacheKey);\n')
        (fresh_snapshot / 'preset-lab-identity.json').write_text(
            json.dumps(asdict(parent), sort_keys=True, separators=(',', ':')))

        actual_source = role_dir / 'engine'
        shutil.copytree(fresh_snapshot, actual_source)
        adjustment = SOURCE_IDENTITY._apply_role_source(
            prepared_role, actual_source, patch_dir, series)
        source_hashes = role_dir / 'source-hashes.json'
        source_hashes.write_text(json.dumps(SOURCE_IDENTITY.file_hashes(actual_source)))
        adjustments_path = role_dir / 'capture-adjustments.diff'
        adjustments_path.write_text(adjustment)
        saved_snapshot = role_dir / 'snapshot' / 'engines' / SOURCE_IDENTITY.digest(asdict(parent))
        saved_snapshot.parent.mkdir(parents=True)
        shutil.copytree(fresh_snapshot, saved_snapshot)
        harness = root / 'harness'
        harness.mkdir()
        (harness / 'worker.cpp').write_text('canonical harness input\n')
        binary = role_dir / 'ndk-build' / 'patch-proof-worker'
        binary.parent.mkdir()
        binary.write_bytes(b'expected worker bytes')

        identity = {
            'role': 'patched',
            'patch_removed': None,
            'ordered_patches': series['patches'],
            'source_commit': series['source_commit'],
            'engine_commit': series['engine_commit'],
            'evaluator_commit': series['evaluator_commit'],
            'parent': asdict(parent),
            'source_hashes': str(source_hashes),
            'adjustments_sha256': SOURCE_IDENTITY.sha(adjustments_path),
            'harness_sha256': SOURCE_IDENTITY.file_hashes(harness),
            'binary': str(binary),
            'binary_sha256': SOURCE_IDENTITY.sha(binary),
        }

        def rebuild(_repo, work):
            destination = work / 'engines' / 'expected'
            destination.parent.mkdir(parents=True)
            shutil.copytree(fresh_snapshot, destination)
            return destination, parent

        return role_dir, identity, series, rebuild

    def validate(self, fixture, ndk=None):
        _role_dir, identity, series, rebuild = fixture
        with patch.object(SOURCE_IDENTITY, '_validate_git_pins'), \
                patch.object(SOURCE_IDENTITY, 'prepare_engine', side_effect=rebuild):
            SOURCE_IDENTITY.validate_prepared_source('patched', identity, series, ndk)

    def test_accepts_source_matching_patched_role(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary), 'patched')
            self.validate(fixture)

    def test_rejects_source_commit_outside_selected_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary), 'patched')
            fixture[1]['source_commit'] = 'b' * 40
            with self.assertRaisesRegex(ValueError, 'source pins'):
                self.validate(fixture)

    def test_rejects_wrong_worker_snapshot_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary), 'patched')
            fixture[1]['series_sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'snapshot identity'):
                self.validate(fixture)

    def test_supports_selected_snapshot_ablation_numbers(self):
        self.assertIn('without-0014', SOURCE_IDENTITY._supported_roles({'patches': [{'number': '0014'}]}))
        self.assertNotIn('without-0014', SOURCE_IDENTITY._supported_roles({'patches': [{'number': '0013'}]}))

    def test_rejects_patched_claim_for_source_with_patch_removed(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = self.make_fixture(Path(temporary), 'without-0010')
            with self.assertRaisesRegex(ValueError, 'prepared source'):
                self.validate(fixture)

    def test_rejects_adjustment_diff_that_disagrees_with_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            role_dir, identity, series, rebuild = self.make_fixture(Path(temporary), 'patched')
            adjustments = role_dir / 'capture-adjustments.diff'
            adjustments.write_text('forged adjustment record\n')
            identity['adjustments_sha256'] = SOURCE_IDENTITY.sha(adjustments)
            with self.assertRaisesRegex(ValueError, 'Capture adjustments differ'):
                self.validate((role_dir, identity, series, rebuild))

    def test_rejects_self_consistent_hash_for_wrong_worker_binary(self):
        with tempfile.TemporaryDirectory() as temporary:
            role_dir, identity, series, rebuild = self.make_fixture(Path(temporary), 'patched')
            binary = Path(identity['binary'])
            binary.write_bytes(b'forged worker bytes')
            identity['binary_sha256'] = SOURCE_IDENTITY.sha(binary)
            harness_template = role_dir.parent / 'harness'

            def copy_harness(destination):
                shutil.copytree(harness_template, destination)
                return destination

            def rebuild_worker(_harness, build_dir, _source, _ndk, _role):
                build_dir.mkdir(parents=True)
                rebuilt = build_dir / 'patch-proof-worker'
                rebuilt.write_bytes(b'expected worker bytes')
                return rebuilt

            with patch.object(SOURCE_IDENTITY, 'validate_ndk'), \
                    patch.object(SOURCE_IDENTITY, 'prepare_harness', side_effect=copy_harness), \
                    patch.object(SOURCE_IDENTITY, 'build_patch_worker', side_effect=rebuild_worker), \
                    patch.object(SOURCE_IDENTITY, 'canonical_worker', side_effect=lambda path, _out, _ndk: path.read_bytes()):
                with self.assertRaisesRegex(ValueError, 'differs from rebuilt source and harness'):
                    self.validate((role_dir, identity, series, rebuild), ndk=Path('/fake/ndk'))


if __name__ == '__main__':
    unittest.main()
