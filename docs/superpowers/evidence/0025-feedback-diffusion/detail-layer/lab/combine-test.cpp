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
    Target(int width, int height, const std::vector<unsigned char>& bytes, bool floating = false) : w(width), h(height) {
        glGenTextures(1, &tex); glBindTexture(GL_TEXTURE_2D, tex);
        glTexImage2D(GL_TEXTURE_2D, 0, floating ? GL_RGBA32F : GL_RGBA8, w, h, 0, GL_RGBA,
                     floating ? GL_FLOAT : GL_UNSIGNED_BYTE, floating ? nullptr : bytes.data());
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

static void Case(GLuint combine, GLuint down, int scale, int base, float alpha, bool invert)
{
    const int count = scale * scale;
    auto bytes = Solid(count, invert ? 255 : 0);
    // A sparse bright dot on black (or its white-background inverse). The
    // authored base is much darker/brighter than the native warp's mean.
    for (int channel = 0; channel < 3; ++channel) bytes[(count / 2) * 4 + channel] = invert ? 0 : 180;
    Target low(1, 1, Solid(1, base)), warp(scale, scale, bytes);
    Target mean(1, 1, Solid(1, 0)), combined(scale, scale, Solid(count, 0));
    glUseProgram(down); Bind(down, "src", 0, warp);
    glUniform1i(glGetUniformLocation(down, "S"), scale); Draw(mean);
    glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
    glUniform1f(glGetUniformLocation(combine, "alpha"), alpha);
    glUniform2f(glGetUniformLocation(combine, "native"), scale, scale); Draw(combined);
    std::vector<unsigned char> actual(count * 4);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, combined.fbo);
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

static void Reconstruction(GLuint combine, int scale)
{
    auto values = Solid(3, 0);
    for (int channel = 0; channel < 3; ++channel) values[4 + channel] = 180;
    Target low(3, 1, values), warp(3 * scale, scale, Solid(3 * scale * scale, 0));
    Target mean(3, 1, Solid(3, 0)), combined(3 * scale, scale, Solid(3 * scale * scale, 0));
    glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
    glUniform1f(glGetUniformLocation(combine, "alpha"), 1);
    glUniform2f(glGetUniformLocation(combine, "native"), 3 * scale, scale); Draw(combined);
    std::vector<unsigned char> actual(3 * scale * scale * 4);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, combined.fbo);
    glReadPixels(0, 0, combined.w, combined.h, GL_RGBA, GL_UNSIGNED_BYTE, actual.data());
    // Hand-derived GL_LINEAR samples of the three authored cells [0,180,0].
    const std::vector<int> row = scale == 2 ? std::vector<int>{0,45,135,135,45,0}
                                          : std::vector<int>{0,0,60,120,180,120,60,0,0};
    for (int y = 0; y < scale; ++y) for (int x = 0; x < 3 * scale; ++x) for (int channel = 0; channel < 3; ++channel)
        if (std::abs(int(actual[(y * 3 * scale + x) * 4 + channel]) - row[x]) > 1)
            throw std::runtime_error("zero-detail combine changed bilinear authored reconstruction");
}

static void NoClipping(GLuint combine, GLuint down, int scale, float alpha)
{
    const int count = scale * scale;
    auto native = Solid(count, 0);
    for (int channel = 0; channel < 3; ++channel) native[(count / 2) * 4 + channel] = 180;
    Target low(1, 1, Solid(1, 5)), warp(scale, scale, native), mean(1, 1, Solid(1, 0));
    Target output(scale, scale, {}, true);
    glUseProgram(down); Bind(down, "src", 0, warp);
    glUniform1i(glGetUniformLocation(down, "S"), scale); Draw(mean);
    glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
    glUniform1f(glGetUniformLocation(combine, "alpha"), alpha);
    glUniform2f(glGetUniformLocation(combine, "native"), scale, scale); Draw(output);
    std::vector<float> values(count * 4);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, output.fbo);
    glReadPixels(0, 0, scale, scale, GL_RGBA, GL_FLOAT, values.data());
    double sum = 0;
    for (int i = 0; i < count; ++i) {
        float value = values[i * 4];
        if (!std::isfinite(value) || value < -1e-6 || value > 1.0f + 1e-6)
            throw std::runtime_error("combine requires framebuffer clipping");
        sum += value;
    }
    if (std::abs(sum / count - 5.0 / 255.0) > 1e-5)
        throw std::runtime_error("combine detail has a nonzero block mean");
}

