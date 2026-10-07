// Exercise the production equation -> mesh upload -> warp shader -> feedback path.
// Sending an unreduced large angle to GPU trig, swapping sine/cosine, or uploading
// the per-frame angle instead of the final per-pixel angle must fail these controls.
#include "gl_context.hpp"
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/MilkdropShader.hpp>
#include <MilkdropPreset/PerPixelMesh.hpp>
#include <MilkdropPreset/PerPixelContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <Renderer/TextureManager.hpp>
#include <Renderer/ShaderCache.hpp>
#include <array>
#include <cmath>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static constexpr int Width = 64, Height = 48;
using Pixels = std::vector<unsigned char>;

static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}

static Pixels Read()
{
    Pixels pixels(Width * Height * 4);
    glReadPixels(0, 0, Width, Height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    Check(glGetError() == GL_NO_ERROR, "rotation draw/readback GL error");
    return pixels;
}

struct Control
{
    ShaderCache cache;
    PresetState state;
    PerFrameContext frame{state.globalMemory, &state.globalRegisters};
    PerPixelContext pixel{state.globalMemory, &state.globalRegisters};
    PerPixelMesh mesh;
    std::shared_ptr<Texture> input = std::make_shared<Texture>("rotation-input", GL_TEXTURE_2D, Width, Height, 1, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
    std::shared_ptr<Texture> output = std::make_shared<Texture>("rotation-output", GL_TEXTURE_2D, Width, Height, 1, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
    GLuint framebuffer{};
    bool preparedReplay{};

    Control(TextureManager& textures, bool custom, bool perPixel)
    {
        std::istringstream source(custom ?
            "MILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=2\n[preset00]\nfDecay=1\nwarp_1=`shader_body { ret=float3(uv.x,uv.y,0.25); }\n" :
            "[preset00]\nfDecay=1\n");
        PresetFileParser parser;
        Check(parser.Read(source), "rotation fixture parse failed");
        state.Initialize(parser);
        state.renderContext.textureManager = &textures;
        state.renderContext.shaderCache = &cache;
        state.renderContext.viewportSizeX = Width;
        state.renderContext.viewportSizeY = Height;
        state.renderContext.perPixelMeshX = 8;
        state.renderContext.perPixelMeshY = 6;
        state.mainTexture = input;
        frame.RegisterBuiltinVariables();
        frame.LoadStateVariables(state);
        *frame.zoom = 2.0;
        *frame.zoomexp = 1.0;
        *frame.rot = 0.0;
        *frame.warp = 0.0;
        *frame.cx = *frame.cy = 0.5;
        *frame.dx = *frame.dy = 0.0;
        *frame.sx = 1.0;
        *frame.sy = -0.99;
        *frame.decay = 1.0;
        *frame.wrap = 0.0;
        pixel.RegisterBuiltinVariables();
        if (perPixel) pixel.CompilePerPixelCode("rot=q1;");
        mesh.LoadWarpShader(state);
        mesh.CompileWarpShader(state);
        // The blue channel also proves the requested custom program was active.
        glGenFramebuffers(1, &framebuffer);
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, output->TextureID(), 0);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "rotation target incomplete");
        glViewport(0, 0, Width, Height);
        glDisable(GL_BLEND);
        glDisable(GL_DITHER);
        Pixels seed(Width * Height * 4);
        for (int y = 0; y < Height; ++y)
            for (int x = 0; x < Width; ++x)
            {
                const int i = (y * Width + x) * 4;
                seed[i] = static_cast<unsigned char>(std::lround((x + 0.5) / Width * 255));
                seed[i + 1] = static_cast<unsigned char>(std::lround((y + 0.5) / Height * 255));
                seed[i + 2] = 191;
                seed[i + 3] = 255;
            }
        glBindTexture(GL_TEXTURE_2D, input->TextureID());
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, Width, Height, GL_RGBA, GL_UNSIGNED_BYTE, seed.data());
        Check(glGetError() == GL_NO_ERROR, "rotation seed upload GL error");
    }

    ~Control() { glDeleteFramebuffers(1, &framebuffer); }

    Pixels Draw(double rotation, bool perPixel, bool varying = false)
    {
        *frame.rot = perPixel ? -0.72 : rotation;
        *frame.q_vars[0] = rotation;
        pixel.LoadStateReadOnlyVariables(state, frame);
        pixel.LoadPerFrameQVariables(state, frame);
        if (preparedReplay)
        {
            mesh.Prepare(state, frame, pixel);
            mesh.DrawAgain(state, frame);
        }
        else mesh.Draw(state, frame, pixel);
        const double retained = perPixel ? *pixel.rot : *frame.rot;
        const double authored = rotation + (varying ? 3.0 : 0.0);
        Check(std::isnan(authored) ? std::isnan(retained) :
                  (varying ? std::abs(retained - authored) < 1e-8 : retained == authored),
              "rendering rewrote authored rotation");
        return Read();
    }
};

