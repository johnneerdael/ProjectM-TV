// Real shape draws: unrelated sampler state must not change main-texture sampling.
#include "gl_context.hpp"
#include <MilkdropPreset/CustomShape.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <Renderer/TextureManager.hpp>
#include <Renderer/ShaderCache.hpp>
#include <array>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <utility>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;

struct DrawState {
    GLint sampler{}, texture{}, wrapS{}, wrapT{}, minFilter{}, magFilter{};
    GLsizei count{};
};
static bool observing = false;
static std::vector<DrawState> draws;

namespace libprojectM {
class FeedbackDetailTestAccess {
public:
    static bool DelayedBlur(const MilkdropPreset::MilkdropPreset& preset) { return preset.m_warpSamplesBlur; }
    static bool AllocatedBlur(const MilkdropPreset::MilkdropPreset& preset)
    {
        const auto descriptors = preset.m_state.blurTexture.GetDescriptorsForBlurLevel(
            MilkdropPreset::BlurTexture::BlurLevel::Blur1);
        return !descriptors.empty() && !descriptors.front().Empty();
    }
};
}

// Observe the live state at the production draw, then issue that real draw once.
static PFNGLDRAWARRAYSPROC realDrawArrays{};

static void ObserveDrawArrays(GLenum mode, GLint first, GLsizei count)
{
    GLint program{};
    glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    if (observing && mode == GL_TRIANGLE_FAN &&
        glGetUniformLocation(program, "texture_sampler") >= 0)
    {
        DrawState state;
        state.count = count;
        glGetIntegerv(GL_SAMPLER_BINDING, &state.sampler);
        glGetIntegerv(GL_TEXTURE_BINDING_2D, &state.texture);
        const std::array<GLenum, 4> names{GL_TEXTURE_WRAP_S, GL_TEXTURE_WRAP_T,
                                        GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER};
        std::array<GLint*, 4> values{&state.wrapS, &state.wrapT, &state.minFilter, &state.magFilter};
        for (size_t i = 0; i < names.size(); ++i)
        {
            if (state.sampler) glGetSamplerParameteriv(state.sampler, names[i], values[i]);
            else glGetTexParameteriv(GL_TEXTURE_2D, names[i], values[i]);
        }
        draws.push_back(state);
    }
    realDrawArrays(mode, first, count);
}

// GLAD dispatches through pointers rather than the platform symbol table.
class DrawHook
{
public:
    DrawHook() { realDrawArrays = glad_glDrawArrays; glad_glDrawArrays = ObserveDrawArrays; }
    ~DrawHook() { glad_glDrawArrays = realDrawArrays; }
};

static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}

struct FixtureDirectory {
    std::filesystem::path path;
    explicit FixtureDirectory(const char* name) : path(name)
    {
        Check(std::filesystem::create_directory(path), "fixture directory must be new");
    }
    ~FixtureDirectory()
    {
        std::error_code error;
        std::filesystem::remove_all(path, error);
    }
};

// An asymmetric 2x2 image distinguishes repeat/clamp and nearest/linear.
static constexpr std::array<unsigned char, 16> pixels{
    240, 0, 0, 255, 0, 160, 0, 255,
    0, 0, 80, 255, 40, 120, 200, 255};

static std::unique_ptr<CustomShape> Shape(PresetState& state, bool textured,
                                        int instances = 1, const std::string& image = "",
                                        bool mixedInstances = false)
{
    std::ostringstream text;
    text << "[preset00]\nshapecode_0_enabled=1\nshapecode_0_sides=4\n"
         << "shapecode_0_textured=" << textured << "\nshapecode_0_num_inst=" << instances
         << "\nshapecode_0_rad=2\nshapecode_0_tex_zoom=0.25\n"
         << "shapecode_0_r=1\nshapecode_0_g=1\nshapecode_0_b=1\nshapecode_0_a=1\n"
         << "shapecode_0_r2=1\nshapecode_0_g2=1\nshapecode_0_b2=1\nshapecode_0_a2=1\n"
         << "shapecode_0_border_a=0\nshapecode_0_image=" << image << '\n';
    if (mixedInstances) text << "shape_0_per_frame1=textured=above(instance,0);\n";
    std::istringstream stream(text.str());
    PresetFileParser parser;
    Check(parser.Read(stream), "fixture preset did not parse");
    state.Initialize(parser);
    auto shape = std::make_unique<CustomShape>(state);
    shape->Initialize(parser, 0);
    std::vector<std::string> warnings;
    shape->CompileCodeAndRunInitExpressions(warnings);
    Check(warnings.empty(), "fixture shape equations failed");
    return shape;
}

