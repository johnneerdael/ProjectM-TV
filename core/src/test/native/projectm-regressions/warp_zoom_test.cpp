// Execute the production warp vertex source and read its UV outputs, not a copied formula.
#include "gl_context.hpp"
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}

static GLuint Compile(GLenum type, const std::string& source)
{
    GLuint shader = glCreateShader(type);
    const char* text = source.c_str();
    glShaderSource(shader, 1, &text, nullptr);
    glCompileShader(shader);
    GLint ok{};
    glGetShaderiv(shader, GL_COMPILE_STATUS, &ok);
    char log[4096]{};
    glGetShaderInfoLog(shader, sizeof(log), nullptr, log);
    Check(ok, std::string("compile: ") + log);
    return shader;
}

struct Vertex
{
    float x, y, radius, angle, zoom, exponent, rotation, warp;
    float cx, cy, dx, dy, sx, sy;
};

static std::array<float, 2> Reference(const Vertex& p)
{
    const float inverse = 1.0f / std::pow(p.zoom, std::pow(p.exponent, p.radius * 2.0f - 1.0f));
    float u = p.x * 0.5f * inverse + 0.5f;
    float v = p.y * 0.5f * inverse + 0.5f;
    u = (u - p.cx) / p.sx + p.cx;
    v = (v - p.cy) / p.sy + p.cy;
    u += p.warp * 0.0035f * std::sin(0.7f * 0.333f + 1.25f * (p.x * 2 - p.y * 5));
    v += p.warp * 0.0035f * std::cos(0.7f * 0.375f - 1.25f * (p.x * 4 + p.y * 3));
    u += p.warp * 0.0035f * std::cos(0.7f * 0.753f - 1.25f * (p.x * 3 - p.y * 4));
    v += p.warp * 0.0035f * std::sin(0.7f * 0.825f + 1.25f * (p.x * 2 + p.y * 5));
    const float u2 = u - p.cx, v2 = v - p.cy;
    u = u2 * std::cos(p.rotation) - v2 * std::sin(p.rotation) + p.cx - p.dx;
    v = u2 * std::sin(p.rotation) + v2 * std::cos(p.rotation) + p.cy - p.dy;
    return {u, v};
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "pass production warp vertex source path");
        GLContext context;
        GLuint framebuffer{}, color{};
        glGenFramebuffers(1, &framebuffer);
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
        glGenRenderbuffers(1, &color);
        glBindRenderbuffer(GL_RENDERBUFFER, color);
        glRenderbufferStorage(GL_RENDERBUFFER, GL_RGBA8, 16, 16);
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, color);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "UV control target incomplete");
        std::ifstream file(argv[1]);
        Check(file.good(), "could not read production shader");
        const std::string source((std::istreambuf_iterator<char>(file)), {});
#ifdef __APPLE__
        const std::string header = "#version 330\n";
#else
        const std::string header = "#version 300 es\n";
