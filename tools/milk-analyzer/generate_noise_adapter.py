"""Extract native noise math with an explicit clock-seed input; no GPU calls."""
import argparse
import hashlib
from pathlib import Path

def generate(engine,output):
    raw=(engine/'src/libprojectM/Renderer/MilkdropNoise.cpp').read_bytes()
    source=raw.decode();start=source.index('auto MilkdropNoise::generate2D(')
    end=source.index('} // namespace Renderer',start);bodies=source[start:end]
    clock='static_cast<uint32_t>(std::chrono::system_clock::now().time_since_epoch().count())'
    if bodies.count(clock)!=2:raise ValueError('native noise clock sites changed')
    adapted=bodies.replace(clock,'declaredNoiseSeed')
    output.write_text('#pragma once\n'+
        f'inline constexpr const char* kNoiseSourceSha="{hashlib.sha256(raw).hexdigest()}";\n'+
        f'inline constexpr const char* kNoiseMathSha="{hashlib.sha256(bodies.encode()).hexdigest()}";\n'+
        f'inline constexpr const char* kNoiseAdaptedSha="{hashlib.sha256(adapted.encode()).hexdigest()}";\n'+
        'inline uint32_t declaredNoiseSeed=0;\n'+
        'struct MilkdropNoise {\n'+
        ' static auto generate2D(int,int)->std::vector<uint32_t>;\n'+
        ' static auto generate3D(int,int)->std::vector<uint32_t>;\n'+
        ' static float fCubicInterpolate(float,float,float,float,float);\n'+
        ' static uint32_t dwCubicInterpolate(uint32_t,uint32_t,uint32_t,uint32_t,float);\n'+
        ' static int GetPreferredInternalFormat(){return GL_BGRA;}\n};\n'+adapted)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--engine',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();generate(args.engine,args.output)