static void Coordinates(const Pixels& pixels, double evaluated, bool custom)
{
    // Independent CPU reference after the same MilkDrop float conversion. Never
    // reduce the double equation result before rounding to the emitted float.
    const float rotation = static_cast<float>(evaluated);
    const double sine = std::sin(static_cast<double>(rotation));
    const double cosine = std::cos(static_cast<double>(rotation));
    Check(std::abs(sine * sine + cosine * cosine - 1.0) < 1e-12, "bad reference rotation");
    for (const auto& point : std::array<std::array<int, 2>, 5>{{{8,8},{50,8},{8,36},{50,36},{31,23}}})
    {
        const int x = point[0], y = point[1], i = (y * Width + x) * 4;
        const double u = ((x + 0.5) / Width - 0.5) / 2.0;
        // projectM's projection flips screen Y; authored negative sy flips it back.
        const double v = -((y + 0.5) / Height - 0.5) / (2.0 * -0.99);
        const double expected[]{u * cosine - v * sine + 0.5, u * sine + v * cosine + 0.5};
        for (int axis = 0; axis < 2; ++axis)
            Check(std::abs(pixels[i + axis] / 255.0 - expected[axis]) < 0.008,
                  "rotation=" + std::to_string(evaluated) + " UV axis=" + std::to_string(axis) +
                  " actual=" + std::to_string(pixels[i + axis] / 255.0) + " expected=" + std::to_string(expected[axis]));
        Check(std::abs(pixels[i + 2] - (custom ? 64 : 191)) <= 1, "custom warp fell back or wrong legacy texture");
    }
}

static void VaryingCoordinates(const Pixels& pixels, double rotation)
{
    // Evaluate each grid corner independently, then interpolate the triangle's UVs.
    // Evaluating trig once per frame or before the per-pixel equation loses this motion.
    const auto vertex = [rotation](double x, double y) {
        const float angle = static_cast<float>(rotation + x * 10.0 - y * 7.0);
        const double sine = std::sin(double(angle)), cosine = std::cos(double(angle));
        const double u = (x - 0.5) / 2.0, v = (y - 0.5) / (2.0 * -0.99);
        return std::array<double, 2>{u * cosine - v * sine + 0.5, u * sine + v * cosine + 0.5};
    };
    for (const auto& point : std::array<std::array<int, 2>, 4>{{{8,8},{50,8},{8,36},{50,36}}})
    {
        const double gx = (point[0] + 0.5) / Width * 8, gy = (1.0 - (point[1] + 0.5) / Height) * 6;
        const int x = int(gx), y = int(gy), i = (point[1] * Width + point[0]) * 4;
        const double fx = gx - x, fy = gy - y;
        const auto a = vertex(x / 8.0, y / 6.0), b = vertex((x + 1) / 8.0, y / 6.0);
        const auto c = vertex(x / 8.0, (y + 1) / 6.0), d = vertex((x + 1) / 8.0, (y + 1) / 6.0);
        for (int axis = 0; axis < 2; ++axis)
        {
            const double expected = fx + fy <= 1 ? a[axis] * (1 - fx - fy) + b[axis] * fx + c[axis] * fy :
                b[axis] * (1 - fy) + c[axis] * (1 - fx) + d[axis] * (fx + fy - 1);
            Check(std::abs(pixels[i + axis] / 255.0 - expected) < 0.008, "varying per-vertex rotation UV mismatch");
        }
    }
}