static void ColoredFeedback(GLuint combine, GLuint down, int scale)
{
    const int cw = 3, ch = 2, w = cw * scale, h = ch * scale;
    auto lowBytes = Solid(cw * ch, 0), highBytes = Solid(w * h, 0);
    const int colors[6][3] = {{5, 120, 250}, {80, 20, 200}, {250, 128, 5},
                              {20, 220, 80}, {128, 128, 128}, {200, 10, 240}};
    for (int i = 0; i < cw * ch; ++i) for (int channel = 0; channel < 3; ++channel)
        lowBytes[i * 4 + channel] = colors[i][channel];
    uint32_t random = 12345;
    for (int i = 0; i < w * h; ++i) for (int channel = 0; channel < 3; ++channel) {
        random = random * 1664525u + 1013904223u;
        highBytes[i * 4 + channel] = random >> 24;
    }
    Target low(cw, ch, lowBytes), warp(w, h, highBytes), mean(cw, ch, Solid(cw * ch, 0));
    Target output(w, h, {}, true), reference(w, h, {}, true);
    std::vector<float> actual(w * h * 4), base(actual.size());
    glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
    glUniform1f(glGetUniformLocation(combine, "alpha"), 0);
    glUniform2f(glGetUniformLocation(combine, "native"), w, h); Draw(reference);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, reference.fbo);
    glReadPixels(0, 0, w, h, GL_RGBA, GL_FLOAT, base.data());
    bool retainedDetail = false;
    for (int frame = 0; frame < 32; ++frame) {
        glUseProgram(down); Bind(down, "src", 0, warp);
        glUniform1i(glGetUniformLocation(down, "S"), scale); Draw(mean);
        glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
        glUniform1f(glGetUniformLocation(combine, "alpha"), frame % 2 ? 0.5f : 1.0f);
        glUniform2f(glGetUniformLocation(combine, "native"), w, h); Draw(output);
        glBindFramebuffer(GL_READ_FRAMEBUFFER, output.fbo);
        glReadPixels(0, 0, w, h, GL_RGBA, GL_FLOAT, actual.data());
        for (int y = 0; y < ch; ++y) for (int x = 0; x < cw; ++x) for (int channel = 0; channel < 3; ++channel) {
            double delta = 0;
            for (int j = 0; j < scale; ++j) for (int i = 0; i < scale; ++i) {
                int pixel = ((y * scale + j) * w + x * scale + i) * 4 + channel;
                if (!std::isfinite(actual[pixel]) || actual[pixel] < -1e-6 || actual[pixel] > 1 + 1e-6)
                    throw std::runtime_error("colored feedback requires clipping");
                delta += actual[pixel] - base[pixel];
                if (std::abs(actual[pixel] - base[pixel]) > 0.01) retainedDetail = true;
            }
            if (std::abs(delta / (scale * scale)) > 1e-5)
                throw std::runtime_error("colored feedback accumulated block-mean drift");
        }
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, warp.fbo);
        glBlitFramebuffer(0, 0, w, h, 0, 0, w, h, GL_COLOR_BUFFER_BIT, GL_NEAREST);
    }
    if (!retainedDetail) throw std::runtime_error("limiter reduced colored feedback to Standard");
    if (glGetError() != GL_NO_ERROR) throw std::runtime_error("OpenGL error in colored feedback");
}

static void ZeroResidualAtWhite(GLuint combine, GLuint down)
{
    auto lowBytes = Solid(2, 128), highBytes = Solid(8, 85);
    for (int channel = 0; channel < 3; ++channel) {
        lowBytes[channel] = 255;
        highBytes[4 + channel] = 0;
        highBytes[5 * 4 + channel] = 170;
    }
    Target low(2, 1, lowBytes), warp(4, 2, highBytes), mean(2, 1, Solid(2, 0));
    Target output(4, 2, {}, true);
    glUseProgram(down); Bind(down, "src", 0, warp);
    glUniform1i(glGetUniformLocation(down, "S"), 2); Draw(mean);
    glUseProgram(combine); Bind(combine, "Lw", 0, low); Bind(combine, "Hw", 1, warp); Bind(combine, "D", 2, mean);
    glUniform1f(glGetUniformLocation(combine, "alpha"), 1);
    glUniform2f(glGetUniformLocation(combine, "native"), 4, 2); Draw(output);
    std::vector<float> values(8 * 4);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, output.fbo);
    glReadPixels(0, 0, 4, 2, GL_RGBA, GL_FLOAT, values.data());
    // White pixels have exactly zero residual; only the +/-85/255 pair
    // should bound the gain. Their available headroom permits visible detail.
    if (values[5 * 4] - values[4] < 0.1f)
        throw std::runtime_error("zero residual at white suppressed valid neighboring detail");
}

int main(int argc, char** argv)
{
    try {
        if (argc != 3) throw std::runtime_error("expected combine and down shader paths");
        GlCapture context(8, 8);
        GLuint vao; glGenVertexArrays(1, &vao); glBindVertexArray(vao);
        GLuint combine = LoadProgram(argv[1]), down = LoadProgram(argv[2]);
        int cases = 0;
        for (int scale : {2, 3}) for (float alpha : {0.0f, 0.5f, 1.0f}) {
            for (int base : {0, 5, 128, 250, 255}) {
                Case(combine, down, scale, base, alpha, base > 128); ++cases;
            }
        }
        for (int scale : {2, 3}) {
            Reconstruction(combine, scale); ++cases;
            for (float alpha : {0.5f, 1.0f}) { NoClipping(combine, down, scale, alpha); ++cases; }
            ColoredFeedback(combine, down, scale); ++cases;
        }
        ZeroResidualAtWhite(combine, down); ++cases;
        glDeleteProgram(combine); glDeleteProgram(down); glDeleteVertexArrays(1, &vao);
        std::cout << cases << " combine cases passed (RGBA8 storage, float range/mean, 32-frame colored feedback)\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
