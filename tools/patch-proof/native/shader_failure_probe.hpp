#pragma once
#include "vendor/json.hpp"
#include <Renderer/Shader.hpp>
#include <Renderer/OpenGL.h>
#include <map>
#include <string>
#include <vector>
#include <stdexcept>

namespace proof {
inline PFNGLCREATESHADERPROC realCreateShader{};
inline std::map<GLuint, GLenum> observedShaderTypes;
inline size_t createdShaders{};
inline GLuint GLAD_API_PTR TrackCreateShader(GLenum type) {
    const auto id = realCreateShader(type);
    if (id) { observedShaderTypes[id] = type; ++createdShaders; }
    return id;
}
class ShaderTracking {
public:
    ShaderTracking() {
        observedShaderTypes.clear(); createdShaders = 0;
        realCreateShader = glad_glCreateShader;
        if (!realCreateShader) throw std::runtime_error("shader observer requires loaded GL functions");
        glad_glCreateShader = TrackCreateShader;
    }
    ~ShaderTracking() { glad_glCreateShader = realCreateShader; }
    ShaderTracking(const ShaderTracking&) = delete;
    ShaderTracking& operator=(const ShaderTracking&) = delete;
};
inline size_t LiveVertexShaders() {
    size_t count = 0;
    for (const auto& item : observedShaderTypes)
        if (item.second == GL_VERTEX_SHADER && glIsShader(item.first)) ++count;
    return count;
}
inline nlohmann::json ShaderFailureProbe() {
    ShaderTracking tracking;
    constexpr const char* vertex = "#version 300 es\nout vec3 value;\nvoid main(){gl_Position=vec4(0.0,0.0,0.0,1.0);value=vec3(1.0);}";
    constexpr const char* invalid = "#version 300 es\nTHIS_IS_NOT_VALID_GLSL\n";
    constexpr const char* valid = "#version 300 es\nprecision highp float;\nin vec3 value;out vec4 colour;void main(){colour=vec4(value,1.0);}";
    std::vector<size_t> liveAfterFailure;
    std::vector<std::string> errors;
    for (int attempt = 0; attempt < 16; ++attempt) {
        bool rejected = false;
        {
            libprojectM::Renderer::Shader shader;
            try { shader.CompileProgram(vertex, invalid); }
            catch (const libprojectM::Renderer::ShaderException& error) {
                rejected = true; errors.push_back(error.what());
            }
        }
        if (!rejected) throw std::runtime_error("driver accepted intentionally invalid fragment shader");
        liveAfterFailure.push_back(LiveVertexShaders());
    }
    const auto leaked = LiveVertexShaders();
    bool retryLinked = false;
    {
        libprojectM::Renderer::Shader retry;
        retry.CompileProgram(vertex, valid);
        retry.Bind();
        GLint program = 0, linked = 0;
        glGetIntegerv(GL_CURRENT_PROGRAM, &program);
        glGetProgramiv(static_cast<GLuint>(program), GL_LINK_STATUS, &linked);
        retryLinked = linked == GL_TRUE;
        libprojectM::Renderer::Shader::Unbind();
    }
    // Observe first; release the diagnostic's leaked objects before rendering the preset.
    for (const auto& item : observedShaderTypes)
        if (glIsShader(item.first)) glDeleteShader(item.first);
    if (createdShaders < 34 || !retryLinked || glGetError() != GL_NO_ERROR)
        throw std::runtime_error("shader observer/retry did not satisfy its GL control");
    return {{"kind", "shader-fragment-failure"}, {"attempts", 16},
            {"created_shader_objects", createdShaders}, {"live_vertex_after_each_failure", liveAfterFailure},
            {"live_vertex_before_cleanup", leaked}, {"retry_linked", retryLinked},
            {"observer_gl_error", 0}, {"diagnostic_cleanup_complete", LiveVertexShaders() == 0},
            {"rejection_messages", errors}};
}
} // namespace proof
