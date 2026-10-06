// Catch collapsed safe ranges and nonfinite progressive blur normalization.
// Exercise production bounds with real per-frame input slots; the default mode needs no GL.
// Optional gl mode checks decoded/raw banks and unchanged candidate presets on a real renderer.
#include <MilkdropPreset/BlurTexture.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <MilkdropPreset/MilkdropShader.hpp>
#include <Renderer/TextureManager.hpp>
#include "gl_context.hpp"

#include <array>
#include <cmath>
#include <filesystem>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <sstream>

using libprojectM::MilkdropPreset::BlurTexture;
using libprojectM::MilkdropPreset::PerFrameContext;
using Values = BlurTexture::Values;
using Inputs = std::array<PRJM_EVAL_F, 3>;

struct Bounds
{
    Values min;
    Values max;
};

// Use the engine's existing friend, without adding test methods to production.
namespace libprojectM {
class FeedbackDetailTestAccess
{
public:
    static MilkdropPreset::PresetState& State(MilkdropPreset::MilkdropPreset& preset) { return preset.m_state; }
    static MilkdropPreset::PerFrameContext& Frame(MilkdropPreset::MilkdropPreset& preset) { return preset.m_perFrameContext; }
    static bool Composite(MilkdropPreset::MilkdropPreset& preset) { return preset.m_finalComposite.HasCompositeShader(); }
};
}

static Bounds Adjust(Inputs min, Inputs max)
{
    PerFrameContext context(nullptr, nullptr);
    context.blur1_min = &min[0];
    context.blur2_min = &min[1];
    context.blur3_min = &min[2];
    context.blur1_max = &max[0];
    context.blur2_max = &max[1];
    context.blur3_max = &max[2];
    Bounds result;
    BlurTexture::GetSafeBlurMinMaxValues(context, result.min, result.max);
    return result;
}

static void Require(bool condition, const std::string& message)
{
    if (!condition) throw std::runtime_error(message);
}

static void Safe(const Bounds& bounds)
{
    Values scale;
    Values bias;
    Require(BlurTexture::GetBlurScaleAndBias(bounds.min, bounds.max, scale, bias),
            "production shader coefficient calculation rejected adjusted bounds");
    // These are the float32 domains consumed by Update, including subtraction
    // after division: a positive input gap alone does not prevent cancellation.
    for (size_t i = 0; i < 3; ++i)
    {
        const float gap = bounds.max[i] - bounds.min[i];
        Require(std::isfinite(bounds.min[i]) && std::isfinite(bounds.max[i]) &&
                    std::isfinite(gap) && gap > 0.0f, "collapsed/nonfinite blur interval at level " + std::to_string(i + 1));
        const float min = i == 0 ? bounds.min[i] :
            (bounds.min[i] - bounds.min[i - 1]) / (bounds.max[i - 1] - bounds.min[i - 1]);
        const float max = i == 0 ? bounds.max[i] :
            (bounds.max[i] - bounds.min[i - 1]) / (bounds.max[i - 1] - bounds.min[i - 1]);
        const float denominator = max - min;
        Require(std::isfinite(denominator) && denominator > 0.0f &&
                    std::isfinite(scale[i]) && scale[i] > 0.0f && std::isfinite(bias[i]),
                "invalid progressive normalization at level " + std::to_string(i + 1));
    }
}

static void Expected(const Bounds& bounds, Values min, Values max)
{
    Safe(bounds);
    for (size_t i = 0; i < 3; ++i)
    {
        Require(std::fabs(bounds.min[i] - min[i]) <= 1e-7f &&
                    std::fabs(bounds.max[i] - max[i]) <= 1e-7f, "unexpected adjusted bounds at level " + std::to_string(i + 1));
    }
}

static void Defaults(const Bounds& bounds)
{
    Expected(bounds, {0.0f, 0.0f, 0.0f}, {1.0f, 1.0f, 1.0f});
}

