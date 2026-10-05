import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile
import json
import hashlib
import io
import shlex
import subprocess
import tarfile
from unittest.mock import patch
import cv2
import numpy as np

spec = importlib.util.spec_from_file_location("trails_runner", Path(__file__).with_name("run_validation.py"))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class ArtifactTests(unittest.TestCase):
    def artifacts(self, temp, contents=b"arm64", abi="arm64-v8a"):
        aar, apk = Path(temp)/"core.aar", Path(temp)/"worker.apk"
        with zipfile.ZipFile(aar, "w") as z:
            z.writestr("jni/arm64-v8a/libprojectmtv.so", b"arm64")
            z.writestr("jni/armeabi-v7a/libprojectmtv.so", b"arm32")
        with zipfile.ZipFile(apk, "w") as z:
            z.writestr("lib/" + abi + "/libprojectmtv.so", contents)
        return {"aar":str(aar), "apk":str(apk), "aar_sha256":runner.file_digest(aar),
                "apk_sha256":runner.file_digest(apk)}

    def test_arm32_worker_requires_its_declared_abi(self):
        with tempfile.TemporaryDirectory() as temp:
            identity = self.artifacts(temp, contents=b"arm32", abi="armeabi-v7a")
            identity["abi"] = "armeabi-v7a"
            runner.check_artifacts(identity)
            identity["abi"] = "arm64-v8a"
            with self.assertRaisesRegex(ValueError, "missing the tested"):
                runner.check_artifacts(identity)
            identity["abi"] = "x86_64"
            with self.assertRaisesRegex(ValueError, "Unsupported worker ABI"):
                runner.check_artifacts(identity)

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


class FakeADB:
    """Exercise the real adb/shell adapters without touching a device."""
    def __init__(self, work, user="7\r\n", package_output=None, fail_instrument=False):
        self.work, self.user = work, user
        self.package_output, self.fail_instrument = package_output, fail_instrument
        self.calls, self.archive = [], b""

    def __call__(self, command, **kwargs):
        if command[:3] != ["adb", "-s", "emulator-fixture"]:
            raise AssertionError("ADB serial was not explicit")
        mode = command[3]
        args = shlex.split(command[4]) if mode == "shell" else command[4:]
        self.calls.append((mode, args))
        if args == ["am", "get-current-user"]: return self.user
        if args[:2] == ["getprop", "ro.build.fingerprint"]: return "fixture-fingerprint\n"
        if args[:2] == ["getprop", "debug.projectmtv.preset"]: return "old-preset\n"
        if mode == "install": return "Performing Streamed Install\nSuccess\n"
        if args[:3] == ["pm", "list", "packages"]:
            return self.package_output if self.package_output is not None else "package:" + args[-1] + "\n"
        if args[:2] == ["am", "instrument"]:
            if self.fail_instrument:
                raise subprocess.CalledProcessError(1, command, "instrumentation failed")
            directory = next((self.work / "jobs").glob("*/request.json")).parent
            request = json.loads((directory / "request.json").read_text())
            with tempfile.TemporaryDirectory() as temp:
                output = Path(temp) / "output"; output.mkdir()
                _, manifest = CaptureTests().manifest(output)
                manifest["job"] = request
                manifest["requestSha256"] = hashlib.sha256((runner.canonical_json(request) + "\n").encode()).hexdigest()
                manifest["presetAssetSha256"] = runner.file_digest(self.work.parent / "repo/core/src/main/assets/presets/witness.milk")
                manifest.update(renderWallDurationMs=100, nativeTrailsStatus="API absent in baseline")
                runner.write(output / "manifest.json", manifest)
                stream = io.BytesIO()
                with tarfile.open(fileobj=stream, mode="w") as archive:
                    for path in output.iterdir(): archive.add(path, arcname="output/" + path.name)
                self.archive = stream.getvalue()
            return "OK\n"
        if mode == "exec-out": return self.archive
        return b"" if not kwargs["text"] else ""


class UserScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name); self.work = self.base / "run"
        self.repo, self.workers = self.base / "repo", self.base / "workers"
        assets = self.repo / "core/src/main/assets/presets"; assets.mkdir(parents=True)
        (assets / "witness.milk").write_bytes(b"frozen preset")
        self.presets = self.base / "presets.txt"; self.presets.write_text("witness.milk\n")
        for role, count in (("baseline-native", 1), ("candidate-native", 2)):
            directory = self.workers / role; directory.mkdir(parents=True)
            identity = ArtifactTests().artifacts(directory)
            identity.update(package="test." + role.replace("-", ""), assets_sha256="same-assets",
                            ordered_patches=[{"name": str(i)} for i in range(count)])
            runner.write(directory / "identity.json", identity)
        profiles = [(name, role, 1, 1, rw, rh, level) for name, role, width, height, rw, rh, level in runner.PROFILES]
        self.addCleanup(patch.stopall)
        patch.object(runner, "ROOT", self.repo).start()
        patch.object(runner, "PROFILES", profiles).start()

    def run_with(self, fake):
        with patch.object(runner.subprocess, "check_output", side_effect=fake):
            runner.run(self.work, self.workers, self.presets, "emulator-fixture", {"authored"})

    def test_mixed_worker_abis_fail_before_freezing_or_contacting_device(self):
        directory = self.workers / "candidate-native"
        identity = json.loads((directory / "identity.json").read_text())
        identity.update(ArtifactTests().artifacts(directory, contents=b"arm32", abi="armeabi-v7a"))
        identity["abi"] = "armeabi-v7a"
        runner.write(directory / "identity.json", identity)
        with patch.object(runner, "shell") as device_call:
            with self.assertRaisesRegex(ValueError, "Baseline/candidate ABIs differ"):
                runner.initialize(self.work, self.workers, self.presets, "emulator-fixture", 7)
            device_call.assert_not_called()
        self.assertFalse((self.work / "protocol.json").exists())

    def test_secondary_user_scopes_install_instrumentation_run_as_paths_and_cleanup(self):
        fake = FakeADB(self.work); self.run_with(fake)
        protocol = json.loads((self.work / "protocol.json").read_text())
        self.assertEqual(protocol["user_id"], 7)
        self.assertEqual(protocol["schema"], 2)
        self.assertEqual(sum(args == ["am", "get-current-user"] for mode, args in fake.calls), 1)
        installed = next(args for mode, args in fake.calls if mode == "install")
        self.assertEqual(installed[:3], ["-r", "--user", "7"])
        lookup = next(args for mode, args in fake.calls if args[:3] == ["pm", "list", "packages"])
        self.assertEqual(lookup[3:5], ["--user", "7"])
        instrumentation = next(args for mode, args in fake.calls if args[:2] == ["am", "instrument"])
        self.assertEqual(instrumentation[2:4], ["--user", "7"])
        stops = [args for mode, args in fake.calls if args[:2] == ["am", "force-stop"]]
        self.assertEqual(len(stops), 2)
        self.assertTrue(all(args[2:4] == ["--user", "7"] for args in stops))
        scoped = [args for mode, args in fake.calls if args[0] == "run-as"]
        self.assertGreaterEqual(len(scoped), 5)
        self.assertTrue(all(args[2:4] == ["--user", "7"] for args in scoped))
        request = json.loads(next((self.work / "jobs").glob("*/request.json")).read_text())
        self.assertTrue(request["pcmPath"].startswith("/data/user/7/"))
        self.assertTrue(request["outputDir"].startswith("/data/user/7/"))
        cleanup = scoped[-1]
        self.assertEqual(cleanup[4:6], ["rm", "-rf"])
        self.assertTrue(cleanup[-1].startswith("/data/user/7/"))

    def test_invalid_current_user_never_reaches_install_or_render_mutations(self):
        for user in ("", "Error: query failed\n", "-1\n", "7\n8\n", "current\n"):
            with self.subTest(user=user):
                fake = FakeADB(self.work, user=user)
                with self.assertRaisesRegex(ValueError, "current.*user"):
                    self.run_with(fake)
                self.assertEqual(fake.calls, [("shell", ["am", "get-current-user"])])

    def test_wrong_user_package_lookup_stops_before_instrumentation(self):
        for output in ("", "package:test.baselinenative.other\n", "Error: invalid user\n"):
            fake = FakeADB(self.work, package_output=output)
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "package"):
                self.run_with(fake)
            self.assertFalse(any(args[:2] == ["am", "instrument"] for mode, args in fake.calls))

    def test_instrumentation_error_restores_property_and_cleans_same_user(self):
        fake = FakeADB(self.work, fail_instrument=True)
        with self.assertRaises(subprocess.CalledProcessError): self.run_with(fake)
        self.assertIn(("shell", ["setprop", "debug.projectmtv.preset", "old-preset"]), fake.calls)
        self.assertTrue(all(args[2:4] == ["--user", "7"] for mode, args in fake.calls if args[:2] == ["am", "force-stop"]))
        cleanup = fake.calls[-1][1]
        self.assertEqual(cleanup[2:6], ["--user", "7", "rm", "-rf"])
        self.assertTrue(cleanup[-1].startswith("/data/user/7/"))

if __name__ == '__main__': unittest.main()
