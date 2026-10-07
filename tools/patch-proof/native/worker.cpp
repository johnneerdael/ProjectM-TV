#include "vendor/json.hpp"
#include "gl_capture.hpp"
#include "analysis_hooks.hpp"
#include "ProjectM.hpp"
#include "Logging.hpp"
#include "Audio/AudioConstants.hpp"
#include <cmath>
#include <fstream>
#include <iostream>
#include <filesystem>
#include <stdexcept>
#include <array>
#include <thread>
#include <projectm-eval.h>

using json = nlohmann::json;

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
            json result = {{"compiled", compiled}, {"streams", streams},
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
#ifdef PATCH_PROOF_TV
        engine.SetLineReferenceSize(line_reference_width, line_reference_height);
        engine.SetLineAntialiasing(cfg.value("line_antialiasing", false));
        engine.SetFeedbackDetail(cfg.value("feedback_detail", -1.0f));
#endif
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
                       {"identity", job.at("identity")}, {"seed", cfg.at("seed")}};
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
