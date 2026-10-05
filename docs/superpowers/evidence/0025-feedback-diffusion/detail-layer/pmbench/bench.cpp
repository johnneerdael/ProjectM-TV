// Offscreen projectM frame-time benchmark: EGL pbuffer + an RGBA8 FBO at the render size, one preset,
// fixed lab clock and seed, real PCM. Reports GPU+CPU time per frame (glFinish after each frame).
#include <EGL/egl.h>
#include <GLES3/gl3.h>
#include "analysis_hooks.hpp"
#include "ProjectM.hpp"
#include "Audio/AudioConstants.hpp"
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef PMBENCH_UPSTREAM
namespace libprojectM { extern unsigned int lab_target_fbo; }
#endif
class Bench : public libprojectM::ProjectM {
public:
    mutable std::string failure;
    void PresetSwitchFailedEvent(const std::string& f, const std::string& r) const override { failure = f + ": " + r; }
};
int main(int argc, char** argv) {
    if (argc < 9) { fprintf(stderr, "usage: pmbench preset textures pcm w h refw refh frames [warmup]\n"); return 2; }
    std::string preset = argv[1], textures = argv[2], pcmPath = argv[3];
    int w = atoi(argv[4]), h = atoi(argv[5]), rw = atoi(argv[6]), rh = atoi(argv[7]), frames = atoi(argv[8]);
    int warmup = argc > 9 ? atoi(argv[9]) : 120;
    EGLDisplay d = eglGetDisplay(EGL_DEFAULT_DISPLAY); eglInitialize(d, nullptr, nullptr);
    const EGLint ca[] = {EGL_RENDERABLE_TYPE, 0x40 /*ES3*/, EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_ALPHA_SIZE, 8, EGL_NONE};
    EGLConfig cfg; EGLint n = 0; eglChooseConfig(d, ca, &cfg, 1, &n);
    const EGLint sa[] = {EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE};
    EGLSurface s = eglCreatePbufferSurface(d, cfg, sa);
    const EGLint xa[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
    EGLContext c = eglCreateContext(d, cfg, EGL_NO_CONTEXT, xa);
    if (!eglMakeCurrent(d, s, s, c)) { fprintf(stderr, "no EGL context\n"); return 1; }
    GLuint fbo, tex; glGenFramebuffers(1, &fbo); glGenTextures(1, &tex); glBindTexture(GL_TEXTURE_2D, tex);
    glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, w, h); glBindFramebuffer(GL_FRAMEBUFFER, fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);
    std::ifstream audio(pcmPath, std::ios::binary);
    if (!audio) { fprintf(stderr, "no pcm\n"); return 1; }
    const int fps = 60; const size_t block = 44100 / fps;
    Bench e; e.SetTexturePaths({textures}); e.SetWindowSize(w, h); e.SetMeshSize(48, 32);
#ifndef PMBENCH_UPSTREAM
    e.SetLineReferenceSize(rw, rh);
#else
    (void)rw; (void)rh;
#endif
    e.SetTargetFramesPerSecond(fps); e.SetPresetLocked(true); e.SetHardCutEnabled(false); e.SetEasterEgg(0);
    e.LoadPresetFile(preset, false);
    if (!e.failure.empty()) { fprintf(stderr, "load failed: %s\n", e.failure.c_str()); return 1; }
    std::vector<float> pcm(block); std::vector<double> ms;
    for (int f = 0; f < warmup + frames; ++f) {
        audio.read(reinterpret_cast<char*>(pcm.data()), pcm.size() * sizeof(float));
        if (!audio) { audio.clear(); audio.seekg(0); audio.read(reinterpret_cast<char*>(pcm.data()), pcm.size() * sizeof(float)); }
        auto count = std::min<size_t>(pcm.size(), libprojectM::Audio::AudioBufferSamples);
        e.PCM().Add(pcm.data() + pcm.size() - count, 1, count);
        lab::clock_seconds = static_cast<double>(f + 1) / fps;
        auto t0 = std::chrono::steady_clock::now();
#ifdef PMBENCH_UPSTREAM
        libprojectM::lab_target_fbo = fbo; e.RenderFrame();
#else
        e.RenderFrame(fbo);
#endif
        glFinish();
        auto t1 = std::chrono::steady_clock::now();
        if (f >= warmup) ms.push_back(std::chrono::duration<double, std::milli>(t1 - t0).count());
    }
    std::vector<double> sorted = ms; std::sort(sorted.begin(), sorted.end());
    double sum = 0; for (double v : ms) sum += v;
    printf("mean %.2f ms (%.1f fps)  median %.2f  p90 %.2f  max %.2f  glerr 0x%x\n", sum / ms.size(), 1000.0 * ms.size() / sum,
           sorted[sorted.size() / 2], sorted[sorted.size() * 9 / 10], sorted.back(), glGetError());
    return 0;
}
