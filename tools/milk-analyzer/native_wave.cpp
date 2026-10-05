// Native waveform math compiled in a data-only namespace; no GL or image input.
#include "cpu_wave_state.hpp"
#include "Waveforms/Factory.hpp"
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
#include "cpu_wave_inputs.hpp"
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

using json=nlohmann::json;
template<size_t N> void arrayInput(const json& values,std::array<float,N>& target) {
    if(!values.is_array()||values.size()!=N)throw std::runtime_error("native waveform/spectrum length mismatch");
    for(size_t i=0;i<N;++i){target[i]=values[i].get<float>();if(!std::isfinite(target[i]))throw std::runtime_error("nonfinite waveform input");}
}
int main(int argc,char** argv) {
    try {
        if(argc!=2)throw std::runtime_error("usage: milk-wave-inputs request.json");
        std::ifstream input(argv[1]);json request;input>>request;
        if(!request.at("mode").is_number_integer())throw std::runtime_error("integer native mode required");
        int mode=request.at("mode").get<int>()%16;
        if(mode<0)throw std::runtime_error("negative native mode has no waveform factory");
        auto math=milk_wave_cpu::MilkdropPreset::Waveforms::Factory::Create(static_cast<milk_wave_cpu::MilkdropPreset::WaveformMode>(mode));
        if(!math)throw std::runtime_error("native waveform factory unavailable");
        milk_wave_cpu::MilkdropPreset::PresetState state;
        state.renderContext.viewportSizeX=request.value("width",512);state.renderContext.viewportSizeY=request.value("height",288);
        if(state.renderContext.viewportSizeX<=0||state.renderContext.viewportSizeY<=0)throw std::runtime_error("positive viewport required");
        state.renderContext.lineReferenceWidth=request.value("line_reference_width",0);
        state.renderContext.lineReferenceHeight=request.value("line_reference_height",0);
        if(state.renderContext.lineReferenceWidth<0||state.renderContext.lineReferenceHeight<0)
            throw std::runtime_error("nonnegative line reference size required");
        state.waveScale=request.value("wave_scale",1.0f);state.waveSmoothing=request.value("wave_smoothing",.75f);
        state.modWaveAlphaByvolume=request.value("modulate_alpha_by_volume",false);
        if(!std::isfinite(state.waveScale)||!std::isfinite(state.waveSmoothing))throw std::runtime_error("finite wave settings required");
        json report={{"schema_version",1},{"basis","pinned waveform math bodies with data-only state adapter; no graphics context"},
            {"uses_rendered_reference",false},{"engine_archive_sha256",kEngineArchiveSha},
            {"source_hashes",json::parse(kWaveSourceHashes)},{"adapter_sha256",kCpuWaveAdapterSha},
            {"render_context_source_sha256",kWaveRenderContextSha},
            {"render_context_time_bits",sizeof(state.renderContext.time)*8},
            {"engine_identity",json::parse(kEngineIdentity)},{"mode",mode},{"frames",json::array()}};
        for(const auto& frame:request.at("frames")) {
            arrayInput(frame.at("waveform_left"),state.audioData.waveformLeft);
            arrayInput(frame.at("waveform_right"),state.audioData.waveformRight);
            arrayInput(frame.at("spectrum_left"),state.audioData.spectrumLeft);
            arrayInput(frame.at("spectrum_right"),state.audioData.spectrumRight);
            state.audioData.vol=frame.value("vol",0.f);state.renderContext.time=frame.value("time",0.0);
            milk_wave_cpu::MilkdropPreset::PerFrameContext context;
            context.x=frame.value("wave_x",.5);context.y=frame.value("wave_y",.5);
            context.mystery=frame.value("wave_mystery",0.0);context.alpha=frame.value("wave_a",.8);
            if(!std::isfinite(context.x)||!std::isfinite(context.y)||!std::isfinite(context.mystery)||!std::isfinite(context.alpha)||
               !std::isfinite(state.renderContext.time)||!std::isfinite(state.audioData.vol))throw std::runtime_error("finite frame settings required");
            auto vertices=math->GetVertices(state,context);json waves=json::array();
            for(const auto& wave:vertices) {
                json points=json::array();for(const auto& point:wave) {
                    if(!std::isfinite(point.x)||!std::isfinite(point.y))throw std::runtime_error("undefined native waveform geometry domain");
                    points.push_back({point.x,point.y});
                }waves.push_back(points);
            }
            report["frames"].push_back({{"vertex_waves",waves},{"closed_loop",math->IsLoop()},{"wave_a_after_geometry",context.alpha}});
        }
        std::filesystem::path output=request.at("output").get<std::string>();
        if(!output.parent_path().empty())std::filesystem::create_directories(output.parent_path());
        std::ofstream saved(output);saved<<report.dump()<<'\n';saved.close();if(!saved)throw std::runtime_error("cannot write geometry report");
        std::cout<<json({{"status","success"},{"mode",mode},{"frames",report["frames"].size()},{"output",output.string()}}).dump()<<'\n';return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
