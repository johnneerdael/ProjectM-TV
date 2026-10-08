#include "gl_context.hpp"
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <cmath>
#include <array>
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
static PFNGLDRAWELEMENTSPROC realElements{};
static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced{};
static std::vector<std::pair<GLenum, int>> submissions;
static std::vector<std::array<float, 4>> endpoints;
static void ObserveElements(GLenum primitive, GLsizei count, GLenum type, const void* indices)
{
    submissions.emplace_back(primitive, count);
    GLint buffer{}, previous{};
    glGetVertexAttribiv(0, GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING, &buffer);
    glGetIntegerv(GL_ARRAY_BUFFER_BINDING, &previous); glBindBuffer(GL_ARRAY_BUFFER, buffer);
    const auto* points = static_cast<const Point*>(glMapBufferRange(
        GL_ARRAY_BUFFER, 0, count * sizeof(Point), GL_MAP_READ_BIT));
    Check(points != nullptr, "dot geometry readback failed");
    endpoints.push_back({points[0].X(), points[0].Y(), points[count - 1].X(), points[count - 1].Y()});
    glUnmapBuffer(GL_ARRAY_BUFFER); glBindBuffer(GL_ARRAY_BUFFER, previous);
    realElements(primitive, count, type, indices);
}
static void ObserveInstanced(GLenum primitive, GLint first, GLsizei count, GLsizei instances)
{
    submissions.emplace_back(primitive, instances);
    realInstanced(primitive, first, count, instances);
}
static void Dots(ShaderCache& cache)
{
    realElements = glad_glDrawElements; glad_glDrawElements = ObserveElements;
    realInstanced = glad_glDrawArraysInstanced; glad_glDrawArraysInstanced = ObserveInstanced;
    for (bool dots : {true, false}) for (bool thick : {false, true}) for (int samples : {2, 1, 0})
    {
        PresetState state; auto& context = state.renderContext;
        context.shaderCache = &cache; state.LoadShaders();
        context.viewportSizeX = context.viewportSizeY = 128;
        context.lineReferenceWidth = context.lineReferenceHeight = 64;
        context.aspectX = context.aspectY = context.invAspectX = context.invAspectY = 1;
        std::istringstream source("wavecode_0_enabled=1\nwavecode_0_samples=" + std::to_string(samples) +
            "\nwavecode_0_bUseDots=" + std::to_string(dots) + "\nwavecode_0_bDrawThick=" +
            std::to_string(thick) + "\nwavecode_0_smoothing=0\n"
            "wave_0_per_point1=" + (samples == 1 ? std::string("x=.25;") : std::string("x=.25+.5*sample;")) +
            "y=.5;r=1;g=0;b=0;a=1;reg00+=1;reg01=sample;\n");
        PresetFileParser parser; Check(parser.Read(source), "could not parse finite dot control");
        state.customWavePerPointCode[0] = parser.GetCode("wave_0_per_point");
        PerFrameContext frame(state.globalMemory, &state.globalRegisters);
        frame.RegisterBuiltinVariables(); frame.LoadStateVariables(state);
        CustomWaveform wave(state); wave.Initialize(parser, 0);
        std::vector<std::string> warnings; wave.CompileCodeAndRunInitExpressions(frame, warnings);
        Check(warnings.empty(), "finite dot code failed to compile");
        Framebuffer canvas(1), native(1);
        canvas.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
        native.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
        canvas.SetSize(64, 64); native.SetSize(128, 128);
        GeometryTargets targets(state, canvas, 0, 64, 64, {}, native, 0);
        submissions.clear(); endpoints.clear(); targets.Authored(); wave.Draw(frame, &targets);
        Check(glGetError() == GL_NO_ERROR, "finite dot draw GL error");
        const int evaluated = dots ? samples : samples >= 2 ? samples : 0;
        Check(state.globalRegisters[0] == evaluated, "wrong point count or Native replay evaluated code twice");
        if (evaluated == 0) {
            Check(submissions.empty(), "empty or single-line wave submitted geometry"); continue;
        }
        if (samples == 1)
            Check(std::isnan(state.globalRegisters[1]), "single-dot sample input invented a finite value");
        if (dots)
        {
            Check(submissions.size() == 2, "dot replay changed pass count");
            for (const auto& draw : submissions)
                Check(draw.first == GL_POINTS && draw.second == samples,
                      "finite two-point dot wave acquired an interpolated midpoint");
        }
        else
        {
            // Authored strips retain their 2N-1 smoothed points; Native quads
            // retain two smoothed segments per pass, including all thick passes.
            for (const auto& draw : submissions)
                Check((draw.first == GL_LINE_STRIP && draw.second == 3) ||
                      (draw.first == GL_TRIANGLE_STRIP && draw.second == 2), "line smoothing changed");
        }
        if (dots) for (const auto& point : endpoints)
            Check(std::abs(point[0] + .5f) < 1e-6f && std::abs(point[1]) < 1e-6f &&
                  std::abs(point[2] - (samples == 1 ? -.5f : .5f)) < 1e-6f && std::abs(point[3]) < 1e-6f,
                  "wave endpoint positions changed");
    }
    glad_glDrawElements = realElements; glad_glDrawArraysInstanced = realInstanced;
}
int main(int argc, char** argv)
{
    try {
        GLContext gl; ShaderCache cache;
        if (argc == 2 && std::string(argv[1]) == "dots") {
            Dots(cache); std::cout << "Custom dots retain authored points and line smoothing\n"; return 0;
        }
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