static void AssertState(size_t count, GLuint texture, GLint wrap, GLint filter,
                        const std::string& label)
{
    Check(draws.size() == count, label + ": wrong textured draw count");
    for (const auto& draw : draws)
    {
        std::cout << label << " sampler=" << draw.sampler << " texture=" << draw.texture
                  << " wrap=" << draw.wrapS << ',' << draw.wrapT << " filter="
                  << draw.minFilter << ',' << draw.magFilter << '\n';
        Check(draw.texture != 0 && (!texture || draw.texture == static_cast<GLint>(texture)),
              label + ": wrong texture");
        Check(draw.sampler != 0 && draw.wrapS == wrap && draw.wrapT == wrap &&
              draw.minFilter == filter && draw.magFilter == filter,
              label + ": inherited sampler changed effective shape sampling");
    }
}

static void AssertEdgePixels()
{
    std::array<unsigned char, 16 * 16 * 4> output{};
    glReadPixels(0, 0, 16, 16, GL_RGBA, GL_UNSIGNED_BYTE, output.data());
    for (int y : {1, 5, 10, 14}) for (int x : {1, 5, 10, 14})
    {
        // The authored rad=2/zoom=.25 fan maps pixel centers affinely, with
        // a projection flip in v. Use this unit-slope UV mapping so the sample
        // coordinates and bilinear weights are exact multiples of 1/16 and 1/8.
        // Both axes still cross the texture edges, so clamp/nearest must fail.
        const float u = .5f + ((x + .5f) / 8.f - 1.f);
        const float v = .5f - ((y + .5f) / 8.f - 1.f);
        const float tx = u * 2.f - .5f, ty = v * 2.f - .5f;
        const int ix = static_cast<int>(std::floor(tx)), iy = static_cast<int>(std::floor(ty));
        const float fx = tx - ix, fy = ty - iy;
        for (int channel = 0; channel < 3; ++channel)
        {
            float expected = 0;
            for (int dy = 0; dy < 2; ++dy) for (int dx = 0; dx < 2; ++dx)
            {
                const int px = ((ix + dx) % 2 + 2) % 2, py = ((iy + dy) % 2 + 2) % 2;
                expected += pixels[(py * 2 + px) * 4 + channel] *
                            (dx ? fx : 1 - fx) * (dy ? fy : 1 - fy);
            }
            const int actual = output[(y * 16 + x) * 4 + channel];
            Check(std::abs(actual - expected) <= 2,
                  "edge-crossing repeat/linear pixel mismatch at " + std::to_string(x) + "," +
                  std::to_string(y) + ": " + std::to_string(actual) + " vs " + std::to_string(expected));
        }
    }
}

