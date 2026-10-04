// Exercise the real JNI render-size and presentation paths with the engine-test fakes.
#define main engine_harness_main
#include "engine_test.cpp"
#undef main

int main() {
    g_engine.pm = projectm_create();
    g_engine.width = 3840;
    g_engine.height = 2160;
    ApplyRenderScale(1.f);
#ifdef PROJECTMTV_RENDERING_POLICY_CAPPED
    assert(g_windowW == 2364 && g_windowH == 1330);
    RenderPresetFrame();
    assert(g_blitSrcW == 2364 && g_blitSrcH == 1330);
    assert(g_blitDstW == 3840 && g_blitDstH == 2160);
    ReleaseScaledTarget(true);
    g_framebufferStatus = 0;
    const int framesBeforeFailure = g_fboFrames;
    RenderPresetFrame();
    assert(g_windowH == 1330);
    assert(g_fboFrames == framesBeforeFailure);
    g_framebufferStatus = GL_FRAMEBUFFER_COMPLETE;
#else
    assert(g_windowW == 3840 && g_windowH == 2160);
    RenderPresetFrame();
    assert(g_blits == 0);
    ApplyRenderScale(0.5f);
    g_framebufferStatus = 0;
    RenderPresetFrame();
    assert(g_windowW == 3840 && g_windowH == 2160);
    g_framebufferStatus = GL_FRAMEBUFFER_COMPLETE;
#endif
    ApplyRenderScale(0.5f);
    assert(g_windowW == 1920 && g_windowH == 1080);
    g_engine.width = 1920;
    g_engine.height = 1080;
    ApplyRenderScale(1.f);
    assert(g_windowW == 1920 && g_windowH == 1080);
    projectm_destroy(g_engine.pm);
    g_engine.pm = nullptr;
    puts("Render policy JNI sizing/presentation checks passed");
}
