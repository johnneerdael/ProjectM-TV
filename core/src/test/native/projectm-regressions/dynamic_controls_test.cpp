// Evaluated controls must reach real GL draws without modifying preset defaults.
#include "gl_context.hpp"
#include <MilkdropPreset/FinalComposite.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/Waveform.hpp>
#include <Renderer/Texture.hpp>
#include <Renderer/TextureManager.hpp>
#include <dlfcn.h>
#include <array>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <sstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
namespace libprojectM {
class FeedbackDetailTestAccess {
public:
    static MilkdropPreset::PresetState& State(MilkdropPreset::MilkdropPreset& p) { return p.m_state; }
    static MilkdropPreset::PerFrameContext& Frame(MilkdropPreset::MilkdropPreset& p) { return p.m_perFrameContext; }
    static bool Composite(const MilkdropPreset::MilkdropPreset& p) { return p.m_finalComposite.HasCompositeShader(); }
};
}
static void Check(bool value, const std::string& message)
{
    if (!value) throw std::runtime_error(message);
}
struct Draw {
    GLenum mode; GLsizei count; GLint source, destination;
    GLsizei instances{1};
    std::array<float, 3> style{};
    std::vector<unsigned char> geometry;
};
static bool observe = false;
static std::vector<Draw> draws;
extern "C" void glDrawArrays(GLenum mode, GLint first, GLsizei count)
{
    using Function = void (*)(GLenum, GLint, GLsizei);
    static auto real = reinterpret_cast<Function>(dlsym(RTLD_NEXT, "glDrawArrays"));
    if (!real) std::abort();
    if (observe)
    {
        Draw draw{mode, count, 0, 0};
        glGetIntegerv(GL_BLEND_SRC_RGB, &draw.source);
        glGetIntegerv(GL_BLEND_DST_RGB, &draw.destination);
        draws.push_back(draw);
    }
    real(mode, first, count);
}
extern "C" void glDrawArraysInstanced(GLenum mode, GLint first, GLsizei count, GLsizei instances)
{
    using Function = void (*)(GLenum, GLint, GLsizei, GLsizei);
    static auto real = reinterpret_cast<Function>(dlsym(RTLD_NEXT, "glDrawArraysInstanced"));
    if (!real) std::abort();
    if (observe)
    {
        Draw draw{mode, count, 0, 0}; draw.instances = instances;
        glGetIntegerv(GL_BLEND_SRC_RGB, &draw.source); glGetIntegerv(GL_BLEND_DST_RGB, &draw.destination);
        GLint program{}, buffer{}, previous{}, size{};
        glGetIntegerv(GL_CURRENT_PROGRAM, &program);
        glGetUniformfv(program, glGetUniformLocation(program, "half_width"), &draw.style[0]);
        glGetUniformfv(program, glGetUniformLocation(program, "pass_offset"), &draw.style[1]);
        glGetVertexAttribiv(0, GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING, &buffer);
        glGetIntegerv(GL_ARRAY_BUFFER_BINDING, &previous); glBindBuffer(GL_ARRAY_BUFFER, buffer);
        glGetBufferParameteriv(GL_ARRAY_BUFFER, GL_BUFFER_SIZE, &size);
        const auto* points = static_cast<unsigned char*>(glMapBufferRange(GL_ARRAY_BUFFER, 0, size, GL_MAP_READ_BIT));
        Check(points != nullptr, "quad geometry readback failed");
        draw.geometry.assign(points, points + size); glUnmapBuffer(GL_ARRAY_BUFFER);
        glBindBuffer(GL_ARRAY_BUFFER, previous);
        draws.push_back(std::move(draw));
    }
    real(mode, first, count, instances);
}
struct Surface
{
    int width, height;
    std::shared_ptr<Texture> texture;
    GLuint framebuffer{};
    Surface(int w, int h) : width(w), height(h), texture(std::make_shared<Texture>("control", w, h, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false))
    {
        glGenFramebuffers(1, &framebuffer);
        Bind();
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture->TextureID(), 0);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "incomplete control target");
    }
    ~Surface() { glDeleteFramebuffers(1, &framebuffer); }
    void Bind() { glBindFramebuffer(GL_FRAMEBUFFER, framebuffer); glViewport(0, 0, width, height); }
    std::vector<unsigned char> Pixels()
    {
        std::vector<unsigned char> pixels(width * height * 4);
        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
        const auto error = glGetError();
        Check(error == GL_NO_ERROR, "GL error in control: " + std::to_string(error));
        return pixels;
    }
};
static void Configure(PresetState& state, int size, bool quad)
{
    auto& context = state.renderContext;
    context.viewportSizeX = context.viewportSizeY = size;
    context.aspectX = context.aspectY = context.invAspectX = context.invAspectY = 1;
    context.time = .5f;
    context.fps = 30;
    context.lineReferenceWidth = context.lineReferenceHeight = quad ? 32 : 0;
    state.hueRandomOffsets.fill(0);
    state.waveAlpha = .7f;
    state.waveR = .8f; state.waveG = .4f; state.waveB = .2f;
    state.waveX = state.waveY = .5f;
    state.audioData = {};
    state.audioData.vol = state.audioData.treb = 1;
    for (size_t i = 0; i < state.audioData.waveformLeft.size(); ++i)
    {
        state.audioData.waveformLeft[i] = .3f * std::sin(i * .13f);
        state.audioData.waveformRight[i] = .2f * std::cos(i * .17f);
    }
}
static void Evaluate(PerFrameContext& frame, PresetState& state)
{
    frame.LoadStateVariables(state);
    frame.ExecutePerFrameCode();
}
static void SamePixels(const std::vector<unsigned char>& a, const std::vector<unsigned char>& b,
                       const std::string& label, int tolerance = 0)
{
    Check(a.size() == b.size(), label + ": wrong surface size");
    int maximum = 0;
    for (size_t i = 0; i < a.size(); ++i) maximum = std::max(maximum, std::abs(int(a[i]) - int(b[i])));
    Check(maximum <= tolerance, label + ": pixels differ by " + std::to_string(maximum));
}
static void WaveControls()
{
    // Retain one dynamic Waveform across switches. Compare actual draws/pixels to
    // static controls with matching per-mode smoothing history and PCM/clock.
    for (const bool quad : {false, true})
    {
        Surface surface(128, 128);
        Check(glGetError() == GL_NO_ERROR, "wave surface setup GL error");
        surface.Pixels();
        PresetState live;
        Configure(live, 128, quad);
        live.waveMode = 0; live.waveDots = live.waveThick = live.additiveWaves = false;
        PerFrameContext frame(live.globalMemory, &live.globalRegisters);
        frame.RegisterBuiltinVariables();
        frame.CompilePerFrameCode("wave_mode=q1;wave_usedots=q2;wave_thick=q3;wave_additive=q4;");
        Waveform waveform(live);
        Check(glGetError() == GL_NO_ERROR, "wave construction GL error");
        for (const int mode : {0, 6, 0, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 22})
        {
            PresetState reference;
            Configure(reference, 128, quad);
            reference.waveMode = mode % 16;
            PerFrameContext staticFrame(reference.globalMemory, &reference.globalRegisters);
            staticFrame.RegisterBuiltinVariables();
            Waveform staticWave(reference);
            for (const int flags : {0, 1, 2, 4, 7})
            {
                frame.LoadStateVariables(live);
                *frame.q_vars[0] = mode + .75;
                *frame.q_vars[1] = flags & 1 ? 1 : 0;
                *frame.q_vars[2] = flags & 2 ? 1 : 0;
                *frame.q_vars[3] = flags & 4 ? 1 : 0;
                frame.ExecutePerFrameCode();
                Check(*frame.wave_mode == mode + .75, "mode equation did not evaluate");
                surface.Bind(); glClearColor(.1f, .15f, .2f, 1); glClear(GL_COLOR_BUFFER_BIT);
                Check(glGetError() == GL_NO_ERROR, "wave predraw GL error");
                draws.clear(); observe = true; waveform.Draw(frame); observe = false;
                Check(glGetError() == GL_NO_ERROR, "wave draw GL error");
                const auto actual = surface.Pixels();
                const auto actualDraws = draws;
                reference.waveDots = flags & 1; reference.waveThick = flags & 2; reference.additiveWaves = flags & 4;
                staticFrame.LoadStateVariables(reference);
                surface.Bind(); glClear(GL_COLOR_BUFFER_BIT);
                draws.clear(); observe = true; staticWave.Draw(staticFrame); observe = false;
                const auto label = "mode=" + std::to_string(mode) + " flags=" + std::to_string(flags) + " quad=" + std::to_string(quad);
                const auto expected = surface.Pixels();
                Check(actualDraws.size() == draws.size(), label + ": wrong offset/draw count");
                for (size_t i = 0; i < draws.size(); ++i)
                {
                    Check(actualDraws[i].mode == draws[i].mode && actualDraws[i].count == draws[i].count,
                          label + ": wrong primitive/geometry count");
                    Check(actualDraws[i].instances == draws[i].instances, label + ": wrong quad segment count");
                    Check(actualDraws[i].style == draws[i].style, label + ": wrong quad width/offset");
                    Check(actualDraws[i].geometry == draws[i].geometry, label + ": wrong quad geometry");
                    Check(actualDraws[i].source == GL_SRC_ALPHA &&
                          actualDraws[i].destination == (flags & 4 ? GL_ONE : GL_ONE_MINUS_SRC_ALPHA), label + ": wrong blending");
                    if (flags & 1) Check(actualDraws[i].mode == GL_POINTS, label + ": dots not selected");
                }
                SamePixels(actual, expected, label);
                Check(live.waveMode == 0 && !live.waveDots && !live.waveThick && !live.additiveWaves, "wave defaults overwritten");
            }
        }
        // Conditional assignments must start from config every frame, not yesterday's output.
        frame.CompilePerFrameCode("if(equal(frame,1),wave_usedots=1,0);");
        live.renderContext.frame = 1; Evaluate(frame, live); Check(*frame.wave_usedots == 1, "conditional wave assignment");
        live.renderContext.frame = 2; Evaluate(frame, live); Check(*frame.wave_usedots == 0, "wave default did not reset");
        // Negative remainder is not a positive wrap. Inputs outside int's domain
        // must not invoke undefined conversion or reuse the last valid mode.
        for (const double mode : {-1., -17., std::numeric_limits<double>::infinity(),
                                  std::numeric_limits<double>::quiet_NaN(), 1e100})
        {
            frame.LoadStateVariables(live); *frame.wave_mode = mode;
            surface.Bind(); glClear(GL_COLOR_BUFFER_BIT);
            const auto untouched = surface.Pixels();
            waveform.Draw(frame); SamePixels(untouched, surface.Pixels(), "unsupported mode");
        }
        frame.LoadStateVariables(live); *frame.wave_mode = -16;
        surface.Bind(); waveform.Draw(frame); // signed remainder zero remains supported
        std::cout << "wave controls: quad=" << quad << " pass\n";
    }
}
static std::vector<unsigned char> ReadFramebuffer(Framebuffer& framebuffer, int size)
{
    framebuffer.Bind(0);
    std::vector<unsigned char> pixels(size * size * 4);
    glReadPixels(0, 0, size, size, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    Check(glGetError() == GL_NO_ERROR, "dual-target GL error");
    return pixels;
}
static void DualWaveControls()
{
    Framebuffer canvas(1), native(1);
    canvas.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
    native.CreateColorAttachment(0, 0, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE);
    canvas.SetSize(64, 64); native.SetSize(128, 128);
    PresetState live; Configure(live, 128, true);
    PerFrameContext frame(live.globalMemory, &live.globalRegisters);
    frame.RegisterBuiltinVariables();
    Waveform waveform(live);
    const auto draw = [&](PresetState& state, PerFrameContext& context, Waveform& wave)
    {
        canvas.Bind(0); glClearColor(0, 0, 0, 1); glClear(GL_COLOR_BUFFER_BIT);
        native.Bind(0); glClear(GL_COLOR_BUFFER_BIT);
        canvas.Bind(0);
        GLint authoredFramebuffer{}; glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &authoredFramebuffer);
        GeometryTargets targets(state, canvas, 0, 64, 64, {}, native, 0);
        targets.Authored(); wave.Draw(context, &targets);
        Check(state.renderContext.viewportSizeX == 64 && state.renderContext.lineReferenceWidth == 0,
              "dual wave failed to restore authored context");
        GLint bound{}; glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &bound);
        Check(bound == authoredFramebuffer, "dual wave failed to restore authored framebuffer");
        auto authored = ReadFramebuffer(canvas, 64);
        auto detail = ReadFramebuffer(native, 128);
        return std::make_pair(authored, detail);
    };
    for (const int mode : {0, 6, 0}) for (const int flags : {0, 1, 2, 4, 7})
    {
        Configure(live, 128, true); frame.LoadStateVariables(live);
        *frame.wave_mode = mode; *frame.wave_usedots = flags & 1;
        *frame.wave_thick = flags & 2; *frame.wave_additive = flags & 4;
        const auto actual = draw(live, frame, waveform);
        PresetState reference; Configure(reference, 128, true);
        reference.waveMode = mode; reference.waveDots = flags & 1;
        reference.waveThick = flags & 2; reference.additiveWaves = flags & 4;
        PerFrameContext staticFrame(reference.globalMemory, &reference.globalRegisters);
        staticFrame.RegisterBuiltinVariables(); staticFrame.LoadStateVariables(reference);
        Waveform staticWave(reference);
        const auto expected = draw(reference, staticFrame, staticWave);
        SamePixels(actual.first, expected.first, "authored wave");
        SamePixels(actual.second, expected.second, "native wave");
    }
    std::cout << "authored/native wave controls pass\n";
}
static void DisplayControls()
{
    // A known constant input gives independent blend predictions after baseline hue.
    for (const int size : {32, 128})
    {
        Surface source(size, size), output(size, size);
        source.Bind(); glClearColor(.2f, .35f, .5f, 1); glClear(GL_COLOR_BUFFER_BIT);
        PresetState state; Configure(state, size, false);
        state.mainTexture = source.texture;
        state.gammaAdj = 1; state.videoEchoAlpha = 0;
        state.brighten = state.darken = state.solarize = state.invert = false;
        state.compositeShaderVersion = 0;
        PerFrameContext frame(state.globalMemory, &state.globalRegisters);
        frame.RegisterBuiltinVariables();
        frame.CompilePerFrameCode("brighten=q1;darken=q2;solarize=q3;invert=q4;");
        FinalComposite composite; composite.LoadCompositeShader(state);
        Evaluate(frame, state); output.Bind(); composite.Draw(state, frame);
        const auto baseline = output.Pixels();
        for (const int flags : {0, 2, 0, 1, 4, 8, 15, 0})
        {
            frame.LoadStateVariables(state);
            for (int i = 0; i < 4; ++i) *frame.q_vars[i] = flags & (1 << i) ? 1 : 0;
            frame.ExecutePerFrameCode(); output.Bind(); composite.Draw(state, frame);
            const auto actual = output.Pixels();
            for (size_t i = 0; i < actual.size(); ++i)
            {
                if (i % 4 == 3) continue;
                float c = baseline[i] / 255.f;
                if (flags & 1) c = 1 - (1-c)*(1-c);
                if (flags & 2) c = c*c;
                if (flags & 4) c = 2*c*(1-c);
                if (flags & 8) c = 1-c;
                Check(std::abs(actual[i] - c*255) <= 4, "filter flags=" + std::to_string(flags) + ": wrong known-colour output");
            }
            Check(!state.brighten && !state.darken && !state.solarize && !state.invert, "display defaults overwritten");
            Check(!glIsEnabled(GL_BLEND), "filter blend enable leaked");
        }
        frame.CompilePerFrameCode("if(equal(frame,1),darken=1,0);");
        state.renderContext.frame = 1; Evaluate(frame, state); Check(*frame.darken == 1, "conditional filter assignment");
        state.renderContext.frame = 2; Evaluate(frame, state); Check(*frame.darken == 0, "filter default did not reset");
        // Asymmetric input distinguishes echo zoom/orientation. Compare to unchanged
        // static branches, including gamma without echo and fractional redraws.
        source.Bind(); glEnable(GL_SCISSOR_TEST); glScissor(0, 0, size/2, size/2);
        glClearColor(.6f, .1f, .25f, 1); glClear(GL_COLOR_BUFFER_BIT); glDisable(GL_SCISSOR_TEST);
        frame.CompilePerFrameCode("gamma=q1;echo_alpha=q2;echo_zoom=q3;echo_orient=q4;");
        for (const float gamma : {0.f, .5f, 1.f, 1.5f, 3.f, 8.f})
        for (const float alpha : {0.f, .001f, .5f, 1.f})
        for (const float zoom : {.001f, 1.f, 2.f, 1000.f})
        for (const int orientation : {-1, 0, 1, 2, 3, 5})
        {
            frame.LoadStateVariables(state);
            *frame.q_vars[0] = gamma; *frame.q_vars[1] = alpha;
            *frame.q_vars[2] = zoom; *frame.q_vars[3] = orientation + .75;
            frame.ExecutePerFrameCode(); output.Bind(); composite.Draw(state, frame);
            const auto actual = output.Pixels();
            PresetState reference; Configure(reference, size, false);
            reference.mainTexture = source.texture; reference.gammaAdj = gamma;
            reference.videoEchoAlpha = alpha; reference.videoEchoZoom = zoom; reference.videoEchoOrientation = orientation;
            reference.compositeShaderVersion = 0;
            reference.brighten = reference.darken = reference.solarize = reference.invert = false;
            PerFrameContext staticFrame(reference.globalMemory, &reference.globalRegisters);
            staticFrame.RegisterBuiltinVariables(); staticFrame.LoadStateVariables(reference);
            FinalComposite staticComposite; staticComposite.LoadCompositeShader(reference);
            output.Bind(); staticComposite.Draw(reference, staticFrame);
            SamePixels(actual, output.Pixels(), "gamma=" + std::to_string(gamma) + " alpha=" + std::to_string(alpha) + " zoom=" + std::to_string(zoom) + " orientation=" + std::to_string(orientation));
            Check(state.gammaAdj == 1 && state.videoEchoAlpha == 0, "echo defaults overwritten");
        }
        std::cout << "legacy display controls: size=" << size << " pass\n";
    }
}
static void Save(const std::filesystem::path& file, const std::vector<unsigned char>& pixels, int size)
{
    std::filesystem::create_directories(file.parent_path());
    std::ofstream image(file, std::ios::binary);
    image << "P6\n" << size << ' ' << size << "\n255\n";
    for (size_t i = 0; i < pixels.size(); i += 4) image.write(reinterpret_cast<const char*>(&pixels[i]), 3);
    Check(image.good(), "capture write failed");
}
static void Capture(const std::filesystem::path& directory)
{
    Surface source(128, 128), output(128, 128);
    source.Bind(); glClearColor(.2f, .35f, .5f, 1); glClear(GL_COLOR_BUFFER_BIT);
    PresetState state; Configure(state, 128, false);
    state.gammaAdj = 1; state.videoEchoAlpha = 0;
    state.brighten = state.darken = state.solarize = state.invert = false;
    state.compositeShaderVersion = 0; state.mainTexture = source.texture;
    PerFrameContext frame(state.globalMemory, &state.globalRegisters); frame.RegisterBuiltinVariables();
    FinalComposite composite; composite.LoadCompositeShader(state);
    frame.CompilePerFrameCode("darken=above(frame,0);");
    for (int index = 0; index < 2; ++index)
    {
        state.renderContext.frame = index; Evaluate(frame, state);
        output.Bind(); composite.Draw(state, frame);
        Save(directory / ("darken-" + std::to_string(index) + ".ppm"), output.Pixels(), 128);
        std::cout << "darken frame=" << index << " evaluated=" << *frame.darken << " static=" << state.darken << '\n';
    }
    Waveform wave(state);
    frame.CompilePerFrameCode("wave_mode=6*above(frame,0);wave_usedots=above(frame,1);wave_additive=above(frame,2);wave_thick=above(frame,3);");
    for (int index = 0; index < 5; ++index)
    {
        state.renderContext.frame = index; Evaluate(frame, state);
        output.Bind(); glClearColor(.1f, .15f, .2f, 1); glClear(GL_COLOR_BUFFER_BIT);
        draws.clear(); observe = true; wave.Draw(frame); observe = false;
        Save(directory / ("wave-" + std::to_string(index) + ".ppm"), output.Pixels(), 128);
        std::cout << "wave frame=" << index << " evaluated_mode=" << *frame.wave_mode
                  << " dots=" << *frame.wave_usedots << " thick=" << *frame.wave_thick
                  << " additive=" << *frame.wave_additive << " draws=" << draws.size();
        for (const auto& draw : draws) std::cout << " [primitive=" << draw.mode << " vertices=" << draw.count
                                                << " blend=" << draw.source << ',' << draw.destination << ']';
        std::cout << '\n';
    }
}
static void PresetControls(const std::filesystem::path& assets, const std::filesystem::path& captures)
{
    const std::array<std::string, 3> names{{"319.milk",
        "Hexcollie - now entering the wormhole2 - mash0000 - if you like this, maybe you, like me, are insane.milk",
        "idiot - Forty Six and 2 (pushit!).milk"}};
    TextureManager manager({(assets / "textures").string()});
    for (const float trails : {-1.f, 0.f, .5f, 1.f})
    for (size_t witness = 0; witness < names.size(); ++witness)
    {
        Surface output(256, 256), initial(256, 256);
        initial.Bind(); glClearColor(.2f, .35f, .5f, 1); glClear(GL_COLOR_BUFFER_BIT);
        MilkdropPreset preset((assets / "presets" / names[witness]).string());
        RenderContext render;
        render.textureManager = &manager;
        render.viewportSizeX = render.viewportSizeY = 256;
        render.aspectX = render.aspectY = render.invAspectX = render.invAspectY = 1;
        render.fps = 30; render.perPixelMeshX = render.perPixelMeshY = 16;
        render.lineReferenceWidth = render.lineReferenceHeight = 64;
        render.feedbackDetailAlpha = trails;
        preset.Initialize(render);
        Check(preset.InitializationWarnings().empty(), names[witness] + ": equation compilation warning");
        auto& state = libprojectM::FeedbackDetailTestAccess::State(preset);
        auto& frame = libprojectM::FeedbackDetailTestAccess::Frame(preset);
        state.hueRandomOffsets.fill(0);
        Check(libprojectM::FeedbackDetailTestAccess::Composite(preset) == (witness == 1), "unexpected composite path");
        if (witness == 0) Check(state.darken, "319 source-default bDarken must be 1");
        PresetState audioSource; Configure(audioSource, 256, false);
        preset.DrawInitialImage(initial.texture, render);
        for (int index = 0; index < 6; ++index)
        {
            auto audio = audioSource.audioData;
            audio.treb = audio.bass = audio.mid = audio.vol = index % 2 == 0 ? .5f : 2.f;
            audio.trebAtt = audio.bassAtt = audio.midAtt = audio.volAtt = 1;
            render.frame = index; render.time = index / 30.f;
            Check(preset.SetOutputTarget(true, output.framebuffer), "original preset output rejected");
            preset.RenderFrame(audio, render);
            if (witness == 0) Check(*frame.darken == (audio.treb < 1 ? 1 : 0), "319 darken equation mismatch");
            if (witness == 1) Check(*frame.wave_mode == std::fmod(std::trunc(*frame.q_vars[7]), 7), "Hexcollie signed remainder mismatch");
            std::cout << "original=" << names[witness] << " trails=" << trails << " frame=" << index
                      << " treb=" << audio.treb << " darken=" << *frame.darken
                      << " mode=" << *frame.wave_mode << " dots=" << *frame.wave_usedots
                      << " thick=" << *frame.wave_thick << " additive=" << *frame.wave_additive << '\n';
            output.Bind();
            const auto pixels = output.Pixels();
            if (!captures.empty() && index < 2)
                Save(captures / ("original-" + std::to_string(witness) + "-trails-" +
                     std::to_string(trails) + "-frame-" + std::to_string(index) + ".ppm"), pixels, 256);
        }
    }
}
int main(int argc, char** argv)
{
    try
    {
        Check(argc >= 2, "pass wave, display, capture or presets");
        GLContext context; Shader::InvalidateBoundProgram();
        std::cout << "renderer=" << glGetString(GL_RENDERER) << " version=" << glGetString(GL_VERSION) << '\n';
        Check(glGetError() == GL_NO_ERROR, "context GL error");
        if (std::string(argv[1]) == "wave") { WaveControls(); DualWaveControls(); }
        else if (std::string(argv[1]) == "display") DisplayControls();
        else if (std::string(argv[1]) == "capture" && argc == 3) Capture(argv[2]);
        else if (std::string(argv[1]) == "presets" && argc >= 3) PresetControls(argv[2], argc == 4 ? argv[3] : "");
        else throw std::runtime_error("unknown control");
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
