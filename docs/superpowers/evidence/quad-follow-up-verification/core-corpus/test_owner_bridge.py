import copy
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent


class OwnerBridgeTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("owner_bridge_under_test", HERE / "owner_bridge.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.original = {"pid": 92211, "avd": "/owned/avds/core.avd", "command": ["emulator", "-avd", "core", "-port", "5580", "-gpu", "host"], "launch_sha256": "old", "ro.kernel.qemu": "1"}
        self.current = dict(self.original, pid=20334, launch_sha256="new")
        self.launch = {"restarted_from_dead_pid": 92211, "prior_launch_sha256": "old"}
        self.device = {"ro.build.fingerprint": "same", "ro.product.cpu.abi": "arm64-v8a"}
        self.gl = {"gl_vendor": "Google (Apple)", "gl_renderer": "M4 Pro", "gl_version": "GLES3"}

    def test_accepts_actual_new_pid_receipt_with_same_render_identity(self):
        self.module.validate_owner_epoch(self.original, self.current, self.launch, self.device, self.device, self.gl, self.gl)

    def test_rejects_other_avd_gpu_flags_or_stale_pid(self):
        for field, value in (("avd", "/other.avd"), ("command", ["emulator", "-gpu", "software"]), ("pid", 92211), ("ro.kernel.qemu", "0")):
            with self.subTest(field=field):
                changed = dict(self.current, **{field: value})
                with self.assertRaises(ValueError):
                    self.module.validate_owner_epoch(self.original, changed, self.launch, self.device, self.device, self.gl, self.gl)

    def test_rejects_broken_chain_device_fingerprint_or_gpu(self):
        for launch, device, gl in ((dict(self.launch, prior_launch_sha256="wrong"), self.device, self.gl), (self.launch, {"ro.build.fingerprint": "different"}, self.gl), (self.launch, self.device, dict(self.gl, gl_renderer="software"))):
            with self.assertRaises(ValueError):
                self.module.validate_owner_epoch(self.original, self.current, launch, self.device, device, self.gl, gl)

    def test_rejects_changed_source_or_input_checksum(self):
        with self.assertRaises(ValueError):
            self.module.require_digest("expected", "different", "frozen renderer")


if __name__ == "__main__":
    unittest.main()
