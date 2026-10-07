// Read shape coverage before composite, using MilkDrop 2's D3D9 sample rule.
#include "gl_context.hpp"
#include <MilkdropPreset/CustomShape.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/TextureManager.hpp>
#include <glm/gtc/type_ptr.hpp>
#include <array>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;

static void Check(bool ok, const char* message)
{
    if (!ok) throw std::runtime_error(message);
}

static void CheckSharedProjection(const std::shared_ptr<Shader>& shader)
{
    shader->Bind();
    GLint program{};
    glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    std::array<float, 16> actual{};
    glGetUniformfv(program, glGetUniformLocation(program, "vertex_transformation"), actual.data());
    const auto* expected = glm::value_ptr(PresetState::orthogonalProjection);
    for (size_t i = 0; i < actual.size(); ++i)
        Check(actual[i] == expected[i], "shape alignment leaked into a shared shader");
}

int main()
{
    try
    {
        GLContext context;
        ShaderCache shaders;
        Shader::InvalidateBoundProgram();
        TextureManager manager(std::vector<std::string>{});
        PresetState state;
        state.renderContext.textureManager = &manager;
        state.renderContext.shaderCache = &shaders;
        state.renderContext.aspectX = 1;
        state.renderContext.aspectY = 144.f / 256;
        state.renderContext.invAspectX = 1;
        state.renderContext.invAspectY = 256.f / 144;
        state.LoadShaders();
        auto white = std::make_shared<Texture>("white", GL_TEXTURE_2D, 1, 1, 1,
                                               GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
        white->Bind(0);
        const std::array<unsigned char, 4> rgba{255, 255, 255, 255};
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, rgba.data());
        state.mainTexture = white;

        for (const auto size : {std::array<int, 2>{256, 144}, std::array<int, 2>{512, 288}})
        {
            const int width = size[0], height = size[1];
            state.renderContext.viewportSizeX = width;
            state.renderContext.viewportSizeY = height;
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

            for (bool textured : {false, true}) for (bool onD3DSample : {true, false})
            {
                // rad .002 is subpixel and survives ES's minimum subpixel grid.
                // MilkDrop .5 maps to the integer D3D sample (width/2,height/2).
                std::ostringstream source;
                source.precision(17);
                source << "[preset00]\nshapecode_0_enabled=1\nshapecode_0_sides=10\n"
                       << "shapecode_0_num_inst=1\nshapecode_0_rad=0.002\nshapecode_0_textured="
                       << textured << "\nshapecode_0_x=" << (.5 + (onD3DSample ? 0 : .5 / width))
                       << "\nshapecode_0_y=" << (.5 + (onD3DSample ? 0 : .5 / height))
                       << "\nshapecode_0_r=1\nshapecode_0_g=1\nshapecode_0_b=1\nshapecode_0_a=1\n"
                       << "shapecode_0_r2=1\nshapecode_0_g2=1\nshapecode_0_b2=1\nshapecode_0_a2=1\n"
                       << "shapecode_0_border_a=0\n";
                std::istringstream input(source.str());
                PresetFileParser parser;
                Check(parser.Read(input), "preset parse failed");
                CustomShape shape(state);
                shape.Initialize(parser, 0);
                std::vector<std::string> warnings;
                shape.CompileCodeAndRunInitExpressions(warnings);
                Check(warnings.empty(), "shape equations failed");

                for (int repeat = 0; repeat < 2; ++repeat)
                {
                    glClearColor(0, 0, 0, 0);
                    glClear(GL_COLOR_BUFFER_BIT);
                    shape.Draw();
                    std::vector<unsigned char> pixels(width * height * 4);
                    glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
                    int count = 0;
                    for (int pixel = 0; pixel < width * height; ++pixel)
                        if (pixels[pixel * 4]) ++count;
                    std::cout << width << 'x' << height << " textured=" << textured
                              << " integer-centre=" << onD3DSample << " pixels=" << count << '\n';
                    Check(count == (onD3DSample ? 1 : 0),
                          "shape coverage differs from MilkDrop 2 / D3D9 integer sample centres");
                    if (onD3DSample)
                        Check(pixels[((height / 2 - 1) * width + width / 2) * 4] == 255,
                              "D3D pixel address or colour changed");
                    CheckSharedProjection(state.untexturedShader.lock());
                    CheckSharedProjection(state.texturedShader.lock());
                    Check(glGetError() == GL_NO_ERROR, "shape GL error");
                }
            }
            glBindFramebuffer(GL_FRAMEBUFFER, 0);
            glDeleteFramebuffers(1, &fbo);
        }
        return 0;
    }
    catch (const std::exception& e)
    {
        std::cerr << e.what() << '\n';
        return 1;
    }
}
