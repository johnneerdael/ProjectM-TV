#include "vendor/json.hpp"
#include "gl_capture.hpp"
#include "analysis_hooks.hpp"
#include "ProjectM.hpp"
#include "Audio/AudioConstants.hpp"
#include <cmath>
#include <fstream>
#include <iostream>
#include <filesystem>
#include <stdexcept>
#include <chrono>

using json = nlohmann::json;

class LabProjectM : public libprojectM::ProjectM {
public:
    mutable std::string failure;
    void PresetSwitchFailedEvent(const std::string& file, const std::string& reason) const override {
        failure = file + ": " + reason;
    }
};

int main(int argc, char** argv) {
    try {
        if (argc != 3 || std::string(argv[1]) != "--job")
            throw std::runtime_error("usage: preset-lab-worker --job job.json");
        std::ifstream request(argv[2]);
        if (!request) throw std::runtime_error("cannot read job");
        json job = json::parse(request);
        if (job.at("schema_version") != 1) throw std::runtime_error("unsupported job schema");
        auto cfg = job.at("config");
        int width = cfg.at("width"), height = cfg.at("height"), fps = cfg.at("fps");
        double warmup = cfg.at("warmup_seconds"), measurement = cfg.at("measurement_seconds");
        double duration = warmup + measurement;
        if (width <= 0 || height <= 0 || width > 4096 || height > 4096 || (fps != 30 && fps != 60)
            || !std::isfinite(duration) || warmup < 0 || measurement <= 0
            || std::abs(duration * fps - std::round(duration * fps)) > 1e-8)
            throw std::runtime_error("invalid job dimensions or timing");
        int frames = static_cast<int>(std::round(duration * fps));
        int block = 44100 / fps;
        std::ifstream audio(job.at("pcm_path").get<std::string>(), std::ios::binary | std::ios::ate);
        if (!audio || audio.tellg() != static_cast<std::streamoff>(frames) * block * sizeof(float))
            throw std::runtime_error("invalid complete-frame PCM length");
        audio.seekg(0);
        std::string preset = job.at("preset_path");
        std::string textures = job.at("texture_root");
        if (!std::filesystem::is_regular_file(preset) || !std::filesystem::is_directory(textures))
            throw std::runtime_error("preset or texture path unavailable");
        GlCapture capture(width, height);
        // Desktop core-profile GL ignores gl_PointSize unless this is enabled; Android's GLES always honours it,
        // so the worker renders dots like the TVs.
        glEnable(GL_PROGRAM_POINT_SIZE);
        lab::clock_seconds = 0;
        std::srand(lab::Seed(1));
        lab::ResetShaderRandom();
        LabProjectM engine;
#ifdef PRESET_LAB_HAS_FRAME_TIME
        engine.SetFrameTime(0);
#endif
        engine.SetTexturePaths({textures});
        engine.SetWindowSize(width, height);
        engine.SetMeshSize(48, 32);
        // Quad lines' reference size; a job with only line_reference_height means a 16:9 reference of that height.
        int line_reference_height = cfg.value("line_reference_height", 0);
        int line_reference_width = cfg.value("line_reference_width",
                                             static_cast<int>(std::lround(line_reference_height * 16.0 / 9.0)));
#ifdef CATALOG_TV
        engine.SetLineReferenceSize(line_reference_width, line_reference_height);
        engine.SetLineAntialiasing(cfg.value("line_antialiasing", false));
        engine.SetFeedbackDetail(cfg.value("feedback_detail", -1.0f));
#endif
        engine.SetTargetFramesPerSecond(fps);
        engine.SetPresetLocked(true);
        engine.SetHardCutEnabled(false);
        engine.SetEasterEgg(0);
        engine.LoadPresetFile(preset, false);
        if (!engine.failure.empty()) throw std::runtime_error(engine.failure);
        using Clock = std::chrono::steady_clock;
        auto milliseconds = [](auto elapsed) { return std::chrono::duration<double, std::milli>(elapsed).count(); };
        const int warmFrames = static_cast<int>(std::round(warmup * fps));
        GLint timerBits = 0;
        glGetQueryiv(GL_TIME_ELAPSED, GL_QUERY_COUNTER_BITS, &timerBits);
        GLuint timer = 0;
        if (timerBits > 0) glGenQueries(1, &timer);
        int timerProbeNonzero = 0;
        bool gpuTimerValid = false;
        json samples = json::array();
        std::vector<float> pcm(block);
        int errorFrames = 0;
        glFinish();
        for (int frame = 0; frame < frames; ++frame) {
            audio.read(reinterpret_cast<char*>(pcm.data()), pcm.size() * sizeof(float));
            if (!audio) throw std::runtime_error("truncated PCM");
            for (float value : pcm)
                if (!std::isfinite(value) || std::abs(value) > 1.0f)
                    throw std::runtime_error("invalid PCM");
            auto count = std::min<size_t>(pcm.size(), libprojectM::Audio::AudioBufferSamples);
            engine.PCM().Add(pcm.data() + pcm.size() - count, 1, count);
            lab::clock_seconds = static_cast<double>(frame + 1) / fps;
#ifdef PRESET_LAB_HAS_FRAME_TIME
            engine.SetFrameTime(lab::clock_seconds);
#endif
            lab::gamma_draw_calls = 0;
            lab::gamma_invocations = 0;
            lab::gamma_value = 0;
            const bool query = timer && (frame < 10 || gpuTimerValid);
            if (query) glBeginQuery(GL_TIME_ELAPSED, timer);
            const auto begin = Clock::now();
            engine.RenderFrame(capture.framebuffer);
            const auto submitted = Clock::now();
            if (query) glEndQuery(GL_TIME_ELAPSED);
            glFinish();
            const auto complete = Clock::now();
            GLuint64 gpuNs = 0;
            if (query) glGetQueryObjectui64v(timer, GL_QUERY_RESULT, &gpuNs);
            if (frame < 10 && gpuNs > 0) ++timerProbeNonzero;
            if (frame == 9) gpuTimerValid = timerProbeNonzero == 10;
            if (glGetError() != GL_NO_ERROR) ++errorFrames;
            samples.push_back({{"frame", frame}, {"measured", frame >= warmFrames},
                {"submit_ms", milliseconds(submitted-begin)}, {"complete_ms", milliseconds(complete-begin)},
                {"gpu_ns", gpuNs}, {"gamma_draws", lab::gamma_draw_calls},
                {"gamma_invocations", lab::gamma_invocations}, {"gamma", lab::gamma_value}});
        }
        if (timer) glDeleteQueries(1, &timer);
        json result = {{"status", errorFrames ? "failed" : "success"}, {"frames", frames},
            {"warmup_frames", warmFrames}, {"width", width}, {"height", height}, {"fps_clock", fps},
            {"gl_error_frames", errorFrames}, {"gl_version", reinterpret_cast<const char*>(glGetString(GL_VERSION))},
            {"gl_renderer", reinterpret_cast<const char*>(glGetString(GL_RENDERER))},
            {"gpu_timer_bits", timerBits}, {"gpu_probe_nonzero", timerProbeNonzero},
            {"gpu_timer_valid", gpuTimerValid}, {"identity", job.at("identity")},
            {"config", cfg}, {"samples", samples}};
        std::ofstream output(job.at("manifest_path").get<std::string>());
        output << result.dump(2) << '\n';
        if (!output) throw std::runtime_error("benchmark output failed");
        return errorFrames ? 2 : 0;
    } catch (const std::exception& error) {
        std::cerr << "preset-lab-worker: " << error.what() << '\n';
        return 1;
    }
}
