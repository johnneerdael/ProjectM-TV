// Unchanged native geometry/hue bodies, with data-only state. No GL calls.
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
#include "Renderer/RenderContext.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <random>
#include <stdexcept>
using json=nlohmann::json;

struct PresetState {
    libprojectM::Renderer::RenderContext renderContext;
    std::array<float,4> hueRandomOffsets;
};
class FinalComposite {
public:
    static constexpr int compositeGridWidth=32,compositeGridHeight=24;
    struct Vertex {float x,y,u,v,radius,angle,r,g,b,a;};
    std::array<Vertex,32*24> m_vertices;
    std::array<int,30*22*6> m_indices;
    int m_viewportWidth=0,m_viewportHeight=0;
    void InitializeMesh(const PresetState&);
    void ApplyHueShaderColors(const PresetState&);
    static float SquishToCenter(float,float);
    static void UvToMathSpace(float,float,float,float,float&,float&);
};
#include "cpu_composite_adapter.hpp"

int main(int argc,char** argv) {
    try {
        if(argc!=2)throw std::runtime_error("usage: milk-composite-inputs request.json");
        std::ifstream input(argv[1]);json request;input>>request;
        if(!request.at("width").is_number_integer()||!request.at("height").is_number_integer())
            throw std::runtime_error("integer viewport required");
        int width=request.at("width"),height=request.at("height");
        if(width<=0||height<=0||width>16384||height>16384)throw std::runtime_error("viewport outside bridge budget");
        PresetState state{};
        state.renderContext.viewportSizeX=width;
        state.renderContext.viewportSizeY=height;
        state.renderContext.aspectX=std::min(1.0f,float(width)/height);
        state.renderContext.aspectY=std::min(1.0f,float(height)/width);
        state.renderContext.time=request.at("time").get<float>();
        if(!std::isfinite(state.renderContext.time))throw std::runtime_error("finite time required");
        if(request.contains("entropy_seed")) {
            const auto& seed=request.at("entropy_seed");
            if(!seed.is_number_integer() || seed.get<double>()<0 || seed.get<double>()>UINT32_MAX || request.contains("hue_offsets"))
                throw std::runtime_error("one explicit uint32 entropy seed or hue offsets required");
            initializeHueOffsets(state.hueRandomOffsets,seed.get<uint32_t>());
        } else {
            if(request.at("hue_offsets").size()!=4)throw std::runtime_error("four hue offsets required");
            for(int i=0;i<4;++i) {
                state.hueRandomOffsets[i]=request.at("hue_offsets").at(i);
                if(!std::isfinite(state.hueRandomOffsets[i]))throw std::runtime_error("nonfinite hue offset");
            }
        }
        FinalComposite mesh;mesh.InitializeMesh(state);mesh.ApplyHueShaderColors(state);
        json result={{"positions",json::array()},{"uv",json::array()},{"polar",json::array()},
                     {"colours",json::array()},{"indices",mesh.m_indices},
                     {"native_source_sha256",kCompositeSourceSha},{"native_bodies_sha256",kCompositeBodiesSha},
                     {"render_context_source_sha256",kCompositeRenderContextSha},
                     {"render_context_time_bits",sizeof(state.renderContext.time)*8},
                     {"hue_offsets",state.hueRandomOffsets},{"hue_initializer_sha256",kHueInitializerSha},
                     {"engine",json::parse(kEngineIdentity)},{"engine_archive_sha256",kEngineArchiveSha},
                     {"native_driver_verified",false},{"adapter","data-only state; native mesh/hue bodies; GL upload omitted"}};
        for(const auto& v:mesh.m_vertices) {
            result["positions"].push_back({v.x,v.y});result["uv"].push_back({v.u,v.v});
            result["polar"].push_back({v.radius,v.angle});result["colours"].push_back({v.r,v.g,v.b,v.a});
        }
        std::cout<<result.dump()<<'\n';return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
