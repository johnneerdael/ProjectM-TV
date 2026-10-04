import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

READER=Path(os.environ.get('MILK_NATIVE_READER',Path(__file__).resolve().parents[2]/'build/milk-analyzer/native/milk-native-reader'))

class NativeReaderTest(unittest.TestCase):
    def read(self,body,version=201):
        self.assertTrue(READER.is_file(), 'Build the native reader before running source tests')
        with tempfile.TemporaryDirectory() as tmp:
            preset=Path(tmp)/'control.milk'
            preset.write_text(f'MILKDROP_PRESET_VERSION={version}\n[preset00]\n'+body)
            return json.loads(subprocess.check_output([str(READER),str(preset)]))
