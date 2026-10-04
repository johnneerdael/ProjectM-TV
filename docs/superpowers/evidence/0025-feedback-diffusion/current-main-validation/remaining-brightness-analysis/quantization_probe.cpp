#include <MilkdropPreset/FeedbackDiffusion.hpp>
#include <Renderer/Texture.hpp>
#include <OpenGL/OpenGL.h>
#include <algorithm>
#include <array>
#include <iostream>
#include <memory>
#include <numeric>
#include <vector>

int main()
{
    CGLPixelFormatAttribute attributes[] = {kCGLPFAOpenGLProfile,
        static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_3_2_Core), static_cast<CGLPixelFormatAttribute>(0)};
    CGLPixelFormatObj format{};
    GLint count{};
    if (CGLChoosePixelFormat(attributes, &format, &count) != kCGLNoError || !format) return 2;
    CGLContextObj context{};
    if (CGLCreateContext(format, nullptr, &context) != kCGLNoError) return 3;
    CGLDestroyPixelFormat(format);
    CGLSetCurrentContext(context);
    constexpr int width = 32, height = 32;
    std::cout << "driver=" << glGetString(GL_RENDERER) << "\n";
    {
        using libprojectM::Renderer::Texture;
        Texture::SetPoolLimit(0);
        auto source = std::make_shared<Texture>("quantization-probe", width, height, GL_RGBA8, GL_RGBA, GL_UNSIGNED_BYTE, false);
        libprojectM::MilkdropPreset::FeedbackDiffusion diffusion;
        GLuint readFramebuffer{};
        glGenFramebuffers(1, &readFramebuffer);
        for (float scale : {2.0f, 3.2475953102111816f})
        {
            diffusion.SetScale(scale);
            if (!diffusion.Active()) return 4;
            for (bool dither : {false, true})
            {
                dither ? glEnable(GL_DITHER) : glDisable(GL_DITHER);
                for (bool constant : {false, true})
                {
                    for (int amplitude : {1, 2, 4, 8, 16})
                    {
                        std::vector<unsigned char> input(width*height*4, 0);
                        for (size_t i=0; i<input.size(); i+=4)
                        {
                            input[i+3] = 255;
                            if (constant) input[i] = static_cast<unsigned char>(amplitude);
                        }
                        if (!constant) input[(16*width+16)*4] = static_cast<unsigned char>(amplitude);
                        source->Bind(0);
                        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, input.data());
                        glViewport(0, 0, width, height);
                        diffusion.Draw(source, false);
                        glBindFramebuffer(GL_READ_FRAMEBUFFER, readFramebuffer);
                        glFramebufferTexture2D(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                                              diffusion.Texture()->TextureID(), 0);
                        glReadBuffer(GL_COLOR_ATTACHMENT0);
                        std::vector<unsigned char> output(input.size());
                        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, output.data());
                        int mass{}, maximum{}, lit{};
                        for (size_t i=0; i<output.size(); i+=4)
                        {
                            mass += output[i];
                            maximum = std::max(maximum, static_cast<int>(output[i]));
                            lit += output[i] != 0;
                        }
                        if (glGetError() != GL_NO_ERROR) return 5;
                        std::cout << "scale=" << scale << " dither=" << dither << " constant=" << constant
                                  << " input_mass=" << amplitude*(constant ? width*height : 1)
                                  << " output_mass=" << mass << " output_max=" << maximum << " lit=" << lit << "\n";
                    }
                }
            }
        }
        glDeleteFramebuffers(1, &readFramebuffer);
    }
    CGLSetCurrentContext(nullptr);
    CGLDestroyContext(context);
}
