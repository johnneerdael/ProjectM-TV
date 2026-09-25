// projectM Android TV - native engine
//
// Threading model
// ---------------
// * GL thread   : everything that touches the projectM handle (create, render, load presets,
//                 settings). projectM compiles shaders while loading presets, so preset switches
//                 MUST happen on the thread that owns the EGL context.
// * Any thread  : commands (next/previous/random), settings and audio are written into atomics /
//                 mutex-protected buffers and picked up by the GL thread at the start of the next
//                 frame. Java never needs to queueEvent() for correctness.
// * Worker      : a single background thread indexes the preset list from the APK assets and
//                 prefetches (reads + decompresses) the next preset so the GL thread only has to
//                 parse/compile it.
//
// Presets are read straight from the APK via AAssetManager, so nothing is extracted to disk.

#include <jni.h>
#include <android/asset_manager.h>
#include <android/asset_manager_jni.h>
#include <android/log.h>
#include <GLES2/gl2.h>
#include <sys/system_properties.h>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <condition_variable>
#include <cstdio>
#include <cstring>
#include <deque>
#include <functional>
#include <mutex>
#include <random>
#include <string>
#include <thread>
#include <unordered_set>
#include <utility>
#include <vector>

#include "projectM-4/projectM.h"

#define LOG_TAG "projectM-Native"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, LOG_TAG, __VA_ARGS__)
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, LOG_TAG, __VA_ARGS__)

namespace {

constexpr const char* kPresetDir = "presets";
constexpr size_t kMaxHistory = 128;
constexpr int kMaxLoadAttemptsPerFrame = 4;

double NowSeconds() {
    using namespace std::chrono;
    return duration<double>(steady_clock::now().time_since_epoch()).count();
}

bool EndsWithMilk(const char* name) {
    size_t len = strlen(name);
    if (len < 5) return false;
    const char* ext = name + len - 5;
    return strncasecmp(ext, ".milk", 5) == 0;
}

// ------------------------------------------------------------------------------------------------
// Preset library: index, shuffle order, history, skip list and background prefetch.
// All public methods are thread-safe.
// ------------------------------------------------------------------------------------------------
class PresetLibrary {
public:
    void Start(AAssetManager* assets, std::string skipFilePath) {
        bool expected = false;
        if (!started_.compare_exchange_strong(expected, true)) return;
        assets_ = assets;
        skipFilePath_ = std::move(skipFilePath);
        std::thread(&PresetLibrary::WorkerLoop, this).detach();
    }

    bool Ready() const { return ready_.load(std::memory_order_acquire); }

    int ActiveCount() {
        std::lock_guard<std::mutex> lock(mutex_);
        return static_cast<int>(order_.size() - std::min(order_.size(), skippedInOrder_));
    }

    int SkippedCount() {
        std::lock_guard<std::mutex> lock(mutex_);
        return static_cast<int>(skipped_.size());
    }

    // Advances the shuffled cursor and returns the next playable preset ("" if none).
    std::string Next() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::string name = PeekNextLocked(true);
        RequestPrefetchLocked();
        return name;
    }

