#include <algorithm>
#include "gl_capture.hpp"
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <string>

static GLuint Program(const std::string& fragment)
{
    const std::string vertex = "#version 330\nvoid main() { vec2 p = vec2(gl_VertexID == 1 ? 3.0 : -1.0, gl_VertexID == 2 ? 3.0 : -1.0); gl_Position = vec4(p, 0.0, 1.0); }";
    GLuint program = glCreateProgram();
    for (auto type : {GL_VERTEX_SHADER, GL_FRAGMENT_SHADER}) {
        const char* source = type == GL_VERTEX_SHADER ? vertex.c_str() : fragment.c_str();
        GLuint shader = glCreateShader(type);
        glShaderSource(shader, 1, &source, nullptr);
        glCompileShader(shader);
        GLint ok; glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
        if (!ok) {
            char log[4096]; glGetShaderInfoLog(shader, sizeof(log), nullptr, log);
            throw std::runtime_error(log);
        }
        glAttachShader(program, shader);
        glDeleteShader(shader);
    }
    glLinkProgram(program);
    GLint ok; glGetProgramiv(program, GL_LINK_STATUS, &ok);
    if (!ok) {
        char log[4096]; glGetProgramInfoLog(program, sizeof(log), nullptr, log);
        throw std::runtime_error(log);
    }
    return program;
}

static GLuint LoadProgram(const char* path)
{
    std::ifstream file(path);
    if (!file) throw std::runtime_error(std::string("cannot read ") + path);
    return Program(std::string(std::istreambuf_iterator<char>(file), {}));
}

struct Target {
    GLuint tex, fbo;
    int w, h;
    Target(int width, int height, const std::vector<unsigned char>& bytes) : w(width), h(height) {
        glGenTextures(1, &tex); glBindTexture(GL_TEXTURE_2D, tex);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, bytes.data());
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE);
        glGenFramebuffers(1, &fbo); glBindFramebuffer(GL_FRAMEBUFFER, fbo);
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex, 0);
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE)
            throw std::runtime_error("fixture framebuffer incomplete");
    }
    ~Target() { glDeleteFramebuffers(1, &fbo); glDeleteTextures(1, &tex); }
};

static std::vector<unsigned char> Solid(int count, int value)
{
    std::vector<unsigned char> bytes(count * 4, static_cast<unsigned char>(value));
    for (int i = 0; i < count; ++i) bytes[i * 4 + 3] = 255;
    return bytes;
}

static void Bind(GLuint prog, const char* name, int unit, const Target& target)
{
    glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, target.tex);
    glUniform1i(glGetUniformLocation(prog, name), unit);
}

static void Draw(const Target& target)
{
    glBindFramebuffer(GL_FRAMEBUFFER, target.fbo); glViewport(0, 0, target.w, target.h);
    glDrawArrays(GL_TRIANGLES, 0, 3);
}

static void Case(GLuint combine, GLuint down, GLuint reanchor, int scale, int base, float alpha, bool invert)
{
    const int count = scale * scale;
    auto bytes = Solid(count, invert ? 255 : 0);
    // A sparse bright dot on black (or its white-background inverse). The
    // authored base is much darker/brighter than the native warp's mean.
    for (int channel = 0; channel < 3; ++channel) bytes[(count / 2) * 4 + channel] = invert ? 0 : 180;
    Target low(1, 1, Solid(1, base)), warp(scale, scale, bytes);
    Target mean(1, 1, Solid(1, 0)), combined(scale, scale, Solid(count, 0));
    Target corrected(scale, scale, Solid(count, 0));
    glUseProgram(down); Bind(down, "src", 0, warp);
    glUniform1i(glGetUniformLocation(down, "S"), scale); Draw(mean);
    glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
    glUniform1f(glGetUniformLocation(combine, "alpha"), alpha);
    glUniform2f(glGetUniformLocation(combine, "native"), scale, scale); Draw(combined);
    const Target* output = &combined;
    if (alpha > 0 && reanchor) {
        glUseProgram(down); Bind(down, "src", 0, combined);
        glUniform1i(glGetUniformLocation(down, "S"), scale); Draw(mean);
        glUseProgram(reanchor); Bind(reanchor, "Lw", 0, low); Bind(reanchor, "Hc", 1, combined); Bind(reanchor, "D", 2, mean);
        glUniform1i(glGetUniformLocation(reanchor, "S"), scale); Draw(corrected);
        output = &corrected;
    }
    std::vector<unsigned char> actual(count * 4);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, output->fbo);
    glReadPixels(0, 0, scale, scale, GL_RGBA, GL_UNSIGNED_BYTE, actual.data());
    for (int channel = 0; channel < 3; ++channel) {
        double sum = 0;
        for (int i = 0; i < count; ++i) sum += actual[i * 4 + channel];
        double error = std::abs(sum / count - base);
        if (error > 1.0) throw std::runtime_error("clipping changed block brightness: S=" + std::to_string(scale)
            + " base=" + std::to_string(base) + " alpha=" + std::to_string(alpha)
            + " mean=" + std::to_string(sum / count));
    }
    if (base == 5 && alpha > 0 && actual[(count / 2) * 4] <= actual[0])
        throw std::runtime_error("correction erased the sparse detail");
    if (glGetError() != GL_NO_ERROR) throw std::runtime_error("OpenGL error in combine regression");
}

int main(int argc, char** argv)
{
    try {
        if (argc != 4) throw std::runtime_error("expected combine, down and reanchor shader paths");
        GlCapture context(8, 8);
        GLuint vao; glGenVertexArrays(1, &vao); glBindVertexArray(vao);
        GLuint combine = LoadProgram(argv[1]), down = LoadProgram(argv[2]);
        GLuint reanchor = std::string(argv[3]) == "-" ? 0 : LoadProgram(argv[3]);
        int cases = 0;
        for (int scale : {2, 3}) for (float alpha : {0.0f, 0.5f, 1.0f}) {
            for (int base : {0, 5, 128, 250, 255}) {
                Case(combine, down, reanchor, scale, base, alpha, base > 128); ++cases;
            }
        }
        glDeleteProgram(combine); glDeleteProgram(down); glDeleteProgram(reanchor); glDeleteVertexArrays(1, &vao);
        std::cout << cases << " RGBA8 combine/reanchor cases passed\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