#endif
        const GLuint vertex = Compile(GL_VERTEX_SHADER, header + source);
        // Both legacy and custom warp use this same vertex shader. Keep both link interfaces tested.
        for (const bool custom : {false, true})
        {
            const GLuint fragment = Compile(GL_FRAGMENT_SHADER, header +
                "precision mediump float;\nin vec4 frag_TEXCOORD0;\nout vec4 result;\nvoid main(){ result=" +
                std::string(custom ? "vec4(frag_TEXCOORD0.xy,0.0,1.0)" : "frag_TEXCOORD0") + "; }\n");
            const GLuint program = glCreateProgram();
            glAttachShader(program, vertex);
            glAttachShader(program, fragment);
            const char* varying = "frag_TEXCOORD0";
            glTransformFeedbackVaryings(program, 1, &varying, GL_INTERLEAVED_ATTRIBS);
            glLinkProgram(program);
            GLint linked{};
            glGetProgramiv(program, GL_LINK_STATUS, &linked);
            Check(linked, "warp vertex link failed");
            glUseProgram(program);
            const float identity[]{1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1};
            glUniformMatrix4fv(glGetUniformLocation(program,"vertex_transformation"),1,GL_FALSE,identity);
            glUniform4f(glGetUniformLocation(program,"aspect"),1,1,1,1);
            glUniform1f(glGetUniformLocation(program,"decay"),1);
            glUniform1f(glGetUniformLocation(program,"warpTime"),0.7f);
            glUniform1f(glGetUniformLocation(program,"warpScaleInverse"),1.25f);
            glUniform4f(glGetUniformLocation(program,"warpFactors"),2,3,4,5);
            std::vector<Vertex> vertices;
            for (const float exponent : {1.0f, 0.75f, 1.5f})
                for (const float sign : {-1.0f, 1.0f})
                    for (const auto& position : std::vector<std::array<float,2>>{{0,0},{1,0},{0,-1},{1,1},{-1,-1}})
                    {
                        if (sign < 0 && exponent != 1) continue; // Undefined GLSL domain remains outside repair.
                        const float radius = std::hypot(position[0],position[1]) / std::sqrt(2.0f);
                        const float zoom = sign < 0 ? -0.9f + radius / 100.0f : 1.002f;
                        vertices.push_back({position[0],position[1],radius,0,zoom,exponent,0,0,0.5f,0.5f,0,0,1,1});
                        vertices.push_back({position[0],position[1],radius,0,zoom,exponent,0.31f,0.2f,0.4f,0.6f,0.02f,-0.03f,1.1f,0.9f});
                    }
            GLuint vao{}, input{}, output{};
            glGenVertexArrays(1,&vao);
            glBindVertexArray(vao);
            glGenBuffers(1,&input);
            glBindBuffer(GL_ARRAY_BUFFER,input);
            glBufferData(GL_ARRAY_BUFFER,vertices.size()*sizeof(Vertex),vertices.data(),GL_STATIC_DRAW);
            const GLuint locations[]{0,3,4,5,6,7};
            const int sizes[]{2,2,4,2,2,2};
            const size_t offsets[]{0,2,4,8,10,12};
            for (GLuint i=0;i<6;++i)
            {
                glEnableVertexAttribArray(locations[i]);
                glVertexAttribPointer(locations[i],sizes[i],GL_FLOAT,GL_FALSE,sizeof(Vertex),reinterpret_cast<void*>(offsets[i]*sizeof(float)));
            }
            glGenBuffers(1,&output);
            glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER,output);
            glBufferData(GL_TRANSFORM_FEEDBACK_BUFFER,vertices.size()*4*sizeof(float),nullptr,GL_STREAM_READ);
            glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,output);
            glEnable(GL_RASTERIZER_DISCARD);
            glBeginTransformFeedback(GL_POINTS);
            glDrawArrays(GL_POINTS,0,static_cast<GLsizei>(vertices.size()));
            glEndTransformFeedback();
            glDisable(GL_RASTERIZER_DISCARD);
            auto* uv = static_cast<float*>(glMapBufferRange(GL_TRANSFORM_FEEDBACK_BUFFER,0,vertices.size()*4*sizeof(float),GL_MAP_READ_BIT));
            Check(uv != nullptr,"UV readback failed");
            bool matched = true;
            for (size_t i=0;i<vertices.size();++i)
            {
                const auto expected = Reference(vertices[i]);
                for (size_t axis=0;axis<2;++axis)
                    if (!std::isfinite(uv[i*4+axis]) || std::abs(uv[i*4+axis]-expected[axis]) > 0.002f)
                    {
                        std::cerr << "zoom=" << vertices[i].zoom << " exponent=" << vertices[i].exponent
                                  << " actual=" << uv[i*4+axis] << " expected=" << expected[axis] << '\n';
                        matched = false;
                    }
            }
            glUnmapBuffer(GL_TRANSFORM_FEEDBACK_BUFFER);
            glDeleteBuffers(1,&output);
            glDeleteBuffers(1,&input);
            glDeleteVertexArrays(1,&vao);
            glDeleteProgram(program);
            glDeleteShader(fragment);
            Check(glGetError()==GL_NO_ERROR,"GL error in warp UV control");
            Check(matched,"production warp UV differs from CPU powf signed transform");
            std::cout << (custom ? "custom" : "legacy") << " interface: " << vertices.size() << " signed/positive UV controls pass\n";
        }
        glDeleteShader(vertex);
        glDeleteRenderbuffers(1, &color);
        glDeleteFramebuffers(1, &framebuffer);
        return 0;
    }
    catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