static void Feedback(TextureManager& textures, bool perPixel, bool preparedReplay)
{
    Control large(textures, false, perPixel), reduced(textures, false, perPixel);
    large.preparedReplay = reduced.preparedReplay = preparedReplay;
    // Frozen float32 angle reference: atan2(sin(10000000),cos(10000000)).
    constexpr double Small = 2.707543636322021484375;
    for (int frame = 0; frame < 4; ++frame)
    {
        glBindFramebuffer(GL_FRAMEBUFFER, large.framebuffer);
        const auto actual = large.Draw(10000000.0, perPixel);
        glBindFramebuffer(GL_FRAMEBUFFER, reduced.framebuffer);
        const auto expected = reduced.Draw(Small, perPixel);
        unsigned long error{};
        int min = 255, max = 0;
        for (size_t i = 0; i < actual.size(); i += 4)
        {
            min = std::min(min, static_cast<int>(actual[i])); max = std::max(max, static_cast<int>(actual[i]));
            for (int axis = 0; axis < 3; ++axis) error += std::abs(int(actual[i + axis]) - int(expected[i + axis]));
        }
        Check(max - min > 5, "large rotation collapsed spatial feedback on frame " + std::to_string(frame));
        Check(double(error) / (Width * Height * 3) < 1.0, "large rotation lost feedback relative to small-angle control");
        for (Control* control : {&large, &reduced})
        {
            std::swap(control->input, control->output);
            control->state.mainTexture = control->input;
            glBindFramebuffer(GL_FRAMEBUFFER, control->framebuffer);
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, control->output->TextureID(), 0);
        }
    }
}

int main()
{
    try
    {
        GLContext gl;
        TextureManager textures(std::vector<std::string>{});
        std::cout << glGetString(GL_RENDERER) << '\n';
        for (bool preparedReplay : {false, true})
        for (bool custom : {false, true})
            for (bool perPixel : {false, true})
            {
                Control control(textures, custom, perPixel);
                control.preparedReplay = preparedReplay;
                for (double rotation : {0.0, -0.0, 0.31, -0.31, 3.141592653589793, -6.283185307179586,
                                        10000000.0, -10000000.0, 10000000.6, -10000000.6,
                                        1e20, -1e20, double(std::numeric_limits<float>::max())})
                    Coordinates(control.Draw(rotation, perPixel), rotation, custom);
                // Nonfinite rotations have no defined image contract. Check that the
                // draw does not rewrite equations or report GL errors, then recovers.
                for (double rotation : {std::numeric_limits<double>::infinity(),
                                        -std::numeric_limits<double>::infinity(), std::numeric_limits<double>::quiet_NaN()})
                    control.Draw(rotation, perPixel);
                Coordinates(control.Draw(-0.31, perPixel), -0.31, custom);
                if (perPixel && custom)
                {
                    projectm_eval_code_destroy(control.pixel.perPixelCodeHandle);
                    control.pixel.perPixelCodeHandle = nullptr;
                    control.pixel.CompilePerPixelCode("rot=q1+x*10-y*7;");
                    for (double rotation : {0.31, 10000000.6, -10000000.6})
                        VaryingCoordinates(control.Draw(rotation, true, true), rotation);
                }
                std::cout << (preparedReplay ? "prepared replay " : "direct ") << (custom ? "custom" : "legacy") << (perPixel ? " per-pixel" : " per-frame") << " UV controls pass\n";
            }
        for (bool preparedReplay : {false, true})
            for (bool perPixel : {false, true}) Feedback(textures, perPixel, preparedReplay);
        std::cout << "multi-frame feedback controls pass\n";
        return 0;
    }
    catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
