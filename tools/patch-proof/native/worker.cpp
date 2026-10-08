#include "analysis_hooks.hpp"
#include "vendor/json.hpp"
#include <cstdint>
#include <cstdlib>
#include <limits>
#include <stdexcept>
#include <string>
#include <iostream>
#include <algorithm>
#include <cmath>

using json = nlohmann::json;

namespace {
constexpr uint32_t kEvaluatorControlSeed = 12345u;

uint32_t ReadSeed(const json& config) {
    const json& value = config.at("seed");
    if (value.is_number_unsigned()) {
        const uint64_t seed = value.get<uint64_t>();
        if (seed <= std::numeric_limits<uint32_t>::max()) return static_cast<uint32_t>(seed);
    } else if (value.is_number_integer()) {
        const int64_t seed = value.get<int64_t>();
        if (seed >= 0 && static_cast<uint64_t>(seed) <= std::numeric_limits<uint32_t>::max())
            return static_cast<uint32_t>(seed);
    }
    throw std::runtime_error("config.seed must be an integer from 0 through 4294967295");
}

uint32_t ConfigureSeed(uint32_t seed) {
    const std::string value = std::to_string(seed);
    if (::setenv("PRESET_LAB_SEED", value.c_str(), 1) != 0)
        throw std::runtime_error("cannot set PRESET_LAB_SEED from the selected seed");
    std::srand(lab::Seed(1));
    lab::ResetShaderRandom();
    return seed;
}

struct AppliedControls {
    int lineReferenceWidth = 0;
    int lineReferenceHeight = 0;
    bool lineAntialiasing = false;
    float feedbackDetailAlpha = -1.0f;

    json ToJson() const {
        return {{"line_reference_width", lineReferenceWidth},
                {"line_reference_height", lineReferenceHeight},
                {"line_antialiasing", lineAntialiasing},
                {"feedback_detail_alpha", feedbackDetailAlpha}};
    }
};

template <typename Engine>
AppliedControls ApplyHostControls(Engine& engine, const json& config) {
    AppliedControls applied;
#ifdef PATCH_PROOF_TV
    const int height = config.value("line_reference_height", 0);
    const int width = config.value("line_reference_width",
                                   static_cast<int>(std::lround(height * 16.0 / 9.0)));
    engine.SetLineReferenceSize(width, height);
    if (width > 0 && height > 0) {
        applied.lineReferenceWidth = width;
        applied.lineReferenceHeight = height;
    }

    applied.lineAntialiasing = config.value("line_antialiasing", false);
    engine.SetLineAntialiasing(applied.lineAntialiasing);

    const float requestedAlpha = config.value("feedback_detail", -1.0f);
    engine.SetFeedbackDetail(requestedAlpha);
    applied.feedbackDetailAlpha = std::isfinite(requestedAlpha) && requestedAlpha >= 0.0f
        ? std::min(requestedAlpha, 1.0f) : -1.0f;
#endif
    return applied;
}
}

