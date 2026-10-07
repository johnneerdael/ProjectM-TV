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
        engine.SetLineReferenceSize(line_reference_width, line_reference_height);
        engine.SetLineAntialiasing(cfg.value("line_antialiasing", false));
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
            lab::clock_seconds = static_cast<double>(frame + 1) / fps;
#ifdef PRESET_LAB_HAS_FRAME_TIME
            engine.SetFrameTime(lab::clock_seconds);
#endif
            engine.RenderFrame(capture.framebuffer);
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
                       {"gl_error_frames", error_frames}, {"gl_version", reinterpret_cast<const char*>(glGetString(GL_VERSION))},
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
