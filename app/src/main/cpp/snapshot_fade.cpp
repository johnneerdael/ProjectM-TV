#include "snapshot_fade.h"

#include <android/log.h>

#include <algorithm>

#define LOG_TAG "projectM-Native"
#define LOGW(...) __android_log_print(ANDROID_LOG_WARN, LOG_TAG, __VA_ARGS__)

namespace {

// Full-screen triangle from gl_VertexID; no vertex buffers needed.
constexpr const char* kVertexShader = R"(#version 300 es
out vec2 vUv;
void main() {
    vec2 p = vec2(float((gl_VertexID << 1) & 2), float(gl_VertexID & 2));
    vUv = p;
    gl_Position = vec4(p * 2.0 - 1.0, 0.0, 1.0);
}
)";

constexpr const char* kFragmentShader = R"(#version 300 es
precision mediump float;
uniform sampler2D uSnapshot;
uniform float uAlpha;
uniform float uScale;
in vec2 vUv;
out vec4 fragColor;
void main() {
    vec2 uv = (vUv - 0.5) / uScale + 0.5;
    fragColor = vec4(texture(uSnapshot, uv).rgb, uAlpha);
}
)";

constexpr float kZoomPerSecond = 0.06f;  // the outgoing frame drifts towards the viewer

GLuint Compile(GLenum type, const char* source) {
    GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint ok = GL_FALSE;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        char log[512] = {0};
        glGetShaderInfoLog(shader, sizeof(log), nullptr, log);
        LOGW("Transition shader failed to compile: %s", log);
        glDeleteShader(shader);
        return 0;
    }
    return shader;
}

}  // namespace

bool SnapshotFade::EnsureProgram() {
    if (program_) return true;
    if (programFailed_) return false;
    programFailed_ = true;  // cleared on success; never retry a broken driver every switch
    GLuint vs = Compile(GL_VERTEX_SHADER, kVertexShader);
    GLuint fs = vs ? Compile(GL_FRAGMENT_SHADER, kFragmentShader) : 0;
    if (!fs) {
        if (vs) glDeleteShader(vs);
        return false;
    }
    GLuint program = glCreateProgram();
    glAttachShader(program, vs);
    glAttachShader(program, fs);
    glLinkProgram(program);
    glDeleteShader(vs);
    glDeleteShader(fs);
    GLint ok = GL_FALSE;
    glGetProgramiv(program, GL_LINK_STATUS, &ok);
    if (!ok) {
        LOGW("Transition shader failed to link");
        glDeleteProgram(program);
        return false;
    }
    program_ = program;
    alphaLoc_ = glGetUniformLocation(program_, "uAlpha");
    scaleLoc_ = glGetUniformLocation(program_, "uScale");
    GLint samplerLoc = glGetUniformLocation(program_, "uSnapshot");
    GLint previous = 0;
    glGetIntegerv(GL_CURRENT_PROGRAM, &previous);
    glUseProgram(program_);
    glUniform1i(samplerLoc, 0);
    glUseProgram(static_cast<GLuint>(previous));
    glGenVertexArrays(1, &vao_);
    programFailed_ = false;
    return true;
}

bool SnapshotFade::Capture(int width, int height) {
    Stop();
    if (width <= 0 || height <= 0 || !EnsureProgram()) return false;

    GLint readFbo = 0, texture = 0, activeTexture = 0;
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &readFbo);
    glGetIntegerv(GL_ACTIVE_TEXTURE, &activeTexture);
    glActiveTexture(GL_TEXTURE0);
    glGetIntegerv(GL_TEXTURE_BINDING_2D, &texture);

    glGenTextures(1, &texture_);
    glBindTexture(GL_TEXTURE_2D, texture_);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
    // Unsized RGB is copyable from any window format (RGBA8888, RGBX8888 or RGB565).
    glBindFramebuffer(GL_READ_FRAMEBUFFER, 0);
    while (glGetError() != GL_NO_ERROR) {}
    glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 0, 0, width, height, 0);
    bool ok = glGetError() == GL_NO_ERROR;

    glBindTexture(GL_TEXTURE_2D, static_cast<GLuint>(texture));
    glActiveTexture(static_cast<GLenum>(activeTexture));
    glBindFramebuffer(GL_READ_FRAMEBUFFER, static_cast<GLuint>(readFbo));
    if (!ok) {
        LOGW("Could not capture the outgoing frame; using projectM's own transition");
        Stop();
    }
    return ok;
}

void SnapshotFade::Start(double now, double seconds) {
    if (!texture_ || seconds <= 0) {
        Stop();
        return;
    }
    active_ = true;
    start_ = now;
    duration_ = seconds;
}

