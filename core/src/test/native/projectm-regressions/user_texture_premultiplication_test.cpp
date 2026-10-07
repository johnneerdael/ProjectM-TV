// Verify decoded user-image RGBA bytes after the production GPU upload.
#include "gl_context.hpp"
#include <Renderer/TextureManager.hpp>
#include <Renderer/Texture.hpp>

#include <array>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}

struct FixtureDirectory
{
    std::filesystem::path path;
    explicit FixtureDirectory(const char* name) : path(name)
    {
        Check(std::filesystem::create_directory(path), "fixture directory must be new");
    }
    ~FixtureDirectory() { std::filesystem::remove_all(path); }
};

struct ReadFramebuffer
{
    GLuint name{};
    ReadFramebuffer() { glGenFramebuffers(1, &name); }
    ~ReadFramebuffer() { glDeleteFramebuffers(1, &name); }
};

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "pass a new fixture directory");
        GLContext context;
        FixtureDirectory fixture(argv[1]);
        // Independent byte expectations from released SOIL2.c:1523-1527:
        // (channel * alpha + 128) >> 8, including the opaque 129 -> 128 case.
        constexpr std::array<unsigned char, 5> channels{0, 127, 128, 129, 255};
        constexpr std::array<unsigned char, 3> alphas{0, 128, 255};
        constexpr std::array<std::array<unsigned char, 5>, 3> expected{{
            {0, 0, 0, 0, 0}, {0, 64, 64, 65, 128}, {0, 127, 128, 128, 254}}};
        constexpr int width = channels.size() * alphas.size();
        std::array<unsigned char, width * 4> wanted{};
        {
            std::ofstream image(fixture.path / "rgba-compatibility.tga", std::ios::binary);
            std::array<unsigned char, 18> header{};
            header[2] = 2; header[12] = width; header[14] = 1;
            header[16] = 32; header[17] = 0x28; // RGBA, one top-origin row.
            image.write(reinterpret_cast<const char*>(header.data()), header.size());
            for (size_t alpha = 0; alpha < alphas.size(); ++alpha)
            for (size_t value = 0; value < channels.size(); ++value)
            {
                const auto green = channels.size() - 1 - value;
                const auto blue = (value + 2) % channels.size();
                const unsigned char bgra[]{channels[blue], channels[green], channels[value], alphas[alpha]};
                image.write(reinterpret_cast<const char*>(bgra), sizeof(bgra));
                const auto offset = (alpha * channels.size() + value) * 4;
                wanted[offset] = expected[alpha][value];
                wanted[offset + 1] = expected[alpha][green];
                wanted[offset + 2] = expected[alpha][blue];
                wanted[offset + 3] = alphas[alpha];
            }
            Check(image.good(), "could not write RGBA fixture");
        }
        libprojectM::Renderer::TextureManager textures({fixture.path.string()});
        const auto descriptor = textures.GetTexture("rgba-compatibility");
        Check(!descriptor.Empty(), "production user texture did not load");
        const auto texture = descriptor.Texture();
        Check(texture->Width() == width && texture->Height() == 1, "decoded dimensions changed");
        ReadFramebuffer framebuffer;
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer.name);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture->TextureID(), 0);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "uploaded texture is not readable");
        glReadBuffer(GL_COLOR_ATTACHMENT0);
        glPixelStorei(GL_PACK_ALIGNMENT, 1);
        std::array<unsigned char, width * 4> actual{};
        glReadPixels(0, 0, width, 1, GL_RGBA, GL_UNSIGNED_BYTE, actual.data());
        Check(glGetError() == GL_NO_ERROR, "RGBA upload/readback GL error");
        for (size_t byte = 0; byte < actual.size(); ++byte)
            Check(actual[byte] == wanted[byte], "uploaded byte " + std::to_string(byte) +
                  " differs: " + std::to_string(actual[byte]) + " vs " + std::to_string(wanted[byte]));
        std::cout << "Production RGBA upload: all 60 legacy bytes exact; alpha 0/128/255 and RGB 0/127/128/129/255 passed\n";
        return 0;
    }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; return 1; }
}
