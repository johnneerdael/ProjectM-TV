"""Guard the narrow Core transformation and source provenance contracts."""
import importlib.util
import inspect
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build_core_aars", HERE / "build_core_aars.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class CoreTransformationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("GITHUB_ACTIONS") == "true":
            git = ["git", "-C", str(builder.REPO)]
            fixture = f"{builder.BASELINE}:{builder.CPP}native-lib.cpp"
            available = subprocess.run([*git, "cat-file", "-e", fixture],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if available.returncode:
                subprocess.run([*git, "fetch", "--no-tags", "--depth=1",
                                "--recurse-submodules=no", "origin", builder.BASELINE], check=True)

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

    def test_candidate_patch_count_comes_from_the_revision(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            patches = root / "tools/projectm-patches"
            patches.mkdir(parents=True)
            for number in range(1, 4):
                (patches / f"{number:04}-candidate.patch").write_text(str(number))
            try:
                manifest = builder.patch_manifest(root, None)
            except ValueError as error:
                self.fail(f"candidate revision's consecutive patch count rejected: {error}")
            self.assertEqual(len(manifest), 3)

    def test_current_engine_clock_is_set_before_each_actual_render(self):
        source = self.source("HEAD")
        self.assertIn("native_frame_time", inspect.signature(builder.transform_core_native).parameters)
        transformed = builder.transform_core_native(source, native_frame_time=True)
        for render in ("projectm_opengl_render_frame(g_engine.pm);",
                       "projectm_opengl_render_frame_fbo(g_engine.pm, g_engine.scaledFbo);"):
            prefix = transformed[:transformed.index(render)].rstrip()
            self.assertTrue(prefix.endswith("projectm_set_frame_time(g_engine.pm, lab::clock_seconds);"))
        self.assertNotIn("projectm_set_frame_time", builder.transform_core_native(self.source(builder.BASELINE)))

    def test_metadata_requires_all_three_production_cpp_and_java(self):
        required = {builder.CPP + name for name in
                    ("native-lib.cpp", "snapshot_fade.cpp", "preset_prewarm.cpp")}
        required.add("core/src/main/java/nl/neerdael/projectm/core/ProjectMJNI.java")
        self.assertTrue(required <= set(builder.CORE_INPUTS))
        for relative in required:
            self.assertTrue((builder.REPO / relative).is_file(), relative)


class PinnedCheckoutTests(unittest.TestCase):
    def git(self, root, *args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE).strip()

    def commit_file(self, root, value):
        (root / "version.txt").write_text(value)
        self.git(root, "add", "version.txt")
        self.git(root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", value)
        return self.git(root, "rev-parse", "HEAD")

    def test_requested_revision_pins_win_over_live_checkout_heads(self):
        self.assertTrue(callable(getattr(builder, "checkout_pinned_engine", None)),
                        "builder must resolve requested revision gitlinks into a private checkout")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / "repo"
            engine = repo / "third_party/projectm"
            evaluator = engine / "vendor/projectm-eval"
            evaluator.mkdir(parents=True)
            for path in (repo, engine, evaluator):
                self.git(path, "init", "-q")
            revisions = []
            for value in ("old", "new"):
                eval_commit = self.commit_file(evaluator, value)
                self.git(engine, "update-index", "--add", "--cacheinfo", "160000", eval_commit, "vendor/projectm-eval")
                engine_commit = self.commit_file(engine, value)
                self.git(repo, "update-index", "--add", "--cacheinfo", "160000", engine_commit, "third_party/projectm")
                source_commit = self.commit_file(repo, value)
                revisions.append((source_commit, engine_commit, eval_commit))
            for index, (source_commit, engine_commit, eval_commit) in enumerate(revisions):
                checkout, engine_pin, evaluator_pin = builder.checkout_pinned_engine(repo, source_commit, root / str(index))
                self.assertEqual((engine_pin, evaluator_pin), (engine_commit, eval_commit))
                self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), engine_commit)
                self.assertEqual(self.git(checkout / "vendor/projectm-eval", "rev-parse", "HEAD"), eval_commit)
                self.assertEqual((checkout / "version.txt").read_text(), ("old", "new")[index])
            self.assertEqual(self.git(engine, "rev-parse", "HEAD"), revisions[1][1])
            self.assertEqual(self.git(evaluator, "rev-parse", "HEAD"), revisions[1][2])
            self.assertEqual(self.git(repo, "status", "--porcelain"), "")


class NativeBridgeSeedTests(unittest.TestCase):
    def test_initialize_resets_actual_shader_rng_for_each_job(self):
        compiler = shutil.which("c++")
        if compiler is None:
            self.skipTest("C++ compiler required for the actual bridge RNG regression")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            # JNI declarations are the only stub; compile the actual bridge and
            # hook, including the same atomic-clock transformation as Android.
            (root / "jni.h").write_text(
                "#define JNIEXPORT\n#define JNICALL\n"
                "struct JNIEnv; using jclass=void*; using jlong=long long; "
                "using jint=int; using jdouble=double;\n")
            hook = (builder.REPO / "tools/preset-lab/src/preset_lab/native/analysis_hooks.hpp").read_text()
            hook = hook.replace("#include <cstdint>", "#include <cstdint>\n#include <atomic>")
            hook = hook.replace("inline double clock_seconds = 0.0;", "inline std::atomic<double> clock_seconds{0.0};")
            (root / "analysis_hooks.hpp").write_text(hook)
            bridge = HERE / "native-lab/lab_bridge.cpp"
            (root / "check.cpp").write_text(
                '#include "' + str(bridge) + '"\n#include <iostream>\n'
                'int main() {\n'
                '  for (unsigned seed : {12345u, 54321u, 12345u}) {\n'
                '    lab::shader_random_state = 777; lab::clock_seconds = 12.0;\n'
                '    Java_nl_neerdael_projectmtv_corpus_LabBridge_initialize(nullptr, nullptr, seed, 1024, 768);\n'
                '    const uint32_t configured = seed ^ 0x9e3779b9u;\n'
                '    const uint32_t expected = (uint64_t(configured) * 16807u) % 2147483647u;\n'
                '    const uint32_t actual = lab::ShaderRandom();\n'
                '    if (actual != expected || lab::clock_seconds != 0.0) {\n'
                '      std::cerr << "configured seed " << seed << ": expected " << expected << ", got " << actual << "\\n"; return 1;\n'
                '    }\n'
                '  }\n  return 0;\n}\n')
            executable = root / "check"
            subprocess.run([compiler, "-std=c++17", "-I", str(root), str(root / "check.cpp"),
                            "-o", str(executable)], check=True, capture_output=True, text=True)
            result = subprocess.run([str(executable)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)



if __name__ == "__main__":
    unittest.main()