static void FiniteUniforms(GLuint program)
{
    GLint count{};
    glGetProgramiv(program, GL_ACTIVE_UNIFORMS, &count);
    for (GLint i = 0; i < count; ++i)
    {
        char name[256]{};
        GLint size{};
        GLenum type{};
        glGetActiveUniform(program, i, sizeof(name), nullptr, &size, &type, name);
        std::string base(name);
        const auto array = base.find("[0]");
        if (array != std::string::npos) base.resize(array);
        for (GLint element = 0; element < size; ++element)
        {
            const std::string uniform = size == 1 ? name : base + '[' + std::to_string(element) + ']';
            const GLint location = glGetUniformLocation(program, uniform.c_str());
            Require(location >= 0, "active uniform location missing: " + uniform);
            std::array<float, 16> values{};
            glGetUniformfv(program, location, values.data());
            for (float value : values) Require(std::isfinite(value), "nonfinite active uniform: " + uniform);
        }
    }
}

static void RenderControls(const std::filesystem::path& assets)
{
    using namespace libprojectM::MilkdropPreset;
    using namespace libprojectM::Renderer;
    GLContext gl;
    TextureManager textures({(assets / "textures").string()});
    RenderContext render;
    render.textureManager = &textures;
    render.viewportSizeX = 128;
    render.viewportSizeY = 96;
    render.fps = 30;
    auto initial = std::make_shared<Texture>("blur-control-source", 128, 96, false);
    auto output = std::make_shared<Texture>("blur-control-output", 128, 96, false);
    GLuint target{};
    glGenFramebuffers(1, &target);
    glBindFramebuffer(GL_FRAMEBUFFER, target);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, initial->TextureID(), 0);
    Require(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "blur source framebuffer incomplete");
    glClearColor(1, 1, 1, 1);
    glClear(GL_COLOR_BUFFER_BIT);
    for (int level = 1; level <= 3; ++level)
    {
        std::ostringstream source;
        source << "MILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=2\nPSVERSION_COMP=2\n"
                  "[preset00]\nfDecay=1\nfWaveAlpha=0\nfGammaAdj=1\nob_a=0\nib_a=0\nmv_a=0\n"
                  "b1n=1\nb1x=1\nb2n=1\nb2x=1\nb3n=1\nb3x=1\n"
                  "b1ed=0\nwarp_1=`shader_body { ret=GetPixel(uv); }\n"
                  "comp_1=`shader_body { ret=float3(GetBlur" << level << "(uv).x,tex2D(sampler_blur"
               << level << ",uv).x,0); }\n";
        std::istringstream stream(source.str());
        MilkdropPreset preset(stream);
        preset.Initialize(render);
        Require(preset.InitializationWarnings().empty(), "synthetic blur equation initialization failed");
        Require(libprojectM::FeedbackDetailTestAccess::Composite(preset), "synthetic composite program missing");
        glViewport(0, 0, render.viewportSizeX, render.viewportSizeY);
        preset.DrawInitialImage(initial, render);
        glBindFramebuffer(GL_FRAMEBUFFER, target);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
        Require(preset.SetOutputTarget(true, target), "synthetic blur output rejected");
        preset.RenderFrame({}, render);
        auto& frame = libprojectM::FeedbackDetailTestAccess::Frame(preset);
        Bounds bounds;
        BlurTexture::GetSafeBlurMinMaxValues(frame, bounds.min, bounds.max);
        Safe(bounds);
        glBindFramebuffer(GL_READ_FRAMEBUFFER, target);
        glReadBuffer(GL_COLOR_ATTACHMENT0);
        std::array<unsigned char, 4> pixel{};
        glReadPixels(64, 48, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel.data());
        std::cout << "fullengine blur" << level << " decoded/raw RGB=" << int(pixel[0]) << ',' << int(pixel[1]) << ',' << int(pixel[2]) << '\n';
        // Constant white maps to ~0.5 in normalized storage, then decodes to 1.
        // Both channels must be right; a zero reconstruction coefficient cannot hide a corrupt raw bank.
        Require(pixel[0] == 255 && std::abs(int(pixel[1]) - 128) <= 1 && pixel[2] == 0,
                "fullengine decoded getter/raw blur result mismatch");
        Require(glGetError() == GL_NO_ERROR, "synthetic blur render GL error");
    }

    const std::array<const char*, 9> candidates = {
        "$$$ Royal - Mashup (29).milk", "Cope - The Cloud.milk", "EVET - Scanazoic --- Isosceles edit.milk",
        "Flexi - emergencey 2 --- Isosceles edit4a enhance.milk",
        "Flexi - emergencey 2 --- Isosceles edit4b enhance warp.milk", "Mig_015.milk",
        "flexi - a julia fractal for hexcollie embossed (Jelly).milk", "goody - woven beads (ps2-0).milk",
        "shadowharlequin, goody - woven beads (ps2-0) [outlined].milk"};
    for (const auto* name : candidates)
    {
        const auto path = assets / "presets" / name;
        MilkdropPreset preset(path.string());
        render.frame = 0;
        render.time = 0;
        preset.Initialize(render);
        Require(preset.InitializationWarnings().empty(), std::string("candidate init warning: ") + name);
        auto& state = libprojectM::FeedbackDetailTestAccess::State(preset);
        auto& frame = libprojectM::FeedbackDetailTestAccess::Frame(preset);
        // Independent compile is evidence about authored programs; fullengine warp
        // selection must be established from MILKDROP_PRESET_DEBUG compiler logs.
        MilkdropShader warp(MilkdropShader::ShaderType::WarpShader);
        warp.LoadCode(state.warpShader);
        warp.LoadTexturesAndCompile(state);
        MilkdropShader comp(MilkdropShader::ShaderType::CompositeShader);
        comp.LoadCode(state.compositeShader);
        comp.LoadTexturesAndCompile(state);
        glViewport(0, 0, render.viewportSizeX, render.viewportSizeY);
        preset.DrawInitialImage(initial, render);
        glBindFramebuffer(GL_FRAMEBUFFER, target);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
        Require(preset.SetOutputTarget(true, target), "candidate blur output rejected");
        for (int i = 0; i < 3; ++i)
        {
            render.frame = i;
            render.time = i / 30.0f;
            preset.RenderFrame({}, render);
            Bounds bounds;
            BlurTexture::GetSafeBlurMinMaxValues(frame, bounds.min, bounds.max);
            Safe(bounds);
            warp.LoadVariables(state, frame);
            GLint program{};
            glGetIntegerv(GL_CURRENT_PROGRAM, &program);
            FiniteUniforms(program);
            comp.LoadVariables(state, frame);
            glGetIntegerv(GL_CURRENT_PROGRAM, &program);
            FiniteUniforms(program);
            std::cout << "candidate " << name << " frame=" << i << " bounds=";
            for (size_t level = 0; level < 3; ++level) std::cout << bounds.min[level] << ':' << bounds.max[level] << ' ';
            std::cout << "full_composite_program=" << libprojectM::FeedbackDetailTestAccess::Composite(preset)
                      << " authored_stages=compiled finite_uniforms=true appearance_verified=false\n";
            Require(glGetError() == GL_NO_ERROR, std::string("candidate render GL error: ") + name);
        }
    }
    glDeleteFramebuffers(1, &target);
}

