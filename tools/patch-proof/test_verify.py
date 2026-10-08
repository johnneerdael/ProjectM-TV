"""Integrity controls reject tampered or incomplete records using a small RGB fixture."""
import importlib.util
import gzip
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw
from capture import pcm

SPEC = importlib.util.spec_from_file_location('patch_proof_verify', Path(__file__).with_name('verify.py'))
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
SERIES = json.loads((Path(__file__).resolve().parents[2] /
                    'docs/superpowers/evidence/current-patch-proof/series.json').read_text())['patches']
SIGNAL = pcm()
WIDTH, HEIGHT = 256, 144
FRAME_SIZE = WIDTH * HEIGHT * 3
FRAME = bytes([255, 0, 0, 0, 255, 0]) * (WIDTH * HEIGHT // 2)
FRAME_DATA = FRAME * 120


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
        inputs = self.work / 'inputs'
        inputs.mkdir()
        self.preset = inputs / 'witness.milk'
        self.preset.write_bytes(b'[preset00]\nfDecay=0.9\n')
        self.textures = inputs / 'textures'
        (self.textures / 'nested').mkdir(parents=True)
        (self.textures / 'nested/texture.png').write_bytes(b'original texture bytes')
        self.signal = SIGNAL
        (self.work / 'audio.f32').write_bytes(self.signal)
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
        retained_worker = self.stage_worker('patched', identity)
        backend = ['vendor', 'hardware GPU', 'GLES3.0', 'GLSL3.00']
        self.remote = '/data/local/tmp/projectmtv-patch-proof-0123456789abcdef'
        self.frame_data = FRAME_DATA
        row = {'status': 'success', 'manifest': {'status': 'success', 'gl_error_frames': 0,
               'frames': 120, 'width': WIDTH, 'height': HEIGHT, 'fps': 30, 'seed': 12345,
               **dict(zip(('gl_vendor', 'gl_renderer', 'gl_version', 'glsl_version'), backend))},
               'frame_hashes': [VERIFY.sha(FRAME)] * 120,
               'stream_sha256': VERIFY.sha(self.frame_data)}
        self.result = {'preset_sha256': VERIFY.sha(self.preset.read_bytes()),
            'textures': {'nested/texture.png': VERIFY.sha(b'original texture bytes')},
            'device': 'emulator-5630', 'user': 0,
            'remote_workspace': self.remote,
            'features': ['feature:android.software.leanback', 'feature:android.hardware.type.television'],
            'clock': 'frame/30.0', 'frames': 120, 'pcm_sha256': VERIFY.sha(self.signal), 'capture_kind': 'image', 'dimensions': [WIDTH, HEIGHT], 'backend': backend, 'roles': {
            'patched': {'worker': identity, 'retained_worker': retained_worker,
                        'repeat_equal': True, 'runs': [row, json.loads(json.dumps(row))]}}}
        for repeat in (0, 1):
            directory = self.work / 'patched' / str(repeat)
            directory.mkdir(parents=True)
            (directory / 'frames.rgb').write_bytes(self.frame_data)
            for frame in (29, 59, 119):
                Image.frombytes('RGB', (WIDTH, HEIGHT), FRAME).save(directory / f'{frame}.png')
        image = Image.new('RGB', (WIDTH, HEIGHT + 32), '#171717')
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

    def stage_worker(self, role, identity):
        data = Path(identity['binary']).read_bytes()
        path = self.work / 'inputs/workers' / role / 'worker'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        identity['binary'] = str(path.resolve())
        return {'path': path.relative_to(self.work).as_posix(),
                'sha256': identity['binary_sha256'], 'bytes': len(data)}

    def save(self):
        for role, value in self.result['roles'].items():
            for repeat, run in enumerate(value['runs']):
                directory = self.work / role / str(repeat)
                directory.mkdir(parents=True, exist_ok=True)
                (directory / 'execution.json').write_text(json.dumps({'exit': run.get('exit', 0)}))
                if 'control' in run:
                    (directory / 'output.txt').write_text(json.dumps(run['control']) + '\n')
                    continue
                if run.get('status') == 'success':
                    manifest = run['manifest']
                    manifest.setdefault('identity', {'role': role, 'repeat': repeat})
                    (directory / 'manifest.json').write_text(json.dumps(manifest))
                cfg = {'width': self.result['dimensions'][0], 'height': self.result['dimensions'][1],
                       'fps': 30, 'seed': 12345, 'warmup_seconds': 0, 'measurement_seconds': 4,
                       'line_reference_height': 0, 'line_antialiasing': False}
                diagnostic = self.result.get('diagnostic_kind')
                if diagnostic == 'shader-fragment-failure': cfg['shader_failure_probe'] = True
                if diagnostic == 'texture-history': cfg['texture_history_probe'] = True
                remote = self.remote
                job = {'schema_version': 1, 'config': cfg, 'identity': {'role': role, 'repeat': repeat},
                       'pcm_path': remote + '/audio.f32', 'preset_path': remote + '/witness.milk',
                       'texture_root': remote + '/textures', 'bands_path': remote + '/bands.jsonl',
                       'manifest_path': remote + '/manifest.json'}
                if self.result['capture_kind'] == 'texture-journey':
                    job['texture_root'] += '/a'
                    job['events'] = [{'frame': 20, 'texture_root': remote + '/textures/b'},
                        {'frame': 21, 'load_preset': remote + '/witness.milk', 'smooth': True},
                        {'frame': 40, 'reset_textures': True}]
                (directory / 'job.json').write_text(json.dumps(job))
        (self.work / 'results.json').write_text(json.dumps(self.result))

    def test_rejects_missing_ndk_for_binary_binding(self):
        with self.assertRaisesRegex(ValueError, 'NDK is required'):
            VERIFY.verify(self.work)

    def test_rejects_missing_or_physical_device_receipt(self):
        for device in (None, '192.168.1.2:5555', 'physical-device-serial', 5630):
            with self.subTest(device=device):
                if device is None: self.result.pop('device', None)
                else: self.result['device'] = device
                self.save()
                with self.assertRaisesRegex(ValueError, 'emulator serial'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_tv_features_or_phone_receipt(self):
        for features in (None, [], ['feature:android.software.leanback'],
                         ['feature:android.hardware.type.television'],
                         ['feature:android.hardware.telephony'],
                         'feature:android.software.leanback feature:android.hardware.type.television'):
            with self.subTest(features=features):
                if features is None: self.result.pop('features', None)
                else: self.result['features'] = features
                self.save()
                with self.assertRaisesRegex(ValueError, 'Android TV features'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_or_invalid_captured_user(self):
        for user in (None, -1, True, '0', 0.0):
            with self.subTest(user=user):
                if user is None: self.result.pop('user', None)
                else: self.result['user'] = user
                self.save()
                with self.assertRaisesRegex(ValueError, 'nonnegative integer Android user'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_accepts_nonzero_android_user_on_tv_emulator(self):
        self.result['user'] = 10
        self.save()
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def test_rejects_capture_bound_to_other_snapshot(self):
        self.result['series_sha256'] = '0' * 64
        self.save()
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_accepts_current_snapshot_and_passes_it_to_source_reconstruction(self):
        series_path = Path(__file__).resolve().parents[2] / 'docs/superpowers/evidence/current-patch-proof/current-series.json'
        selected = json.loads(series_path.read_text())
        self.result['series_sha256'] = VERIFY.digest(selected)
        self.result['roles']['patched']['worker']['ordered_patches'] = selected['patches']
        self.save()
        with patch.object(VERIFY, 'validate_prepared_source') as validate:
            self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk', series_path)['successful_roles'], ['patched'])
            self.assertEqual(validate.call_args.args[2], selected)

    def test_rejects_missing_snapshot_binding_when_current_manifest_selected(self):
        series = Path(__file__).resolve().parents[2] / 'docs/superpowers/evidence/current-patch-proof/current-series.json'
        with self.assertRaisesRegex(ValueError, 'snapshot'):
            VERIFY.verify(self.work, self.root / 'ndk', series)

    def test_rejects_wrong_manifest_role_and_repeat(self):
        self.result['roles']['patched']['runs'][0]['manifest']['identity'] = {'role': 'upstream', 'repeat': 7}
        self.save()
        with self.assertRaisesRegex(ValueError, 'run identity'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_wrong_frozen_seed_and_fps(self):
        for field, value in [('seed', 999), ('fps', 60)]:
            with self.subTest(field=field):
                manifest = self.result['roles']['patched']['runs'][0]['manifest']
                original = manifest[field]; manifest[field] = value; self.save()
                with self.assertRaisesRegex(ValueError, 'run protocol'):
                    VERIFY.verify(self.work, self.root / 'ndk')
                manifest[field] = original

    def test_rejects_retained_manifest_different_from_inline_record(self):
        path = self.work / 'patched/0/manifest.json'
        value = json.loads(path.read_text()); value['seed'] = 999; path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'Retained manifest'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_retained_job_with_other_role(self):
        path = self.work / 'patched/0/job.json'
        value = json.loads(path.read_text()); value['identity']['role'] = 'upstream'; path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'job identity'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_retained_job_with_other_seed_or_reference(self):
        path = self.work / 'patched/0/job.json'; original = path.read_text()
        for key, changed in [('seed', 999), ('line_reference_height', 1080)]:
            with self.subTest(key=key):
                value = json.loads(original); value['config'][key] = changed; path.write_text(json.dumps(value))
                with self.assertRaisesRegex(ValueError, 'job protocol'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_unrecorded_host_events(self):
        path = self.work / 'patched/0/job.json'; value = json.loads(path.read_text())
        value['events'] = [{'frame': 21, 'reset_textures': True}]; path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'host events'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_input_paths_changed_between_repeats(self):
        path = self.work / 'patched/1/job.json'
        value = json.loads(path.read_text()); value['preset_path'] = '/owned/different.milk'
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'job input/output paths'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def add_successful_role(self):
        value = json.loads(json.dumps(self.result['roles']['patched']))
        value['worker']['role'] = 'upstream'
        value['worker']['ordered_patches'] = []
        value['retained_worker'] = self.stage_worker('upstream', value['worker'])
        for repeat, run in enumerate(value['runs']):
            run['manifest']['identity'] = {'role': 'upstream', 'repeat': repeat}
        self.result['roles']['upstream'] = value
        shutil.copytree(self.work / 'patched', self.work / 'upstream')
        self.save()
        image = Image.new('RGB', (WIDTH * 2, HEIGHT + 32), '#171717')
        draw = ImageDraw.Draw(image)
        for col, role in enumerate(('patched', 'upstream')):
            draw.text((col * WIDTH + 4, 8), role, fill='white')
            image.paste(Image.open(self.work / role / '0/119.png'), (col * WIDTH, 32))
        image.save(self.work / 'comparison.png')

    def rewrite_all_jobs(self, edit):
        for role in self.result['roles']:
            for repeat in (0, 1):
                path = self.work / role / str(repeat) / 'job.json'
                job = json.loads(path.read_text())
                edit(job)
                path.write_text(json.dumps(job))

    def test_rejects_consistent_job_path_substitutions_across_all_roles_and_repeats(self):
        self.add_successful_role()
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched', 'upstream'])
        for key, path in (('pcm_path', self.remote + '/different.f32'),
                          ('preset_path', self.remote + '/different.milk'),
                          ('texture_root', self.remote + '/other-textures'),
                          ('texture_root', self.remote + '/textures/../textures'),
                          ('texture_root', '/unowned/textures'),
                          ('bands_path', self.remote + '/other-bands.jsonl'),
                          ('manifest_path', self.remote + '/other-manifest.json')):
            with self.subTest(key=key, path=path):
                self.save()
                self.rewrite_all_jobs(lambda job: job.__setitem__(key, path))
                with self.assertRaisesRegex(ValueError, 'job input/output paths'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def journey_fixture(self):
        self.result['capture_kind'] = 'texture-journey'
        for repeat in (0, 1):
            Image.frombytes('RGB', (WIDTH, HEIGHT), FRAME).save(
                self.work / 'patched' / str(repeat) / '40.png')
        self.save()

    def test_accepts_workspace_bound_texture_journey(self):
        self.journey_fixture()
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def test_rejects_consistent_journey_root_and_preset_substitutions(self):
        self.journey_fixture()
        self.add_successful_role()
        def edit_roots(job):
            job['texture_root'] = '/unowned/textures/a'
            job['events'][0]['texture_root'] = '/unowned/textures/b'
        def edit_preset(job):
            job['preset_path'] = '/unowned/other.milk'
            job['events'][1]['load_preset'] = '/unowned/other.milk'
        for edit in (edit_roots, edit_preset):
            with self.subTest(edit=edit.__name__):
                self.save()
                self.rewrite_all_jobs(edit)
                with self.assertRaisesRegex(ValueError, 'job input/output paths'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_consistent_journey_event_path_substitutions(self):
        self.journey_fixture()
        self.add_successful_role()
        for event, key, path in ((0, 'texture_root', '/unowned/textures/b'),
                                  (1, 'load_preset', '/unowned/other.milk'),
                                  (1, 'load_preset', self.remote + '/subdir/../witness.milk')):
            with self.subTest(event=event, key=key):
                self.save()
                self.rewrite_all_jobs(lambda job: job['events'][event].__setitem__(key, path))
                with self.assertRaisesRegex(ValueError, 'host events'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_requires_explicit_remote_workspace_for_historical_capture(self):
        self.result.pop('remote_workspace')
        self.save()
        with self.assertRaisesRegex(ValueError, 'Historical capture.*--historical-remote-workspace'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_accepts_explicit_historical_workspace_with_limited_scope(self):
        self.result.pop('remote_workspace')
        self.save()
        report = VERIFY.verify(self.work, self.root / 'ndk', historical_remote_workspace=self.remote)
        self.assertEqual(report['remote_workspace_verification']['source'], 'explicit-historical')
        self.assertIn('original remote workspace was not recorded', report['scope'])
        self.assertNotIn('remote_workspace', json.loads((self.work / 'results.json').read_text()))

    def test_rejects_unowned_or_traversing_remote_workspace(self):
        for remote in ('/data/local/tmp', '/unowned/proof', self.remote + '/..',
                       '/data/local/tmp/../tmp/projectmtv-patch-proof-0123456789abcdef',
                       '/data/local/tmp/projectmtv-patch-proof-not-a-hash'):
            with self.subTest(remote=remote):
                self.result['remote_workspace'] = remote
                self.save()
                with self.assertRaisesRegex(ValueError, 'owned hashed remote workspace'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_unowned_explicit_historical_workspace(self):
        self.result.pop('remote_workspace')
        self.save()
        with self.assertRaisesRegex(ValueError, 'owned hashed remote workspace'):
            VERIFY.verify(self.work, self.root / 'ndk', historical_remote_workspace='/unowned/proof')

    def test_historical_workspace_cannot_override_recorded_workspace(self):
        self.result['remote_workspace'] = '/unowned/proof'
        self.save()
        with self.assertRaisesRegex(ValueError, 'owned hashed remote workspace'):
            VERIFY.verify(self.work, self.root / 'ndk', historical_remote_workspace=self.remote)

    def test_rejects_changed_frozen_audio(self):
        (self.work / 'audio.f32').write_bytes(b'changed PCM')
        with self.assertRaisesRegex(ValueError, 'PCM'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_jointly_changed_pcm_and_inline_hash(self):
        changed = bytearray(self.signal)
        changed[0] ^= 1
        (self.work / 'audio.f32').write_bytes(changed)
        self.result['pcm_sha256'] = VERIFY.sha(changed)
        self.save()
        with self.assertRaisesRegex(ValueError, 'PCM differs from frozen capture input'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_agreeingly_changed_unsupported_dimensions(self):
        self.result['dimensions'] = [2, 1]
        frame = bytes([255, 0, 0, 0, 255, 0])
        stream = frame * 120
        for repeat, run in enumerate(self.result['roles']['patched']['runs']):
            run['manifest']['width'], run['manifest']['height'] = 2, 1
            run['frame_hashes'] = [VERIFY.sha(frame)] * 120
            run['stream_sha256'] = VERIFY.sha(stream)
            directory = self.work / 'patched' / str(repeat)
            (directory / 'frames.rgb').write_bytes(stream)
            for snapshot in (29, 59, 119):
                Image.frombytes('RGB', (2, 1), frame).save(directory / f'{snapshot}.png')
        comparison = Image.new('RGB', (2, 33), '#171717')
        ImageDraw.Draw(comparison).text((4, 8), 'patched', fill='white')
        comparison.paste(Image.frombytes('RGB', (2, 1), frame), (0, 32))
        comparison.save(self.work / 'comparison.png')
        self.save()
        with self.assertRaisesRegex(ValueError, 'Capture dimensions differ from supported 16:9 sizes'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_malformed_or_wrong_aspect_dimensions(self):
        for dimensions in (None, [], [256], [256, 144, 0], ['256', 144], [256.0, 144],
                           [256, 144.0], [True, 144], [256, True], [256, 145], [257, 144]):
            with self.subTest(dimensions=dimensions):
                if dimensions is None: self.result.pop('dimensions', None)
                else: self.result['dimensions'] = dimensions
                (self.work / 'results.json').write_text(json.dumps(self.result))
                with self.assertRaisesRegex(ValueError, 'Capture dimensions differ from supported 16:9 sizes'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_accepts_all_six_supported_dimensions_in_nonimage_control(self):
        self.evaluator_fixture(list(range(128)))
        for dimensions in ([256, 144], [512, 288], [1280, 720], [1920, 1080], [2560, 1440], [3840, 2160]):
            with self.subTest(dimensions=dimensions):
                self.result['dimensions'] = dimensions
                self.save()
                self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'],
                                 ['patched', 'upstream', 'without-0003'])

    def test_accepts_intact_payloads(self):
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'], ['patched'])

    def test_rejects_changed_retained_preset(self):
        self.preset.write_bytes(b'[preset00]\nfDecay=0.1\n')
        with self.assertRaisesRegex(ValueError, 'Preset input hash differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_retained_texture_inventory(self):
        path = self.textures / 'nested/texture.png'
        for change in ('changed', 'added', 'removed'):
            with self.subTest(change=change):
                path.write_bytes(b'original texture bytes')
                extra = self.textures / 'extra.png'
                if extra.exists(): extra.unlink()
                if change == 'changed': path.write_bytes(b'changed texture bytes')
                if change == 'added': extra.write_bytes(b'unrecorded texture')
                if change == 'removed': path.unlink()
                with self.assertRaisesRegex(ValueError, 'Texture input inventory differs'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def historical_inputs(self):
        external = self.root / 'historical-inputs'
        (self.work / 'inputs').rename(external)
        return external / 'witness.milk', external / 'textures'

    def test_requires_explicit_inputs_for_historical_capture(self):
        self.historical_inputs()
        with self.assertRaisesRegex(ValueError, 'Historical capture.*--preset.*--textures'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_incomplete_explicit_historical_inputs(self):
        preset, textures = self.historical_inputs()
        for arguments in ({'preset': preset}, {'textures': textures}):
            with self.subTest(arguments=arguments):
                with self.assertRaisesRegex(ValueError, 'Historical capture.*--preset.*--textures'):
                    VERIFY.verify(self.work, self.root / 'ndk', **arguments)

    def test_checks_exact_explicit_historical_input_hashes(self):
        preset, textures = self.historical_inputs()
        report = VERIFY.verify_inputs(self.work, self.result, preset, textures)
        self.assertEqual(report['source'], 'explicit-external')

    def test_explicit_historical_inputs_cannot_bypass_unretained_worker(self):
        preset, textures = self.historical_inputs()
        self.result.pop('remote_workspace')
        self.save()
        with self.assertRaisesRegex(ValueError, 'Retained worker is unavailable'):
            VERIFY.verify(self.work, self.root / 'ndk', preset=preset, textures=textures,
                          historical_remote_workspace=self.remote)

    def test_rejects_wrong_explicit_historical_inputs(self):
        preset, textures = self.historical_inputs()
        preset.write_bytes(b'different preset')
        with self.assertRaisesRegex(ValueError, 'Preset input hash differs'):
            VERIFY.verify(self.work, self.root / 'ndk', preset=preset, textures=textures)

    def test_rejects_wrong_explicit_historical_textures(self):
        preset, textures = self.historical_inputs()
        (textures / 'nested/texture.png').write_bytes(b'different texture')
        with self.assertRaisesRegex(ValueError, 'Texture input inventory differs'):
            VERIFY.verify(self.work, self.root / 'ndk', preset=preset, textures=textures)

    def test_external_inputs_cannot_override_incomplete_retained_inputs(self):
        external = self.root / 'external-inputs'
        shutil.copytree(self.work / 'inputs', external)
        self.preset.unlink()
        with self.assertRaisesRegex(ValueError, 'Retained capture inputs are incomplete'):
            VERIFY.verify(self.work, self.root / 'ndk', preset=external / 'witness.milk',
                          textures=external / 'textures')

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
        data[FRAME_SIZE * 17] ^= 1
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
        Image.new('RGB', (WIDTH, HEIGHT), 'black').save(self.work / 'patched/0/119.png')
        with self.assertRaisesRegex(ValueError, 'PNG payload'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_worker_binary(self):
        Path(self.result['roles']['patched']['worker']['binary']).write_bytes(b'new binary')
        with self.assertRaisesRegex(ValueError, 'binary changed'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_requires_retained_worker_record(self):
        self.result['roles']['patched'].pop('retained_worker')
        self.save()
        with self.assertRaisesRegex(ValueError, 'Retained worker record differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_retained_worker_metadata(self):
        original = dict(self.result['roles']['patched']['retained_worker'])
        for key, value in (('path', '../worker'), ('path', 'inputs/workers/upstream/worker'),
                           ('sha256', '0' * 64), ('bytes', original['bytes'] + 1),
                           ('bytes', float(original['bytes']))):
            with self.subTest(key=key, value=value):
                self.result['roles']['patched']['retained_worker'] = {**original, key: value}
                self.save()
                with self.assertRaisesRegex(ValueError, 'Retained worker record differs'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_retained_worker_bytes(self):
        Path(self.result['roles']['patched']['worker']['binary']).unlink()
        with self.assertRaisesRegex(ValueError, 'Retained worker is unavailable'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_external_worker_identity_despite_identical_bytes(self):
        identity = self.result['roles']['patched']['worker']
        external = self.root / 'external-worker'
        external.write_bytes(Path(identity['binary']).read_bytes())
        identity['binary'] = str(external)
        self.save()
        with self.assertRaisesRegex(ValueError, 'Worker identity does not name its retained binary'):
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

    def add_rejected_role(self, row, repeat_equal=False, log=b'Preset load failed\n', manifest=None):
        self.result['roles']['upstream'] = {
            'worker': {**self.result['roles']['patched']['worker'], 'role': 'upstream', 'ordered_patches': []},
            'repeat_equal': repeat_equal, 'runs': [dict(row), dict(row)]}
        self.result['roles']['upstream']['retained_worker'] = self.stage_worker(
            'upstream', self.result['roles']['upstream']['worker'])
        self.save()
        for repeat, run in enumerate(self.result['roles']['upstream']['runs']):
            directory = self.work / 'upstream' / str(repeat)
            for name in ('render.log', 'manifest.json', 'frames.rgb'):
                (directory / name).unlink(missing_ok=True)
            artifacts = {'render.log': log, 'frames.rgb': b'partial RGB'}
            run['log'] = log.decode('utf-8', errors='replace')
            if manifest is not None:
                actual_manifest = {**self.result['roles']['patched']['runs'][repeat]['manifest'],
                                   **manifest, 'identity': {'role': 'upstream', 'repeat': repeat}}
                artifacts['manifest.json'] = json.dumps(actual_manifest).encode()
                run['manifest'] = actual_manifest
            run['retained_artifacts'] = {}
            for name, data in artifacts.items():
                (directory / name).write_bytes(data)
                run['retained_artifacts'][name] = {'sha256': VERIFY.sha(data), 'bytes': len(data)}
        (self.work / 'results.json').write_text(json.dumps(self.result))
        image = Image.new('RGB', (WIDTH * 2, HEIGHT + 32), '#171717')
        draw = ImageDraw.Draw(image)
        draw.text((4, 8), 'patched', fill='white')
        draw.text((WIDTH + 4, 8), 'upstream', fill='white')
        image.paste(Image.open(self.work / 'patched/0/119.png'), (0, 32))
        draw.text((WIDTH + 8, 80), 'Rejected or unstable\nNo verified framebuffer', fill='#ffb4ab')
        image.save(self.work / 'comparison.png')

    def test_accepts_explicit_failed_repeats_as_rejected(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2})
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['rejected_roles'], ['upstream'])

    def test_accepts_gl_failed_manifest_without_nonempty_log(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2}, log=b'',
                               manifest={'status': 'failed', 'gl_error_frames': 1, 'frames': 120})
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['rejected_roles'], ['upstream'])

    def test_rejects_successful_runs_relabelled_as_failed(self):
        self.add_successful_role()
        for repeat, run in enumerate(self.result['roles']['upstream']['runs']):
            run['status'], run['exit'] = 'failed', 2
            run['retained_artifacts'] = {}
            run['log'] = 'made-up failure\n'
            directory = self.work / 'upstream' / str(repeat)
            (directory / 'render.log').write_text(run['log'])
            for name in ('manifest.json', 'render.log', 'frames.rgb'):
                data = (directory / name).read_bytes()
                run['retained_artifacts'][name] = {'sha256': VERIFY.sha(data), 'bytes': len(data)}
        self.result['roles']['upstream']['repeat_equal'] = False
        self.save()
        comparison = Image.new('RGB', (WIDTH * 2, HEIGHT + 32), '#171717')
        draw = ImageDraw.Draw(comparison)
        for col, role in enumerate(('patched', 'upstream')):
            draw.text((col * WIDTH + 4, 8), role, fill='white')
        comparison.paste(Image.open(self.work / 'patched/0/119.png'), (0, 32))
        draw.text((WIDTH + 8, 80), 'Rejected or unstable\nNo verified framebuffer', fill='#ffb4ab')
        comparison.save(self.work / 'comparison.png')
        with self.assertRaisesRegex(ValueError, 'Failed run retains successful output|failure manifest'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_failed_run_with_successful_manifest(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2},
                               manifest={'status': 'success', 'gl_error_frames': 0, 'frames': 120})
        with self.assertRaisesRegex(ValueError, 'failure manifest'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_self_consistent_failed_manifest_from_other_run_or_backend(self):
        for key, value, message in (
                ('identity', {'role': 'patched', 'repeat': 7}, 'run identity'),
                ('seed', 999, 'run protocol'), ('fps', 60, 'run protocol'),
                ('frames', 119, 'failure manifest dimensions/frame count'),
                ('width', 512, 'failure manifest dimensions/frame count'),
                ('height', 288, 'failure manifest dimensions/frame count'),
                ('gl_renderer', 'other GPU', 'Backend'),
                ('gl_renderer', 'SwiftShader', 'Software renderer')):
            with self.subTest(key=key, value=value):
                self.add_rejected_role({'status': 'failed', 'exit': 2},
                                       manifest={'status': 'failed', 'gl_error_frames': 1})
                for repeat, run in enumerate(self.result['roles']['upstream']['runs']):
                    manifest = run['manifest']
                    manifest[key] = value
                    data = json.dumps(manifest).encode()
                    (self.work / 'upstream' / str(repeat) / 'manifest.json').write_bytes(data)
                    run['retained_artifacts']['manifest.json'] = {'sha256': VERIFY.sha(data), 'bytes': len(data)}
                (self.work / 'results.json').write_text(json.dumps(self.result))
                with self.assertRaisesRegex(ValueError, message):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_failed_run_without_failure_diagnostics(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2}, log=b'')
        with self.assertRaisesRegex(ValueError, 'Failed run has no retained failure diagnostic'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_changed_failed_artifact_hash_or_size(self):
        for field, value in (('sha256', '0' * 64), ('bytes', 999), ('bytes', 19.0)):
            with self.subTest(field=field):
                self.add_rejected_role({'status': 'failed', 'exit': 2})
                self.result['roles']['upstream']['runs'][0]['retained_artifacts']['render.log'][field] = value
                (self.work / 'results.json').write_text(json.dumps(self.result))
                with self.assertRaisesRegex(ValueError, 'Retained failure artifact differs'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_or_unrecorded_failed_artifacts(self):
        for change in ('missing', 'unrecorded', 'undeclared', 'escape'):
            with self.subTest(change=change):
                self.add_rejected_role({'status': 'failed', 'exit': 2})
                directory = self.work / 'upstream/0'
                run = self.result['roles']['upstream']['runs'][0]
                if change == 'missing': (directory / 'frames.rgb').unlink()
                if change == 'unrecorded': (directory / 'manifest.json').write_text('{}')
                if change == 'undeclared': run['retained_artifacts'].pop('frames.rgb')
                if change == 'escape': run['retained_artifacts']['../outside'] = {'sha256': '0' * 64, 'bytes': 1}
                (self.work / 'results.json').write_text(json.dumps(self.result))
                with self.assertRaisesRegex(ValueError, 'Retained failure artifact inventory differs'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_failed_run_with_successful_derived_pixels(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2})
        Image.frombytes('RGB', (WIDTH, HEIGHT), FRAME).save(self.work / 'upstream/0/119.png')
        with self.assertRaisesRegex(ValueError, 'Failed run retains successful output'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_failed_job_path_substitution(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2})
        for repeat in (0, 1):
            path = self.work / 'upstream' / str(repeat) / 'job.json'
            job = json.loads(path.read_text()); job['pcm_path'] = self.remote + '/other.f32'
            path.write_text(json.dumps(job))
        with self.assertRaisesRegex(ValueError, 'job input/output paths'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_or_mismatched_execution_receipts(self):
        for receipt in (None, 'not JSON', {'exit': 2}, {'exit': False}):
            with self.subTest(receipt=receipt):
                self.save()
                path = self.work / 'patched/0/execution.json'
                if receipt is None: path.unlink()
                elif isinstance(receipt, str): path.write_text(receipt)
                else: path.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(ValueError, 'Retained execution'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_failed_execution_exit_different_from_row(self):
        self.add_rejected_role({'status': 'failed', 'exit': 2})
        (self.work / 'upstream/0/execution.json').write_text(json.dumps({'exit': 3}))
        with self.assertRaisesRegex(ValueError, 'Retained execution'):
            VERIFY.verify(self.work, self.root / 'ndk')

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
        stream[50 * FRAME_SIZE] ^= 1
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
        changed_frame = bytearray(FRAME)
        changed_frame[0] ^= 1
        changed_hash = VERIFY.sha(changed_frame)
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

    def test_rejects_consistently_edited_software_backend(self):
        for renderer in ('SwiftShader', 'LLVMpipe', 'softpipe', 'lavapipe', 'Software Rasterizer'):
            with self.subTest(renderer=renderer):
                self.result['backend'][1] = renderer
                for run in self.result['roles']['patched']['runs']:
                    run['manifest']['gl_renderer'] = renderer
                self.save()
                with self.assertRaisesRegex(ValueError, 'Software renderer is outside GPU proof scope'):
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
        self.evaluator_fixture(list(range(128)))
        control = {'seed': 12345, 'compiled': [True, True], 'streams': [list(range(128)), list(range(1, 129))],
                   'fresh_thread_streams_equal': False, 'lone_dot_is_zero': True}
        self.result['roles']['patched']['runs'] = [{'exit': 0, 'control': control}] * 2
        self.save()
        with self.assertRaisesRegex(ValueError, 'thread-isolation'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_broken_evaluator_lone_dot_contract(self):
        self.evaluator_fixture(list(range(128)))
        control = {'seed': 12345, 'compiled': [True, True], 'streams': [list(range(128))] * 2,
                   'fresh_thread_streams_equal': True, 'lone_dot_is_zero': False}
        self.result['roles']['patched']['runs'] = [{'exit': 0, 'control': control}] * 2
        self.save()
        with self.assertRaisesRegex(ValueError, 'lone-dot'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_altered_rejection_panel(self):
        self.add_rejected_role({'status': 'failed', 'exit': 1})
        image = Image.open(self.work / 'comparison.png')
        image.putpixel((WIDTH, 32), (255, 255, 255))
        image.save(self.work / 'comparison.png')
        with self.assertRaisesRegex(ValueError, 'rejection panels'):
            VERIFY.verify(self.work, self.root / 'ndk')


    def evaluator_fixture(self, stream):
        self.result['capture_kind'] = 'evaluator'
        control = {'seed': 12345, 'compiled': [True, True], 'streams': [stream, stream],
                   'fresh_thread_streams_equal': True, 'lone_dot_is_zero': True}
        self.result['roles']['patched']['runs'] = [{'exit': 0, 'control': control}] * 2
        for role in ('upstream', 'without-0003'):
            identity = {**self.result['roles']['patched']['worker'], 'role': role,
                        'patch_removed': 3 if role == 'without-0003' else None,
                        'ordered_patches': SERIES if role == 'without-0003' else []}
            other = {'seed': 12345, 'compiled': [True, True],
                     'streams': [stream, [(v + 1000) % 1000000 for v in stream]],
                     'fresh_thread_streams_equal': False, 'lone_dot_is_zero': False}
            self.result['roles'][role] = {'worker': identity,
                'retained_worker': self.stage_worker(role, identity),
                'runs': [{'exit': 0, 'control': other}] * 2, 'repeat_equal': True}
        self.save()

    def test_accepts_valid_retained_evaluator_contract(self):
        self.evaluator_fixture(list(range(128)))
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'],
                         ['patched', 'upstream', 'without-0003'])

    def test_rejects_incomplete_or_extra_evaluator_roles_before_source_rebuild(self):
        patched = json.loads(json.dumps(self.result['roles']['patched']))
        for roles in (('patched',), ('upstream', 'patched'), ('without-0003', 'patched'),
                      ('upstream', 'without-0003'),
                      ('upstream', 'without-0003', 'patched', 'without-0010')):
            with self.subTest(roles=roles):
                self.result['roles'] = {'patched': json.loads(json.dumps(patched))}
                self.evaluator_fixture(list(range(128)))
                if 'without-0010' in roles:
                    self.result['roles']['without-0010'] = self.result['roles']['patched']
                self.result['roles'] = {role: self.result['roles'][role] for role in roles}
                self.save()
                with patch.object(VERIFY, 'validate_prepared_source') as rebuild:
                    with self.assertRaisesRegex(ValueError, 'Evaluator capture requires exactly'):
                        VERIFY.verify(self.work, self.root / 'ndk')
                    rebuild.assert_not_called()

    def test_rejects_evaluator_execution_with_nonzero_exit(self):
        self.evaluator_fixture(list(range(128)))
        (self.work / 'without-0003/1/execution.json').write_text(json.dumps({'exit': 2}))
        with self.assertRaisesRegex(ValueError, 'Retained execution'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_or_changed_retained_evaluator_seed(self):
        for seed in (None, 0, 999, True, 12345.0):
            with self.subTest(seed=seed):
                self.evaluator_fixture(list(range(128)))
                for run in self.result['roles']['patched']['runs']:
                    if seed is None: run['control'].pop('seed', None)
                    else: run['control']['seed'] = seed
                self.save()
                with self.assertRaisesRegex(ValueError, 'Evaluator seed differs from frozen capture seed'):
                    VERIFY.verify(self.work, self.root / 'ndk')

    def test_accepts_retained_evaluator_stdout_with_stderr(self):
        self.evaluator_fixture(list(range(128)))
        for repeat in (0, 1):
            path = self.work / 'patched' / str(repeat) / 'output.txt'
            path.write_text(path.read_text() + 'worker diagnostic on stderr\n')
        self.assertEqual(VERIFY.verify(self.work, self.root / 'ndk')['successful_roles'],
                         ['patched', 'upstream', 'without-0003'])

    def test_rejects_both_inline_evaluator_controls_tampered_together(self):
        self.evaluator_fixture(list(range(128)))
        for run in self.result['roles']['patched']['runs']:
            run['control']['streams'] = [list(range(1, 129))] * 2
        (self.work / 'results.json').write_text(json.dumps(self.result))
        with self.assertRaisesRegex(ValueError, 'Retained evaluator output differs'):
            VERIFY.verify(self.work, self.root / 'ndk')

    def test_rejects_missing_or_malformed_retained_evaluator_output(self):
        for malformed in (None, 'not worker JSON\n'):
            with self.subTest(malformed=malformed):
                self.evaluator_fixture(list(range(128)))
                path = self.work / 'patched/1/output.txt'
                if malformed is None: path.unlink()
                else: path.write_text(malformed)
                with self.assertRaisesRegex(ValueError, 'Retained evaluator output is unavailable or invalid'):
                    VERIFY.verify(self.work, self.root / 'ndk')

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
