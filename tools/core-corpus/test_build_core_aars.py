"""Guard the narrow Core transformation and source provenance contracts."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build_core_aars", HERE / "build_core_aars.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CoreTransformationTests(unittest.TestCase):
    def source(self, commit):
        return subprocess.check_output(
            ["git", "-C", str(builder.REPO), "show", f"{commit}:{builder.CPP}native-lib.cpp"], text=True)

    def test_both_real_sources_transform_only_allowed_spans(self):
        for commit in (builder.BASELINE, "HEAD"):
            with self.subTest(commit=commit):
                original = self.source(commit)
                transformed = builder.transform_core_native(original)
                restored = transformed.replace('#include "lab_bridge.hpp"\n', "")
                restored = restored.replace("double NowSeconds() {\n    return lab::clock_seconds;\n}", builder.CLOCK_BODY)
                restored = restored.replace("core_corpus::reference_width, core_corpus::reference_height", "1024, 768")
                self.assertEqual(original, restored)
                cpu = original.split("double ThreadCpuSeconds() {", 1)[1].split("\n}", 1)[0]
                self.assertIn("double ThreadCpuSeconds() {" + cpu, transformed)

    def test_clock_source_drift_and_duplicates_fail_closed(self):
        source = self.source(builder.BASELINE)
        for drift in (source.replace("steady_clock::now()", "system_clock::now()"),
                      source + "\n" + builder.CLOCK_BODY):
            with self.subTest(drift=drift[-100:]):
                with self.assertRaisesRegex(ValueError, "core clock"):
                    builder.transform_core_native(drift)

    def test_missing_or_duplicate_reference_fails_closed(self):
        source = self.source(builder.BASELINE)
        ref = "projectm_opengl_set_line_reference_size(g_engine.pm, 1024, 768);"
        for drift in (source.replace(ref, ""), source + "\n" + ref):
            with self.assertRaisesRegex(ValueError, "line reference dimensions"):
                builder.transform_core_native(drift)

    def test_shader_hook_moves_without_changing_source_or_hook_count(self):
        source = '#include "../analysis_hooks.hpp"\n#include "MilkdropShader.hpp"\n\nnamespace libprojectM {\n}\n'
        result = builder.relocate_shader_hook(source)
        self.assertTrue(result.startswith('#include "MilkdropShader.hpp"'))
        self.assertEqual(result.count('analysis_hooks.hpp'), 1)
        self.assertEqual(result.replace('#include "../analysis_hooks.hpp"\n', '').replace('\n\nnamespace', '\nnamespace'),
                         source.replace('#include "../analysis_hooks.hpp"\n', ''))
        with self.assertRaisesRegex(ValueError, "prepended shader hook"):
            builder.relocate_shader_hook(result)

    def test_patch_series_missing_and_nonconsecutive_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            patches = root / "tools/projectm-patches"
            patches.mkdir(parents=True)
            (patches / "0001-first.patch").write_text("one")
            (patches / "0003-third.patch").write_text("three")
            with self.assertRaisesRegex(ValueError, "consecutive"):
                builder.patch_manifest(root, 2)
            with self.assertRaisesRegex(ValueError, "expected 3"):
                builder.patch_manifest(root, 3)

    def test_metadata_requires_all_three_production_cpp_and_java(self):
        required = {builder.CPP + name for name in
                    ("native-lib.cpp", "snapshot_fade.cpp", "preset_prewarm.cpp")}
        required.add("core/src/main/java/nl/neerdael/projectm/core/ProjectMJNI.java")
        self.assertTrue(required <= set(builder.CORE_INPUTS))
        for relative in required:
            self.assertTrue((builder.REPO / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
