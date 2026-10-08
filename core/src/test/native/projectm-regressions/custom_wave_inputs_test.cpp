#include "gl_context.hpp"
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <cmath>
#include <iostream>
#include <sstream>
#include <stdexcept>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool value, const std::string& message)
{
    if (!value) throw std::runtime_error(message);
}
static void Window(ShaderCache& cache, int samples, int separation, bool spectrum,
                   int firstLeft, int firstRight, int lastLeft, int lastRight, bool replay)
{
    PresetState state;
    auto& context = state.renderContext;
    context.shaderCache = &cache;
    context.viewportSizeX = context.viewportSizeY = 128;
    context.lineReferenceWidth = context.lineReferenceHeight = 64;
    context.aspectX = context.aspectY = context.invAspectX = context.invAspectY = 1;
    context.fps = 30; state.LoadShaders();
    const int maxSamples = spectrum ? libprojectM::Audio::SpectrumSamples : libprojectM::Audio::WaveformSamples;
    for (int i = 0; i < maxSamples; ++i)
    {
        const float left = float(i) / maxSamples, right = float(2 * i + 1) / maxSamples;
        if (spectrum) { state.audioData.spectrumLeft[i] = left; state.audioData.spectrumRight[i] = right; }
        else { state.audioData.waveformLeft[i] = left; state.audioData.waveformRight[i] = right; }
    }
    std::istringstream source("wavecode_0_enabled=1\nwavecode_0_samples=" + std::to_string(samples) +
        "\nwavecode_0_sep=" + std::to_string(separation) + "\nwavecode_0_bSpectrum=" +
        std::to_string(spectrum) + "\nwavecode_0_smoothing=0\nwavecode_0_scaling=1\n"
        "wave_0_per_point1=reg00=if(equal(sample,0),value1,reg00);reg01=if(equal(sample,0),value2,reg01);"
        "reg02=value1;reg03=value2;reg04=reg04+1;x=sample;y=.5;\n");
    PresetFileParser parser; Check(parser.Read(source), "could not parse window control");
    state.customWavePerPointCode[0] = parser.GetCode("wave_0_per_point");
    PerFrameContext frame(state.globalMemory, &state.globalRegisters);
    frame.RegisterBuiltinVariables(); frame.LoadStateVariables(state);
    CustomWaveform wave(state); wave.Initialize(parser, 0);
    std::vector<std::string> warnings;
    wave.CompileCodeAndRunInitExpressions(frame, warnings);
    Check(warnings.empty(), "window point code failed to compile");
    Framebuffer canvas(1), native(1);
    canvas.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
    native.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
    canvas.SetSize(64, 64); native.SetSize(128, 128);
    GeometryTargets targets(state, canvas, 0, 64, 64, {}, native, 0);
    targets.Authored(); wave.Draw(frame, replay ? &targets : nullptr);
    Check(glGetError() == GL_NO_ERROR, "window draw GL error");
    const float factor = spectrum ? .15f : .004f;
    const float expected[] = {float(firstLeft) / maxSamples * factor,
        float(2 * firstRight + 1) / maxSamples * factor,
        float(lastLeft) / maxSamples * factor, float(2 * lastRight + 1) / maxSamples * factor};
    const std::string label = "samples=" + std::to_string(samples) + " sep=" + std::to_string(separation) +
                              " spectrum=" + std::to_string(spectrum) + " replay=" + std::to_string(replay);
    for (int i = 0; i < 4; ++i)
        Check(std::abs(state.globalRegisters[i] - expected[i]) < 1e-7,
              label + " input " + std::to_string(i) + " expected " + std::to_string(expected[i]) +
              " got " + std::to_string(state.globalRegisters[i]));
    Check(state.globalRegisters[4] == samples, label + " reevaluated point code during Native replay");
    Check(context.viewportSizeX == 64 && context.lineReferenceWidth == 0, label + " lost authored context");
}
int main()
{
    try {
        GLContext gl; ShaderCache cache;
        for (bool replay : {false, true}) {
            Window(cache, 2, 0, false, 239, 239, 240, 240, replay);
            Window(cache, 4, 2, false, 237, 239, 240, 242, replay);
            Window(cache, 4, -2, false, 239, 237, 242, 240, replay);
            Window(cache, 4, 470, false, 3, 473, 6, 476, replay);
            Window(cache, 480, 0, false, 0, 0, 479, 479, replay);
            // Preserve the upstream safety contracts outside valid original windows.
            Window(cache, 512, 17, false, 0, 0, 479, 479, replay);
            Window(cache, 480, 2, false, 0, 0, 479, 479, replay);
            Window(cache, 4, 2, true, 0, 0, 382, 382, replay);
        }
        std::cout << "Centered finite windows, safe fallbacks, spectrum and prepared replay pass\n";
        return 0;
    } catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
