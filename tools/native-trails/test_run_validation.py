import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("trails_runner", Path(__file__).with_name("run_validation.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class ArtifactTests(unittest.TestCase):
    def artifacts(self, temp, contents=b"arm64"):
        aar, apk = Path(temp)/"core.aar", Path(temp)/"worker.apk"
        with zipfile.ZipFile(aar, "w") as z:
            z.writestr("jni/arm64-v8a/libprojectmtv.so", b"arm64")
            z.writestr("jni/armeabi-v7a/libprojectmtv.so", b"arm32")
        with zipfile.ZipFile(apk, "w") as z:
            z.writestr("lib/arm64-v8a/libprojectmtv.so", contents)
        return {"aar":str(aar), "apk":str(apk), "aar_sha256":runner.file_digest(aar),
                "apk_sha256":runner.file_digest(apk)}

    def test_arm64_worker_can_use_unmodified_dual_abi_release(self):
        with tempfile.TemporaryDirectory() as temp:
            runner.check_artifacts(self.artifacts(temp))

    def test_wrong_selected_native_bytes_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError): runner.check_artifacts(self.artifacts(temp,b"wrong"))

    def test_mutated_frozen_apk_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            identity = self.artifacts(temp)
            Path(identity["apk"]).write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError,"Frozen apk"): runner.check_artifacts(identity)

if __name__ == '__main__': unittest.main()
