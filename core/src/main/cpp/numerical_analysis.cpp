#include "numerical_analysis.h"
#include <projectM-4/projectM.h>
#include <algorithm>
#include <cstdlib>
#include <memory>
#include <string>

namespace {
struct Session {
    projectm_handle engine = nullptr;
    std::string error;
    ~Session() { if (engine) projectm_destroy(engine); }
};

void Failed(const char*, const char* message, void* context) {
    static_cast<Session*>(context)->error = message ? message : "Preset load failed";
}
}

void* projectmtv_analysis_create(int width, int height, int fps,
                                const char* textures, unsigned int seed) {
    if (width < 1 || height < 1 || width > 4096 || height > 4096 ||
        (fps != 30 && fps != 60) || !textures || !*textures) return nullptr;
    std::srand(seed);
    auto session = std::make_unique<Session>();
    session->engine = projectm_create();
    if (!session->engine) return nullptr;
    projectm_set_beat_sensitivity(session->engine, 1.0f);
    // Keep the authoring reference used by ProjectMJNI::onSurfaceCreated.
    projectm_opengl_set_line_reference_size(session->engine, 1024, 768);
    projectm_set_window_size(session->engine, width, height);
    projectm_set_mesh_size(session->engine, 48, 32);
    projectm_set_fps(session->engine, fps);
    projectm_set_preset_locked(session->engine, true);
    projectm_set_hard_cut_enabled(session->engine, false);
    projectm_set_easter_egg(session->engine, 0);
    const char* paths[] = {textures};
    projectm_set_texture_search_paths(session->engine, paths, 1);
    projectm_set_preset_switch_failed_event_callback(session->engine, Failed, session.get());
    return session.release();
}

int projectmtv_analysis_load(void* handle, const char* preset) {
    if (!handle || !preset || !*preset) return 0;
    auto& session = *static_cast<Session*>(handle);
    session.error.clear();
    projectm_load_preset_file(session.engine, preset, false);
    return session.error.empty() ? 1 : 0;
}

const char* projectmtv_analysis_error(void* handle) {
    return handle ? static_cast<Session*>(handle)->error.c_str() : "No analysis session";
}

void projectmtv_analysis_audio(void* handle, const float* pcm, unsigned int count) {
    if (!handle || !pcm || !count) return;
    unsigned int maximum = projectm_pcm_get_max_samples();
    unsigned int used = std::min(count, maximum);
    projectm_pcm_add_float(static_cast<Session*>(handle)->engine, pcm + count - used, used, PROJECTM_MONO);
}

void projectmtv_analysis_render(void* handle, unsigned int framebuffer) {
    if (handle) projectm_opengl_render_frame_fbo(static_cast<Session*>(handle)->engine, framebuffer);
}

void projectmtv_analysis_destroy(void* handle) {
    delete static_cast<Session*>(handle);
}
