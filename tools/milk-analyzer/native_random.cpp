// Source-generated shader inputs. No renderer/GL context or reference frames.
#include "vendor/json.hpp"
#include <glm/gtc/matrix_transform.hpp>
#include <glm/mat4x4.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <memory>
#include <random>
#include <stdexcept>
using json = nlohmann::json;

static std::uint64_t drawsConsumed = 0;
static bool declaredInputs=false;
static std::mt19937 inputGenerator;
static void seedInputs(uint32_t seed) {srand(seed);inputGenerator.seed(seed);}
static int countedRand() {
    ++drawsConsumed;
    return declaredInputs?static_cast<int>(inputGenerator()&0x7fffffffU):rand();
}

struct UniformRecorder {
    json values = json::object();
    void SetUniformFloat4(const char* name, const glm::vec4& vector) {
        json value = json::array();
        for (int i = 0; i < 4; ++i) {
            if (!std::isfinite(vector[i])) throw std::runtime_error("nonfinite random vector");
            value.push_back(vector[i]);
        }
        values[name] = value;
    }
    // Same conversion/signature as Renderer::Shader. The implicit mat4->mat3x4
    // conversion drops the fourth column; do not restore translation.
    void SetUniformMat3x4(const char* name, const glm::mat3x4& matrix) {
        json value = json::array();
        for (int row = 0; row < 4; ++row) {
            json columns = json::array();
            for (int col = 0; col < 3; ++col) {
                if (!std::isfinite(matrix[col][row])) throw std::runtime_error("nonfinite random matrix");
                columns.push_back(matrix[col][row]);
            }
            value.push_back(columns);
        }
        values[name] = value;
    }
};

struct PresetState {
    struct RenderContext { int frame; float feedbackDetailAlpha; } renderContext;
};

class MilkdropShader {
public:
    enum class ShaderType { WarpShader, CompositeShader };
    ShaderType m_type;
    std::array<float, 4> m_randValues{};
    std::array<glm::vec3, 20> m_randTranslation{};
    std::array<glm::vec3, 20> m_randRotationCenters{};
    std::array<glm::vec3, 20> m_randRotationSpeeds{};
    int m_randomFrame{-1};
    glm::vec4 m_frameRandom{};
    std::array<glm::mat4, 4> m_frameMatrices{};
    UniformRecorder m_shader;
    explicit MilkdropShader(ShaderType type);
    void LoadRandomVariables(float floatTime, const PresetState& presetState);
};
#include "cpu_random_adapter.hpp"

static std::uint32_t parseSeed(const json& value) {
    if(!value.is_number_integer() || value.get<double>()<0 ||
       value.get<double>()>std::numeric_limits<std::uint32_t>::max())
        throw std::runtime_error("uint32 post-mix C-rand seed required");
    return value.get<std::uint32_t>();
}

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("usage: milk-shader-random request.json");
        std::ifstream input(argv[1]); json request; input >> request;
        const auto seed = parseSeed(request.at("seed"));
        const auto policy=request.value("rand_policy",std::string("host-c-rand-v1"));
        if(policy!="host-c-rand-v1" && policy!="declared-mt19937-u31-v1")
            throw std::runtime_error("unknown random input policy");
        declaredInputs=policy=="declared-mt19937-u31-v1";
        const auto& events = request.at("events");
        if (!events.is_array() || events.size() > 100000)
            throw std::runtime_error("event ledger exceeds adapter budget");
        seedInputs(seed);
        std::map<std::string, std::unique_ptr<MilkdropShader>> states;
        json records = json::array(), loads = json::array();
        for (std::size_t i = 0; i < events.size(); ++i) {
            const auto& event = events.at(i);
            std::string kind = event.at("kind"), id = event.at("id");
            if (id.empty()) throw std::runtime_error("nonempty shader id required");
            const auto before = drawsConsumed;
            if (kind == "reseed") {
                seedInputs(parseSeed(event.at("seed")));
            } else if (kind == "construct") {
                if (states.count(id)) throw std::runtime_error("duplicate shader construction id");
                // Constructor type does not affect its random initialization.
                states[id] = std::make_unique<MilkdropShader>(MilkdropShader::ShaderType::WarpShader);
            } else if (kind == "load") {
                if (!states.count(id)) throw std::runtime_error("unknown shader load id");
                if (!event.at("time").is_number()) throw std::runtime_error("numeric shader time required");
                float time = event.at("time").get<float>();
                if (!std::isfinite(time)) throw std::runtime_error("finite float32 shader time required");
                auto frameValue = event.value("frame", json(0));
                if (!frameValue.is_number_integer() || frameValue.get<double>() < 0 ||
                    frameValue.get<double>() > std::numeric_limits<int>::max())
                    throw std::runtime_error("nonnegative int32 shader frame required");
                auto detailValue = event.value("feedback_detail_alpha", json(-1.0f));
                if (!detailValue.is_number()) throw std::runtime_error("numeric feedback detail alpha required");
                float detail = detailValue.get<float>();
                if (!std::isfinite(detail)) throw std::runtime_error("finite float32 feedback detail alpha required");
                if (!kRandomFrameCache && detail >= 0.0f)
                    throw std::runtime_error("feedback detail random caching unavailable in this engine");
                PresetState presetState{{frameValue.get<int>(), detail}};
                auto& state = *states.at(id);
                state.LoadRandomVariables(time, presetState);
                loads.push_back({{"event_index", i}, {"id", id}, {"time", time},
                                 {"frame", presetState.renderContext.frame}, {"feedback_detail_alpha", detail},
                                 {"uniforms", state.m_shader.values},
                                 {"draws_before", before}, {"draws_after", drawsConsumed}});
            } else throw std::runtime_error("unknown random lifecycle event");
            json record={{"kind",kind},{"id",id},{"draws_before",before},{"draws_after",drawsConsumed}};
            if(kind=="reseed")record["seed"]=parseSeed(event.at("seed"));
            records.push_back(record);
        }
#if defined(__APPLE__)
        const char* platform = "macOS";
#elif defined(__BIONIC__)
        const char* platform = "Android/bionic";
#elif defined(__GLIBC__)
        const char* platform = "Linux/glibc";
#else
        const char* platform = "other host libc";
#endif
        json result = {{"schema_version", 1}, {"seed", seed}, {"events", records}, {"loads", loads},
            {"draws_consumed", drawsConsumed}, {"source_sha256", kRandomSourceSha},
            {"bodies_sha256", kRandomBodiesSha}, {"glm_sha256", kRandomGlmSha},
            {"upload_source_sha256", kRandomUploadSourceSha},
            {"frame_cache_policy", kRandomFrameCache ? "core235-feedback-detail-v1" : "none"},
            {"rendered_frames_consumed", false}, {"target_driver_verified", false},
            {"profile", {{"rng", declaredInputs?"declared-mt19937-u31-v1":"host C rand"}, {"platform", platform},
                         {"compiler", __VERSION__}, {"rand_max", RAND_MAX}, {"glm_version", GLM_VERSION}}},
            {"scope", "Explicit source lifecycle, host-libc RNG and copied native CPU matrix bodies. "
                      "No inferred preset/idle/fallback lifecycle or Android equivalence."}};
        std::cout << result.dump() << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
