import hashlib
from pathlib import Path
import tempfile
import unittest

import cv2
import numpy as np

import run_corpus as runner


class RunnerTests(unittest.TestCase):
    def test_unsigned_audio_uses_exact_round_clip_mapping_and_fixed_length(self):
        samples = np.array([-2, -1, 0, .5, 1, 2], dtype=np.float32)
        self.assertEqual(runner.to_unsigned_pcm(samples).tolist(), [0, 1, 128, 192, 255, 255])
        floating, unsigned = runner.signal()
        self.assertEqual(len(unsigned), 705600)
        self.assertEqual(len(floating), 705600 * 4)
        self.assertEqual(runner.signal(), (floating, unsigned))

    def test_utf8_prefix_is_bounded_without_splitting_unicode(self):
        name = "é" * 80 + ".milk"
        prefix = runner.preset_prefix(name)
        self.assertEqual(len(prefix.encode("utf-8")), 80)
        self.assertTrue(name.startswith(prefix))
        for unsafe in ("../a.milk", "a\n.milk", "a\x00.milk"):
            with self.assertRaises(ValueError):
                runner.preset_prefix(unsafe)

    def test_png_rgb_hash_ignores_alpha_but_preserves_channel_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frame.png"
            rgba = np.zeros((2, 3, 4), np.uint8)
            rgba[:, :, :3] = [31, 63, 127]
            rgba[:, :, 3] = 255
            cv2.imwrite(str(path), rgba[:, :, [2, 1, 0, 3]])
            capture = {"width": 3, "height": 2,
                       "rgbSha256": hashlib.sha256(rgba[:, :, :3].tobytes()).hexdigest(),
                       "pngSha256": runner.file_hash(path)}
            frame = runner.decode_capture(path, capture)
            self.assertEqual(frame[0, 0].tolist(), [31, 63, 127])
            with self.assertRaises(ValueError):
                runner.decode_capture(path, dict(capture, rgbSha256="incorrect"))

    def test_adb_shell_quotes_arguments_including_property_prefix(self):
        command = runner.remote_command(["setprop", "debug.projectmtv.preset", "a 'quoted' $name; .milk"])
        import shlex
        self.assertEqual(shlex.split(command), ["setprop", "debug.projectmtv.preset", "a 'quoted' $name; .milk"])

    def test_sleeping_device_is_rejected_without_wake_command(self):
        class FakeAdb:
            calls = []
            def shell(self, *args, **kwargs):
                self.calls.append(args)
                return "mWakefulness=Asleep\nmInteractive=false"
        adb = FakeAdb()
        with self.assertRaisesRegex(RuntimeError, "awake"):
            runner.require_awake(adb)
        self.assertEqual(adb.calls, [("dumpsys", "power")])