    std::string Random(const std::string& avoid) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (order_.empty()) return {};
        std::uniform_int_distribution<size_t> dist(0, order_.size() - 1);
        for (int i = 0; i < 32; ++i) {
            const std::string& candidate = order_[dist(rng_)];
            if (candidate != avoid && !skipped_.count(candidate)) return candidate;
        }
        return PeekNextLocked(true);
    }

    // Returns the preset shown before the current one ("" if there is no history).
    std::string Previous() {
        std::lock_guard<std::mutex> lock(mutex_);
        while (history_.size() >= 2) {
            history_.pop_back();  // current
            std::string candidate = history_.back();
            if (!skipped_.count(candidate)) {
                history_.pop_back();  // will be pushed again when it is shown
                return candidate;
            }
        }
        return {};
    }

    void RecordShown(const std::string& name) {
        std::lock_guard<std::mutex> lock(mutex_);
        history_.push_back(name);
        if (history_.size() > kMaxHistory) history_.pop_front();
    }

    void MarkSkipped(const std::string& name, const char* reason) {
        if (name.empty()) return;
        std::lock_guard<std::mutex> lock(mutex_);
        if (!skipped_.insert(name).second) return;
        ++skippedInOrder_;
        LOGW("Skipping preset '%s' permanently: %s", name.c_str(), reason);
        FILE* f = fopen(skipFilePath_.c_str(), "a");
        if (f) {
            fprintf(f, "%s\n", name.c_str());
            fclose(f);
        }
    }

    void ResetSkipped() {
        std::lock_guard<std::mutex> lock(mutex_);
        skipped_.clear();
        skippedInOrder_ = 0;
        FILE* f = fopen(skipFilePath_.c_str(), "w");
        if (f) fclose(f);
        LOGI("Skip list cleared");
    }

    // Returns the preset file contents, using the prefetched copy when available.
    std::string Load(const std::string& name) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (prefetchedName_ == name) {
                prefetchedName_.clear();
                return std::move(prefetchedData_);
            }
        }
        return ReadAsset(name);
    }

private:
    std::string ReadAsset(const std::string& name) const {
        std::string path = std::string(kPresetDir) + "/" + name;
        AAsset* asset = AAssetManager_open(assets_, path.c_str(), AASSET_MODE_BUFFER);
        if (!asset) {
            LOGE("Unable to open asset %s", path.c_str());
            return {};
        }
        std::string data;
        const void* buffer = AAsset_getBuffer(asset);
        off_t length = AAsset_getLength(asset);
        if (buffer && length > 0) data.assign(static_cast<const char*>(buffer), length);
        AAsset_close(asset);
        return data;
    }

    std::string PeekNextLocked(bool advance) {
        if (order_.empty()) return {};
        size_t cursor = cursor_;
        for (size_t i = 0; i < order_.size(); ++i) {
            if (cursor >= order_.size()) {
                cursor = 0;
                if (advance) std::shuffle(order_.begin(), order_.end(), rng_);
            }
            const std::string& candidate = order_[cursor++];
            if (!skipped_.count(candidate)) {
                if (advance) cursor_ = cursor;
                return candidate;
            }
        }
        return {};
    }

    void RequestPrefetchLocked() {
        prefetchWanted_ = true;
        cv_.notify_one();
    }

    void WorkerLoop() {
        BuildIndex();
        std::unique_lock<std::mutex> lock(mutex_);
        for (;;) {
            cv_.wait(lock, [this] { return prefetchWanted_; });
            prefetchWanted_ = false;
            std::string name = PeekNextLocked(false);
            if (name.empty() || name == prefetchedName_) continue;
            lock.unlock();
            std::string data = ReadAsset(name);
            lock.lock();
            prefetchedName_ = name;
            prefetchedData_ = std::move(data);
        }
    }

    void BuildIndex() {
        double start = NowSeconds();
        std::vector<std::string> names;
        names.reserve(10000);
        AAssetDir* dir = AAssetManager_openDir(assets_, kPresetDir);
        if (dir) {
            while (const char* file = AAssetDir_getNextFileName(dir)) {
                if (EndsWithMilk(file)) names.emplace_back(file);
            }
            AAssetDir_close(dir);
        }

        std::unordered_set<std::string> skipped;
        if (FILE* f = fopen(skipFilePath_.c_str(), "r")) {
            char line[1024];
            while (fgets(line, sizeof(line), f)) {
                size_t len = strcspn(line, "\r\n");
                line[len] = '\0';
                if (len > 0) skipped.insert(line);
            }
            fclose(f);
        }

        std::lock_guard<std::mutex> lock(mutex_);
        rng_.seed(std::random_device{}());
        std::shuffle(names.begin(), names.end(), rng_);
        order_ = std::move(names);
        skipped_ = std::move(skipped);
        skippedInOrder_ = 0;
        for (const auto& n : order_) skippedInOrder_ += skipped_.count(n);
        cursor_ = 0;
        ready_.store(true, std::memory_order_release);
        prefetchWanted_ = true;  // warm up the first preset
        LOGI("Indexed %zu presets (%zu skipped) in %.0f ms", order_.size(), skippedInOrder_,
             (NowSeconds() - start) * 1000.0);
    }

    std::atomic<bool> started_{false};
    std::atomic<bool> ready_{false};
    AAssetManager* assets_ = nullptr;
    std::string skipFilePath_;

    std::mutex mutex_;
    std::condition_variable cv_;
    std::mt19937 rng_;
    std::vector<std::string> order_;
    size_t cursor_ = 0;
    std::deque<std::string> history_;
    std::unordered_set<std::string> skipped_;
    size_t skippedInOrder_ = 0;
    bool prefetchWanted_ = false;
    std::string prefetchedName_;
    std::string prefetchedData_;
};

