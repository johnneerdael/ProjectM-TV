# Core Numerical Backend Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans for inline execution.
> This is the backend subplan of the approved full-corpus audience-review design.

**Goal:** Execute numerical analysis through the patched ProjectM-TV core library.

**Architecture:** Add an opt-in exported analysis ABI to the debug core AAR. The
Android EGL harness owns a context, creates one isolated engine per preset, feeds
PCM and reads numerical frame fields. Identify the core AAR, native library,
patch series, input fixture and renderer in every run. Source interpretation and
AI video diagnosis remain available for learning and explaining discrepancies.

**Tech stack:** Android Gradle, C++17, projectM C API, EGL/GLES, Python orchestration.

## Task 1: opt-in core ABI

Files: `core/build.gradle`, `core/src/main/cpp/CMakeLists.txt`,
`core/src/main/cpp/numerical_analysis.cpp`,
`core/src/main/cpp/numerical_analysis.h`.

- [ ] Confirm ordinary `core-debug.aar` does not export analysis functions.
- [ ] Pass `-DPROJECTMTV_ANALYSIS_API=ON` only when Gradle receives
  `-PprojectmAnalysis=true`; CMake rejects enabling it outside Debug builds.
- [ ] Export a C ABI with these exact entry points:

```cpp
void* projectmtv_analysis_create(int width, int height, int fps,
                                const char* textures, unsigned int seed);
int projectmtv_analysis_load(void* session, const char* preset);
const char* projectmtv_analysis_error(void* session);
void projectmtv_analysis_audio(void* session, const float* pcm, unsigned int count);
void projectmtv_analysis_render(void* session, unsigned int framebuffer);
void projectmtv_analysis_destroy(void* session);
```

Create sets beat sensitivity 1, line reference 1024×768, mesh 48×32, target FPS,
preset lock and disabled automatic beat cuts. Texture search paths use the
supplied real directory. Load hard-cuts and retains the native failure callback
reason. Audio respects projectM's maximum mono sample count. Calls require the
owning GL context/thread. Invalid dimensions, missing paths or unsupported FPS
return an error instead of substituting a preset. Destroy releases the engine.

- [ ] Build: `./gradlew :core:assembleDebug -PprojectmAnalysis=true --console=plain`.
- [ ] Verify exported symbols with the configured NDK `llvm-nm -D`.
- [ ] Verify normal Debug and Release builds omit the ABI. Run existing core tests.
- [ ] Commit and push the isolated interface checkpoint.

## Task 2: deterministic harness and throughput benchmark

Files: create `tools/milk-analyzer/core_backend_worker.cpp` and
`tools/milk-analyzer/core_backend.py`; reuse the existing independent EGL pbuffer
probe setup and descriptor stream.

- [ ] Load the actual analysis-enabled `libprojectmtv.so` from `:core`.
- [ ] Test deterministic frame time with a preset whose output encodes `time`;
  do not silently use accelerated wall-clock time as a 30 FPS simulation.
- [ ] Test a constant-color preset, a custom waveform and a preset with a shader
  domain unsupported by the independent interpreter. Preserve load/GL failures.
- [ ] Benchmark a pinned representative batch, including recent corrected cases.
  Record elapsed time, renderer and library hashes; derive the corpus ETA from it.
- [ ] Commit and push the verified harness before starting the long run.

## Downstream completion gates

The full-corpus runner must resume from per-preset results, diagnose every
unscored entry, and verify finite scores against the exact corpus inventory.
Generated overlapping indexes and score metadata then feed the ProjectM-TV
All/Chill/Normal/Party debug build. Those stages follow the backend benchmark;
this subplan does not claim their completion or independent audience accuracy.
