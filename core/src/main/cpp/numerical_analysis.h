#pragma once

// Opt-in debug analysis ABI. Calls require a current context on the owning GL
// thread. These are isolated sessions, not the app's live JNI engine instance.
extern "C" {
__attribute__((visibility("default"))) void* projectmtv_analysis_create(
    int width, int height, int fps, const char* textures, unsigned int seed);
__attribute__((visibility("default"))) int projectmtv_analysis_load(void*, const char* preset);
__attribute__((visibility("default"))) const char* projectmtv_analysis_error(void*);
__attribute__((visibility("default"))) void projectmtv_analysis_audio(void*, const float*, unsigned int count);
__attribute__((visibility("default"))) void projectmtv_analysis_render(void*, unsigned int framebuffer);
__attribute__((visibility("default"))) void projectmtv_analysis_destroy(void*);
}
