// The production composite must copy a same-size feedback texture without extra blur.
#include "gl_context.hpp"
#include <MilkdropPreset/FinalComposite.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/TextureManager.hpp>
#include <array>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;

static void Check(bool ok, const char* message)
{
    if (!ok) throw std::runtime_error(message);
}

int main()
{
    try
    {
        GLContext context;
        ShaderCache cache;
        TextureManager manager(std::vector<std::string>{});
        Shader::InvalidateBoundProgram();
        PresetState state;
        state.renderContext.textureManager = &manager;
        state.renderContext.shaderCache = &cache;
        state.LoadShaders();
        PerFrameContext frame(state.globalMemory, &state.globalRegisters);
        frame.RegisterBuiltinVariables();
        state.compositeShaderVersion = 3;
        state.compositeShader = "shader_body { ret = GetPixel(uv); }";
        FinalComposite composite;
        composite.LoadCompositeShader(state);

        for (const auto size : {std::array<int, 2>{16, 8}, std::array<int, 2>{64, 32},
                                std::array<int, 2>{16, 8}})
        {
            const int width = size[0], height = size[1];
            state.renderContext.viewportSizeX = width;
            state.renderContext.viewportSizeY = height;
            state.renderContext.aspectX = state.renderContext.invAspectX = 1;
            state.renderContext.aspectY = float(height) / width;
            state.renderContext.invAspectY = float(width) / height;
            frame.LoadStateVariables(state);
            for (bool impulse : {true, false})
            {
                std::vector<unsigned char> input(width * height * 4);
                for (int y = 0; y < height; ++y) for (int x = 0; x < width; ++x)
                {
                    const int index = (y * width + x) * 4;
                    input[index + 3] = 255;
                    if (!impulse)
                    {
                        input[index] = (17 * x + 11 * y) % 251;
                        input[index + 1] = (3 * x + 21 * y) % 247;
                        input[index + 2] = (7 * x + 13 * y) % 239;
                    }
                }
                if (impulse) input[((height / 3) * width + width / 3) * 4] = 255;
                auto source = std::make_shared<Texture>("main", GL_TEXTURE_2D, width, height, 1,
                                                       GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
                source->Bind(0);
                glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA,
                                GL_UNSIGNED_BYTE, input.data());
                state.mainTexture = source;
                composite.CompileCompositeShader(state);
                auto target = std::make_shared<Texture>("output", GL_TEXTURE_2D, width, height, 1,
                                                       GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
                GLuint fbo{};
                glGenFramebuffers(1, &fbo);
                glBindFramebuffer(GL_FRAMEBUFFER, fbo);
                glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                                       target->TextureID(), 0);
                Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "target incomplete");
                glViewport(0, 0, width, height);
                glDisable(GL_DEPTH_TEST);
                for (int repeat = 0; repeat < 2; ++repeat)
                {
                    composite.Draw(state, frame);
                    std::vector<unsigned char> output(input.size());
                    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, output.data());
                    int lit = 0, peak = 0;
                    for (int y = 0; y < height; ++y) for (int x = 0; x < width; ++x)
                    {
                        const int index = (y * width + x) * 4;
                        const int reference = ((height - 1 - y) * width + x) * 4;
                        if (output[index]) ++lit;
                        peak = std::max(peak, int(output[index]));
                        for (int channel = 0; channel < 3; ++channel)
                            Check(std::abs(int(output[index + channel]) - input[reference + channel]) <= 1,
                                  "pass-through composite changed a feedback texel");
                    }
                    if (impulse)
                        Check(lit == 1 && peak == 255, "composite diluted a single feedback pixel");
                    Check(glGetError() == GL_NO_ERROR, "composite GL error");
                    std::cout << width << 'x' << height << " impulse=" << impulse
                              << " texels copied without an extra sampling bias\n";
                }
                glBindFramebuffer(GL_FRAMEBUFFER, 0);
                glDeleteFramebuffers(1, &fbo);
            }
        }
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