static void Controls(const std::filesystem::path& fixtures)
{
    GLContext context;
    DrawHook drawHook;
    ShaderCache shaders;
    Shader::InvalidateBoundProgram();
    TextureManager manager({fixtures.string()});
    PresetState state;
    state.renderContext.textureManager = &manager;
    state.renderContext.shaderCache = &shaders;
    state.LoadShaders();
    state.renderContext.viewportSizeX = state.renderContext.viewportSizeY = 16;
    state.renderContext.aspectX = state.renderContext.aspectY = 1;
    state.renderContext.invAspectX = state.renderContext.invAspectY = 1;
    // The default Texture constructor creates unsized RGB storage, which GLES
    // rejects for this RGBA upload. Allocate matching sized fixture storage.
    auto source = std::make_shared<Texture>("shape-source", GL_TEXTURE_2D, 2, 2, 1,
                                            GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
    source->Bind(0);
    Check(glGetError() == GL_NO_ERROR, "shape source allocation or binding failed");
    glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 2, 2, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    Check(glGetError() == GL_NO_ERROR, "shape fixture texture upload failed");
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    state.mainTexture = source;
    auto target = std::make_shared<Texture>("shape-output", 16, 16, false);
    GLuint framebuffer{};
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, target->TextureID(), 0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "incomplete target");
    glViewport(0, 0, 16, 16);
    glDisable(GL_DEPTH_TEST);
    auto mainShape = Shape(state, true, 3);
    auto untextured = Shape(state, false);
    auto secondShape = Shape(state, true);
    auto mixedShape = Shape(state, true, 3, "", true);
    for (bool presetWrap : {false, true})
    for (const auto mode : std::array<std::pair<GLint, GLint>, 5>{{
        {0, 0}, {GL_CLAMP_TO_EDGE, GL_LINEAR}, {GL_CLAMP_TO_EDGE, GL_NEAREST},
        {GL_REPEAT, GL_LINEAR}, {GL_REPEAT, GL_NEAREST}}})
    {
        state.texWrap = presetWrap;
        auto unrelated = mode.first ? std::make_shared<Sampler>(mode.first, mode.second) : nullptr;
        if (unrelated) unrelated->Bind(0); else Sampler::Unbind(0);
        glClearColor(0, 0, 0, 0);
        glClear(GL_COLOR_BUFFER_BIT);
        draws.clear(); observing = true;
        untextured->Draw(); // An untextured draw must not be needed to repair unit0.
        unsigned char solid[4]{};
        glReadPixels(8, 8, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, solid);
        Check(solid[0] == 255 && solid[1] == 255 && solid[2] == 255,
              "untextured shape changed under unrelated sampler state");
        mainShape->Draw();
        secondShape->Draw();
        observing = false;
        AssertState(4, source->TextureID(), GL_REPEAT, GL_LINEAR, "main-shapes");
        AssertEdgePixels();
        if (unrelated) unrelated->Bind(0); else Sampler::Unbind(0);
        draws.clear(); observing = true;
        mixedShape->Draw(); // First instance untextured, later instances textured.
        observing = false;
        AssertState(2, source->TextureID(), GL_REPEAT, GL_LINEAR, "mixed-instances");
        Check(glGetError() == GL_NO_ERROR, "main shape GL error");
    }
    for (const std::string qualifier : {"fw_", "fc_", "pw_", "pc_"})
    {
        auto named = Shape(state, true, 2, qualifier + "asymmetric");
        auto descriptor = manager.GetTexture(qualifier + "asymmetric");
        Check(!descriptor.Empty(), "named texture did not load");
        auto unrelated = std::make_shared<Sampler>(GL_CLAMP_TO_EDGE, GL_NEAREST);
        unrelated->Bind(0);
        draws.clear(); observing = true;
        named->Draw();
        observing = false;
        AssertState(2, descriptor.Texture()->TextureID(), qualifier[1] == 'w' ? GL_REPEAT : GL_CLAMP_TO_EDGE,
                    qualifier[0] == 'f' ? GL_LINEAR : GL_NEAREST, qualifier);
        Check(glGetError() == GL_NO_ERROR, "named shape GL error");
    }
    glDeleteFramebuffers(1, &framebuffer);
}

static void PresetControls(const std::filesystem::path& fixtures)
{
    GLContext context;
    DrawHook drawHook;
    ShaderCache shaders;
    Shader::InvalidateBoundProgram();
    TextureManager manager({fixtures.string()});
    RenderContext render;
    render.shaderCache = &shaders;
    render.textureManager = &manager;
    render.viewportSizeX = render.viewportSizeY = 128;
    render.perPixelMeshX = 8; render.perPixelMeshY = 6;
    render.fps = 30;
    auto output = std::make_shared<Texture>("full-output", 128, 128, false);
    GLuint framebuffer{};
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
    const std::array<std::string, 4> warps{
        "ret=tex2D(sampler_main,uv).rgb;",
        "ret=GetBlur1(uv);",
        "ret=tex2D(sampler_main,uv).rgb; // blur comment only",
        "float blur_marker=1; ret=tex2D(sampler_main,uv).rgb*blur_marker;"};
    for (bool wrap : {false, true}) for (size_t index = 0; index < warps.size(); ++index)
    {
        // Case 3 mentions blur in executable code but requests no blur texture.
        std::istringstream source("[preset00]\nMILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=2\n"
            "PSVERSION_COMP=2\nfWaveAlpha=0\nwave_a=0\nob_size=0\nib_size=0\nbTexWrap=" +
            std::to_string(wrap) + "\nwarp_1=`shader_body { " + warps[index] + "\n"
            "warp_2=`}\ncomp_1=`shader_body { ret=tex2D(sampler_main,uv).rgb; }\n"
            "shapecode_0_enabled=1\nshapecode_0_textured=1\nshapecode_0_num_inst=2\n"
            "shapecode_0_sides=4\nshapecode_0_rad=.7\nshapecode_0_tex_zoom=.2\n"
            "shapecode_0_border_a=0\n");
        libprojectM::MilkdropPreset::MilkdropPreset preset(source);
        preset.Initialize(render);
        Check(preset.InitializationWarnings().empty(), "full preset initialization warnings");
        Check(preset.SetOutputTarget(true, framebuffer), "full preset target rejected");
        for (int frame = 0; frame < 3; ++frame)
        {
            render.frame = frame; render.time = frame / 30.f;
            draws.clear(); observing = true;
            preset.RenderFrame({}, render);
            observing = false;
            const std::string label = "full-warp-" + std::to_string(index) + "-wrap-" + std::to_string(wrap);
            AssertState(2, 0, GL_REPEAT, GL_LINEAR, label);
            const bool delayed = libprojectM::FeedbackDetailTestAccess::DelayedBlur(preset);
            const bool allocated = libprojectM::FeedbackDetailTestAccess::AllocatedBlur(preset);
            // Shader comments survive parsing: timing uses a lexical mention,
            // while sampler discovery allocates only the actually used blur.
            Check(delayed == (index != 0), label + ": unexpected blur timing");
            Check(allocated == (index == 1), label + ": unexpected blur allocation");
            Check(glGetError() == GL_NO_ERROR, label + ": GL error");
        }
    }
    glDeleteFramebuffers(1, &framebuffer);
}

