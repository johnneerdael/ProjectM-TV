// Exact pinned PCM/FFT/alignment/band execution without graphics or image input.
#include "Audio/PCM.hpp"
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif

using json=nlohmann::json;
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
            {"fps",fps},{"channels",channels},{"frames",json::array()}};
        libprojectM::Audio::PCM pcm;double previous=0;
        for(int frame=0;frame<frames;++frame) {
            size_t count=std::min<size_t>(block,libprojectM::Audio::AudioBufferSamples);
            pcm.Add(samples.data()+(static_cast<size_t>(frame)*block+block-count)*channels,channels,count);
            double time=static_cast<double>(frame+1)/fps;
            pcm.UpdateFrameAudioData(time-previous,frame);previous=time;
            auto values=pcm.GetFrameAudioData();
            report["frames"].push_back({{"time",time},{"frame",frame},{"fps",fps},{"progress",0},
                {"bass",values.bass},{"mid",values.mid},{"treb",values.treb},{"bass_att",values.bassAtt},
                {"mid_att",values.midAtt},{"treb_att",values.trebAtt},{"vol",values.vol},{"vol_att",values.volAtt},
                {"waveform_left",values.waveformLeft},{"waveform_right",values.waveformRight},
                {"spectrum_left",values.spectrumLeft},{"spectrum_right",values.spectrumRight}});
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
