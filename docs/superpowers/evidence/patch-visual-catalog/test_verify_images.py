"""Bounded regressions for exchanging or dropping catalog run receipts."""
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from PIL import Image

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]
spec = importlib.util.spec_from_file_location('catalog_verifier', EVIDENCE / 'verify_images.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class RunReceiptBinding(unittest.TestCase):
    def check(self, change=None, overrides=None, image_swap=None, image_overrides=None):
        overrides = overrides or {}
        def write_override(path, value):
            if value is None:
                return
            path.write_text(value if isinstance(value, str) else json.dumps(value))
        runs = json.loads((EVIDENCE / 'run-manifests.json').read_text())
        if change:
            change(runs)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / 'docs/superpowers/evidence/patch-visual-catalog'
            evidence.mkdir(parents=True)
            for path in EVIDENCE.iterdir():
                if path.name == 'run-manifests.json':
                    continue
                if path.name in overrides:
                    write_override(evidence / path.name, overrides[path.name])
                elif path.is_dir() and any(name.startswith(path.name + '/') for name in overrides):
                    (evidence / path.name).mkdir()
                    for child in path.iterdir():
                        key = path.name + '/' + child.name
                        if key in overrides:
                            write_override(evidence / key, overrides[key])
                        else:
                            (evidence / key).symlink_to(child)
                else:
                    (evidence / path.name).symlink_to(path, target_is_directory=path.is_dir())
            (evidence / 'run-manifests.json').write_text(json.dumps(runs))
            assets = root / 'docs/user-guide/images/patches'
            assets.mkdir(parents=True)
            guide = root / 'docs/user-guide/engine'
            guide.mkdir(parents=True)
            (guide / 'patches.md').symlink_to(REPO / 'docs/user-guide/engine/patches.md')
            presets = root / 'core/src/main/assets'
            presets.mkdir(parents=True)
            (presets / 'presets').symlink_to(REPO / 'core/src/main/assets/presets', target_is_directory=True)
            (presets / 'textures').symlink_to(REPO / 'core/src/main/assets/textures', target_is_directory=True)
            originals = REPO / 'docs/user-guide/images/patches/audit'
            if image_swap or image_overrides:
                (assets / 'audit').mkdir()
                for path in originals.glob('*.png'):
                    if image_overrides and path.name in image_overrides:
                        (assets / 'audit' / path.name).write_bytes(image_overrides[path.name])
                        continue
                    source_name = (image_swap[1] if image_swap and path.name == image_swap[0] else
                                   image_swap[0] if image_swap and path.name == image_swap[1] else path.name)
                    (assets / 'audit' / path.name).symlink_to(originals / source_name)
            else:
                (assets / 'audit').symlink_to(originals, target_is_directory=True)
            verifier.verify(root)

    def test_frozen_receipts_pass(self):
        self.check()

    def test_exchanged_same_length_720p_4k_manifests_fail(self):
        def exchange(runs):
            a, b = runs['I16'][0], runs['I19-4k'][0]
            a['manifest'], b['manifest'] = b['manifest'], a['manifest']
        with self.assertRaisesRegex(AssertionError, 'I16'):
            self.check(exchange)

    def test_missing_unpublished_capture_case_fails(self):
        with self.assertRaisesRegex(AssertionError, 'case sets differ'):
            self.check(lambda runs: runs.pop('I17'))

    def test_wrong_role_worker_identity_fails(self):
        def exchange(runs):
            runs['I16'][0]['manifest']['identity'] = copy.deepcopy(runs['I16'][2]['manifest']['identity'])
        with self.assertRaisesRegex(AssertionError, 'worker mismatch'):
            self.check(exchange)

    def test_duplicate_role_repeat_fails(self):
        with self.assertRaisesRegex(AssertionError, 'duplicate run'):
            self.check(lambda runs: runs['I16'][3].update(repeat=0))

    def test_wrong_audio_hash_fails(self):
        with self.assertRaisesRegex(AssertionError, 'I16'):
            self.check(lambda runs: runs['I16'][0]['inputs'].update(pcm_sha256='0' * 64))

    def test_texture_inventory_tamper_fails(self):
        textures = json.loads((EVIDENCE / 'textures.json').read_text())
        textures[next(iter(textures))] = '0' * 64
        with self.assertRaisesRegex(AssertionError, 'preserved texture bytes'):
            self.check(overrides={'textures.json': textures})

    def test_source_inventory_tamper_fails(self):
        source = json.loads((EVIDENCE / 'upstream-source-tree.json').read_text())
        source[next(iter(source))] = '0' * 64
        with self.assertRaisesRegex(AssertionError, 'source inventory'):
            self.check(overrides={'upstream-source-tree.json': source})

    def test_joint_upstream_inventory_and_worker_digest_drift_fails(self):
        source = json.loads((EVIDENCE / 'upstream-source-tree.json').read_text())
        source['src/libprojectM/MilkdropPreset/VideoEcho.cpp'] = '0' * 64
        workers = json.loads((EVIDENCE / 'workers.json').read_text())
        workers['upstream']['source_tree_sha256'] = verifier.inventory_digest(source)
        with self.assertRaisesRegex(AssertionError, 'frozen upstream source anchor'):
            self.check(overrides={'upstream-source-tree.json': source, 'workers.json': workers})

    def test_frozen_worker_record_tamper_fails(self):
        workers = json.loads((EVIDENCE / 'workers.json').read_text())
        workers['upstream']['worker_sha256'] = '0' * 64
        with self.assertRaisesRegex(AssertionError, 'canonical worker'):
            self.check(overrides={'workers.json': workers})

    def test_joint_capture_and_run_worker_drift_fails(self):
        capture = json.loads((EVIDENCE / 'captures/I16.json').read_text())
        capture['roles']['upstream']['identity']['worker_sha256'] = '0' * 64
        def drift(runs):
            for record in runs['I16'][:2]:
                record['manifest']['identity']['worker_sha256'] = '0' * 64
        with self.assertRaisesRegex(AssertionError, 'canonical worker'):
            self.check(drift, {'captures/I16.json': capture})

    def test_exchanged_png_and_role_metadata_fails(self):
        images = json.loads((EVIDENCE / 'images.json').read_text())
        before, after = 'I17-4k-upstream.png', 'I17-4k-patched.png'
        images[before], images[after] = images[after], images[before]
        with self.assertRaisesRegex(AssertionError, 'filename identity'):
            self.check(overrides={'images.json': images}, image_swap=(before, after))

    def test_gallery_frame_drift_fails(self):
        gallery = json.loads((EVIDENCE / 'gallery.json').read_text())
        gallery[0]['frame'] = 119
        with self.assertRaisesRegex(AssertionError, 'gallery frame'):
            self.check(overrides={'gallery.json': gallery})

    def test_stale_repeat_flag_cannot_hide_hash_difference(self):
        with self.assertRaisesRegex(AssertionError, 'repeat frame hashes'):
            self.check(lambda runs: runs['I16'][1]['frame_sha256'].__setitem__(17, '0' * 64))

    def test_preserved_fixture_tamper_fails(self):
        fixture = 'fixtures/audit negative echo.milk'
        altered = (EVIDENCE / fixture).read_text() + '\n// changed fixture\n'
        with self.assertRaisesRegex(AssertionError, 'preset bytes'):
            self.check(overrides={fixture: altered})

    def test_missing_preserved_fixture_fails(self):
        with self.assertRaisesRegex(AssertionError, 'preset file missing'):
            self.check(overrides={'fixtures/audit negative echo.milk': None})

    def test_preserved_pcm_tamper_fails(self):
        with self.assertRaisesRegex(AssertionError, 'PCM bytes'):
            self.check(overrides={'audio/frozen-240-frames.f32': ''})

    def test_same_area_reshape_with_matching_metadata_fails(self):
        name = 'I31-upstream.png'
        images = json.loads((EVIDENCE / 'images.json').read_text())
        with Image.open(REPO / 'docs/user-guide/images/patches/audit' / name) as image:
            reshaped = Image.frombytes('RGB', (640, 1440), image.tobytes())
        payload = io.BytesIO()
        reshaped.save(payload, format='PNG')
        data = payload.getvalue()
        images[name].update(width=640, height=1440, png_sha256=verifier.sha(data))
        with self.assertRaisesRegex(AssertionError, 'image dimensions'):
            self.check(overrides={'images.json': images}, image_overrides={name: data})

    def test_changed_complete_request_controls_fail(self):
        runs = json.loads((EVIDENCE / 'run-manifests.json').read_text())
        captures = json.loads((EVIDENCE / 'captures/I16.json').read_text())
        canonical = {r: captures['roles'][r]['identity'] for r in ('upstream', 'patched')}
        for field, value in [('width', 3840), ('height', 2160), ('fps', 60),
                             ('seed', 1), ('warmup_seconds', 1),
                             ('measurement_seconds', 16.0),
                             ('line_reference_height', 1080), ('line_antialiasing', True)]:
            with self.subTest(field=field):
                record = copy.deepcopy(runs['I16'][0])
                record['request']['config'][field] = value
                with self.assertRaisesRegex(AssertionError, 'request config ' + field):
                    verifier.verify_request(record, captures, canonical, 'I16')

    def test_unexpected_request_override_fails(self):
        with self.assertRaisesRegex(AssertionError, 'request config fields'):
            self.check(lambda runs: runs['I16'][0]['request']['config'].update(line_reference_width=1920))

    def test_wrong_request_worker_fails(self):
        def change(runs):
            runs['I16'][0]['request']['identity'] = runs['I16'][2]['request']['identity']
        with self.assertRaisesRegex(AssertionError, 'request worker'):
            self.check(change)

    def test_missing_complete_request_fails(self):
        with self.assertRaises(KeyError):
            self.check(lambda runs: runs['I16'][0].pop('request'))

    def test_changed_request_paths_fail(self):
        runs = json.loads((EVIDENCE / 'run-manifests.json').read_text())
        capture = json.loads((EVIDENCE / 'captures/I16.json').read_text())
        canonical = {r: capture['roles'][r]['identity'] for r in ('upstream', 'patched')}
        for field, label in [('preset_path', 'preset'), ('pcm_path', 'PCM'),
                             ('texture_root', 'texture'), ('bands_path', 'bands'),
                             ('manifest_path', 'manifest')]:
            with self.subTest(field=field):
                record = copy.deepcopy(runs['I16'][0])
                record['request'][field] += '.wrong'
                with self.assertRaisesRegex(AssertionError, 'request ' + label + ' path'):
                    verifier.verify_request(record, capture, canonical, 'I16')


class GuideRoleBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (REPO / 'docs/user-guide/engine/patches.md').read_text()
        cls.gallery = json.loads((EVIDENCE / 'gallery.json').read_text())
        cls.captures = {p.stem: json.loads(p.read_text()) for p in (EVIDENCE / 'captures').glob('*.json')}

    def verify(self, source):
        verifier.verify_guide(source, self.gallery, self.captures)

    def test_guide_passes(self):
        self.verify(self.source)

    def test_guide_role_reference_swap_fails(self):
        changed = self.source.replace('I17-4k-upstream.png', 'ROLE-SWAP.png').replace(
            'I17-4k-patched.png', 'I17-4k-upstream.png').replace('ROLE-SWAP.png', 'I17-4k-patched.png')
        with self.assertRaisesRegex(AssertionError, 'guide role reference'):
            self.verify(changed)

    def test_guide_link_without_image_swap_fails(self):
        changed = self.source.replace('href="../../images/patches/audit/I17-4k-upstream.png"',
                                      'href="../../images/patches/audit/I17-4k-patched.png"', 1)
        with self.assertRaisesRegex(AssertionError, 'guide role reference'):
            self.verify(changed)

    def test_guide_visible_role_label_swap_fails(self):
        changed = self.source.replace('Before · upstream master</strong><a href="../../images/patches/audit/I17-',
                                      'After · ProjectM TV</strong><a href="../../images/patches/audit/I17-', 1)
        with self.assertRaisesRegex(AssertionError, 'guide role label'):
            self.verify(changed)

    def test_guide_alt_role_label_swap_fails(self):
        changed = self.source.replace('alt="Happening.milk — Before · upstream master"',
                                      'alt="Happening.milk — After · ProjectM TV"', 1)
        with self.assertRaisesRegex(AssertionError, 'guide image label'):
            self.verify(changed)

    def test_guide_zoom_reference_swap_fails(self):
        changed = self.source.replace('class="patch-crop" href="../../images/patches/audit/I08-4k-upstream.png"',
                                      'class="patch-crop" href="../../images/patches/audit/I08-4k-patched.png"', 1)
        with self.assertRaisesRegex(AssertionError, 'guide role reference'):
            self.verify(changed)

    def test_guide_same_but_wrong_crop_fails(self):
        changed = self.source.replace('--image-top:-75.000000000%;', '--image-top:-74.000000000%;')
        with self.assertRaisesRegex(AssertionError, 'guide crop rectangle'):
            self.verify(changed)

    def test_guide_extra_crop_style_fails(self):
        changed = self.source.replace('--crop-ratio:1152/864;', '--crop-ratio:1152/864;filter:brightness(2);')
        with self.assertRaisesRegex(AssertionError, 'guide crop rectangle'):
            self.verify(changed)

    def test_guide_image_colour_adjustment_fails(self):
        changed = self.source.replace('alt="Happening.milk — Before · upstream master"',
                                      'style="filter:brightness(2)" alt="Happening.milk — Before · upstream master"', 1)
        with self.assertRaisesRegex(AssertionError, 'guide panel style'):
            self.verify(changed)

    def test_guide_caption_frame_drift_fails(self):
        changed = self.source.replace('3840×2160, frame 239 at 30 Hz.', '3840×2160, frame 119 at 30 Hz.', 1)
        with self.assertRaisesRegex(AssertionError, 'guide frame caption'):
            self.verify(changed)

    def test_guide_wrong_patch_section_fails(self):
        changed = self.source.replace('## 0017 — Built-in wave opacity', '## 0018 — Built-in wave opacity')
        with self.assertRaisesRegex(AssertionError, 'guide patch section'):
            self.verify(changed)

    def test_guide_additional_unbound_image_fails(self):
        changed = self.source + '\n<img src="../../images/patches/audit/I17-4k-upstream.png">\n'
        with self.assertRaisesRegex(AssertionError, 'unbound audit image'):
            self.verify(changed)

    def test_guide_markdown_image_outside_figure_fails(self):
        changed = self.source + '\n![Wrong After](../../images/patches/audit/I17-4k-upstream.png)\n'
        with self.assertRaisesRegex(AssertionError, 'unbound audit image'):
            self.verify(changed)


class FrozenCaptureAudio(unittest.TestCase):
    def test_preserved_pcm_bytes_pass_both_workloads(self):
        from frozen_protocol import frozen_pcm, FROZEN_PCM
        for frames in (240, 480):
            with self.subTest(frames=frames):
                payload = frozen_pcm(EVIDENCE, frames)
                self.assertEqual(verifier.sha(payload), FROZEN_PCM[frames])

    def test_capture_rejects_altered_audio_before_either_worker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / 'docs/superpowers/evidence/patch-visual-catalog/audio'
            evidence.mkdir(parents=True)
            data = bytearray((EVIDENCE / 'audio/frozen-240-frames.f32').read_bytes())
            data[0] ^= 1
            (evidence / 'frozen-240-frames.f32').write_bytes(data)
            work = root / 'new-work'
            result = subprocess.run([sys.executable, str(EVIDENCE / 'capture_host.py'),
                                     '--repo', str(root), '--work', str(work), '--name', 'negative',
                                     '--preset', str(root / 'unused.milk'), '--frames', '240'],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('frozen PCM bytes changed', result.stderr)
            self.assertFalse(work.exists(), 'audio must reject before capture setup or worker launch')

    def test_unsupported_frame_count_rejects(self):
        from frozen_protocol import frozen_pcm
        with self.assertRaisesRegex(ValueError, '240 or 480'):
            frozen_pcm(EVIDENCE, 120)


if __name__ == '__main__':
    unittest.main()
