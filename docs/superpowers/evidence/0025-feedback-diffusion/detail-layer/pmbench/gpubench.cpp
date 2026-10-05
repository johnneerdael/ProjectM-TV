// GPU micro-benchmark for warp fragment shader variants on Android (EGL pbuffer, offscreen FBO).
// usage: gpubench W H canvasW canvasH tapX tapY iterations shader1.frag [shader2.frag ...]
#include <EGL/egl.h>
#include <GLES3/gl3.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

static const char* Vertex = R"(#version 300 es
layout(location = 0) in vec2 pos;
out vec4 frag_COLOR; out highp vec4 frag_TEXCOORD0; out vec2 frag_TEXCOORD1;
void main() {
    gl_Position = vec4(pos, 0.0, 1.0);
    vec2 uv = pos * 0.5 + 0.5;
    frag_COLOR = vec4(0.98);
    frag_TEXCOORD0 = vec4((uv - 0.5) * 0.9787 + 0.5 + vec2(0.0013, -0.0007), uv); // zoom + shift: fractional phases
    frag_TEXCOORD1 = vec2(length(uv - 0.5), 0.0);
})";

static GLuint Compile(GLenum type, const std::string& source)
{
    GLuint s = glCreateShader(type);
    const char* p = source.c_str();
    glShaderSource(s, 1, &p, nullptr);
    glCompileShader(s);
    GLint ok = 0; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) { char log[4096]; glGetShaderInfoLog(s, sizeof log, nullptr, log); fprintf(stderr, "compile failed: %s\n", log); return 0; }
    return s;
}

