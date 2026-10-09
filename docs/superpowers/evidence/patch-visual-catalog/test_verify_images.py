"""Bounded regressions for exchanging or dropping catalog run receipts."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]
spec = importlib.util.spec_from_file_location('catalog_verifier', EVIDENCE / 'verify_images.py')
verifier = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verifier)


class RunReceiptBinding(unittest.TestCase):
    def check(self, change=None, overrides=None, image_swap=None):
        overrides = overrides or {}
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
                    (evidence / path.name).write_text(json.dumps(overrides[path.name]))
                elif path.name == 'captures' and any(name.startswith('captures/') for name in overrides):
                    (evidence / 'captures').mkdir()
                    for child in path.iterdir():
                        key = 'captures/' + child.name
                        if key in overrides:
                            (evidence / key).write_text(json.dumps(overrides[key]))
                        else:
                            (evidence / key).symlink_to(child)
                else:
                    (evidence / path.name).symlink_to(path, target_is_directory=path.is_dir())
            (evidence / 'run-manifests.json').write_text(json.dumps(runs))
            assets = root / 'docs/user-guide/images/patches'
            assets.mkdir(parents=True)
            originals = REPO / 'docs/user-guide/images/patches/audit'
            if image_swap:
                (assets / 'audit').mkdir()
                for path in originals.glob('*.png'):
                    source_name = (image_swap[1] if path.name == image_swap[0] else
                                   image_swap[0] if path.name == image_swap[1] else path.name)
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
        with self.assertRaisesRegex(AssertionError, 'texture inventory mismatch'):
            self.check(overrides={'textures.json': textures})

    def test_source_inventory_tamper_fails(self):
        source = json.loads((EVIDENCE / 'upstream-source-tree.json').read_text())
        source[next(iter(source))] = '0' * 64
        with self.assertRaisesRegex(AssertionError, 'source inventory'):
            self.check(overrides={'upstream-source-tree.json': source})

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


if __name__ == '__main__':
    unittest.main()
