#include "gl_context.hpp"
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/Waveforms/Factory.hpp>
#include <Renderer/ShaderCache.hpp>
#include <iostream>
#include <stdexcept>
#include <string>
using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool value,const std::string& message){if(!value)throw std::runtime_error(message);}
static void Configure(PresetState& state,ShaderCache& cache){
 state.renderContext.shaderCache=&cache;
 state.renderContext.viewportSizeX=state.renderContext.viewportSizeY=64;
 state.renderContext.aspectX=state.renderContext.aspectY=1;
 state.renderContext.invAspectX=state.renderContext.invAspectY=1;
 state.LoadShaders();
}
static void Samples(ShaderCache& cache)
{
    struct Canvas { int width, height, referenceWidth, referenceHeight, derivative, line; };
    const Canvas canvases[] = {
        {1, 1, 0, 0, 2, 2},
        {8, 8, 0, 0, 2, 2},
        {256, 144, 0, 0, 85, 85},
        {1024, 768, 0, 0, 341, 240},
        {3840, 2160, 0, 0, 480, 240},
        {3840, 2160, 1024, 768, 394, 240},
        {3840, 2160, 1280, 720, 426, 240},
        {1280, 720, 1280, 720, 426, 240},
    };
    PresetState state; state.audioData={}; Configure(state, cache);
    PerFrameContext frame(state.globalMemory, &state.globalRegisters); frame.RegisterBuiltinVariables();
    for (const auto& canvas : canvases)
    {
        auto& context = state.renderContext;
        context.viewportSizeX = canvas.width; context.viewportSizeY = canvas.height;
        context.lineReferenceWidth = canvas.referenceWidth; context.lineReferenceHeight = canvas.referenceHeight;
        frame.LoadStateVariables(state);
        for (int mode : {4, 6, 7, 8})
        {
            auto math = Waveforms::Factory::Create(static_cast<WaveformMode>(mode));
            const auto vertices = math->GetVertices(state, frame);
            // Smoothing returns 2N-1 points; it must not change the raw sample budget.
            const auto expected = mode == 4 ? canvas.derivative : mode == 8 ? 256 : canvas.line;
            const auto label = "mode " + std::to_string(mode) + " width " + std::to_string(canvas.width) +
                               " reference " + std::to_string(canvas.referenceWidth);
            Check(vertices[0].size() == size_t(2 * expected - 1),
                  label + " expected raw samples " + std::to_string(expected) +
                  " got " + std::to_string((vertices[0].size() + 1) / 2));
            Check(vertices[1].size() == (mode == 7 ? vertices[0].size() : 0), label + " wrong second-wave count");
        }
    }
}
int main(){try{GLContext gl;ShaderCache cache;Samples(cache);std::cout<<"Source sample caps/reference widths and unchanged extended mode pass\n";return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