#if defined(PATCH_PROOF_SEED_TEST) || defined(PATCH_PROOF_CONTROLS_TEST)
#ifdef PATCH_PROOF_SEED_TEST
int main(int argc, char** argv) {
    try {
        uint32_t seed;
        if (argc == 3 && std::string(argv[1]) == "job") {
            seed = ConfigureSeed(ReadSeed(json::parse(argv[2])));
        } else if (argc == 2 && std::string(argv[1]) == "evaluator-control") {
            seed = ConfigureSeed(kEvaluatorControlSeed);
        } else {
            throw std::runtime_error("usage: worker-seed-control job <config-json> | evaluator-control");
        }
        json result = {{"seed", seed}, {"environment_seed", std::getenv("PRESET_LAB_SEED")},
                       {"libc_random", std::rand()}, {"shader_random", lab::ShaderRandom()}};
        std::cout << result.dump() << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
#else
class ControlStateProbe {
public:
    int lineReferenceWidth = 0;
    int lineReferenceHeight = 0;
    bool lineAntialiasing = false;
    float feedbackDetailAlpha = -1.0f;

    void SetLineReferenceSize(int width, int height) {
        lineReferenceWidth = width > 0 && height > 0 ? width : 0;
        lineReferenceHeight = width > 0 && height > 0 ? height : 0;
    }
    void SetLineAntialiasing(bool enabled) { lineAntialiasing = enabled; }
    void SetFeedbackDetail(float alpha) {
        feedbackDetailAlpha = std::isfinite(alpha) && alpha >= 0.0f
            ? std::min(alpha, 1.0f) : -1.0f;
    }
};

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("usage: worker-controls <config-json>");
        ControlStateProbe engine;
        const auto applied = ApplyHostControls(engine, json::parse(argv[1]));
        json state = {{"line_reference_width", engine.lineReferenceWidth},
                      {"line_reference_height", engine.lineReferenceHeight},
                      {"line_antialiasing", engine.lineAntialiasing},
                      {"feedback_detail_alpha", engine.feedbackDetailAlpha}};
        std::cout << json{{"applied_controls", applied.ToJson()}, {"setter_state", state}}.dump()
                  << std::endl;
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
#endif
#else
#include "gl_capture.hpp"
#include "shader_failure_probe.hpp"
#include "texture_history_probe.hpp"
#include "ProjectM.hpp"
#include "Logging.hpp"
#include "Audio/AudioConstants.hpp"
#include <cmath>
#include <fstream>
#include <filesystem>
#include <array>
#include <thread>
#include <projectm-eval.h>

std::vector<json> capturedLogs;
void CaptureLog(const char* message,int severity,void*) { capturedLogs.push_back({{"severity",severity},{"message",message}}); std::cerr << "projectM[" << severity << "] " << message << std::endl; }

class LabProjectM : public libprojectM::ProjectM {
public:
    mutable std::string failure;
#ifdef PATCH_PROOF_TV
    void PresetInitializationWarningEvent(const std::string& file,const std::string& message) const override {
        CaptureLog((file+": "+message).c_str(),4,nullptr);
    }
#endif
    void PresetSwitchFailedEvent(const std::string& file, const std::string& reason) const override {
        failure = file + ": " + reason;
    }
};

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--evaluator-control") {
            const uint32_t seed = ConfigureSeed(kEvaluatorControlSeed);
            std::array<std::array<double, 128>, 2> streams{};
            std::array<bool, 2> compiled{};
            for (size_t i = 0; i < streams.size(); ++i) {
                std::thread thread([&, i] {
                    auto* context = projectm_eval_context_create(nullptr, nullptr);
                    auto* value = projectm_eval_context_register_variable(context, "value");
                    auto* code = projectm_eval_code_compile(context, "value=rand(1000000);");
                    compiled[i] = code != nullptr;
                    if (code) {
                        for (auto& sample : streams[i]) {
                            projectm_eval_code_execute(code);
                            sample = *value;
                        }
                        projectm_eval_code_destroy(code);
                    }
                    projectm_eval_context_destroy(context);
                });
                thread.join();
            }
            auto* context = projectm_eval_context_create(nullptr, nullptr);
            auto* value = projectm_eval_context_register_variable(context, "value");
            auto* code = projectm_eval_code_compile(context, "value=.;");
            bool loneDot = code != nullptr;
            if (code) {
                projectm_eval_code_execute(code);
                loneDot = *value == 0.0;
                projectm_eval_code_destroy(code);
            }
            projectm_eval_context_destroy(context);
            json result = {{"seed", seed}, {"compiled", compiled}, {"streams", streams},
                           {"fresh_thread_streams_equal", streams[0] == streams[1]},
                           {"lone_dot_is_zero", loneDot}};
            std::cout << result.dump() << std::endl;
            return compiled[0] && compiled[1] ? 0 : 1;
        }
        if (argc != 3 || std::string(argv[1]) != "--job")
            throw std::runtime_error("usage: preset-lab-worker --job job.json");
        std::ifstream request(argv[2]);
        if (!request) throw std::runtime_error("cannot read job");
        json job = json::parse(request);
        if (job.at("schema_version") != 1) throw std::runtime_error("unsupported job schema");
        auto cfg = job.at("config");
        const uint32_t seed = ConfigureSeed(ReadSeed(cfg));
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
        libprojectM::Logging::SetGlobalCallback({CaptureLog,nullptr});
        GlCapture capture(width, height);
        json diagnostics = json::object();
        if (cfg.value("shader_failure_probe", false)) diagnostics = proof::ShaderFailureProbe();
        if (cfg.value("texture_history_probe", false)) diagnostics = proof::TextureHistoryProbe();
        lab::clock_seconds = 0;
        LabProjectM engine;
#ifdef PRESET_LAB_HAS_FRAME_TIME
        engine.SetFrameTime(0);
#endif
        engine.SetTexturePaths({textures});
        engine.SetWindowSize(width, height);
        engine.SetMeshSize(48, 32);
        const auto appliedControls = ApplyHostControls(engine, cfg);
        engine.SetSoftCutDuration(cfg.value("soft_cut_seconds",2.0));
        engine.SetTargetFramesPerSecond(fps);
        engine.SetPresetLocked(true);
        engine.SetHardCutEnabled(false);
        engine.SetEasterEgg(0);
        engine.LoadPresetFile(preset, false);
        if (!engine.failure.empty()) throw std::runtime_error(engine.failure);
        std::ofstream bands(job.at("bands_path").get<std::string>());
        if (!bands) throw std::runtime_error("cannot write engine-band trace");
        std::vector<float> pcm(block);
        int error_frames = 0;
        for (int frame = 0; frame < frames; ++frame) {
            audio.read(reinterpret_cast<char*>(pcm.data()), pcm.size() * sizeof(float));
            if (!audio) throw std::runtime_error("truncated PCM");
            for (float sample : pcm)
                if (!std::isfinite(sample) || std::abs(sample) > 1.0f)
                    throw std::runtime_error("PCM contains invalid or out-of-range samples");
            auto count = std::min<size_t>(pcm.size(), libprojectM::Audio::AudioBufferSamples);
            engine.PCM().Add(pcm.data() + pcm.size() - count, 1, count);
            lab::clock_seconds = static_cast<double>(frame) / fps;
#ifdef PRESET_LAB_HAS_FRAME_TIME
            engine.SetFrameTime(lab::clock_seconds);
#endif
            if (job.contains("events")) for (const auto& event:job.at("events")) {
                if (event.at("frame").get<int>()!=frame) continue;
                if (event.contains("texture_root")) engine.SetTexturePaths({event.at("texture_root").get<std::string>()});
                if (event.value("reset_textures",false)) engine.ResetTextures();
                if (event.contains("load_preset")) engine.LoadPresetFile(event.at("load_preset"),event.value("smooth",false));
            }
            engine.RenderFrame(capture.framebuffer);
            if (!engine.failure.empty()) throw std::runtime_error(engine.failure);
            auto pixels = capture.Read();
            if (glGetError() != GL_NO_ERROR) ++error_frames;
            auto values = engine.PCM().GetFrameAudioData();
            json band = {{"time", lab::clock_seconds}, {"bass", values.bass}, {"mid", values.mid},
                         {"treble", values.treb}, {"bass_att", values.bassAtt},
                         {"mid_att", values.midAtt}, {"treble_att", values.trebAtt}};
            bands << band.dump() << '\n';
            std::cout.write(reinterpret_cast<char*>(pixels.data()), pixels.size());
            if (!std::cout) throw std::runtime_error("frame consumer closed");
        }
        bands.close();
        if (!bands) throw std::runtime_error("band trace write failed");
        json result = {{"status", error_frames ? "failed" : "success"}, {"frames", frames},
                       {"width", width}, {"height", height}, {"fps", fps},
                       {"gl_vendor", reinterpret_cast<const char*>(glGetString(GL_VENDOR))}, {"glsl_version", reinterpret_cast<const char*>(glGetString(GL_SHADING_LANGUAGE_VERSION))}, {"messages",capturedLogs}, {"gl_error_frames", error_frames}, {"gl_version", reinterpret_cast<const char*>(glGetString(GL_VERSION))},
                       {"gl_renderer", reinterpret_cast<const char*>(glGetString(GL_RENDERER))},
                       {"identity", job.at("identity")}, {"seed", seed}};
        result["applied_controls"] = appliedControls.ToJson();
        if (!diagnostics.empty()) result["diagnostics"] = diagnostics;
        std::string target = job.at("manifest_path");
        std::ofstream manifest(target + ".tmp");
        manifest << result.dump();
        manifest.close();
        if (!manifest) throw std::runtime_error("manifest write failed");
        std::filesystem::rename(target + ".tmp", target);
        return error_frames ? 2 : 0;
    } catch (const std::exception& error) {
        std::cerr << "preset-lab-worker: " << error.what() << '\n';
        return 1;
    }
}
#endif
