import importlib.util
import inspect
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

    def test_native_frame_time_reaches_both_core_render_paths(self):
        source = self.source() + ("    projectm_opengl_render_frame(g_engine.pm);\n"
                                  "    projectm_opengl_render_frame_fbo(g_engine.pm, target);\n")
        self.assertIn("native_frame_time", inspect.signature(builder.instrument_core).parameters)
        changed = builder.instrument_core(source, native_frame_time=True)
        for render in ("projectm_opengl_render_frame(g_engine.pm);",
                       "projectm_opengl_render_frame_fbo(g_engine.pm, target);"):
            self.assertIn("projectm_set_frame_time(g_engine.pm, lab::clock_seconds.load());\n    " + render, changed)
        self.assertEqual(changed.count("projectm_set_frame_time("), 2)
        self.assertNotIn("projectm_set_frame_time", builder.instrument_core(source))
        with self.assertRaisesRegex(ValueError, "render"):
            builder.instrument_core(self.source(), native_frame_time=True)

    def test_worker_keeps_the_selected_native_abi(self):
        source = (builder.ROOT / "tools/core-corpus/android-worker/app/build.gradle").read_text()
        for abi in ("armeabi-v7a", "arm64-v8a"):
            changed = builder.instrument_worker_abi(source, abi)
            self.assertIn("ndk { abiFilters '" + abi + "' }", changed)
            if abi == "armeabi-v7a":
                self.assertNotIn("arm64-v8a", changed)
        with self.assertRaises(ValueError):
            builder.instrument_worker_abi(source + source, "armeabi-v7a")

    def test_invalid_abi_is_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "Unsupported ABI"):
                builder.build("HEAD", "native", "candidate-native", Path(temp), abi="x86_64")
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_rebase_roles_use_unique_packages_without_relabeling_old_roles(self):
        self.assertTrue(callable(getattr(builder, "worker_package", None)))
        self.assertEqual(builder.worker_package("rebase-baseline"), "nl.neerdael.projectmtv.corpusrebasebaseline")
        self.assertEqual(builder.worker_package("rebase-candidate"), "nl.neerdael.projectmtv.corpusrebasecandidate")
        self.assertEqual(builder.worker_package("baseline-native"), "nl.neerdael.projectmtv.corpusbaseline")
        self.assertEqual(builder.worker_package("candidate-native"), "nl.neerdael.projectmtv.corpuscandidate")
        source = (builder.ROOT / "tools/core-corpus/android-worker/app/build.gradle").read_text()
        for role in ("rebase-baseline", "rebase-candidate"):
            package = builder.worker_package(role)
            transformed = builder.instrument_worker_package(source, package)
            self.assertIn("'" + package + "'", transformed)
            self.assertEqual(transformed.replace(", '" + package + "'", ""), source)
        self.assertEqual(builder.instrument_worker_package(source, "nl.neerdael.projectmtv.corpusbaseline"), source)
        with self.assertRaisesRegex(ValueError, "role"):
            builder.worker_package("../escape")

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
