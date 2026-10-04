// Exercise the patched engine itself, including the evaluator and real GL drawing.
#include "gl_context.hpp"
#include <HLSLParser.h>
#include <HLSLTree.h>
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>

#ifdef __APPLE__
#include <OpenGL/OpenGL.h>
#else
#include <EGL/egl.h>
#endif

#include <cmath>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static void Check(bool ok, const char* message)
{
    if (!ok) throw std::runtime_error(message);
}

static void TestMacros()
{
    for (const auto& source : {
             "#define sampler_rand00 sampler_rand00\nsampler2D sampler_rand00;\n",
             "#define value value\nfloat value;\n#define alias value\nfloat result = alias;\n",
             "#define value 2\n#define twice(x) x * 2\nfloat result = twice(value);\n"})
    {
        M4::Allocator allocator;
        M4::HLSLTree tree(&allocator);
        M4::HLSLParser parser(&allocator, &tree);
        std::string input(source), output;
        Check(parser.ApplyPreprocessor("regression.hlsl", input.data(), input.size(), output),
              "macro preprocessing failed");
        Check(parser.Parse("regression.hlsl", output.data(), output.size()),
              "preprocessed shader did not parse");
        Check(tree.FindGlobalDeclaration(input.find("sampler_rand00") != std::string::npos
                                            ? "sampler_rand00" : "result") != nullptr,
              "macro preprocessing lost a declaration");
    }
}

static void TestWaveforms()
{
    GLContext gl;
    using namespace libprojectM::MilkdropPreset;
    PresetState state;
    state.renderContext.viewportSizeX = 16;
    state.renderContext.viewportSizeY = 16;
    state.renderContext.invAspectX = 1;
    state.renderContext.invAspectY = 1;
    PerFrameContext frame(state.globalMemory, &state.globalRegisters);
    frame.RegisterBuiltinVariables();
    for (size_t i = 0; i < state.audioData.waveformLeft.size(); ++i)
    {
        state.audioData.waveformLeft[i] = static_cast<float>(i);
        state.audioData.waveformRight[i] = -static_cast<float>(i);
    }
    for (size_t i = 0; i < state.audioData.spectrumLeft.size(); ++i)
    {
        state.audioData.spectrumLeft[i] = static_cast<float>(i);
        state.audioData.spectrumRight[i] = -static_cast<float>(i);
    }
    // Per-point code reports how many points ran and the final audio values through real
    // evaluator registers, independently of the GL driver's rasterization.
    state.customWavePerPointCode[0] = "reg00=reg00+1;reg01=value1;reg02=value2;reg03=sample;";
    struct Case { bool spectrum; int samples; int separation; int points; float last; };
    for (const auto& test : {
             Case{false, 480, 0, 480, 1.916f},
             Case{false, 480, 1000000, 480, 1.916f},
             Case{false, 480, -1000000, 480, 1.916f},
             Case{false, 512, 0, 512, 1.916f},
             Case{false, 1000000, 0, 512, 1.916f},
             Case{false, 2, 0, 2, 0.004f},
             Case{true, 512, 0, 512, 76.65f},
             Case{true, 512, 1000000, 512, 0.0f},
             Case{true, 512, -1000000, 512, 76.65f},
             Case{true, 2, 1, 2, 38.25f},
             Case{false, -1, 0, 0, 0.0f},
             Case{false, 0, 0, 0, 0.0f},
             Case{false, 1, 0, 0, 0.0f},
             Case{true, 0, 1000000, 0, 0.0f}})
    {
        std::cout << "waveform spectrum=" << test.spectrum << " samples=" << test.samples
                  << " sep=" << test.separation << std::endl;
        std::ostringstream text;
        text << "[preset00]\nwavecode_0_enabled=1\nwavecode_0_samples=" << test.samples
             << "\nwavecode_0_sep=" << test.separation
             << "\nwavecode_0_bSpectrum=" << test.spectrum << "\nwavecode_0_smoothing=0\n";
        std::istringstream input(text.str());
        PresetFileParser preset;
        Check(preset.Read(input), "fixture preset did not parse");
        CustomWaveform wave(state);
        wave.Initialize(preset, 0);
        std::vector<std::string> warnings;
        wave.CompileCodeAndRunInitExpressions(frame, warnings);
        Check(warnings.empty(), "fixture waveform code did not compile");
        for (auto& value : state.globalRegisters) value = 0;
        wave.Draw(frame);
        Check(state.globalRegisters[0] == test.points, "wrong number of waveform points");
        if (test.points)
        {
            Check(std::abs(state.globalRegisters[1] - test.last) < 0.0001,
                  "wrong left-channel sample");
            Check(std::abs(state.globalRegisters[2] + test.last) < 0.0001,
                  "wrong right-channel sample");
            Check(state.globalRegisters[3] == 1.0, "waveform did not reach its endpoint");
        }
    }
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "expected macro or waveform");
        const std::string mode(argv[1]);
        if (mode == "macro") TestMacros();
        else if (mode == "waveform") TestWaveforms();
        else throw std::runtime_error("unknown test mode");
        std::cout << mode << " regressions passed\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
