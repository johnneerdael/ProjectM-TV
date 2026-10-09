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
    def check(self, change=None):
        runs = json.loads((EVIDENCE / 'run-manifests.json').read_text())
        if change:
            change(runs)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / 'docs/superpowers/evidence/patch-visual-catalog'
            evidence.mkdir(parents=True)
            for path in EVIDENCE.iterdir():
                if path.name != 'run-manifests.json':
                    (evidence / path.name).symlink_to(path, target_is_directory=path.is_dir())
            (evidence / 'run-manifests.json').write_text(json.dumps(runs))
            assets = root / 'docs/user-guide/images/patches'
            assets.mkdir(parents=True)
            (assets / 'audit').symlink_to(REPO / 'docs/user-guide/images/patches/audit', target_is_directory=True)
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


if __name__ == '__main__':
    unittest.main()
