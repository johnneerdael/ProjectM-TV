// Unchanged native geometry/hue bodies, with data-only state. No GL calls.
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <stdexcept>
using json=nlohmann::json;

struct PresetState {
    struct {int viewportSizeX,viewportSizeY;float aspectX,aspectY;double time;} renderContext;
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
        PresetState state{};state.renderContext={width,height,std::min(1.0f,float(width)/height),
                                                    std::min(1.0f,float(height)/width),request.at("time")};
        if(!std::isfinite(state.renderContext.time)||request.at("hue_offsets").size()!=4)
            throw std::runtime_error("finite time and four hue offsets required");
        for(int i=0;i<4;++i) {
            state.hueRandomOffsets[i]=request.at("hue_offsets").at(i);
            if(!std::isfinite(state.hueRandomOffsets[i]))throw std::runtime_error("nonfinite hue offset");
        }
        FinalComposite mesh;mesh.InitializeMesh(state);mesh.ApplyHueShaderColors(state);
        json result={{"positions",json::array()},{"uv",json::array()},{"polar",json::array()},
                     {"colours",json::array()},{"indices",mesh.m_indices},
                     {"native_source_sha256",kCompositeSourceSha},{"native_bodies_sha256",kCompositeBodiesSha},
                     {"engine",json::parse(kEngineIdentity)},{"engine_archive_sha256",kEngineArchiveSha},
                     {"native_driver_verified",false},{"adapter","data-only state; native mesh/hue bodies; GL upload omitted"}};
        for(const auto& v:mesh.m_vertices) {
            result["positions"].push_back({v.x,v.y});result["uv"].push_back({v.u,v.v});
            result["polar"].push_back({v.radius,v.angle});result["colours"].push_back({v.r,v.g,v.b,v.a});
        }
        std::cout<<result.dump()<<'\n';return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
