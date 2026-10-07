"""Guard engine-pin helpers and the retained deterministic Native trails bridge."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("build_core_aars", HERE / "build_core_aars.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


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