int main(int argc, char** argv)
{
    if (argc < 9) { fprintf(stderr, "usage\n"); return 2; }
    const int W = atoi(argv[1]), H = atoi(argv[2]);
    const float cw = atof(argv[3]), ch = atof(argv[4]), tx = atof(argv[5]), ty = atof(argv[6]);
    const int iterations = atoi(argv[7]);
    EGLDisplay d = eglGetDisplay(EGL_DEFAULT_DISPLAY); eglInitialize(d, nullptr, nullptr);
    const EGLint ca[] = {EGL_SURFACE_TYPE, EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE, 0x40, EGL_RED_SIZE, 8, EGL_GREEN_SIZE, 8, EGL_BLUE_SIZE, 8, EGL_NONE};
    EGLConfig cfg; EGLint n; eglChooseConfig(d, ca, &cfg, 1, &n);
    const EGLint pa[] = {EGL_WIDTH, 16, EGL_HEIGHT, 16, EGL_NONE};
    EGLSurface surf = eglCreatePbufferSurface(d, cfg, pa);
    const EGLint xa[] = {EGL_CONTEXT_CLIENT_VERSION, 3, EGL_NONE};
    EGLContext ctx = eglCreateContext(d, cfg, EGL_NO_CONTEXT, xa);
    if (!eglMakeCurrent(d, surf, surf, ctx)) { fprintf(stderr, "no context\n"); return 1; }
    printf("renderer: %s\n", glGetString(GL_RENDERER));
    // Source "previous frame": smooth noise-ish pattern.
    const int SW = getenv("SRC_W") ? atoi(getenv("SRC_W")) : W, SH = getenv("SRC_H") ? atoi(getenv("SRC_H")) : H;
    std::vector<unsigned char> pixels(static_cast<size_t>(SW) * SH * 4);
    for (int y = 0; y < SH; ++y) for (int x = 0; x < SW; ++x) { auto* p = &pixels[(static_cast<size_t>(y) * SW + x) * 4];
        p[0] = (x * 7 + y * 3) & 255; p[1] = (x ^ y) & 255; p[2] = ((x * y) >> 4) & 255; p[3] = 255; }
    GLuint tex[4]; glGenTextures(4, tex);
    // A canvas-size texture for the detail layer's small inputs (Lw, D).
    { std::vector<unsigned char> small(static_cast<size_t>(cw) * ch * 4, 128); glBindTexture(GL_TEXTURE_2D, tex[3]);
      glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, static_cast<int>(cw), static_cast<int>(ch), 0, GL_RGBA, GL_UNSIGNED_BYTE, small.data());
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR); }
    glBindTexture(GL_TEXTURE_2D, tex[0]);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, SW, SH, 0, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
    std::vector<unsigned char> vol(32 * 32 * 32 * 4); for (size_t i = 0; i < vol.size(); ++i) vol[i] = (i * 2654435761u) >> 24;
    glBindTexture(GL_TEXTURE_3D, tex[1]);
    glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA8, 32, 32, 32, 0, GL_RGBA, GL_UNSIGNED_BYTE, vol.data());
    glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    // Two render targets, as the warp pass (colour + motion-vector uv).
    // A smooth uv map (RG16F, as projectM's motion-vector map): a zooming read.
    std::vector<float> uvf(static_cast<size_t>(W) * H * 2);
    for (int y = 0; y < H; ++y) for (int x = 0; x < W; ++x) { float u = (x + 0.5f) / W, v = (y + 0.5f) / H;
        uvf[(static_cast<size_t>(y) * W + x) * 2] = (u - 0.5f) * 0.9787f + 0.5013f; uvf[(static_cast<size_t>(y) * W + x) * 2 + 1] = (v - 0.5f) * 0.9787f + 0.4993f; }
    glBindTexture(GL_TEXTURE_2D, tex[2]);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RG16F, W, H, 0, GL_RG, GL_FLOAT, uvf.data());
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST); glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    // Polyphase: s*s layers of (W/s)x(H/s), built from the frame by a separate pass ("@build" argument).
    const int S = getenv("POLY_S") ? atoi(getenv("POLY_S")) : 2;
    const int CW = W / S, CH = H / S, layers = S * S;
    GLuint polyTex; glGenTextures(1, &polyTex); glBindTexture(GL_TEXTURE_2D_ARRAY, polyTex);
    glTexStorage3D(GL_TEXTURE_2D_ARRAY, 1, GL_RGBA8, CW, CH, layers);
    glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MIN_FILTER, GL_LINEAR); glTexParameteri(GL_TEXTURE_2D_ARRAY, GL_TEXTURE_MAG_FILTER, GL_LINEAR);
    std::vector<GLuint> polyFbo((layers + 3) / 4); glGenFramebuffers(static_cast<GLsizei>(polyFbo.size()), polyFbo.data());
    for (size_t g = 0; g < polyFbo.size(); ++g) {
        glBindFramebuffer(GL_FRAMEBUFFER, polyFbo[g]); std::vector<GLenum> b;
        for (int k = 0; k < 4 && static_cast<int>(g * 4) + k < layers; ++k) {
            glFramebufferTextureLayer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + k, polyTex, 0, static_cast<GLint>(g * 4 + k)); b.push_back(GL_COLOR_ATTACHMENT0 + k); }
        glDrawBuffers(static_cast<GLsizei>(b.size()), b.data());
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) { fprintf(stderr, "poly fbo incomplete\n"); return 1; }
    }
    // Two framebuffers, alternated per draw: each draw is its own render pass, so tile-based overdraw
    // elimination cannot drop earlier full-screen draws.
    GLuint fbo[2], rt[4]; glGenFramebuffers(2, fbo); glGenTextures(4, rt);
    for (int f = 0; f < 2; ++f) {
        glBindFramebuffer(GL_FRAMEBUFFER, fbo[f]);
        for (int i = 0; i < 2; ++i) { glBindTexture(GL_TEXTURE_2D, rt[f * 2 + i]); glTexStorage2D(GL_TEXTURE_2D, 1, GL_RGBA8, W, H);
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0 + i, GL_TEXTURE_2D, rt[f * 2 + i], 0); }
        const GLenum bufs[] = {GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1}; glDrawBuffers(2, bufs);
        if (glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE) { fprintf(stderr, "fbo incomplete\n"); return 1; }
    }
    glViewport(0, 0, W, H);
    const float quad[] = {-1, -1, 1, -1, -1, 1, 1, 1};
    GLuint vbo, vao; glGenVertexArrays(1, &vao); glBindVertexArray(vao); glGenBuffers(1, &vbo); glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof quad, quad, GL_STATIC_DRAW); glEnableVertexAttribArray(0); glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, nullptr);
    GLuint vs = Compile(GL_VERTEX_SHADER, Vertex);
    // Build program: each fragment of a canvas-size pass writes up to 4 layers (one bilinear fetch each,
    // offset by the coupling epsilon toward its block centre).
    auto buildSource = [&](int group) {
        std::string src = "#version 300 es\nprecision highp float;\nuniform sampler2D source;\nuniform highp vec2 size;\n";
        int n = 0; for (int k = 0; k < 4 && group * 4 + k < layers; ++k, ++n) src += "layout(location = " + std::to_string(k) + ") out vec4 o" + std::to_string(k) + ";\n";
        src += "void main() {\n    highp vec2 base = floor(gl_FragCoord.xy) * " + std::to_string(S) + ".0;\n";
        for (int k = 0; k < n; ++k) { int l = group * 4 + k; int i = l % S, j = l / S;
            src += "    o" + std::to_string(k) + " = texture(source, (base + vec2(" + std::to_string(i) + ".5, " + std::to_string(j) + ".5) + 0.0625 * sign(vec2(" + std::to_string(S) + ".0 * 0.5) - vec2(" + std::to_string(i) + ".5, " + std::to_string(j) + ".5))) / size);\n"; }
        src += "}\n"; return src; };
    std::vector<GLuint> buildProg;
    for (size_t g = 0; g < polyFbo.size(); ++g) { GLuint f = Compile(GL_FRAGMENT_SHADER, buildSource(static_cast<int>(g)));
        GLuint p = glCreateProgram(); glAttachShader(p, vs); glAttachShader(p, f); glLinkProgram(p); buildProg.push_back(p); }
    for (int a = 8; a < argc; ++a)
    {
        if (std::string(argv[a]) == "@build")
        {
            const auto build = [&]() { glViewport(0, 0, CW, CH);
                for (size_t g = 0; g < polyFbo.size(); ++g) { glBindFramebuffer(GL_FRAMEBUFFER, polyFbo[g]); glUseProgram(buildProg[g]);
                    glActiveTexture(GL_TEXTURE0); glBindTexture(GL_TEXTURE_2D, tex[0]); glUniform1i(glGetUniformLocation(buildProg[g], "source"), 0);
                    glUniform2f(glGetUniformLocation(buildProg[g], "size"), static_cast<float>(W), static_cast<float>(H));
                    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4); glFlush(); }
                glViewport(0, 0, W, H); };
            for (int i = 0; i < 10; ++i) build(); glFinish();
            double best = 1e9;
            for (int round = 0; round < 3; ++round) { auto t0 = std::chrono::steady_clock::now();
                for (int i = 0; i < iterations; ++i) build(); glFinish();
                best = std::min(best, std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count() / iterations); }
            printf("%-40s %8.3f ms/pass  (err 0x%x, %d layers)\n", "@build (polyphase layers)", best, glGetError(), layers);
            continue;
        }
        std::ifstream in(argv[a]); std::stringstream ss; ss << in.rdbuf();
        GLuint fs = Compile(GL_FRAGMENT_SHADER, ss.str());
        if (!fs) { printf("%-40s COMPILE_FAILED\n", argv[a]); continue; }
        GLuint prog = glCreateProgram(); glAttachShader(prog, vs); glAttachShader(prog, fs); glLinkProgram(prog);
        GLint ok = 0; glGetProgramiv(prog, GL_LINK_STATUS, &ok);
        if (!ok) { char log[4096]; glGetProgramInfoLog(prog, sizeof log, nullptr, log); printf("%-40s LINK_FAILED %s\n", argv[a], log); continue; }
        glUseProgram(prog);
        // Bind every sampler: 2D -> the frame, 3D -> volume noise. Set the uniforms the warp needs.
        GLint count = 0; glGetProgramiv(prog, GL_ACTIVE_UNIFORMS, &count); int unit = 0;
        for (GLint u = 0; u < count; ++u)
        {
            char name[256]; GLint size; GLenum type; glGetActiveUniform(prog, u, sizeof name, nullptr, &size, &type, name);
            GLint loc = glGetUniformLocation(prog, name);
            if (type == GL_SAMPLER_2D && (std::string(name) == "Lw" || std::string(name) == "D")) { glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, tex[3]); glUniform1i(loc, unit++); }
            else if (type == GL_SAMPLER_2D && std::string(name) == "uvmap") { glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, tex[2]); glUniform1i(loc, unit++); }
            else if (type == GL_SAMPLER_2D) { glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D, tex[0]); glUniform1i(loc, unit++); }
            else if (type == GL_SAMPLER_2D_ARRAY) { glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_2D_ARRAY, polyTex); glUniform1i(loc, unit++); }
            else if (type == GL_SAMPLER_3D) { glActiveTexture(GL_TEXTURE0 + unit); glBindTexture(GL_TEXTURE_3D, tex[1]); glUniform1i(loc, unit++); }
            else if (std::string(name) == "_c7") glUniform4f(loc, cw, ch, 1.0f / cw, 1.0f / ch);
            else if (std::string(name) == "diffusion_canvas" && type == GL_FLOAT_VEC4) glUniform4f(loc, cw, ch, tx / W, ty / H);
            else if (std::string(name) == "diffusion_canvas") glUniform2f(loc, cw, ch);
            else if (std::string(name) == "_c5" || std::string(name) == "_c6") glUniform4f(loc, 1, 0, 1, 0);
            else if (type == GL_FLOAT_VEC4) glUniform4f(loc, 0.3f, 0.2f, 0.1f, 0.5f);
            else if (type == GL_FLOAT_VEC2) glUniform2f(loc, cw, ch);
            else if (type == GL_FLOAT) glUniform1f(loc, 0.5f);
            else if (type == GL_INT) glUniform1i(loc, getenv("POLY_S") ? atoi(getenv("POLY_S")) : 2);
        }
        const auto pass = [&](int i) { glBindFramebuffer(GL_FRAMEBUFFER, fbo[i & 1]); glDrawArrays(GL_TRIANGLE_STRIP, 0, 4); glFlush(); };
        for (int i = 0; i < 10; ++i) pass(i);
        glFinish();
        double best = 1e9;
        for (int round = 0; round < 3; ++round)
        {
            auto t0 = std::chrono::steady_clock::now();
            for (int i = 0; i < iterations; ++i) pass(i);
            glFinish();
            const double ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - t0).count() / iterations;
            best = std::min(best, ms);
        }
        printf("%-40s %8.3f ms/pass  (err 0x%x)\n", argv[a], best, glGetError());
        glDeleteProgram(prog); glDeleteShader(fs);
    }
    return 0;
}
