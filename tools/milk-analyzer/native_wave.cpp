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
#include <limits>
#include <stdexcept>

using json=nlohmann::json;
template<size_t N> void arrayInput(const json& values,std::array<float,N>& target) {
    if(!values.is_array()||values.size()!=N)throw std::runtime_error("native waveform/spectrum length mismatch");
    for(size_t i=0;i<N;++i){target[i]=values[i].get<float>();if(!std::isfinite(target[i]))throw std::runtime_error("nonfinite waveform input");}
}
template<class T> auto pointX(const T& point) -> decltype(point.X()){return point.X();}
template<class T> auto pointY(const T& point) -> decltype(point.Y()){return point.Y();}
inline float pointX(const milk_wave_cpu::Renderer::RenderItem::Point& point){return point.x;}
inline float pointY(const milk_wave_cpu::Renderer::RenderItem::Point& point){return point.y;}

int main(int argc,char** argv) {
    try {
        if(argc!=2)throw std::runtime_error("usage: milk-wave-inputs request.json");
        std::ifstream input(argv[1]);json request;input>>request;
        if(!request.at("mode").is_number_integer())throw std::runtime_error("integer native mode required");
        const auto policy=request.value("mode_policy",std::string("static-v1"));
        if(policy!="static-v1"&&policy!="evaluated-live-v1")throw std::runtime_error("unknown waveform mode policy");
        const bool live=policy=="evaluated-live-v1";
        const auto engine=json::parse(kEngineIdentity);
        const bool oldLive = engine.at("commit")=="e0b0a967f0ffd7d332106c366668ed271718472b" &&
            (engine.at("patches_sha256")=="7ef297fcab5d42d0531ec621ac6a464a5a0e7982da02bb40996bc62a886ae527" ||
             engine.at("patches_sha256")=="cd01f0f3cce4f6be05d781b06192dadadbd8254a6fa1c03ea52394d3e48f9ded" ||
             engine.at("patches_sha256")=="bc80791e28e7559b81c33036c91b8163cfe611d9d9793e7d3e10f8cb4e5290c8");
        const bool core42Live = engine.at("commit")=="6f64807467e312034883a4389e6aa80a675458bc" &&
            engine.at("patches_sha256")=="fd02c15d040ca073f7c09a0b798040c2696fa6bf2252d6ddc6c7b6ff7bcd92eb";
        if(live && !oldLive && !core42Live)
            throw std::runtime_error("live waveform engine identity mismatch");
        int mode=request.at("mode").get<int>()%16;
        std::unique_ptr<milk_wave_cpu::MilkdropPreset::Waveforms::WaveformMath> math;
        if(!live) {
            if(mode<0)throw std::runtime_error("negative native mode has no waveform factory");
            math=milk_wave_cpu::MilkdropPreset::Waveforms::Factory::Create(static_cast<milk_wave_cpu::MilkdropPreset::WaveformMode>(mode));
            if(!math)throw std::runtime_error("native waveform factory unavailable");
        }
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
            {"engine_identity",engine},{"mode",mode},{"mode_policy",policy},{"frames",json::array()}};
        for(const auto& frame:request.at("frames")) {
            if(live) {
                if(!frame.contains("wave_mode"))throw std::runtime_error("explicit evaluated waveform mode required");
                const auto& value=frame.at("wave_mode");
                double raw;
                if(value.is_number())raw=value.get<double>();
                else if(value.is_object()&&value.size()==1&&value.contains("ieee")&&value.at("ieee").is_string()) {
                    const auto tag=value.at("ieee").get<std::string>();
                    if(tag!="nan"&&tag!="positive_infinity"&&tag!="negative_infinity")
                        throw std::runtime_error("unknown waveform IEEE tag");
                    raw=std::numeric_limits<double>::quiet_NaN();
                }else throw std::runtime_error("explicit evaluated waveform mode required");
                const auto truncated=std::trunc(raw);
                if(!std::isfinite(truncated)||truncated<std::numeric_limits<int>::min()||truncated>std::numeric_limits<int>::max()) {
                    report["frames"].push_back({{"mode",nullptr},{"omitted",true},{"vertex_waves",json::array()},
                        {"closed_loop",false},{"wave_a_after_geometry",0}});
                    continue;
                }
                const int next=static_cast<int>(truncated)%16;
                if(!math||next!=mode) {
                    mode=next;
                    math=milk_wave_cpu::MilkdropPreset::Waveforms::Factory::Create(static_cast<milk_wave_cpu::MilkdropPreset::WaveformMode>(mode));
                }
                if(!math) {
                    report["frames"].push_back({{"mode",nullptr},{"omitted",true},{"vertex_waves",json::array()},
                        {"closed_loop",false},{"wave_a_after_geometry",0}});
                    continue;
                }
            }
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
                    if(!std::isfinite(pointX(point))||!std::isfinite(pointY(point)))throw std::runtime_error("undefined native waveform geometry domain");
                    points.push_back({pointX(point),pointY(point)});
                }waves.push_back(points);
            }
            report["frames"].push_back({{"mode",mode},{"omitted",false},{"vertex_waves",waves},
                {"closed_loop",math->IsLoop()},{"wave_a_after_geometry",context.alpha}});
        }
        std::filesystem::path output=request.at("output").get<std::string>();
        if(!output.parent_path().empty())std::filesystem::create_directories(output.parent_path());
        std::ofstream saved(output);saved<<report.dump()<<'\n';saved.close();if(!saved)throw std::runtime_error("cannot write geometry report");
        std::cout<<json({{"status","success"},{"mode",mode},{"frames",report["frames"].size()},{"output",output.string()}}).dump()<<'\n';return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
