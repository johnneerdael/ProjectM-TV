// Pinned image decoder + SOIL alpha processing; no GL calls or context.
#include "vendor/json.hpp"
#include "image_inputs.hpp"
#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>
#include <fstream>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
using json=nlohmann::json;

int main(int argc,char** argv) {
    try {
        if(argc!=2)throw std::runtime_error("usage: milk-image-inputs request.json");
        std::ifstream input(argv[1]);json request;input>>request;
        if(!request.at("maximum_texture_size").is_number_integer())throw std::runtime_error("integer size limit required");
        int maximum=request.at("maximum_texture_size");
        if(maximum<1||maximum>16384)throw std::runtime_error("texture size outside decoder budget");
        json rows=json::array();
        for(const auto& file:request.at("files")) {
            std::string path=file.at("input"),output=file.at("output");
            int width=0,height=0,channels=0;
            if(!stbi_info(path.c_str(),&width,&height,&channels))throw std::runtime_error("cannot read source image header");
            if(width<1||height<1||width>maximum||height>maximum)throw std::runtime_error("source texture size requires unsupported rescaling");
            unsigned char* decoded=stbi_load(path.c_str(),&width,&height,&channels,4);
            if(!decoded)throw std::runtime_error(std::string("source image decode failed: ")+stbi_failure_reason());
            std::unique_ptr<unsigned char,decltype(&stbi_image_free)> pixels(decoded,stbi_image_free);
            // SOIL_internal_create_OGL_texture, SOIL_FLAG_MULTIPLY_ALPHA, case 4.
            std::size_t size=static_cast<std::size_t>(width)*height*4;
            for(std::size_t i=0;i<size;i+=4) {
                decoded[i+0]=(decoded[i+0]*decoded[i+3]+128)>>8;
                decoded[i+1]=(decoded[i+1]*decoded[i+3]+128)>>8;
                decoded[i+2]=(decoded[i+2]*decoded[i+3]+128)>>8;
            }
            std::ofstream saved(output,std::ios::binary);
            saved.write(reinterpret_cast<char*>(decoded),static_cast<std::streamsize>(size));saved.close();
            if(!saved)throw std::runtime_error("cannot write source texture input");
            rows.push_back({{"width",width},{"height",height},{"channels",4},{"output",output}});
        }
        std::cout<<json({{"schema_version",1},{"rows",rows},{"uses_rendered_reference",false},
            {"decoder_source_sha256",kImageDecoderSha},
            {"decoder_backend",kImageDecoderBackend},
            {"decoder_implementation_source_path",kImageImplementationPath},
            {"decoder_implementation_source_sha256",kImageImplementationSha},
            {"soil_source_sha256",std::string(kSoilSourceSha).empty()?json(nullptr):json(kSoilSourceSha)},
            {"texture_manager_sha256",kTextureManagerSha},{"upload_encoding","RGBA8 premultiplied; original row order"},
            {"limits","No GL texture-size query/rescaling, mipmaps, missing-placeholder state or target driver validation"}}).dump()<<'\n';
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
