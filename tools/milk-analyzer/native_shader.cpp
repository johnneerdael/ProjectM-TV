// CPU-only source preparation/GLSL generation. No renderer or GL calls.
#include "reader_inputs.hpp"
#include "vendor/json.hpp"
#include "GLSLGenerator.h"
#include "HLSLParser.h"
#include "Utils.hpp"
#include <cstdio>
#include <fstream>
#include <iostream>
#include <locale>
#include <regex>
#include <set>
#include <sstream>
#include <stdexcept>
#include <unistd.h>

using json = nlohmann::json;
namespace Utils = libprojectM::Utils;
namespace Renderer { using ShaderException = std::runtime_error; }

// Native copied bodies reference these views instead of GL-owning objects.
class MilkdropStaticShaders {
public:
    static inline M4::GLSLGenerator::Version version = M4::GLSLGenerator::Version_330;
    static MilkdropStaticShaders* Get() { static MilkdropStaticShaders data; return &data; }
    std::string GetPresetShaderHeader() { return kShaderHeader; }
    auto GetGlslGeneratorVersion() { return version; }
};
class MilkdropShader {
public:
    enum class ShaderType { WarpShader, CompositeShader };
    ShaderType m_type;
    struct BlurTexture {
        enum class BlurLevel {None,Blur1,Blur2,Blur3};
    };
    std::set<std::string> m_samplerNames;
    BlurTexture::BlurLevel m_maxBlurLevelRequired{BlurTexture::BlurLevel::None};
    explicit MilkdropShader(ShaderType type): m_type(type) {}
    void PreprocessPresetShader(std::string& program);
    void GetReferencedSamplers(const std::string& program);
    void UpdateMaxBlurLevel(BlurTexture::BlurLevel requestedLevel);
};
#include "cpu_shader_adapter.hpp"

class ParserDiagnostics {
    int saved;
public:
    ParserDiagnostics(): saved(dup(STDOUT_FILENO)) {
        if (saved < 0 || dup2(STDERR_FILENO, STDOUT_FILENO) < 0)
            throw std::runtime_error("cannot route native parser diagnostics");
    }
    ~ParserDiagnostics() { std::fflush(stdout); dup2(saved, STDOUT_FILENO); close(saved); }
};

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("usage: milk-shader-translate request.json");
        std::ifstream stream(argv[1]);
        json request; stream >> request;
        const auto stage = request.at("stage").get<std::string>();
        const auto profile = request.at("profile").get<std::string>();
        if (stage != "warp" && stage != "composite") throw std::runtime_error("invalid stage");
        if (profile != "glsl330" && profile != "gles300") throw std::runtime_error("invalid profile");
        MilkdropStaticShaders::version = profile == "glsl330" ? M4::GLSLGenerator::Version_330
                                                             : M4::GLSLGenerator::Version_300_ES;
        std::set<std::string> samplers, sizes;
        for (const auto& entry : request.at("samplers").items()) {
            const auto type = entry.value().get<std::string>();
            if (!std::regex_match(entry.key(), std::regex("sampler_[A-Za-z_][A-Za-z_0-9]*")) ||
                (type != "sampler2D" && type != "sampler3D"))
                throw std::runtime_error("invalid explicit sampler declaration");
            samplers.insert("uniform " + type + " " + entry.key() + ";\n");
        }
        for (const auto& entry : request.at("texture_sizes")) {
            const auto name = entry.get<std::string>();
            if (!std::regex_match(name, std::regex("texsize_[A-Za-z_][A-Za-z_0-9]*")))
                throw std::runtime_error("invalid explicit texture-size declaration");
            sizes.insert("uniform float4 " + name + ";\n");
        }
        json result = {{"profile", profile}, {"stage", stage},
            {"engine", json::parse(kEngineIdentity)}, {"engine_archive_sha256", kEngineArchiveSha},
            {"shader_header_sha256", kShaderHeaderSha}, {"native_source_sha256", kNativeShaderSourceSha},
            {"float_formatter_sha256", kFloatFormatterSha}, {"float_literal_policy", kFloatLiteralPolicy},
            {"preprocess_body_sha256", kNativePreprocessBodySha},
            {"translation_body_sha256", kNativeTranslationBodySha},
            {"sampler_reference_body_sha256", kNativeSamplerReferenceBodySha},
            {"random_binding_contract", json::parse(kRandomBindingContract)},
            {"adapter", "unchanged native CPU bodies; explicit descriptor declarations and static header/version views"},
            {"native_driver_verified", false}};
        {
            ParserDiagnostics diagnostics;
            try {
                auto code = request.at("code").get<std::string>();
                MilkdropShader shader(stage == "warp" ? MilkdropShader::ShaderType::WarpShader
                                                       : MilkdropShader::ShaderType::CompositeShader);
                shader.GetReferencedSamplers(code);
                result["referenced_samplers"] = shader.m_samplerNames;
                for (const auto& name : shader.m_samplerNames) {
                    if (!std::regex_match(name,std::regex("[A-Za-z0-9_]+")))
                        throw Renderer::ShaderException("Native sampler scan produced invalid descriptor identifier: " + name);
                }
                shader.PreprocessPresetShader(code);
                result["glsl"] = targetTranslate(code, stage, samplers, sizes);
                result["status"] = "translated";
            } catch (const std::exception& error) {
                result["status"] = "rejected";
                result["reason"] = error.what();
            }
        }
        std::cout << result.dump(-1, ' ', false, json::error_handler_t::replace) << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
