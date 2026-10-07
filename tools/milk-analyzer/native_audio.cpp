// Exact pinned PCM/FFT/alignment/band execution without graphics or image input.
#include "Audio/PCM.hpp"
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <random>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif

using json=nlohmann::json;
#if defined(_LIBCPP_VERSION) && _LIBCPP_VERSION == 200100
constexpr bool kQualifiedDurationDistribution=true;
constexpr const char* kDurationDistribution="libcxx-200100-fresh-normal-v1";
#else
constexpr bool kQualifiedDurationDistribution=false;
constexpr const char* kDurationDistribution="unqualified-standard-library";
#endif
std::string digest(const std::vector<unsigned char>& bytes) {
    unsigned char hash[32];
#ifdef __APPLE__
    CC_SHA256(bytes.data(),static_cast<CC_LONG>(bytes.size()),hash);
#else
    SHA256(bytes.data(),bytes.size(),hash);
#endif
    std::ostringstream out;for(auto value:hash)out<<std::hex<<std::setw(2)<<std::setfill('0')<<static_cast<int>(value);
    return out.str();
}

int main(int argc,char** argv) {
    try {
        if(argc!=2)throw std::runtime_error("usage: milk-audio-inputs request.json");
        std::ifstream input(argv[1]);if(!input)throw std::runtime_error("cannot read audio request");
        json request;input>>request;
        for(const auto* name:{"fps","frames","channels"})
            if(request.contains(name)&&!request.at(name).is_number_integer())throw std::runtime_error("audio schedule/channels must be integers");
        int fps=request.at("fps").get<int>(),frames=request.at("frames").get<int>(),channels=request.value("channels",1);
        if((fps!=30&&fps!=60)||frames<1||frames>108000||(channels!=1&&channels!=2))
            throw std::runtime_error("invalid audio frame schedule/channels");
        const auto clockPolicy=request.value("clock_policy",std::string("ideal-frame-fractions-v1"));
        const bool roundedClock=clockPolicy=="projectmtv-jni-rounded-nanoseconds30-v1";
        if((clockPolicy!="ideal-frame-fractions-v1"&&!roundedClock)||(roundedClock&&fps!=30))
            throw std::runtime_error("unsupported audio clock policy/cadence");
        const auto progressPolicy=request.value("preset_progress_policy",std::string("explicit-zero-placeholder-v1"));
        const bool cold2316=progressPolicy=="projectmtv-core-2.3.16-cold-jni-v1";
        const bool cold2317=progressPolicy=="projectmtv-core-2.3.17-cold-jni-v1";
        const bool coldProgress=cold2316||cold2317;
        double presetDuration=0.0;
        uint32_t entropySeed=0;
        if(coldProgress) {
            if(!kQualifiedDurationDistribution)
                throw std::runtime_error("cold JNI progress requires qualified libcxx-200100 duration distribution");
            const auto identity=json::parse(kEngineIdentity);
            const char* expectedPatches=cold2317
                ?"bc80791e28e7559b81c33036c91b8163cfe611d9d9793e7d3e10f8cb4e5290c8"
                :"cd01f0f3cce4f6be05d781b06192dadadbd8254a6fa1c03ea52394d3e48f9ded";
            if(!roundedClock||frames>30||channels!=1||
               identity.value("patches_sha256","")!=expectedPatches||
               identity.value("commit","")!="e0b0a967f0ffd7d332106c366668ed271718472b"||
               !request.contains("entropy_seed")||!request.at("entropy_seed").is_number_integer()||
               request.at("entropy_seed").get<double>()<0||request.at("entropy_seed").get<double>()>UINT32_MAX)
                throw std::runtime_error(std::string("cold JNI progress requires pinned ")+(cold2317?"2.3.17":"2.3.16")+", mono rounded-clock <=30 frames and uint32 entropy seed");
            entropySeed=request.at("entropy_seed").get<uint32_t>();
            std::mt19937 generator(entropySeed);
            // Initialize: idle hard load, explicit StartPreset; first JNI draw: authored hard load.
            // TimeKeeper constructs a fresh distribution each call, discarding its cached companion.
            for(int load=0;load<3;++load) {
                std::normal_distribution<double> distribution(30.0,1.0);
                presetDuration=std::max(1.0,distribution(generator));
            }
        } else if(progressPolicy!="explicit-zero-placeholder-v1"||request.contains("entropy_seed")) {
            throw std::runtime_error("unsupported preset progress policy/seed");
        }
        const size_t block=44100/fps;
        std::ifstream pcmFile(request.at("pcm_path").get<std::string>(),std::ios::binary);
        if(!pcmFile)throw std::runtime_error("cannot read PCM");
        std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(pcmFile)),std::istreambuf_iterator<char>());
        if(bytes.size()!=static_cast<size_t>(frames)*block*channels*4)throw std::runtime_error("PCM length does not match complete frames");
        std::vector<float> samples(bytes.size()/4);
        for(size_t i=0;i<samples.size();++i) {
            uint32_t word=0;for(int j=0;j<4;++j)word|=static_cast<uint32_t>(bytes[i*4+j])<<(j*8);
            std::memcpy(&samples[i],&word,4);
            if(!std::isfinite(samples[i])||std::abs(samples[i])>1)throw std::runtime_error("invalid/out-of-range PCM sample");
        }
        json report={{"schema_version",1},{"basis","pinned native PCM/FFT/alignment and relative bands; no graphics context"},
            {"uses_rendered_reference",false},{"engine_archive_sha256",kEngineArchiveSha},{"engine_identity",json::parse(kEngineIdentity)},
            {"pcm_sha256",digest(bytes)},{"pcm_encoding","float32 little endian interleaved"},{"sample_rate",44100},
            {"fps",fps},{"channels",channels},{"render_clock_policy",clockPolicy},
            {"preset_progress_policy",progressPolicy},{"duration_distribution_model",kDurationDistribution},
            {"frames",json::array()}};
        if(coldProgress)report["preset_timing"]={{"sampled_duration_seconds",presetDuration},
            {"entropy_seed",entropySeed},{"duration_draws",3},{"mean_seconds",30.0},{"modifier_seconds",1.0},
            {"distribution_lifetime","fresh per draw"},{"preset_start_seconds",0.0},
            {"equation_fps",35},{"physical_fps",30},
            {"conditional_host","cold ready single-preset JNI host; no intervening reload, failure or smoothing"}};
        libprojectM::Audio::PCM pcm;double previous=0;
        for(int frame=0;frame<frames;++frame) {
            size_t count=std::min<size_t>(block,libprojectM::Audio::AudioBufferSamples);
            pcm.Add(samples.data()+(static_cast<size_t>(frame)*block+block-count)*channels,channels,count);
            double time=static_cast<double>(frame+1)/fps;
            int64_t clockNanoseconds=0;
            if(roundedClock) {
                // Match the declared JNI helper's Java Math.round at 30 Hz.
                // Use the same elapsed clock for both EEL inputs and loudness decay.
                clockNanoseconds=static_cast<int64_t>(std::floor((frame+1)*1000000000.0/30.0+0.5));
                time=static_cast<double>(clockNanoseconds)/1000000000.0;
            }
            pcm.UpdateFrameAudioData(time-previous,frame);previous=time;
            auto values=pcm.GetFrameAudioData();
            report["frames"].push_back({{"time",time},{"frame",frame},{"fps",coldProgress?35:fps},
                {"progress",coldProgress?std::min(1.0,time/presetDuration):0.0},
                {"bass",values.bass},{"mid",values.mid},{"treb",values.treb},{"bass_att",values.bassAtt},
                {"mid_att",values.midAtt},{"treb_att",values.trebAtt},{"vol",values.vol},{"vol_att",values.volAtt},
                {"waveform_left",values.waveformLeft},{"waveform_right",values.waveformRight},
                {"spectrum_left",values.spectrumLeft},{"spectrum_right",values.spectrumRight}});
            if(roundedClock)report["frames"].back()["clock_nanoseconds"]=clockNanoseconds;
        }
        std::filesystem::path output=request.at("output").get<std::string>();
        if(!output.parent_path().empty())std::filesystem::create_directories(output.parent_path());
        auto partial=output;partial+=".partial";
        std::ofstream saved(partial);saved<<report.dump()<<'\n';saved.close();
        if(!saved)throw std::runtime_error("cannot write audio report");
        std::filesystem::rename(partial,output);
        std::cout<<json({{"status","success"},{"frames",frames},{"output",output.string()},{"uses_rendered_reference",false}}).dump()<<'\n';
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
