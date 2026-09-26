#include "preset_prewarm.h"

#include <EGL/egl.h>
#include <EGL/eglext.h>
#include <android/log.h>
#include <sys/resource.h>
#include <unistd.h>

#include <chrono>

#include "projectM-4/projectM.h"

#define LOG_TAG "projectM-Native"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)

namespace {

// A fresh instance after this many presets releases the textures the old one loaded.
constexpr int kLoadsPerInstance = 20;

double NowMs() {
    using namespace std::chrono;
    return duration<double, std::milli>(steady_clock::now().time_since_epoch()).count();
}

// An OpenGL ES 3 context on a tiny off-screen surface, current on the calling thread.
class PbufferContext {
public:
    bool Create() {
        display_ = eglGetDisplay(EGL_DEFAULT_DISPLAY);
        if (display_ == EGL_NO_DISPLAY || !eglInitialize(display_, nullptr, nullptr)) return false;
        const EGLint configAttribs[] = {EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT_KHR,
                                        EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
                                        EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8,
                                        EGL_NONE};
        EGLConfig config = nullptr;
        EGLint count = 0;
        if (!eglChooseConfig(display_, configAttribs, &config, 1, &count) || count < 1) return false;
        const EGLint contextAttribs[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
        context_ = eglCreateContext(display_, config, EGL_NO_CONTEXT, contextAttribs);
        const EGLint surfaceAttribs[] = {EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE};
        surface_ = eglCreatePbufferSurface(display_, config, surfaceAttribs);
        return context_ != EGL_NO_CONTEXT && surface_ != EGL_NO_SURFACE &&
               eglMakeCurrent(display_, surface_, surface_, context_);
    }

    ~PbufferContext() {
        if (display_ == EGL_NO_DISPLAY) return;
        eglMakeCurrent(display_, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
        if (surface_ != EGL_NO_SURFACE) eglDestroySurface(display_, surface_);
        if (context_ != EGL_NO_CONTEXT) eglDestroyContext(display_, context_);
        eglReleaseThread();
    }

private:
    EGLDisplay display_ = EGL_NO_DISPLAY;
    EGLContext context_ = EGL_NO_CONTEXT;
    EGLSurface surface_ = EGL_NO_SURFACE;
};

}  // namespace

void PresetPrewarmer::Start(const std::string& textureDir, Reader reader) {
    if (thread_.joinable()) return;
    stop_ = false;
    reader_ = std::move(reader);
    thread_ = std::thread(&PresetPrewarmer::Run, this, textureDir);
}

void PresetPrewarmer::Stop() {
    {
        std::lock_guard<std::mutex> lock(mutex_);
        stop_ = true;
    }
    cv_.notify_all();
    if (thread_.joinable()) thread_.join();
    pending_.clear();
    last_.clear();
}

void PresetPrewarmer::Request(const std::string& name) {
    if (name.empty()) return;
    std::lock_guard<std::mutex> lock(mutex_);
    if (name == last_ || name == pending_) return;
    pending_ = name;
    cv_.notify_one();
}

void PresetPrewarmer::Run(std::string textureDir) {
    // Below the render thread: compiling must not cost it frames.
    setpriority(PRIO_PROCESS, gettid(), 10);
    PbufferContext context;
    if (!context.Create()) {
        LOGW("PREWARM unavailable: no off-screen OpenGL ES 3 context (error 0x%x)", eglGetError());
        return;
    }
    projectm_handle pm = nullptr;
    int loads = 0;
    for (;;) {
        std::string name;
        {
            std::unique_lock<std::mutex> lock(mutex_);
            cv_.wait(lock, [this] { return stop_ || !pending_.empty(); });
            if (stop_) break;
            name.swap(pending_);
            last_ = name;
        }
        std::string data = reader_(name);
        if (data.empty()) continue;
        if (pm && loads >= kLoadsPerInstance) {
            projectm_destroy(pm);
            pm = nullptr;
        }
        if (!pm) {
            pm = projectm_create();
            if (!pm) {
                LOGW("PREWARM unavailable: projectm_create failed");
                break;
            }
            loads = 0;
            const char* paths[] = {textureDir.c_str()};
            if (!textureDir.empty()) projectm_set_texture_search_paths(pm, paths, 1);
            projectm_set_window_size(pm, 64, 36);
        }
        double start = NowMs();
        projectm_load_preset_data(pm, data.c_str(), false);
        ++loads;
        uint32_t hits = 0, misses = 0;
        projectm_opengl_program_cache_stats(&hits, &misses);
        LOGI("PREWARM preset='%s' ms=%.0f cache_hits=%u cache_misses=%u", name.c_str(), NowMs() - start,
             hits, misses);
    }
    if (pm) projectm_destroy(pm);
}
