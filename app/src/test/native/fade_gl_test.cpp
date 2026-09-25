// Runs app/src/main/cpp/snapshot_fade.cpp against a real OpenGL ES 3 driver (Mesa llvmpipe on a
// headless EGL pbuffer). Checks the captured frame, the fade curve, the end of the fade, and that
// the GL state projectM relies on is restored. Run via run_native_tests.sh.
#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <GLES3/gl3.h>

#include <cstdarg>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "snapshot_fade.h"

extern "C" int __android_log_print(int, const char*, const char* fmt, ...) {
    va_list ap;
    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    fputc('\n', stderr);
    va_end(ap);
    return 0;
}

#define CHECK(c) do { if (!(c)) { fprintf(stderr, "FAIL %s:%d %s\n", __FILE__, __LINE__, #c); exit(1); } else printf("  ok: %s\n", #c); } while (0)

static const int kSize = 64;

static void Fill(float r, float g, float b) {
    glClearColor(r, g, b, 1.f);
    glClear(GL_COLOR_BUFFER_BIT);
}

static void Pixel(int x, int y, unsigned char out[4]) {
    glReadPixels(x, y, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, out);
}

static bool Near(int a, int b) { return a >= b - 6 && a <= b + 6; }

static bool InitEgl() {
    auto getPlatformDisplay =
        reinterpret_cast<PFNEGLGETPLATFORMDISPLAYEXTPROC>(eglGetProcAddress("eglGetPlatformDisplayEXT"));
    EGLDisplay display = getPlatformDisplay
        ? getPlatformDisplay(EGL_PLATFORM_SURFACELESS_MESA, EGL_DEFAULT_DISPLAY, nullptr)
        : eglGetDisplay(EGL_DEFAULT_DISPLAY);
    if (display == EGL_NO_DISPLAY || !eglInitialize(display, nullptr, nullptr)) return false;
    const EGLint configAttribs[] = {EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT,
                                    EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_NONE};
    EGLConfig config;
    EGLint count = 0;
    if (!eglChooseConfig(display, configAttribs, &config, 1, &count) || count == 0) return false;
    const EGLint surfaceAttribs[] = {EGL_WIDTH, kSize, EGL_HEIGHT, kSize, EGL_NONE};
    EGLSurface surface = eglCreatePbufferSurface(display, config, surfaceAttribs);
    eglBindAPI(EGL_OPENGL_ES_API);
    const EGLint contextAttribs[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
    EGLContext context = eglCreateContext(display, config, EGL_NO_CONTEXT, contextAttribs);
    return surface != EGL_NO_SURFACE && context != EGL_NO_CONTEXT &&
           eglMakeCurrent(display, surface, surface, context);
}

int main() {
    setvbuf(stdout, nullptr, _IONBF, 0);
    if (!InitEgl()) {
        fprintf(stderr, "No EGL/GLES3 driver available\n");
        return 2;
    }
    printf("GL: %s | %s\n", glGetString(GL_VERSION), glGetString(GL_RENDERER));
    glViewport(0, 0, kSize, kSize);
    unsigned char px[4];
    SnapshotFade fade;

    printf("capture copies the frame just rendered\n");
    Fill(1, 0, 0);
    CHECK(fade.Capture(kSize, kSize));
    CHECK(!fade.Active());

    printf("state projectM left behind is restored after a fade frame\n");
    GLuint sampler = 0, texture = 0;
    glGenSamplers(1, &sampler);
    glGenTextures(1, &texture);
    glActiveTexture(GL_TEXTURE3);
    glBindSampler(0, sampler);
    glActiveTexture(GL_TEXTURE0);
    glBindTexture(GL_TEXTURE_2D, texture);
    glActiveTexture(GL_TEXTURE3);
    glEnable(GL_SCISSOR_TEST);
    glScissor(0, 0, kSize, kSize);
    glBlendFunc(GL_ONE, GL_ONE);
    glDisable(GL_BLEND);

    fade.Start(10.0, 1.0);
    CHECK(fade.Active());
    Fill(0, 1, 0);
    fade.Draw(10.0);
    Pixel(kSize / 2, kSize / 2, px);
    CHECK(Near(px[0], 255) && Near(px[1], 0));  // start: only the outgoing frame is visible

    GLint value = 0;
    CHECK(!glIsEnabled(GL_BLEND));
    CHECK(glIsEnabled(GL_SCISSOR_TEST));
    glGetIntegerv(GL_BLEND_SRC_RGB, &value); CHECK(value == GL_ONE);
    glGetIntegerv(GL_BLEND_DST_ALPHA, &value); CHECK(value == GL_ONE);
    glGetIntegerv(GL_ACTIVE_TEXTURE, &value); CHECK(value == GL_TEXTURE3);
    glGetIntegerv(GL_CURRENT_PROGRAM, &value); CHECK(value == 0);
    glGetIntegerv(GL_VERTEX_ARRAY_BINDING, &value); CHECK(value == 0);
    glActiveTexture(GL_TEXTURE0);
    glGetIntegerv(GL_TEXTURE_BINDING_2D, &value); CHECK(value == static_cast<GLint>(texture));
    glGetIntegerv(GL_SAMPLER_BINDING, &value); CHECK(value == static_cast<GLint>(sampler));
    glDisable(GL_SCISSOR_TEST);
    CHECK(glGetError() == GL_NO_ERROR);

    printf("halfway: both frames mixed\n");
    Fill(0, 1, 0);
    fade.Draw(10.5);
    Pixel(kSize / 2, kSize / 2, px);
    CHECK(Near(px[0], 128) && Near(px[1], 128));

    printf("end: the fade stops itself and leaves the new preset untouched\n");
    Fill(0, 1, 0);
    fade.Draw(11.0);
    CHECK(!fade.Active());
    Pixel(kSize / 2, kSize / 2, px);
    CHECK(Near(px[0], 0) && Near(px[1], 255));

    printf("stop drops a capture that was never used\n");
    Fill(0, 0, 1);
    CHECK(fade.Capture(kSize, kSize));
    fade.Stop();
    fade.Start(0.0, 1.0);
    CHECK(!fade.Active());  // no snapshot: nothing to fade

    fade.Release();
    CHECK(glGetError() == GL_NO_ERROR);
    printf("ALL GL TESTS PASSED\n");
    return 0;
}
