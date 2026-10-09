#pragma once
#include <SDL.h>
#if __has_include(<Renderer/Platform/GladLoader.hpp>)
#include <Renderer/OpenGL.h>
#include <Renderer/Platform/GLResolver.hpp>
#include <Renderer/Platform/GladLoader.hpp>
#define PRESET_LAB_GLAD_LOADER
#elif defined(__APPLE__)
#include <OpenGL/gl3.h>
#else
#define GL_GLEXT_PROTOTYPES
#include <SDL_opengl.h>
#endif
#include <stdexcept>
#include <vector>

class GlCapture {
public:
    SDL_Window* window = nullptr;
    SDL_GLContext context = nullptr;
    GLuint framebuffer = 0;
    GLuint texture = 0;
    int width, height;

    GlCapture(int w, int h) : width(w), height(h) {
        if (SDL_Init(SDL_INIT_VIDEO)) throw std::runtime_error(SDL_GetError());
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 3);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, 3);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS, SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG);
        window = SDL_CreateWindow("Preset Lab", 0, 0, w, h, SDL_WINDOW_OPENGL | SDL_WINDOW_HIDDEN);
        if (!window) throw std::runtime_error(SDL_GetError());
        context = SDL_GL_CreateContext(window);
        if (!context) throw std::runtime_error(SDL_GetError());
        if (SDL_GL_MakeCurrent(window, context)) throw std::runtime_error(SDL_GetError());
#ifdef PRESET_LAB_GLAD_LOADER
        if (!libprojectM::Renderer::Platform::GLResolver::Instance().Initialize(nullptr, nullptr))
            throw std::runtime_error("could not initialize GL resolver for SDL context");
        if (!libprojectM::Renderer::Platform::GladLoader::Instance().Initialize())
            throw std::runtime_error("could not load entry points for the available SDL GL context");
#endif
        glGenFramebuffers(1, &framebuffer);
        glGenTextures(1, &texture);
        glBindTexture(GL_TEXTURE_2D, texture);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
            throw std::runtime_error("capture framebuffer incomplete");
        glClearColor(0, 0, 0, 1);
        glClear(GL_COLOR_BUFFER_BIT);
        glPixelStorei(GL_PACK_ALIGNMENT, 1);
    }
    std::vector<unsigned char> Read() {
        std::vector<unsigned char> data(width * height * 3), flipped(data.size());
        glBindFramebuffer(GL_READ_FRAMEBUFFER, framebuffer);
        glReadBuffer(GL_COLOR_ATTACHMENT0);
        glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE, data.data());
        for (int row = 0; row < height; ++row)
            std::copy_n(data.data() + (height - row - 1) * width * 3, width * 3,
                        flipped.data() + row * width * 3);
        return flipped;
    }
    ~GlCapture() {
        if (context) {
            glDeleteFramebuffers(1, &framebuffer);
            glDeleteTextures(1, &texture);
            SDL_GL_DeleteContext(context);
        }
        if (window) SDL_DestroyWindow(window);
        SDL_Quit();
    }
};
