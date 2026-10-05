import importlib.util
from pathlib import Path
import unittest
import tempfile
import zipfile

spec = importlib.util.spec_from_file_location("trails_builder", Path(__file__).with_name("build_validation.py"))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class TransformTests(unittest.TestCase):
    def source(self):
        return '#include "snapshot_fade.h"\n' + builder.CLOCK_BODY + '\nprojectm_opengl_set_line_reference_size(g_engine.pm, 1024, 768);\nprojectm_opengl_set_line_reference_size(pm, width, height);\n'

    def test_all_reference_paths_share_one_frozen_override(self):
        changed = builder.instrument_core(self.source())
        self.assertEqual(changed.count('core_corpus::reference_width, core_corpus::reference_height'), 2)
        self.assertNotIn('steady_clock::now()', changed)
        self.assertIn('lab::clock_seconds.load()', changed)

    def test_native_directory_entries_are_not_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'sample.aar'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('jni/', b'')
                archive.writestr('jni/arm64-v8a/', b'')
                archive.writestr('jni/arm64-v8a/libprojectmtv.so', b'native')
            with zipfile.ZipFile(path) as archive:
                self.assertEqual(set(builder.native_hashes(archive)), {'jni/arm64-v8a/libprojectmtv.so'})

    def test_missing_or_ambiguous_clock_and_reference_fail_closed(self):
        for source in (self.source().replace(builder.CLOCK_BODY, ''), self.source() + builder.CLOCK_BODY,
                       self.source().split('projectm_opengl_set_line_reference_size')[0]):
            with self.assertRaises(ValueError): builder.instrument_core(source)

if __name__ == '__main__': unittest.main()