// ------------------------------------------------------------------------------------------------
// Detects presets that render (almost) nothing while music is playing.
// Samples a sparse grid of rows/columns of the final frame a few times after the transition.
// ------------------------------------------------------------------------------------------------
class BlackFrameDetector {
public:
    void Arm(double now, double settleSeconds) {
        active_ = true;
        nextSampleAt_ = now + settleSeconds;
        deadline_ = nextSampleAt_ + kEvaluationWindow;
        blackSamples_ = 0;
    }

    void Disarm() { active_ = false; }

    // Returns true when the current preset has been judged as rendering nothing.
    bool Update(double now, int width, int height, bool audioPresent) {
        if (!active_ || now < nextSampleAt_) return false;
        if (now > deadline_) {
            active_ = false;
            return false;
        }
        nextSampleAt_ = now + kSampleInterval;
        if (!audioPresent) return false;  // silence legitimately makes many presets dark

        if (!FrameIsBlack(width, height)) {
            active_ = false;  // preset produces output, stop checking
            return false;
        }
        if (++blackSamples_ >= kRequiredBlackSamples) {
            active_ = false;
            return true;
        }
        return false;
    }

private:
    static constexpr double kSampleInterval = 0.5;
    static constexpr double kEvaluationWindow = 20.0;
    static constexpr int kRequiredBlackSamples = 5;
    static constexpr int kLines = 5;
    static constexpr int kPixelStep = 4;
    static constexpr uint8_t kMaxBlackChannel = 20;  // ~8% brightness

    bool FrameIsBlack(int width, int height) {
        if (width <= 0 || height <= 0) return false;
        buffer_.resize(static_cast<size_t>(std::max(width, height)) * 4);
        for (int i = 1; i <= kLines; ++i) {
            int y = height * i / (kLines + 1);
            glReadPixels(0, y, width, 1, GL_RGBA, GL_UNSIGNED_BYTE, buffer_.data());
            if (!SpanIsBlack(width)) return false;
            int x = width * i / (kLines + 1);
            glReadPixels(x, 0, 1, height, GL_RGBA, GL_UNSIGNED_BYTE, buffer_.data());
            if (!SpanIsBlack(height)) return false;
        }
        return true;
    }

    bool SpanIsBlack(int pixels) const {
        for (int p = 0; p < pixels; p += kPixelStep) {
            const uint8_t* px = &buffer_[static_cast<size_t>(p) * 4];
            if (px[0] > kMaxBlackChannel || px[1] > kMaxBlackChannel || px[2] > kMaxBlackChannel) {
                return false;
            }
        }
        return true;
    }

    bool active_ = false;
    double nextSampleAt_ = 0;
    double deadline_ = 0;
    int blackSamples_ = 0;
    std::vector<uint8_t> buffer_;
};

// ------------------------------------------------------------------------------------------------
// Cross-thread inputs (written from UI / audio threads, consumed on the GL thread).
// ------------------------------------------------------------------------------------------------
enum Command : int { kNone = 0, kNext, kPrevious, kRandom, kSkipCurrent };

struct Inputs {
    std::atomic<int> command{kNone};
    std::atomic<bool> commandHardCut{true};
    std::atomic<bool> forceHardCut{false};  // next automatic switch must be a hard cut
    std::atomic<bool> blankDetection{true};

