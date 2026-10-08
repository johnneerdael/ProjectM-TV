// CPU-only procedural shader inputs from the pinned projectM implementation.
// No OpenGL context, texture upload, preset rendering or reference images.
#ifndef MILK_RAW_NOISE_ADAPTER
#include "Renderer/MilkdropNoise.hpp"
#endif
#include "vendor/json.hpp"
#include "reader_inputs.hpp"
#include <cstdint>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <random>
#include <climits>
#ifdef MILK_RAW_NOISE_ADAPTER
#include "Renderer/OpenGL.h"
#include "cpu_noise_adapter.hpp"
#endif
#ifdef __APPLE__
#include <CommonCrypto/CommonDigest.h>
#else
#include <openssl/sha.h>
#endif

using json=nlohmann::json;
#ifdef MILK_RAW_NOISE_ADAPTER
using NoiseAccess=MilkdropNoise;
#else
struct NoiseAccess:libprojectM::Renderer::MilkdropNoise {
    using MilkdropNoise::generate2D;
    using MilkdropNoise::generate3D;
    using MilkdropNoise::GetPreferredInternalFormat;
};
#endif

std::string sha256(const std::vector<unsigned char>& bytes) {
    unsigned char digest[32];
#ifdef __APPLE__
    CC_SHA256(bytes.data(),static_cast<CC_LONG>(bytes.size()),digest);
#else
    SHA256(bytes.data(),bytes.size(),digest);
#endif
    std::ostringstream out;
    for(auto value:digest)out<<std::hex<<std::setfill('0')<<std::setw(2)<<static_cast<int>(value);
    return out.str();
}

int main(int argc,char** argv) {
    try {
        if(argc!=2)throw std::runtime_error("usage: milk-noise-inputs request.json");
        std::ifstream input(argv[1]);if(!input)throw std::runtime_error("cannot read request");
        json request;input>>request;
        if(!request.at("seed").is_number_integer()||request.at("seed")<0||request.at("seed")>UINT32_MAX)
            throw std::runtime_error("seed must be uint32");
        auto seed=request.at("seed").get<uint32_t>();
        const auto policy=request.value("seed_policy",std::string("lab-subsystem-seed-v1"));
        if(policy!="lab-subsystem-seed-v1" && policy!="production-clock-seed-v1")
            throw std::runtime_error("unsupported procedural seed policy");
        const auto identity=json::parse(kEngineIdentity);
        const bool knownMix=identity.value("instrumentation_sha256",std::string{})==
            "254db5d7418da6162c8db449ed400df19e9b6391ba405c0d20a0e19c3a005ef8";
#ifdef MILK_RAW_NOISE_ADAPTER
        const bool rawNoise=identity.value("commit","")=="6f64807467e312034883a4389e6aa80a675458bc" &&
            (identity.value("patches_sha256","")=="fd02c15d040ca073f7c09a0b798040c2696fa6bf2252d6ddc6c7b6ff7bcd92eb" || identity.value("patches_sha256","")=="3ade58a837591acde97d07a45f703d53047bbe0fc3993149bdfe0dd54298a381" || identity.value("patches_sha256","")=="6e27be9d314e464c6ed67925c65092164e35e8a1b5273f81b1bf0b6786beefae");
        if(!rawNoise || policy!="production-clock-seed-v1")
            throw std::runtime_error("raw native noise requires exact 4.2 identity and production-clock seed policy");
#else
        const bool rawNoise=false;
#endif
        if(policy=="production-clock-seed-v1" && !knownMix && !rawNoise)
            throw std::runtime_error("production noise seed requires verified lab instrumentation");
        std::filesystem::path output=request.at("output").get<std::string>();
        std::filesystem::create_directories(output);
        struct Settings {int size,zoom,dimensions;};
        const std::map<std::string,Settings> settings={
            {"noise_lq",{256,1,2}},{"noise_lq_lite",{32,1,2}},
            {"noise_mq",{256,4,2}},{"noise_hq",{256,8,2}},
            {"noisevol_lq",{32,1,3}},{"noisevol_hq",{32,4,3}}};
        json manifest={{"schema_version",1},{"basis","pinned native procedural texture generation"},
            {"uses_rendered_reference",false},{"seed",seed},{"seed_policy",policy},
            {"engine_archive_sha256",kEngineArchiveSha},
            {"engine_identity",json::parse(kEngineIdentity)},{"packed_word_encoding","uint32 little endian"},
            {"native_upload_format",NoiseAccess::GetPreferredInternalFormat()==GL_BGRA?"BGRA":"RGBA"},
            {"textures",json::object()}};
#ifdef MILK_RAW_NOISE_ADAPTER
        manifest["seed_model"]="raw-declared-native-noise-v1";
        manifest["source_sha256"]=kNoiseSourceSha;
        manifest["math_body_sha256"]=kNoiseMathSha;
        manifest["adapted_body_sha256"]=kNoiseAdaptedSha;
#endif
        for(const auto& value:request.at("names")) {
            auto name=value.get<std::string>();auto found=settings.find(name);
            if(found==settings.end())throw std::runtime_error("unknown builtin noise input: "+name);
            auto spec=found->second;
            // The private archive XORs lab::Seed(101) with dimensions. Invert
            // only that verified test-host policy to supply production's raw seed.
            const uint32_t mix=101u*0x9e3779b9u ^ static_cast<uint32_t>(spec.size*31+spec.zoom);
            const uint32_t configured=rawNoise ? seed : policy=="production-clock-seed-v1" ? seed^mix : seed;
#ifdef MILK_RAW_NOISE_ADAPTER
            declaredNoiseSeed=configured;
#endif
            const auto seedText=std::to_string(configured);
            if(setenv("PRESET_LAB_SEED",seedText.c_str(),1)!=0)
                throw std::runtime_error("cannot set procedural seed");
            auto words=spec.dimensions==2?NoiseAccess::generate2D(spec.size,spec.zoom):NoiseAccess::generate3D(spec.size,spec.zoom);
            std::vector<unsigned char> bytes;bytes.reserve(words.size()*4);
            for(auto word:words)for(int shift=0;shift<32;shift+=8)bytes.push_back(static_cast<unsigned char>(word>>shift));
            auto file=name+".u32le";std::ofstream target(output/file,std::ios::binary);
            target.write(reinterpret_cast<const char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));
            target.close();if(!target)throw std::runtime_error("cannot write procedural input");
            manifest["textures"][name]={{"dimensions",{spec.size,spec.size,spec.dimensions==3?spec.size:1}},
                {"zoom_factor",spec.zoom},{"file",file},{"sha256",sha256(bytes)}};
            if(knownMix||rawNoise)manifest["textures"][name]["generator_seed"]=rawNoise?configured:configured^mix;
        }
        std::ofstream saved(output/"manifest.json");saved<<manifest.dump(2)<<'\n';saved.close();
        if(!saved)throw std::runtime_error("cannot write manifest");
        std::cout<<manifest.dump()<<'\n';return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
