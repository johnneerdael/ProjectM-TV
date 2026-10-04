from pathlib import Path
import datetime, hashlib, json, os, platform, shutil, subprocess
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FILTER = "ShaderFailureTest.VertexRejectionReleasesShader:ShaderFailureTest.FragmentRejectionReleasesBothShaders:ShaderFailureTest.LinkRejectionReleasesBothShaders:ShaderFailureTest.RepeatedRejectedProgramsDoNotAccumulateShaders"
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
records = []
for state, config in [("red", "worker-final.json"), ("green", "worker-diagnostics-fixed.json")]:
    worker_path = ROOT / "build/follow-ups" / config
    worker = json.loads(worker_path.read_text())
    build_key = Path(worker["exe"]).parent.name
    lab = "lab-final" if state == "red" else "lab-diagnostics-fixed"
    snapshot = ROOT / "build/follow-ups" / lab / "engines" / build_key
    src = snapshot / "src/libprojectM/Renderer"
    dest = OUT / "allocation" / state
    copied_src = dest / "src/libprojectM/Renderer"
    copied_test = dest / "tests/libprojectM/ShaderFailureTest.cpp"
    copied_src.mkdir(parents=True, exist_ok=True); copied_test.parent.mkdir(parents=True, exist_ok=True)
    for name in ["Shader.cpp", "Shader.hpp"]: shutil.copyfile(src / name, copied_src / name)
    test_source = ROOT / "third_party/projectm/tests/libprojectM/ShaderFailureTest.cpp"
    test = test_source.read_text().replace("#include <algorithm>", "#include <algorithm>\n#include <cstdio>")
    # Diagnostic what() is tested separately. Isolate resource ownership in both copied fixtures.
    test = test.replace("        EXPECT_EQ(error.message(), error.what());\n", "")
    context_ready = "        ASSERT_EQ(CGLSetCurrentContext(m_context), kCGLNoError);\n"
    assert test.count(context_ready) == 1
    test = test.replace(context_ready, context_ready + '        printf("GL_CONTEXT renderer=%s version=%s\\n", glGetString(GL_RENDERER), glGetString(GL_VERSION));\n')
    fragment_end = "    EXPECT_EQ(LiveShaders(), 0u);\n}\n\nTEST_F(ShaderFailureTest, LinkRejectionReleasesBothShaders)"
    assert test.count(fragment_end) == 1
    test = test.replace(fragment_end, "    printf(\"RESOURCE_ENDPOINT fragment_attempts=1 live_shaders=%zu\\n\", LiveShaders());\n" + fragment_end)
    repeat_end = "        EXPECT_EQ(LiveShaders(), 0u);\n    }\n}\n\nTEST_F(ShaderFailureTest, RejectedProgramCanCompileAndBindSuccessfullyAfterRetry)"
    assert test.count(repeat_end) == 1
    test = test.replace(repeat_end, "        EXPECT_EQ(LiveShaders(), 0u);\n    }\n    printf(\"RESOURCE_ENDPOINT repeated_attempts=16 live_shaders=%zu\\n\", LiveShaders());\n}\n\nTEST_F(ShaderFailureTest, RejectedProgramCanCompileAndBindSuccessfullyAfterRetry)")
    copied_test.write_text(test)
    binary = dest / "shader-failure-test"
    command = ["clang++", "-std=c++17", "-DGL_SILENCE_DEPRECATION", "-I"+str(ROOT/"third_party/projectm/src/libprojectM"), "-I"+str(ROOT/"third_party/projectm/vendor"), "-I/opt/homebrew/include", str(copied_test), "/opt/homebrew/lib/libgtest.a", "/opt/homebrew/lib/libgtest_main.a", "-framework", "OpenGL", "-o", str(binary)]
    env = os.environ.copy(); (OUT / "tmp").mkdir(exist_ok=True); env["TMPDIR"] = str(OUT / "tmp")
    compile_result = subprocess.run(command, text=True, capture_output=True, env=env)
    (dest / "compile.log").write_text(compile_result.stdout + compile_result.stderr)
    assert compile_result.returncode == 0, compile_result.stderr
    execution = [str(binary), "--gtest_filter="+FILTER]
    run = subprocess.run(execution, text=True, capture_output=True, env=env)
    log = dest / "run.log"; log.write_text(run.stdout + run.stderr)
    assert run.returncode == (1 if state == "red" else 0), run.stdout + run.stderr
    assert "RESOURCE_ENDPOINT" in log.read_text() and "[  SKIPPED ]" not in log.read_text()
    records.append({"state":state,"description":"Fresh CGL rerun; not the unsaved original session run.","rerun_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"host":platform.platform(),"gl_context_lines":[line for line in log.read_text().splitlines() if line.startswith("GL_CONTEXT")],"snapshot":str(snapshot.relative_to(ROOT)),"worker_config":{"path":str(worker_path.relative_to(ROOT)),"sha256":digest(worker_path)},"worker_identity":worker["identity"],"copied_sources":[{"original_path":str((src/name).relative_to(ROOT)),"original_sha256":digest(src/name),"copy_path":str((copied_src/name).relative_to(OUT)),"copy_sha256":digest(copied_src/name)} for name in ["Shader.cpp","Shader.hpp"]],"test_original_path":str(test_source.relative_to(ROOT)),"test_original_sha256":digest(test_source),"test_copy_path":str(copied_test.relative_to(OUT)),"test_copy_sha256":digest(copied_test),"test_copy_changes":["Remove what() comparison to isolate allocation lifetime", "Print two measured glIsShader endpoints after existing checks", "Print actual CGL renderer/version identity"],"compile_command":command,"compile_exit_code":compile_result.returncode,"run_command":execution,"run_exit_code":run.returncode,"binary_sha256":digest(binary),"log_path":str(log.relative_to(OUT)),"log_sha256":digest(log)})
    print(state, "exit",run.returncode)
    print("\n".join(line for line in log.read_text().splitlines() if "RESOURCE_ENDPOINT" in line or "[  PASSED  ]" in line or "[  FAILED  ]" in line))
(OUT / "allocation-builds.json").write_text(json.dumps(records, indent=2))