    std::atomic<int> presetDuration{30};
    std::atomic<int> softCutDuration{7};
    std::atomic<bool> autoChange{true};
    std::atomic<int> meshWidth{48};
    std::atomic<int> meshHeight{32};
    std::atomic<bool> settingsDirty{true};

    std::mutex pcmMutex;
    std::vector<uint8_t> pcm;
    std::atomic<float> audioLevel{0.f};
    std::atomic<double> audioLevelTime{0.0};
};

// Published state, read from any thread.
struct Published {
    std::mutex mutex;
    std::string currentPreset;
    std::atomic<int> changeCounter{0};
};

// GL-thread-only state.
struct Engine {
    projectm_handle pm = nullptr;
    int width = 0;
    int height = 0;
    std::string current;         // preset currently shown
    std::string loading;         // preset being loaded (for failure attribution)
    bool loadFailed = false;
    bool switchRequested = false;
    bool switchHardCut = false;
    BlackFrameDetector blackDetector;
    std::vector<uint8_t> pcmScratch;
    int framesSinceFps = 0;
    double fpsWindowStart = 0;
    int appliedMeshWidth = 0;
    int appliedMeshHeight = 0;
};

// Intentionally never destroyed: its detached worker thread lives as long as the process.
PresetLibrary& g_library = *new PresetLibrary();
Inputs g_inputs;
Published g_published;
Engine g_engine;
std::mutex g_engineMutex;  // guards g_engine against create/destroy races across Activities
jobject g_assetManagerRef = nullptr;

constexpr float kAudioPresentLevel = 0.02f;  // RMS of normalized 8-bit PCM

bool AudioPresent(double now) {
    return (now - g_inputs.audioLevelTime.load()) < 1.0 && g_inputs.audioLevel.load() > kAudioPresentLevel;
}

void OnSwitchRequested(bool isHardCut, void*) {
    g_engine.switchRequested = true;
    g_engine.switchHardCut = isHardCut;
}

void OnSwitchFailed(const char* filename, const char* message, void*) {
    LOGW("Preset load failed (%s): %s", filename ? filename : "", message ? message : "");
    g_engine.loadFailed = true;
}

void ApplySettings() {
    projectm_handle pm = g_engine.pm;
    projectm_set_preset_duration(pm, g_inputs.presetDuration.load());
    projectm_set_soft_cut_duration(pm, g_inputs.softCutDuration.load());
    projectm_set_preset_locked(pm, !g_inputs.autoChange.load());
    int meshWidth = g_inputs.meshWidth.load();
    int meshHeight = g_inputs.meshHeight.load();
    if (meshWidth != g_engine.appliedMeshWidth || meshHeight != g_engine.appliedMeshHeight) {
        // Only on real changes: a new mesh size rebuilds the per-vertex grid.
        projectm_set_mesh_size(pm, meshWidth, meshHeight);
        g_engine.appliedMeshWidth = meshWidth;
        g_engine.appliedMeshHeight = meshHeight;
    }
}

void Publish(const std::string& name) {
    {
        std::lock_guard<std::mutex> lock(g_published.mutex);
        g_published.currentPreset = name;
    }
    g_published.changeCounter.fetch_add(1);
}

// Loads one preset; returns false if it could not be loaded (and marks it as skipped).
bool LoadPreset(const std::string& name, bool smooth) {
    std::string data = g_library.Load(name);
    if (data.empty()) {
        g_library.MarkSkipped(name, "unreadable or empty");
        return false;
    }
    g_engine.loading = name;
    g_engine.loadFailed = false;
    projectm_load_preset_data(g_engine.pm, data.c_str(), smooth);
    if (g_engine.loadFailed) {
        g_library.MarkSkipped(name, "failed to load/compile");
        g_engine.loadFailed = false;
        return false;
    }
    g_engine.current = name;
    g_library.RecordShown(name);
    Publish(name);
    double settle = (smooth ? g_inputs.softCutDuration.load() : 0) + 2.0;
    g_engine.blackDetector.Arm(NowSeconds(), settle);
    return true;
}

