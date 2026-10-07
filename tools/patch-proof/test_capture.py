"""Failed workers retain structured diagnostics before the owned remote cleanup."""
from contextlib import nullcontext
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('patch_proof_capture', Path(__file__).with_name('capture.py'))
CAPTURE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CAPTURE)


class FailedCaptureRetention(unittest.TestCase):
    def run_failed_worker(self, missing_manifest=False):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            binary = root / 'worker'
            binary.write_bytes(b'worker identity')
            workers = root / 'workers.json'
            workers.write_text(json.dumps({'patched': {
                'binary': str(binary), 'binary_sha256': CAPTURE.sha(binary.read_bytes())}}))
            preset = root / 'preset.milk'
            preset.write_text('[preset00]\n')
            textures = root / 'textures'
            textures.mkdir()
            work = root / 'capture'
            calls = []

            def fake_run(command, **kwargs):
                args = command[3:]
                calls.append(args)
                output, code = '', 0
                if args == ['shell', 'am', 'get-current-user']:
                    output = '0\n'
                elif args == ['shell', 'getprop', 'ro.kernel.qemu']:
                    output = '1\n'
                elif args == ['shell', 'pm', 'list', 'features']:
                    output = 'feature:android.software.leanback\nfeature:android.hardware.type.television\n'
                elif args[0] == 'shell' and '--job' in args[-1]:
                    code = 2
                elif args[0] == 'pull':
                    target = Path(args[2])
                    name = Path(args[1]).name
                    if name == 'render.log':
                        target.write_text('GL error on frame 2\n')
                    elif name == 'manifest.json' and missing_manifest:
                        code = 1
                        output = 'manifest unavailable'
                    elif name == 'manifest.json':
                        target.write_text(json.dumps({'status': 'gl_error', 'gl_error_frames': 1, 'frames': 3}))
                    elif name == 'frames.rgb':
                        target.write_bytes(b'partial RGB stream')
                return subprocess.CompletedProcess(command, code, output, '')

            argv = ['capture.py', '--workers', str(workers), '--preset', str(preset),
                    '--textures', str(textures), '--device', 'emulator-5630',
                    '--user', '0', '--work', str(work)]
            with patch.object(sys, 'argv', argv), patch.object(CAPTURE, 'session_lock', return_value=nullcontext()), \
                    patch.object(CAPTURE.subprocess, 'run', side_effect=fake_run):
                CAPTURE.main()
            result = json.loads((work / 'results.json').read_text())
            for repeat, run in enumerate(result['roles']['patched']['runs']):
                directory = work / 'patched' / str(repeat)
                self.assertEqual(run['status'], 'failed')
                self.assertEqual(run['exit'], 2)
                self.assertTrue((directory / 'frames.rgb').is_file(), 'Failed RGB stream was discarded')
                self.assertEqual((directory / 'frames.rgb').read_bytes(), b'partial RGB stream')
                if missing_manifest:
                    self.assertIn('manifest.json', run['pull_errors'])
                else:
                    self.assertEqual(run['manifest']['gl_error_frames'], 1)
                    self.assertTrue((directory / 'manifest.json').is_file())
                self.assertFalse(result['roles']['patched']['repeat_equal'])
            self.assertEqual(calls[-1][:3], ['shell', 'rm', '-rf'])

    def test_retains_gl_failed_manifest_and_stream(self):
        self.run_failed_worker()

    def test_retains_stream_when_failure_manifest_is_unavailable(self):
        self.run_failed_worker(missing_manifest=True)


if __name__ == '__main__':
    unittest.main()