static void ExactPresetControl(const std::filesystem::path& fixtures, const std::string& path)
{
    GLContext context;
    DrawHook drawHook;
    ShaderCache shaders;
    Shader::InvalidateBoundProgram();
    TextureManager manager({fixtures.string()});
    RenderContext render;
    render.shaderCache = &shaders;
    render.textureManager = &manager;
    render.viewportSizeX = 256; render.viewportSizeY = 144;
    render.aspectX = 1; render.aspectY = 144.f / 256.f;
    render.invAspectX = 1; render.invAspectY = 256.f / 144.f;
    render.perPixelMeshX = 48; render.perPixelMeshY = 32;
    render.fps = 30;
    auto output = std::make_shared<Texture>("exact-output", 256, 144, false);
    GLuint framebuffer{};
    glGenFramebuffers(1, &framebuffer);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
    libprojectM::MilkdropPreset::MilkdropPreset preset(path);
    preset.Initialize(render);
    Check(preset.InitializationWarnings().empty(), "exact preset initialization warnings");
    Check(preset.SetOutputTarget(true, framebuffer), "exact preset target rejected");
    for (int frame = 0; frame < 3; ++frame)
    {
        render.frame = frame; render.time = frame / 30.f;
        draws.clear(); observing = true;
        preset.RenderFrame({}, render);
        observing = false;
        AssertState(1, 0, GL_REPEAT, GL_LINEAR, "widest-swing-frame-" + std::to_string(frame));
        Check(draws.front().count == 102, "exact preset did not use authored 100-side shape");
        Check(libprojectM::FeedbackDetailTestAccess::DelayedBlur(preset) &&
              libprojectM::FeedbackDetailTestAccess::AllocatedBlur(preset), "exact preset blur missing");
        Check(glGetError() == GL_NO_ERROR, "exact preset GL error");
    }
    glDeleteFramebuffers(1, &framebuffer);
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2 || argc == 3,
              "usage: shape-sampler-regressions NEW_FIXTURE_DIRECTORY [EXACT_PRESET_PATH]");
        const FixtureDirectory directory(argv[1]);
        const auto& fixtures = directory.path;
        {
            std::ofstream image(fixtures / "asymmetric.tga", std::ios::binary);
            unsigned char header[18]{};
            header[2] = 2; header[12] = 2; header[14] = 2; header[16] = 24;
            image.write(reinterpret_cast<char*>(header), sizeof(header));
            for (size_t i = 0; i < pixels.size(); i += 4)
            {
                const unsigned char bgr[]{pixels[i + 2], pixels[i + 1], pixels[i]};
                image.write(reinterpret_cast<const char*>(bgr), sizeof(bgr));
            }
            Check(image.good(), "could not write named texture");
        }
        if (argc == 3) ExactPresetControl(fixtures, argv[2]);
        else
        {
            Controls(fixtures);
            Controls(fixtures); // Independent context teardown/recreation, no static GL object cache.
            PresetControls(fixtures);
        }
        std::cout << "shape sampler regression controls passed\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