// Switches using the given selector, retrying a few times when presets fail to load.
template <typename Selector>
void SwitchPreset(Selector select, bool smooth) {
    for (int attempt = 0; attempt < kMaxLoadAttemptsPerFrame; ++attempt) {
        std::string name = select();
        if (name.empty()) return;
        if (LoadPreset(name, smooth)) return;
    }
}

// Selector that tries `first` (if non-empty) and falls back to the shuffled order.
std::function<std::string()> FirstThenNext(std::string first) {
    return [first = std::move(first)]() mutable {
        if (!first.empty()) return std::exchange(first, std::string());
        return g_library.Next();
    };
}

void HandleCommands() {
    int command = g_inputs.command.exchange(kNone);
    if (command != kNone) {
        bool smooth = !g_inputs.commandHardCut.load();
        switch (command) {
            case kNext:
                SwitchPreset([] { return g_library.Next(); }, smooth);
                break;
            case kRandom:
                SwitchPreset([] { return g_library.Random(g_engine.current); }, smooth);
                break;
            case kSkipCurrent:
                g_library.MarkSkipped(g_engine.current, "too slow on this device");
                SwitchPreset([] { return g_library.Next(); }, false);
                break;
            case kPrevious: {
                std::string previous = g_library.Previous();
                if (!previous.empty()) SwitchPreset(FirstThenNext(previous), smooth);
                break;
            }
            default:
                break;
        }
        g_engine.switchRequested = false;
        return;
    }
    if (g_engine.switchRequested) {
        g_engine.switchRequested = false;
        bool hardCut = g_engine.switchHardCut || g_inputs.forceHardCut.exchange(false);
        SwitchPreset([] { return g_library.Next(); }, !hardCut);
    }
}

void FeedAudio() {
    {
        std::lock_guard<std::mutex> lock(g_inputs.pcmMutex);
        g_engine.pcmScratch.swap(g_inputs.pcm);
        g_inputs.pcm.clear();
    }
    auto& pcm = g_engine.pcmScratch;
    if (pcm.empty()) return;
    size_t maxSamples = projectm_pcm_get_max_samples();
    size_t offset = pcm.size() > maxSamples ? pcm.size() - maxSamples : 0;
    projectm_pcm_add_uint8(g_engine.pm, pcm.data() + offset,
                           static_cast<unsigned int>(pcm.size() - offset), PROJECTM_MONO);
    pcm.clear();
}

void UpdateFps(double now) {
    ++g_engine.framesSinceFps;
    double elapsed = now - g_engine.fpsWindowStart;
    if (elapsed >= 1.0) {
        projectm_set_fps(g_engine.pm, static_cast<int32_t>(g_engine.framesSinceFps / elapsed + 0.5));
        g_engine.framesSinceFps = 0;
        g_engine.fpsWindowStart = now;
    }
}

void DestroyEngineLocked() {
    if (g_engine.pm) {
        projectm_destroy(g_engine.pm);
        g_engine.pm = nullptr;
    }
    g_engine.width = g_engine.height = 0;
    g_engine.appliedMeshWidth = g_engine.appliedMeshHeight = 0;
    g_engine.current.clear();  // the next instance resumes from g_published.currentPreset
    g_engine.switchRequested = false;
    g_engine.blackDetector.Disarm();
}

}  // namespace

#define JNI_FN(name) Java_com_example_projectm_visualizer_ProjectMJNI_##name

