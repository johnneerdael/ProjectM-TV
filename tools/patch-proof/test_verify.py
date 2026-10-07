"""Integrity controls reject tampered or incomplete records using a small RGB fixture."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from PIL import Image

SPEC = importlib.util.spec_from_file_location('patch_proof_verify', Path(__file__).with_name('verify.py'))
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class RetainedEvidenceIntegrity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.work = self.root / 'capture'
        self.work.mkdir()
        source = self.root / 'worker/engine'
        source.mkdir(parents=True)
        (source / 'renderer.cpp').write_text('observed compiled source\n')
        binary = self.root / 'worker/worker'
        binary.write_bytes(b'observed binary')
        manifest = self.root / 'worker/source-hashes.json'
        manifest.write_text(json.dumps({'renderer.cpp': VERIFY.sha((source / 'renderer.cpp').read_bytes())}))
        identity = {'binary': str(binary), 'binary_sha256': VERIFY.sha(binary.read_bytes()),
                    'source_hashes': str(manifest)}
        backend = ['vendor', 'hardware GPU', 'GLES3.0', 'GLSL3.00']
        row = {'status': 'success', 'manifest': {'status': 'success', 'gl_error_frames': 0,
               'frames': 120, 'width': 2, 'height': 1,
               **dict(zip(('gl_vendor', 'gl_renderer', 'gl_version', 'glsl_version'), backend))},
               'frame_hashes': [VERIFY.sha(bytes([255, 0, 0, 0, 255, 0]))] * 120}
        self.result = {'dimensions': [2, 1], 'backend': backend, 'roles': {
            'patched': {'worker': identity, 'repeat_equal': True, 'runs': [row, json.loads(json.dumps(row))]}}}
        for repeat in (0, 1):
            directory = self.work / 'patched' / str(repeat)
            directory.mkdir(parents=True)
            for frame in (29, 59, 119):
                Image.frombytes('RGB', (2, 1), bytes([255, 0, 0, 0, 255, 0])).save(directory / f'{frame}.png')
        self.save()

    def tearDown(self):
        self.temporary.cleanup()

    def save(self):
        (self.work / 'results.json').write_text(json.dumps(self.result))

    def test_accepts_intact_payloads(self):
        self.assertEqual(VERIFY.verify(self.work)['successful_roles'], ['patched'])

    def test_rejects_changed_png_despite_unchanged_manifest(self):
        Image.new('RGB', (2, 1), 'black').save(self.work / 'patched/0/119.png')
        with self.assertRaisesRegex(ValueError, 'PNG payload'):
            VERIFY.verify(self.work)

    def test_rejects_changed_worker_binary(self):
        Path(self.result['roles']['patched']['worker']['binary']).write_bytes(b'new binary')
        with self.assertRaisesRegex(ValueError, 'binary changed'):
            VERIFY.verify(self.work)

    def test_rejects_changed_compiled_source(self):
        (self.root / 'worker/engine/renderer.cpp').write_text('unrecorded source\n')
        with self.assertRaisesRegex(ValueError, 'source inventory'):
            VERIFY.verify(self.work)

    def test_rejects_mixed_success_and_failure(self):
        self.result['roles']['patched']['runs'][1] = {'status': 'failed', 'exit': 1}
        self.save()
        with self.assertRaisesRegex(ValueError, 'Mixed success'):
            VERIFY.verify(self.work)

    def test_rejects_matching_repeats_with_missing_frames(self):
        for row in self.result['roles']['patched']['runs']:
            row['frame_hashes'] = row['frame_hashes'][:-1]
        self.save()
        with self.assertRaisesRegex(ValueError, 'frame count'):
            VERIFY.verify(self.work)

    def test_rejects_backend_change(self):
        self.result['roles']['patched']['runs'][1]['manifest']['gl_renderer'] = 'other GPU'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Backend'):
            VERIFY.verify(self.work)


if __name__ == '__main__':
    unittest.main()