void SnapshotFade::Draw(double now, int width, int height) {
    if (!active_) return;
    float t = static_cast<float>((now - start_) / duration_);
    if (t >= 1.f) {
        Stop();
        return;
    }
    t = std::max(t, 0.f);
    float alpha = 1.f - t * t * (3.f - 2.f * t);  // smoothstep ease-out of the old frame
    float scale = 1.f + kZoomPerSecond * static_cast<float>(now - start_);

    // Save exactly the state this pass changes.
    GLint program = 0, vao = 0, activeTexture = 0, texture = 0, sampler = 0, drawFbo = 0;
    GLint viewport[4] = {0, 0, 0, 0};
    glGetIntegerv(GL_VIEWPORT, viewport);
    GLint srcRgb = 0, dstRgb = 0, srcAlpha = 0, dstAlpha = 0, eqRgb = 0, eqAlpha = 0;
    glGetIntegerv(GL_CURRENT_PROGRAM, &program);
    glGetIntegerv(GL_VERTEX_ARRAY_BINDING, &vao);
    glGetIntegerv(GL_ACTIVE_TEXTURE, &activeTexture);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING, &drawFbo);
    glGetIntegerv(GL_BLEND_SRC_RGB, &srcRgb);
    glGetIntegerv(GL_BLEND_DST_RGB, &dstRgb);
    glGetIntegerv(GL_BLEND_SRC_ALPHA, &srcAlpha);
    glGetIntegerv(GL_BLEND_DST_ALPHA, &dstAlpha);
    glGetIntegerv(GL_BLEND_EQUATION_RGB, &eqRgb);
    glGetIntegerv(GL_BLEND_EQUATION_ALPHA, &eqAlpha);
    GLboolean blend = glIsEnabled(GL_BLEND);
    GLboolean depth = glIsEnabled(GL_DEPTH_TEST);
    GLboolean scissor = glIsEnabled(GL_SCISSOR_TEST);
    GLboolean cull = glIsEnabled(GL_CULL_FACE);
    glActiveTexture(GL_TEXTURE0);
    glGetIntegerv(GL_TEXTURE_BINDING_2D, &texture);
    glGetIntegerv(GL_SAMPLER_BINDING, &sampler);

    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0);
    glViewport(0, 0, width, height);
    glDisable(GL_DEPTH_TEST);
    glDisable(GL_SCISSOR_TEST);
    glDisable(GL_CULL_FACE);
    glEnable(GL_BLEND);
    glBlendEquation(GL_FUNC_ADD);
    glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ZERO, GL_ONE);
    glUseProgram(program_);
    glUniform1f(alphaLoc_, alpha);
    glUniform1f(scaleLoc_, scale);
    glBindSampler(0, 0);  // projectM binds sampler objects, which would override our filtering
    glBindTexture(GL_TEXTURE_2D, texture_);
    glBindVertexArray(vao_);
    glDrawArrays(GL_TRIANGLES, 0, 3);

    glBindVertexArray(static_cast<GLuint>(vao));
    glBindTexture(GL_TEXTURE_2D, static_cast<GLuint>(texture));
    glBindSampler(0, static_cast<GLuint>(sampler));
    glActiveTexture(static_cast<GLenum>(activeTexture));
    glUseProgram(static_cast<GLuint>(program));
    glBlendEquationSeparate(static_cast<GLenum>(eqRgb), static_cast<GLenum>(eqAlpha));
    glBlendFuncSeparate(static_cast<GLenum>(srcRgb), static_cast<GLenum>(dstRgb),
                        static_cast<GLenum>(srcAlpha), static_cast<GLenum>(dstAlpha));
    if (!blend) glDisable(GL_BLEND);
    if (depth) glEnable(GL_DEPTH_TEST);
    if (scissor) glEnable(GL_SCISSOR_TEST);
    if (cull) glEnable(GL_CULL_FACE);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, static_cast<GLuint>(drawFbo));
    glViewport(viewport[0], viewport[1], viewport[2], viewport[3]);
}

void SnapshotFade::Stop() {
    active_ = false;
    if (texture_) {
        glDeleteTextures(1, &texture_);
        texture_ = 0;
    }
}

void SnapshotFade::Forget() {
    active_ = false;
    texture_ = program_ = vao_ = 0;
    programFailed_ = false;
}

void SnapshotFade::Release() {
    Stop();
    if (program_) glDeleteProgram(program_);
    if (vao_) glDeleteVertexArrays(1, &vao_);
    Forget();
}