int main(int argc, char** argv)
{
    try
    {
        Expected(Adjust({1, 1, 1}, {1, 1, 1}), {.95f, .95f, .95f}, {1.05f, 1.05f, 1.05f});
        Expected(Adjust({.4f, .4f, .4f}, {.45f, .45f, .45f}), {.375f, .375f, .375f}, {.475f, .475f, .475f});
        Expected(Adjust({.8f, .8f, .8f}, {.2f, .2f, .2f}), {.45f, .45f, .45f}, {.55f, .55f, .55f});
        Defaults(Adjust({0, 0, 0}, {1, 1, 1}));
        Expected(Adjust({0, .2f, .3f}, {1, .8f, .7f}), {0, .2f, .3f}, {1, .8f, .7f});
        const auto progressive = Adjust({0, .25f, .375f}, {1, .75f, .625f});
        Safe(progressive);
        Values scale;
        Values bias;
        Require(BlurTexture::GetBlurScaleAndBias(progressive.min, progressive.max, scale, bias) &&
                    scale == Values{1, 2, 2} && bias == Values{0, -.5f, -.5f},
                "progressive shader coefficients changed for ordinary nested bounds");
        Expected(Adjust({-1, -2, -3}, {2, 3, 4}), {-1, -1, -1}, {2, 2, 2});
        // Preserve the legacy clamp-then-expand order; expansion can exceed a parent.
        Expected(Adjust({0, .95f, .975f}, {1, 1.5f, 1.5f}), {0, .925f, .95f}, {1, 1.025f, 1.05f});
        const float threshold = .1f;
        const float below = std::nextafter(threshold, 0.0f);
        const float above = std::nextafter(threshold, 1.0f);
        const auto narrow = Adjust({0, 0, 0}, {below, below, below});
        Safe(narrow);
        Require(narrow.min[0] < 0.0f && narrow.max[0] >= below,
                "below-threshold interval was not expanded");
        for (float gap : {threshold, above})
        {
            const auto bounds = Adjust({0, 0, 0}, {gap, gap, gap});
            Safe(bounds);
            Require(bounds.min == Values{0, 0, 0} && bounds.max == Values{gap, gap, gap}, "threshold/above interval changed");
        }
        const auto maximum = std::numeric_limits<float>::max();
        for (const auto bounds : {Adjust({1e30f, 1e30f, 1e30f}, {2e30f, 2e30f, 2e30f}),
                                  Adjust({-maximum / 2, -maximum / 2, -maximum / 2},
                                         {maximum / 2, maximum / 2, maximum / 2})})
            Safe(bounds);
        const auto large = Adjust({1e30f, 1e30f, 1e30f}, {2e30f, 2e30f, 2e30f});
        Require(large.min == Values{1e30f, 1e30f, 1e30f} && large.max == Values{2e30f, 2e30f, 2e30f},
                "representable extreme interval changed");
        Defaults(Adjust({maximum, maximum, maximum}, {maximum, maximum, maximum}));
        Defaults(Adjust({-maximum, -maximum, -maximum}, {maximum, maximum, maximum}));
        Defaults(Adjust({1e30, 1e30, 1e30}, {1e30, 1e30, 1e30}));
        // Finite positive gaps can still disappear in progressive float32 coordinates.
        Defaults(Adjust({-1e30, .5f, .5f}, {1e30, .6f, .6f}));
        Defaults(Adjust({1e300, 0, 0}, {1e300, 1, 1}));
        for (PRJM_EVAL_F invalid : {std::numeric_limits<PRJM_EVAL_F>::infinity(),
                                   -std::numeric_limits<PRJM_EVAL_F>::infinity(),
                                   std::numeric_limits<PRJM_EVAL_F>::quiet_NaN()})
        {
            for (size_t level = 0; level < 3; ++level)
            {
                Inputs min{0, 0, 0};
                Inputs max{1, 1, 1};
                min[level] = invalid;
                Defaults(Adjust(min, max));
                min[level] = 0;
                max[level] = invalid;
                Defaults(Adjust(min, max));
            }
        }
        std::cout << "Blur intervals, thresholds, nesting and unsupported numeric domains passed\n";
        if (argc == 3 && std::string(argv[1]) == "gl") RenderControls(argv[2]);
        else Require(argc == 1, "expected no arguments or gl <bundled-assets-path>");
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
