#pragma once
#include <stdexcept>
#include <Renderer/OpenGL.h>
#include <Renderer/Platform/GLResolver.hpp>
#include <Renderer/Platform/GladLoader.hpp>
#ifdef __APPLE__
#include <OpenGL/OpenGL.h>
#else
#include <EGL/egl.h>
#endif

class GLContext
{
public:
    GLContext()
    {
#ifdef __APPLE__
        CGLPixelFormatAttribute attributes[] = {
            kCGLPFAOpenGLProfile, static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_3_2_Core),
            static_cast<CGLPixelFormatAttribute>(0)};
        CGLPixelFormatObj format = nullptr;
        GLint count = 0;
        Require(CGLChoosePixelFormat(attributes, &format, &count) == kCGLNoError && format,
              "could not choose a GL pixel format");
        const auto error = CGLCreateContext(format, nullptr, &context);
        CGLDestroyPixelFormat(format);
        Require(error == kCGLNoError, "could not create a GL context");
        Require(CGLSetCurrentContext(context) == kCGLNoError, "could not make GL context current");
#else
        display = eglGetDisplay(EGL_DEFAULT_DISPLAY);
        Require(eglInitialize(display, nullptr, nullptr), "could not initialize EGL");
        Require(eglBindAPI(EGL_OPENGL_ES_API), "could not bind GLES");
        const EGLint attributes[] = {EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
                                     EGL_RENDERABLE_TYPE, EGL_OPENGL_ES3_BIT,
                                     EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_NONE};
        EGLConfig config;
        EGLint count;
        Require(eglChooseConfig(display, attributes, &config, 1, &count) && count,
              "could not choose a GLES3 config");
        const EGLint surfaceAttributes[] = {EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE};
        surface = eglCreatePbufferSurface(display, config, surfaceAttributes);
        const EGLint contextAttributes[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
        context = eglCreateContext(display, config, EGL_NO_CONTEXT, contextAttributes);
        Require(surface != EGL_NO_SURFACE && context != EGL_NO_CONTEXT,
              "could not create a GLES3 context");
        Require(eglMakeCurrent(display, surface, surface, context), "could not make GLES current");
#endif
        Require(libprojectM::Renderer::Platform::GLResolver::Instance().Initialize(nullptr, nullptr),
                "could not initialize GL resolver for the current context");
        Require(libprojectM::Renderer::Platform::GladLoader::Instance().Initialize(),
                "could not load entry points for the available GL context");
    }

    ~GLContext()
    {
#ifdef __APPLE__
        CGLSetCurrentContext(nullptr);
        CGLDestroyContext(context);
#else
        eglMakeCurrent(display, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT);
        eglDestroyContext(display, context);
        eglDestroySurface(display, surface);
        eglTerminate(display);
#endif
    }

private:
    static void Require(bool ok, const char* message) { if (!ok) throw std::runtime_error(message); }
#ifdef __APPLE__
    CGLContextObj context = nullptr;
#else
    EGLDisplay display = EGL_NO_DISPLAY;
    EGLSurface surface = EGL_NO_SURFACE;
    EGLContext context = EGL_NO_CONTEXT;
#endif
};
