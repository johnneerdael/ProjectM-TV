// Independent MilkDrop 2.25c controls: milkdropfs.cpp 2927-2946, 3359, 4117-4144.
#include "gl_context.hpp"
#include <MilkdropPreset/FinalComposite.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/Waveform.hpp>
#include <MilkdropPreset/Waveforms/Factory.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/Texture.hpp>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}
struct Surface
{
    std::shared_ptr<Texture> texture;
    GLuint fbo{};
    Surface()
        : texture(std::make_shared<Texture>("control", GL_TEXTURE_2D, 64, 64, 1,
                                            GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false))
    {
        glGenFramebuffers(1, &fbo); Bind();
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                               texture->TextureID(), 0);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "incomplete FBO");
    }
    ~Surface() { glDeleteFramebuffers(1, &fbo); }
    void Bind() { glBindFramebuffer(GL_FRAMEBUFFER, fbo); glViewport(0, 0, 64, 64); }
    std::vector<unsigned char> Pixels()
    {
        std::vector<unsigned char> pixels(64 * 64 * 4);
        glReadPixels(0, 0, 64, 64, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
        Check(glGetError() == GL_NO_ERROR, "readback GL error");
        return pixels;
    }
};
static void Configure(PresetState& state, ShaderCache& cache)
{
    state.renderContext.shaderCache = &cache;
    state.renderContext.viewportSizeX = state.renderContext.viewportSizeY = 64;
    state.renderContext.aspectX = state.renderContext.aspectY = 1;
    state.renderContext.invAspectX = state.renderContext.invAspectY = 1;
    state.renderContext.time = .5f;
    state.LoadShaders();
    state.hueRandomOffsets.fill(0);
}
static void Hue(ShaderCache& cache)
{
    Surface input, output;
    input.Bind(); glClearColor(64.f / 255, 128.f / 255, 192.f / 255, 1); glClear(GL_COLOR_BUFFER_BIT);
    PresetState state; Configure(state, cache);
    state.mainTexture = input.texture;
    state.gammaAdj = 1; state.videoEchoZoom = 1;
    state.compositeShaderVersion = 0;
    PerFrameContext frame(state.globalMemory, &state.globalRegisters); frame.RegisterBuiltinVariables();
    FinalComposite composite; composite.LoadCompositeShader(state);
    for (float echo : {0.f, .5f, 1.f})
    {
        state.videoEchoAlpha = echo;
        std::vector<unsigned char> fullHue;
        for (float amount : {1.f, 0.f, .001f, .5f})
        {
            state.shader = amount; frame.LoadStateVariables(state);
            output.Bind(); composite.Draw(state, frame);
            const auto pixels = output.Pixels();
            if (amount == 1) { fullHue = pixels; continue; }
            for (size_t i = 0; i < pixels.size(); ++i)
            {
                if (i % 4 == 3) continue;
                const int original = 64 * (int(i % 4) + 1);
                const float expected = amount <= .001f ? original : .5f * (original + fullHue[i]);
                Check(std::abs(pixels[i] - expected) <= 2,
                      "legacy fShader=" + std::to_string(amount) + " unexpectedly tinted a constant texel");
            }
        }
    }
}
static PFNGLDRAWELEMENTSPROC realDraw{};
static std::vector<float> alphas;
static std::vector<GLenum> primitives;
static void Observe(GLenum mode, GLsizei count, GLenum type, const void* indices)
{
    float color[4]{}; glGetVertexAttribfv(1, GL_CURRENT_VERTEX_ATTRIB, color);
    alphas.push_back(color[3]); primitives.push_back(mode);
    realDraw(mode, count, type, indices);
}
static void Wave(ShaderCache& cache, bool topology)
{
    Surface output;
    PresetState state; Configure(state, cache);
    state.waveMode = 1; state.waveAlpha = .4f;
    state.waveR = 1; state.waveG = state.waveB = 0;
    state.waveScale = 128; state.waveParam = -.5f;
    state.waveX = state.waveY = .5f;
    for (size_t i = 0; i < state.audioData.waveformLeft.size(); ++i)
    {
        state.audioData.waveformLeft[i] = .3f * std::sin(i * .13f);
        state.audioData.waveformRight[i] = .2f * std::cos(i * .17f);
    }
    PerFrameContext frame(state.globalMemory, &state.globalRegisters); frame.RegisterBuiltinVariables();
    Waveform wave(state);
    realDraw = glad_glDrawElements; glad_glDrawElements = Observe;
    for (bool modulate : {false, true})
    for (float volume : {.5f, 2.f})
    for (float alpha : {.4f, .9f})
    {
        state.modWaveAlphaByvolume = modulate;
        state.modWaveAlphaStart = 0; state.modWaveAlphaEnd = 2;
        state.audioData.vol = volume;
        state.waveAlpha = alpha; frame.LoadStateVariables(state);
        alphas.clear(); primitives.clear();
        output.Bind(); wave.Draw(frame); output.Pixels();
        Check(!alphas.empty(), "wave produced no observed draw");
        for (size_t i = 0; i < alphas.size(); ++i)
        {
            if (topology) Check(primitives[i] == GL_LINE_STRIP, "mode-1 spiral added a closing segment");
            else Check(std::abs(alphas[i] - std::min(1.f, alpha * 1.25f * (modulate ? volume / 2 : 1))) < 1e-6f,
                       "mode-1 waveform omitted MilkDrop alpha multiplier/clamp");
        }
    }
    glad_glDrawElements = realDraw;
}
static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced{};
static void ObserveInstanced(GLenum mode, GLint first, GLsizei count, GLsizei instances)
{
    GLint buffer{}, previous{};
    glGetVertexAttribiv(0, GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING, &buffer);
    glGetIntegerv(GL_ARRAY_BUFFER_BINDING, &previous);
    glBindBuffer(GL_ARRAY_BUFFER, buffer);
    const auto* point = static_cast<const ColoredPoint*>(glMapBufferRange(
        GL_ARRAY_BUFFER, 0, sizeof(ColoredPoint), GL_MAP_READ_BIT));
    Check(point != nullptr, "quad color readback failed");
    alphas.push_back(point->a);
    glUnmapBuffer(GL_ARRAY_BUFFER); glBindBuffer(GL_ARRAY_BUFFER, previous);
    realInstanced(mode, first, count, instances);
}
static void Opacity(ShaderCache& cache)
{
    struct Case { int mode; float alpha, volume, treble, start, end; bool modulate; float small, native; };
    const Case cases[] = {
        {2, .8f, .85f, 1, .75f, .95f, true, .028f, .044f},
        {0, .1f, 2.2f, 1, .75f, .95f, true, .725f, .725f},
        {3, .5f, 1, 1, 0, 2, false, .0975f, .286f},
        {3, 0, 1, 1, 0, 2, false, .0975f, .286f},
        {1, .003f, 1, 1, 0, 2, false, 0, 0},
        // float(.0032) * float(1.25) rounds below float(.004).
        {1, .0032f, 1, 1, 0, 2, false, 0, 0},
        {1, .0033f, 1, 1, 0, 2, false, .004125f, .004125f},
        {0, .004f, 1, 1, 0, 2, false, .004f, .004f},
        {2, .8f, 1, 1, 0, 2, false, .056f, .088f},
        {0, .8f, -.1f, 1, 0, 2, true, 0, 0},
        {1, .8f, 4, 1, 0, 2, true, 1, 1},
        {4, .4f, 1, 1, 0, 2, true, .2f, .2f},
    };
    Surface output;
    PresetState state; Configure(state, cache);
    state.waveR = 1; state.waveG = state.waveB = 0;
    PerFrameContext frame(state.globalMemory, &state.globalRegisters); frame.RegisterBuiltinVariables();
    Waveform wave(state);
    realDraw = glad_glDrawElements; glad_glDrawElements = Observe;
    realInstanced = glad_glDrawArraysInstanced; glad_glDrawArraysInstanced = ObserveInstanced;
    for (bool native : {false, true})
    for (const auto& c : cases)
    {
        auto& context = state.renderContext;
        context.viewportSizeX = native ? 3840 : 256;
        context.viewportSizeY = native ? 2160 : 144;
        context.lineReferenceWidth = native ? 1024 : 0;
        context.lineReferenceHeight = native ? 768 : 0;
        state.waveMode = c.mode; state.waveAlpha = c.alpha;
        state.modWaveAlphaByvolume = c.modulate;
        state.modWaveAlphaStart = c.start; state.modWaveAlphaEnd = c.end;
        state.audioData.vol = c.volume; state.audioData.treb = c.treble;
        frame.LoadStateVariables(state);
        alphas.clear(); primitives.clear(); output.Bind(); wave.Draw(frame); output.Pixels();
        const auto expected = native ? c.native : c.small;
        const auto label = "mode " + std::to_string(c.mode) + (native ? " Native 4K" : " matched canvas");
        if (expected == 0) Check(alphas.empty(), label + " submitted alpha below MilkDrop threshold");
        else {
            Check(!alphas.empty(), label + " submitted no geometry");
            for (auto alpha : alphas) Check(std::abs(alpha - expected) < 1e-6f,
                label + " expected alpha " + std::to_string(expected) + " got " + std::to_string(alpha));
        }
    }
    glad_glDrawElements = realDraw; glad_glDrawArraysInstanced = realInstanced;
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
    PresetState state; Configure(state, cache);
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
int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "expected hue, wave-alpha or wave-topology");
        GLContext context; ShaderCache cache; Shader::InvalidateBoundProgram();
        const std::string control = argv[1];
        if (control == "hue") Hue(cache);
        else if (control == "wave-alpha" || control == "wave-topology") Wave(cache, control == "wave-topology");
        else if (control == "opacity") Opacity(cache);
        else if (control == "samples") Samples(cache);
        else throw std::runtime_error("unknown control");
        std::cout << control << " matches MilkDrop 2.25c\n";
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
