// Build as a separate USE_GLES executable with the production loader, resolver,
// probe, Logging and vendored GLAD sources. Run each case in a fresh process:
// their singletons and global GLAD pointers must never share the renderer suite.
// This supplies version-query entry points, not a real EGL context or renderer.
#include <Renderer/OpenGL.h>
#include <Renderer/Platform/GladLoader.hpp>
#include <Renderer/Platform/GLResolver.hpp>
#include <Logging.hpp>

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <string>

namespace {
int apiMajor = 3;
const char* shaderVersion = "OpenGL ES GLSL ES 3.00";

const GLubyte* GLAD_API_PTR GetString(GLenum name)
{
    const char* value = "";
    switch (name)
    {
        case GL_VERSION: value = apiMajor == 3 ? "OpenGL ES 3.0" : "OpenGL ES 2.0"; break;
        case GL_SHADING_LANGUAGE_VERSION: value = shaderVersion; break;
        case GL_VENDOR: value = "ProjectM loader regression"; break;
        case GL_RENDERER: value = "Version-query fixture (no GPU)"; break;
        default: break;
    }
    return reinterpret_cast<const GLubyte*>(value);
}

GLenum GLAD_API_PTR GetError()
{
    return GL_NO_ERROR;
}

void GLAD_API_PTR GetIntegerv(GLenum name, GLint* value)
{
    *value = name == GL_MAJOR_VERSION ? apiMajor : 0;
}

const GLubyte* GLAD_API_PTR GetStringi(GLenum, GLuint)
{
    return reinterpret_cast<const GLubyte*>("");
}

void* Resolve(const char* name, void*)
{
    using libprojectM::Renderer::Platform::FunctionToSymbol;
    if (std::strcmp(name, "glGetString") == 0) return FunctionToSymbol(&GetString);
    if (std::strcmp(name, "glGetError") == 0) return FunctionToSymbol(&GetError);
    if (std::strcmp(name, "glGetIntegerv") == 0) return FunctionToSymbol(&GetIntegerv);
    if (std::strcmp(name, "glGetStringi") == 0) return FunctionToSymbol(&GetStringi);
    return nullptr;
}

void Log(const char* message, int, void*)
{
    std::cerr << message << '\n';
}

void SetEnvironment(const char* name, const char* value)
{
#ifdef _WIN32
    _putenv_s(name, value);
#else
    setenv(name, value, 1);
#endif
}
} // namespace

int main(int argc, char** argv)
{
    if (argc != 2)
    {
        std::cerr << "usage: gles-loader-regressions gles30|gles20|glsl100\n";
        return 2;
    }
    const std::string control = argv[1];
    const bool expected = control == "gles30";
    if (control == "gles20")
    {
        apiMajor = 2;
        shaderVersion = "OpenGL ES GLSL ES 1.00";
    }
    else if (control == "glsl100")
    {
        shaderVersion = "OpenGL ES GLSL ES 1.00";
    }
    else if (control != "gles30")
    {
        std::cerr << "unknown control: " << control << '\n';
        return 2;
    }

    // No native context is created. Disable only its per-call presence gate in
    // this test process; keep GladLoader's real API/GLSL requirement checks.
    SetEnvironment("PROJECTM_GLRESOLVER_STRICT_CONTEXT_GATE", "0");
    SetEnvironment("PROJECTM_GLRESOLVER_TRACE_LOGGING", "0");
    libprojectM::Logging::SetGlobalCallback({&Log, nullptr});
    libprojectM::Logging::SetGlobalLogLevel(libprojectM::Logging::LogLevel::Error);
    using namespace libprojectM::Renderer::Platform;
    if (!GLResolver::Instance().Initialize(&Resolve, nullptr))
    {
        std::cerr << "fixture resolver initialization failed\n";
        return 1;
    }
    const bool loaded = GladLoader::Instance().Initialize();
    if (loaded != expected)
    {
        std::cerr << control << ": loader accepted=" << loaded
                  << ", expected=" << expected << '\n';
        return 1;
    }
    if (loaded && (!GLAD_GL_ES_VERSION_3_0 || GLAD_GL_ES_VERSION_3_1 || GLAD_GL_ES_VERSION_3_2))
    {
        std::cerr << "GLAD did not load exactly the advertised GLES 3.0 version\n";
        return 1;
    }
    std::cout << control << ": expected " << (expected ? "acceptance" : "rejection") << " passed\n";
    return 0;
}
