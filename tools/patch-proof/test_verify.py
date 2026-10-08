"""Integrity controls reject tampered or incomplete records using a small RGB fixture."""
import importlib.util
import gzip
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

SPEC = importlib.util.spec_from_file_location('patch_proof_verify', Path(__file__).with_name('verify.py'))
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
SERIES = json.loads((Path(__file__).resolve().parents[2] /
                    'docs/superpowers/evidence/current-patch-proof/series.json').read_text())['patches']


class RetainedEvidenceIntegrity(unittest.TestCase):
    def setUp(self):
        self.source_validation = patch.object(VERIFY, 'validate_prepared_source')
        self.source_validation.start()
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / 'ndk').mkdir()
        (self.root / 'ndk/source.properties').write_text('Pkg.Revision = 27.3.13750724\n')
        self.work = self.root / 'capture'
        self.work.mkdir()
        source = self.root / 'worker/engine'
        source.mkdir(parents=True)
        (source / 'renderer.cpp').write_text('observed compiled source\n')
        binary = self.root / 'worker/worker'
        binary.write_bytes(b'observed binary')
        manifest = self.root / 'worker/source-hashes.json'
        manifest.write_text(json.dumps({'renderer.cpp': VERIFY.sha((source / 'renderer.cpp').read_bytes())}))
        identity = {'role': 'patched', 'patch_removed': None,
                    'ordered_patches': SERIES,
                    'binary': str(binary), 'binary_sha256': VERIFY.sha(binary.read_bytes()),
                    'source_hashes': str(manifest)}
        backend = ['vendor', 'hardware GPU', 'GLES3.0', 'GLSL3.00']
        self.frame_data = bytes([255, 0, 0, 0, 255, 0]) * 120
        row = {'status': 'success', 'manifest': {'status': 'success', 'gl_error_frames': 0,
               'frames': 120, 'width': 2, 'height': 1,
               **dict(zip(('gl_vendor', 'gl_renderer', 'gl_version', 'glsl_version'), backend))},
               'frame_hashes': [VERIFY.sha(self.frame_data[i * 6:(i + 1) * 6]) for i in range(120)],
               'stream_sha256': VERIFY.sha(self.frame_data)}
        self.result = {'capture_kind': 'image', 'dimensions': [2, 1], 'backend': backend, 'roles': {
            'patched': {'worker': identity, 'repeat_equal': True, 'runs': [row, json.loads(json.dumps(row))]}}}
        for repeat in (0, 1):
            directory = self.work / 'patched' / str(repeat)
            directory.mkdir(parents=True)
            (directory / 'frames.rgb').write_bytes(self.frame_data)
            for frame in (29, 59, 119):
                Image.frombytes('RGB', (2, 1), self.frame_data[frame * 6:(frame + 1) * 6]).save(directory / f'{frame}.png')
        image = Image.new('RGB', (2, 33), '#171717')
        ImageDraw.Draw(image).text((4, 8), 'patched', fill='white')
        image.paste(Image.open(self.work / 'patched/0/119.png'), (0, 32))
        image.save(self.work / 'comparison.png')
        self.save()

    def tearDown(self):
        self.disable_source_validation()
        self.temporary.cleanup()

    def disable_source_validation(self):
        if self.source_validation is not None:
            self.source_validation.stop()
            self.source_validation = None

    def save(self):
        (self.work / 'results.json').write_text(json.dumps(self.result))

    def test_rejects_missing_ndk_for_binary_binding(self):
        with self.assertRaisesRegex(ValueError, 'NDK is required'):
            VERIFY.verify(self.work)

    def test_accepts_intact_payloads(self):
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def shader_probe_fixture(self):
        self.result['diagnostic_kind'] = 'shader-fragment-failure'
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics'] = {
                'kind': 'shader-fragment-failure', 'attempts': 16,
                'created_shader_objects': 34, 'live_vertex_after_each_failure': [0] * 16,
                'live_vertex_before_cleanup': 0, 'retry_linked': True,
                'observer_gl_error': 0, 'diagnostic_cleanup_complete': True,
                'rejection_messages': ['[Shader] Error compiling fragment shader: intentional syntax rejection'] * 16}

    def test_accepts_valid_shader_lifetime_observations(self):
        self.shader_probe_fixture()
        self.save()
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def test_rejects_ineffective_shader_lifetime_observer(self):
        self.shader_probe_fixture()
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics']['created_shader_objects'] = 0
        self.save()
        with self.assertRaisesRegex(ValueError, 'Shader lifetime diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_leaked_shaders_in_corrected_role(self):
        self.shader_probe_fixture()
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics']['live_vertex_before_cleanup'] = 16
            run['manifest']['diagnostics']['live_vertex_after_each_failure'] = list(range(1, 17))
        self.save()
        with self.assertRaisesRegex(ValueError, 'Shader lifetime diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def texture_history_fixture(self):
        self.result['diagnostic_kind'] = 'texture-history'
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics'] = {
                'kind': 'texture-history', 'width': 64, 'height': 48,
                'controlled_poison_rgba': [0, 160, 80, 255], 'poison_control_passed': True,
                'fresh_rgba': [0] * (64 * 48 * 4), 'recreated_rgba': [0] * (64 * 48 * 4),
                'driver_allocations': 1, 'pool_available': True,
                'pool_bytes_after_retire': 64 * 48 * 4,
                'caller_state_preserved': [True, True], 'observer_gl_error': 0}

    def test_accepts_texture_history_pixel_state_and_allocation_contract(self):
        self.texture_history_fixture()
        self.save()
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def test_rejects_ineffective_texture_allocation_control(self):
        self.texture_history_fixture()
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics']['poison_control_passed'] = False
        self.save()
        with self.assertRaisesRegex(ValueError, 'Texture history diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_unobserved_pool_reuse(self):
        self.texture_history_fixture()
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics']['driver_allocations'] = 2
        self.save()
        with self.assertRaisesRegex(ValueError, 'Texture history diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_uncleared_feedback_pixels(self):
        self.texture_history_fixture()
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics']['fresh_rgba'] = [0, 160, 80, 255] * (64 * 48)
        self.save()
        with self.assertRaisesRegex(ValueError, 'Texture history diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_texture_clear_caller_state_damage(self):
        self.texture_history_fixture()
        for run in self.result['roles']['patched']['runs']:
            run['manifest']['diagnostics']['caller_state_preserved'] = [False, True]
        self.save()
        with self.assertRaisesRegex(ValueError, 'Texture history diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_accepts_complete_lossless_compressed_streams(self):
        for repeat in (0, 1):
            raw = self.work / 'patched' / str(repeat) / 'frames.rgb'
            raw.with_suffix('.rgb.gz').write_bytes(gzip.compress(raw.read_bytes(), mtime=0))
            raw.unlink()
        try:
            report = VERIFY.verify(self.work, self.root / 'ndk')
        except FileNotFoundError:
            self.fail('Lossless compressed complete-frame payload must remain verifiable')
        self.assertEqual(report['successful_roles'], ['patched'])

    def test_rejects_changed_frame_in_compressed_stream(self):
        raw = self.work / 'patched/0/frames.rgb'
        data = bytearray(raw.read_bytes())
        data[6 * 17] ^= 1
        raw.with_suffix('.rgb.gz').write_bytes(gzip.compress(data, mtime=0))
        raw.unlink()
        with self.assertRaisesRegex(ValueError, 'RGB stream hash differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_extra_frame_bytes_in_compressed_stream(self):
        raw = self.work / 'patched/0/frames.rgb'
        raw.with_suffix('.rgb.gz').write_bytes(gzip.compress(raw.read_bytes() + b'x', mtime=0))
        raw.unlink()
        with self.assertRaisesRegex(ValueError, 'RGB stream length differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_png_despite_unchanged_manifest(self):
        Image.new('RGB', (2, 1), 'black').save(self.work / 'patched/0/119.png')
        with self.assertRaisesRegex(ValueError, 'PNG payload'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_worker_binary(self):
        Path(self.result['roles']['patched']['worker']['binary']).write_bytes(b'new binary')
        with self.assertRaisesRegex(ValueError, 'binary changed'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_compiled_source(self):
        (self.root / 'worker/engine/renderer.cpp').write_text('unrecorded source\n')
        with self.assertRaisesRegex(ValueError, 'source inventory'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_mixed_success_and_failure(self):
        self.result['roles']['patched']['runs'][1] = {'status': 'failed', 'exit': 1}
        self.save()
        with self.assertRaisesRegex(ValueError, 'Mixed success'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def add_rejected_role(self, row, repeat_equal=False):
        self.result['roles']['upstream'] = {
            'worker': {**self.result['roles']['patched']['worker'], 'role': 'upstream', 'ordered_patches': []},
            'repeat_equal': repeat_equal, 'runs': [row, dict(row)]}
        self.save()
        image = Image.new('RGB', (4, 33), '#171717')
        draw = ImageDraw.Draw(image)
        draw.text((4, 8), 'patched', fill='white')
        draw.text((6, 8), 'upstream', fill='white')
        image.paste(Image.open(self.work / 'patched/0/119.png'), (0, 32))
        draw.text((10, 80), 'Rejected or unstable\nNo verified framebuffer', fill='#ffb4ab')
        image.save(self.work / 'comparison.png')

    def test_accepts_explicit_failed_repeats_as_rejected(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2})
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['rejected_roles'], ['upstream'])

    def test_rejects_malformed_failure_records(self):
        for row in ({'exit': 2}, {'status': 'pending', 'exit': 2},
                    {'status': 'failed'}, {'status': 'failed', 'exit': 0},
                    {'status': 'failed', 'exit': True}):
            with self.subTest(row=row):
                self.add_rejected_role(row)
                with self.assertRaisesRegex(ValueError, 'Invalid failure record'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_failed_repeats_claimed_equal(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2}, repeat_equal=True)
        with self.assertRaisesRegex(ValueError, 'Failed repeats cannot'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_swapped_worker_role(self):
        self.result['roles']['patched']['worker']['role'] = 'without-0010'
        self.save()
        self.disable_source_validation()
        with self.assertRaisesRegex(ValueError, 'Worker role metadata differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_wrong_patch_removal_metadata(self):
        self.result['roles']['patched']['worker']['patch_removed'] = 10
        self.save()
        self.disable_source_validation()
        with self.assertRaisesRegex(ValueError, 'Worker role metadata differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_wrong_prepared_patch_inventory(self):
        self.result['roles']['patched']['worker']['ordered_patches'] = []
        self.save()
        self.disable_source_validation()
        with self.assertRaisesRegex(ValueError, 'Worker role metadata differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_matching_repeats_with_missing_frames(self):
        for row in self.result['roles']['patched']['runs']:
            row['frame_hashes'] = row['frame_hashes'][:-1]
        self.save()
        with self.assertRaisesRegex(ValueError, 'frame count'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_unretained_rgb_frame(self):
        stream = bytearray(self.frame_data)
        stream[50 * 6] ^= 1
        (self.work / 'patched/0/frames.rgb').write_bytes(stream)
        with self.assertRaisesRegex(ValueError, 'frame hashes|stream hash'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_stream_digest(self):
        for row in self.result['roles']['patched']['runs']:
            row['stream_sha256'] = '0' * 64
        self.save()
        with self.assertRaisesRegex(ValueError, 'stream hash'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_matching_tampered_unretained_frame_hashes(self):
        changed_hash = VERIFY.sha(bytes([254, 0, 0, 0, 255, 0]))
        for row in self.result['roles']['patched']['runs']:
            row['frame_hashes'][50] = changed_hash
        self.save()
        with self.assertRaisesRegex(ValueError, 'frame hashes|stream hash'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_backend_change(self):
        self.result['roles']['patched']['runs'][1]['manifest']['gl_renderer'] = 'other GPU'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Backend'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_comparison(self):
        (self.work / 'comparison.png').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing comparison'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_texture_journey_frame(self):
        self.result['capture_kind'] = 'texture-journey'
        self.save()
        with self.assertRaises(FileNotFoundError):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_broken_evaluator_thread_contract(self):
        self.result['capture_kind'] = 'evaluator'
        control = {'compiled': [True, True], 'streams': [list(range(128)), list(range(1, 129))],
                   'fresh_thread_streams_equal': False, 'lone_dot_is_zero': True}
        self.result['roles']['patched']['runs'] = [{'exit': 0, 'control': control}] * 2
        self.save()
        with self.assertRaisesRegex(ValueError, 'thread-isolation'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_broken_evaluator_lone_dot_contract(self):
        self.result['capture_kind'] = 'evaluator'
        control = {'compiled': [True, True], 'streams': [list(range(128))] * 2,
                   'fresh_thread_streams_equal': True, 'lone_dot_is_zero': False}
        self.result['roles']['patched']['runs'] = [{'exit': 0, 'control': control}] * 2
        self.save()
        with self.assertRaisesRegex(ValueError, 'lone-dot'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_altered_rejection_panel(self):
        self.result['roles']['upstream'] = {
            'worker': {**self.result['roles']['patched']['worker'], 'role': 'upstream', 'ordered_patches': []},
            'repeat_equal': False, 'runs': [{'status': 'failed', 'exit': 1}] * 2}
        self.save()
        image = Image.new('RGB', (4, 33), '#171717')
        ImageDraw.Draw(image).text((4, 8), 'patched', fill='white')
        image.paste(Image.open(self.work / 'patched/0/119.png'), (0, 32))
        image.putpixel((2, 32), (255, 255, 255))
        image.save(self.work / 'comparison.png')
        with self.assertRaisesRegex(ValueError, 'rejection panels'):
            VERIFY.verify(self.work, self.root / 'ndk')


    def evaluator_fixture(self, stream):
        self.result['capture_kind'] = 'evaluator'
        control = {'compiled': [True, True], 'streams': [stream, stream],
                   'fresh_thread_streams_equal': True, 'lone_dot_is_zero': True}
        self.result['roles']['patched']['runs'] = [{'exit': 0, 'control': control}] * 2
        self.save()

    def test_accepts_valid_evaluator_contract(self):
        self.evaluator_fixture(list(range(128)))
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def test_rejects_constant_random_stream(self):
        self.evaluator_fixture([0] * 128)
        with self.assertRaisesRegex(ValueError, 'constant'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_nonfinite_random_stream(self):
        self.evaluator_fixture(list(range(127)) + [float('nan')])
        with self.assertRaisesRegex(ValueError, 'samples are invalid'):
            VERIFY.verify(self.work, self.root / 'ndk')



if __name__ == '__main__':
    unittest.main()
