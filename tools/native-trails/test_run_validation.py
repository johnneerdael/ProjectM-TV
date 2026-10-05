import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
import json
import hashlib
import cv2
import numpy as np

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

class CaptureTests(unittest.TestCase):
    def manifest(self, path):
        request = {"preset":"witness.milk", "width":1, "height":1}
        manifest = {"status":"ok", "framesRendered":480, "job":request,
            "requestSha256":hashlib.sha256((runner.canonical_json(request)+"\n").encode()).hexdigest(),
            "presetAssetSha256":"preset-sha", "verifiedPresetName":"witness.milk",
            "coreReleased":True, "eglDestroyed":True, "glErrorChecks":480,
            "presetNameChecks":480, "eligiblePresetCountAfterFrame479":1, "presetChangeCounter":1,
            "captures":[]}
        for frame in runner.CAPTURES:
            file = path/('frame-%03d.png' % frame)
            pixels = np.array([[[10,20,30]]],dtype=np.uint8)
            cv2.imwrite(str(file),pixels)
            manifest['captures'].append({'frame':frame,'pngSha256':runner.file_digest(file),
                'rgbSha256':hashlib.sha256(cv2.cvtColor(pixels,cv2.COLOR_BGR2RGB).tobytes()).hexdigest()})
        runner.write(path/'manifest.json',manifest)
        return request,manifest

    def test_valid_selected_frames_and_exact_request_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp); request,_ = self.manifest(path)
            runner.verify(path,request,'preset-sha')

    def test_missing_gl_checks_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp); request,manifest = self.manifest(path)
            manifest['glErrorChecks'] = 479; runner.write(path/'manifest.json',manifest)
            with self.assertRaises(ValueError): runner.verify(path,request,'preset-sha')

    def test_replaced_frame_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp); request,_ = self.manifest(path)
            (path/'frame-120.png').write_bytes(b'corrupt')
            with self.assertRaisesRegex(ValueError,'PNG checksum'): runner.verify(path,request,'preset-sha')

    def test_missing_temporal_frame_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp); request,manifest = self.manifest(path)
            manifest['captures'].pop(); runner.write(path/'manifest.json',manifest)
            with self.assertRaisesRegex(ValueError,'temporal'): runner.verify(path,request,'preset-sha')

if __name__ == '__main__': unittest.main()