extern "C" {

JNIEXPORT void JNICALL JNI_FN(init)(JNIEnv* env, jclass, jobject assetManager, jstring skipFile) {
    if (!g_assetManagerRef) g_assetManagerRef = env->NewGlobalRef(assetManager);
    AAssetManager* assets = AAssetManager_fromJava(env, g_assetManagerRef);
    const char* path = env->GetStringUTFChars(skipFile, nullptr);
    g_library.Start(assets, path);
    env->ReleaseStringUTFChars(skipFile, path);
}

JNIEXPORT void JNICALL JNI_FN(onSurfaceCreated)(JNIEnv*, jclass) {
    std::lock_guard<std::mutex> lock(g_engineMutex);
    // A new EGL context invalidates all GL objects of a previous instance.
    DestroyEngineLocked();
    g_engine.pm = projectm_create();
    if (!g_engine.pm) {
        LOGE("projectm_create failed");
        return;
    }
    projectm_set_hard_cut_enabled(g_engine.pm, true);
    projectm_set_beat_sensitivity(g_engine.pm, 1.0f);
    projectm_set_preset_switch_requested_event_callback(g_engine.pm, OnSwitchRequested, nullptr);
    projectm_set_preset_switch_failed_event_callback(g_engine.pm, OnSwitchFailed, nullptr);
    g_inputs.settingsDirty = true;
    g_engine.fpsWindowStart = NowSeconds();
    LOGI("projectM instance created");
}

JNIEXPORT void JNICALL JNI_FN(onSurfaceChanged)(JNIEnv*, jclass, jint width, jint height) {
    std::lock_guard<std::mutex> lock(g_engineMutex);
    if (!g_engine.pm) return;
    if (width != g_engine.width || height != g_engine.height) {
        // Resets projectM's renderer, so only call it on real size changes.
        projectm_set_window_size(g_engine.pm, width, height);
        g_engine.width = width;
        g_engine.height = height;
        LOGI("Render size %dx%d", width, height);
    }
    glViewport(0, 0, width, height);
}

JNIEXPORT void JNICALL JNI_FN(onDrawFrame)(JNIEnv*, jclass) {
    std::lock_guard<std::mutex> lock(g_engineMutex);
    if (!g_engine.pm) return;
    double now = NowSeconds();

    if (g_inputs.settingsDirty.exchange(false)) ApplySettings();

    if (g_engine.loadFailed) {  // failure reported outside of a load call
        g_library.MarkSkipped(g_engine.loading, "failed to load/compile");
        g_engine.loadFailed = false;
    }

    if (g_engine.current.empty()) {
        // First frame(s): show the idle preset until the index is ready, then start immediately.
        if (g_library.Ready()) {
            std::string resume;  // preset shown before an EGL context loss, if any
            {
                std::lock_guard<std::mutex> published(g_published.mutex);
                resume = g_published.currentPreset;
            }
            SwitchPreset(FirstThenNext(resume), false);
        }
    } else {
        HandleCommands();
    }

    FeedAudio();
    projectm_opengl_render_frame(g_engine.pm);

    if (g_inputs.blankDetection.load() &&
        g_engine.blackDetector.Update(now, g_engine.width, g_engine.height, AudioPresent(now))) {
        g_library.MarkSkipped(g_engine.current, "renders no visible output");
        SwitchPreset([] { return g_library.Next(); }, false);
    }
    UpdateFps(now);
}

JNIEXPORT void JNICALL JNI_FN(release)(JNIEnv*, jclass) {
    std::lock_guard<std::mutex> lock(g_engineMutex);
    DestroyEngineLocked();
}

JNIEXPORT void JNICALL JNI_FN(addWaveform)(JNIEnv* env, jclass, jbyteArray waveform, jint length) {
    if (length <= 0) return;
    std::lock_guard<std::mutex> lock(g_inputs.pcmMutex);
    auto& pcm = g_inputs.pcm;
    size_t oldSize = pcm.size();
    pcm.resize(oldSize + length);
    env->GetByteArrayRegion(waveform, 0, length, reinterpret_cast<jbyte*>(pcm.data() + oldSize));

    // RMS of the 8-bit unsigned samples (128 = silence) used to gate black-frame detection.
    double sum = 0;
    for (size_t i = oldSize; i < pcm.size(); ++i) {
        double s = (static_cast<int>(pcm[i]) - 128) / 128.0;
        sum += s * s;
    }
    g_inputs.audioLevel = static_cast<float>(std::sqrt(sum / length));
    g_inputs.audioLevelTime = NowSeconds();

    constexpr size_t kMaxPending = 8192;  // never let the buffer grow while rendering is paused
    if (pcm.size() > kMaxPending) pcm.erase(pcm.begin(), pcm.end() - kMaxPending);
}

JNIEXPORT void JNICALL JNI_FN(nextPreset)(JNIEnv*, jclass, jboolean hardCut) {
    g_inputs.commandHardCut = hardCut;
    g_inputs.command = kNext;
}

JNIEXPORT void JNICALL JNI_FN(previousPreset)(JNIEnv*, jclass, jboolean hardCut) {
    g_inputs.commandHardCut = hardCut;
    g_inputs.command = kPrevious;
}

JNIEXPORT void JNICALL JNI_FN(randomPreset)(JNIEnv*, jclass, jboolean hardCut) {
    g_inputs.commandHardCut = hardCut;
    g_inputs.command = kRandom;
}

JNIEXPORT void JNICALL JNI_FN(setPresetDuration)(JNIEnv*, jclass, jint seconds) {
    g_inputs.presetDuration = std::max(1, static_cast<int>(seconds));
    g_inputs.settingsDirty = true;
}

JNIEXPORT void JNICALL JNI_FN(setSoftCutDuration)(JNIEnv*, jclass, jint seconds) {
    g_inputs.softCutDuration = std::max(0, static_cast<int>(seconds));
    g_inputs.settingsDirty = true;
}

JNIEXPORT void JNICALL JNI_FN(setAutoChange)(JNIEnv*, jclass, jboolean enabled) {
    g_inputs.autoChange = enabled;
    g_inputs.settingsDirty = true;
}

JNIEXPORT void JNICALL JNI_FN(setMeshSize)(JNIEnv*, jclass, jint width, jint height) {
    g_inputs.meshWidth = width;
    g_inputs.meshHeight = height;
    g_inputs.settingsDirty = true;
}

JNIEXPORT void JNICALL JNI_FN(skipCurrentPreset)(JNIEnv*, jclass) {
    g_inputs.command = kSkipCurrent;
}

JNIEXPORT void JNICALL JNI_FN(setBlankDetection)(JNIEnv*, jclass, jboolean enabled) {
    g_inputs.blankDetection = enabled;
}

JNIEXPORT void JNICALL JNI_FN(setForceHardCut)(JNIEnv*, jclass, jboolean enabled) {
    g_inputs.forceHardCut = enabled;
}

JNIEXPORT jstring JNICALL JNI_FN(getSystemProperty)(JNIEnv* env, jclass, jstring name) {
    const char* key = env->GetStringUTFChars(name, nullptr);
    char value[PROP_VALUE_MAX] = {0};
    __system_property_get(key, value);
    env->ReleaseStringUTFChars(name, key);
    return env->NewStringUTF(value);
}

JNIEXPORT jstring JNICALL JNI_FN(getCurrentPresetName)(JNIEnv* env, jclass) {
    std::lock_guard<std::mutex> lock(g_published.mutex);
    return env->NewStringUTF(g_published.currentPreset.c_str());
}

JNIEXPORT jint JNICALL JNI_FN(getPresetChangeCounter)(JNIEnv*, jclass) {
    return g_published.changeCounter.load();
}

JNIEXPORT jint JNICALL JNI_FN(getPresetCount)(JNIEnv*, jclass) {
    return g_library.ActiveCount();
}

JNIEXPORT jint JNICALL JNI_FN(getSkippedCount)(JNIEnv*, jclass) {
    return g_library.SkippedCount();
}

JNIEXPORT void JNICALL JNI_FN(resetSkippedPresets)(JNIEnv*, jclass) {
    g_library.ResetSkipped();
}

JNIEXPORT jstring JNICALL JNI_FN(getVersion)(JNIEnv* env, jclass) {
    char* version = projectm_get_version_string();
    jstring result = env->NewStringUTF(version ? version : "unknown");
    if (version) projectm_free_string(version);
    return result;
}

}  // extern "C"
