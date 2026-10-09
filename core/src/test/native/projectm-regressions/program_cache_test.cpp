// The program binary cache switch (patch 0035): off, programs are linked from source without the
// binary-retrievable hint and never loaded with glProgramBinary; on again, the cache starts empty.
#include "gl_context.hpp"
#include <Renderer/Shader.hpp>
#include <projectM-4/render_opengl.h>

#include <cstdint>
#include <iostream>
#include <stdexcept>
#include <string>

namespace {

void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}

struct Stats
{
    uint32_t hits{};
    uint32_t misses{};
};

Stats CacheStats()
{
    Stats stats;
    projectm_opengl_program_cache_stats(&stats.hits, &stats.misses);
    return stats;
}

#ifdef USE_GLES
const char* const versionLine = "#version 300 es\nprecision mediump float;\n";
#else
const char* const versionLine = "#version 330\n";
#endif

std::string VertexSource()
{
    return std::string(versionLine) + "layout(location = 0) in vec2 position;\n"
                                      "void main() { gl_Position = vec4(position, 0.0, 1.0); }\n";
}

std::string FragmentSource(const char* colour)
{
    return std::string(versionLine) + "out vec4 color;\nvoid main() { color = vec4(" + colour + "); }\n";
}

// Compiles through projectM's Shader and returns the linked program's binary-retrievable hint
// (GL_FALSE where the context cannot report it).
GLint CompileAndInspect(libprojectM::Renderer::Shader& shader, const char* colour)
{
    shader.CompileProgram(VertexSource(), FragmentSource(colour));
    libprojectM::Renderer::Shader::InvalidateBoundProgram();
    shader.Bind();
    GLint program{};
    glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    Check(program != 0, "no program bound after compiling");
    GLint linked{};
    glGetProgramiv(static_cast<GLuint>(program), GL_LINK_STATUS, &linked);
    Check(linked == GL_TRUE, "program did not link");
    GLint hint{GL_FALSE};
#ifdef USE_GLES
    glGetProgramiv(static_cast<GLuint>(program), GL_PROGRAM_BINARY_RETRIEVABLE_HINT, &hint);
#endif
    Check(glGetError() == GL_NO_ERROR, "GL error while inspecting the program");
    return hint;
}

} // namespace

int main()
{
    try
    {
        GLContext context;
        GLint formats{};
#ifdef USE_GLES
        glGetIntegerv(GL_NUM_PROGRAM_BINARY_FORMATS, &formats);
#endif
        const bool binaries = formats > 0;
        using libprojectM::Renderer::Shader;

        // Enabled (default): a fresh source is compiled with the hint; with binary formats, the
        // same source then loads from the cache.
        Stats before = CacheStats();
        {
            Shader first;
            GLint hint = CompileAndInspect(first, "1.0, 0.0, 0.0, 1.0");
#ifdef USE_GLES
            Check(hint == GL_TRUE, "enabled cache must request retrievable binaries");
#else
            (void) hint;
#endif
            Shader second;
            CompileAndInspect(second, "1.0, 0.0, 0.0, 1.0");
        }
        Stats enabled = CacheStats();
        if (binaries)
        {
            Check(enabled.hits == before.hits + 1, "enabled cache must load the repeated program");
        }

        // Disabled: every program is linked from source, without the hint, and never loaded from
        // a binary, also a source that was cached before.
        projectm_opengl_set_program_cache_enabled(false);
        {
            Shader repeated;
            GLint hint = CompileAndInspect(repeated, "1.0, 0.0, 0.0, 1.0");
            Check(hint == GL_FALSE, "disabled cache must not request retrievable binaries");
            Shader fresh;
            CompileAndInspect(fresh, "0.0, 1.0, 0.0, 1.0");
            Shader freshAgain;
            CompileAndInspect(freshAgain, "0.0, 1.0, 0.0, 1.0");
        }
        Stats disabled = CacheStats();
        Check(disabled.hits == enabled.hits, "disabled cache must not load any program binary");
#ifdef USE_GLES
        Check(disabled.misses == enabled.misses + 3, "disabled cache must count compiled programs");
#endif

        // Enabled again: entries cached before the switch were dropped, so the old source is
        // compiled once more, then cached.
        projectm_opengl_set_program_cache_enabled(true);
        {
            Shader again;
            GLint hint = CompileAndInspect(again, "1.0, 0.0, 0.0, 1.0");
#ifdef USE_GLES
            Check(hint == GL_TRUE, "re-enabled cache must request retrievable binaries");
#else
            (void) hint;
#endif
            Stats reenabled = CacheStats();
            Check(reenabled.hits == disabled.hits, "re-enabled cache must start empty");
            Shader cached;
            CompileAndInspect(cached, "1.0, 0.0, 0.0, 1.0");
        }
        Stats last = CacheStats();
        if (binaries)
        {
            Check(last.hits == disabled.hits + 1, "re-enabled cache must cache programs again");
        }

        std::cout << "program cache switch: binary formats=" << formats << " hits=" << last.hits
                  << " misses=" << last.misses << (binaries ? "" : " (binary loads not exercised)") << "\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "program-cache-regressions: " << error.what() << "\n";
        return 1;
    }
}
