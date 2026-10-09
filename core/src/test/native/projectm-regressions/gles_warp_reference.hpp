#pragma once
// Test-only independent MilkDrop oscillator/rotation reference. Never load or
// replace production shader source here. Included after the fixture's Check().
#ifndef __APPLE__
#include <algorithm>
#include <cstddef>

struct WarpUniformObservation
{
    std::array<float, 4> aspect{}, factors{};
    std::array<float, 2> offset{};
    float time{}, scale{};
    void Capture(GLuint program)
    {
        auto read = [program](const char* name, float* value) {
            const auto location = glGetUniformLocation(program, name);
            Check(location >= 0, std::string("missing production uniform ") + name);
            glGetUniformfv(program, location, value);
        };
        read("aspect", aspect.data()); read("warpFactors", factors.data());
        read("texelOffset", offset.data()); read("warpTime", &time);
        read("warpScaleInverse", &scale);
    }
};

struct WarpReferenceVertex { float x, y, sine, cosine, dx, dy, warp; };
struct WarpReferenceResult { std::array<float, 4> uv, oscillators; };

// Absolute forward-error ledger for arithmetic and transport, NOT GPU trig.
// Each operation adds queried relative storage precision at its intermediate
// magnitude, including cancellation. Reference trig results are common inputs;
// their cross-program reproducibility is an explicitly qualified backend premise.
class WarpArithmeticBudget
{
public:
    struct Number { double value, error; };
    WarpArithmeticBudget()
    {
        GLint range[2]{}, precision{};
        glGetShaderPrecisionFormat(GL_VERTEX_SHADER, GL_MEDIUM_FLOAT, range, &precision);
        Check(glGetError() == GL_NO_ERROR && precision >= 10 && range[0] >= 14 && range[1] >= 14,
              "invalid/unsupported vertex mediump precision query");
        epsilon = std::ldexp(1.0, -precision);
        floor = std::ldexp(1.0, -range[0]);
        maximum = std::ldexp(1.0, range[1]);
        GLint highRange[2]{}, highPrecision{};
        glGetShaderPrecisionFormat(GL_VERTEX_SHADER, GL_HIGH_FLOAT, highRange, &highPrecision);
        Check(glGetError() == GL_NO_ERROR && highPrecision >= precision,
              "invalid vertex highp precision query");
        std::cout << "GLES warp reference: renderer=" << glGetString(GL_RENDERER)
                  << " version=" << glGetString(GL_VERSION)
                  << " mediump=" << range[0] << ',' << range[1] << '/' << precision
                  << " highp=" << highRange[0] << ',' << highRange[1] << '/' << highPrecision << '\n';
    }
    Number Input(double value) const
    {
        // Only universally representable small fixture constants get exact input credit.
        if (value == 0 || value == 1 || value == -1 || value == .5 || value == -.5)
            return {value, 0};
        return Round({value, 0});
    }
    Number Add(Number a, Number b) const { return Round({a.value+b.value, a.error+b.error}); }
    Number Sub(Number a, Number b) const { return Add(a, {-b.value,b.error}); }
    Number Mul(Number a, Number b) const
    {
        return Round({a.value*b.value, std::abs(a.value)*b.error + std::abs(b.value)*a.error + a.error*b.error});
    }
    std::array<double, 4> Bounds(const WarpReferenceVertex& p, const WarpReferenceResult& sample) const
    {
        const auto c = Input(.5), one = Input(1), zero = Input(0);
        const auto x = Input(p.x), y = Input(p.y), sine = Input(p.sine), cosine = Input(p.cosine);
        const auto gain = Mul(Input(p.warp), Input(.0035f));
        auto graph = [&](bool production) {
            auto u = Add(Mul(x,c),c), v = Add(Mul(y,c),c);
            if (production) {
                // Unit stretch division is exactly the identity for these fixture values.
                u = Add(Sub(u,c),c); v = Add(Sub(v,c),c);
            }
            u = Add(u,Mul(gain,Input(sample.oscillators[0])));
            v = Add(v,Mul(gain,Input(sample.oscillators[1])));
            u = Add(u,Mul(gain,Input(sample.oscillators[2])));
            v = Add(v,Mul(gain,Input(sample.oscillators[3])));
            const auto a = Sub(u,c), b = Sub(v,c);
            u = Sub(Add(Sub(Mul(a,cosine),Mul(b,sine)),c),Input(p.dx));
            v = Sub(Add(Add(Mul(a,sine),Mul(b,cosine)),c),Input(p.dy));
            if (production) {
                u = Add(Mul(Sub(u,c),one),c); v = Add(Mul(Sub(v,c),one),c);
                u = Add(u,zero); v = Add(v,zero);
            }
            return std::array<Number,2>{u,v};
        };
        const auto actual = graph(true), oracle = graph(false);
        // TF retains mediump output, then converts it exactly to highp storage.
        const auto originalU = Add(Mul(x,c),c), originalV = Add(Mul(y,c),c);
        return {Round(actual[0]).error+Round(oracle[0]).error,
                Round(actual[1]).error+Round(oracle[1]).error,
                2*Round(originalU).error, 2*Round(originalV).error};
    }
private:
    Number Round(Number n) const
    {
        Check(std::isfinite(n.value) && std::isfinite(n.error) && n.error >= 0 &&
                  std::abs(n.value)+n.error < maximum,
              "arithmetic budget left queried finite range");
        n.error += epsilon * std::max(std::abs(n.value)+n.error, floor);
        return n;
    }
    double epsilon{}, floor{}, maximum{};
};

class GlesWarpReference
{
public:
    GlesWarpReference()
    {
        // Source derived from MilkDrop2's physical oscillator equations, with
        // current custom positive-Y policy stated independently. Rotation uses
        // the already independently checked actual CPU trig/displacement inputs.
        const std::string vertex = R"GLSL(#version 300 es
precision mediump float;
layout(location=0) in vec2 point;
layout(location=1) in vec2 rotationPair;
layout(location=2) in vec2 displacement;
layout(location=3) in float strength;
uniform float clockValue;
uniform vec4 frequencies;
uniform int legacyPhysicalY;
out vec4 referenceUV;
out vec4 referenceOscillators;
void main() {
    float physicalY = legacyPhysicalY != 0 ? -point.y : point.y;
    referenceOscillators = vec4(
        sin(clockValue*.333 + (point.x*frequencies.x - physicalY*frequencies.w)),
        cos(clockValue*.375 - (point.x*frequencies.z + physicalY*frequencies.y)),
        cos(clockValue*.753 - (point.x*frequencies.y - physicalY*frequencies.z)),
        sin(clockValue*.825 + (point.x*frequencies.x + physicalY*frequencies.w)));
    vec2 uv = point*.5 + .5;
    float gain = strength*.0035;
    uv.x += gain*referenceOscillators.x;
    uv.y += gain*referenceOscillators.y;
    uv.x += gain*referenceOscillators.z;
    uv.y += gain*referenceOscillators.w;
    vec2 delta = uv - .5;
    referenceUV = vec4(
        delta.x*rotationPair.y - delta.y*rotationPair.x + .5 - displacement.x,
        delta.x*rotationPair.x + delta.y*rotationPair.y + .5 - displacement.y,
        point*.5 + .5);
    gl_Position = vec4(point,0,1);
})GLSL";
        const std::string fragment = R"GLSL(#version 300 es
precision mediump float;
out vec4 result;
void main(){ result=vec4(0); }
)GLSL";
        const auto vs = Compile(GL_VERTEX_SHADER,vertex), fs = Compile(GL_FRAGMENT_SHADER,fragment);
        program = glCreateProgram(); glAttachShader(program,vs); glAttachShader(program,fs);
        const char* varyings[]{"referenceUV","referenceOscillators"};
        glTransformFeedbackVaryings(program,2,varyings,GL_INTERLEAVED_ATTRIBS);
        glLinkProgram(program); GLint ok{}; glGetProgramiv(program,GL_LINK_STATUS,&ok);
        glDeleteShader(vs); glDeleteShader(fs);
        Check(ok,"independent mediump GPU reference link failed");
        glGenVertexArrays(1,&vao); glGenBuffers(1,&input); glGenBuffers(1,&output);
    }
    ~GlesWarpReference()
    { glDeleteBuffers(1,&output); glDeleteBuffers(1,&input); glDeleteVertexArrays(1,&vao); glDeleteProgram(program); }
    std::vector<WarpReferenceResult> Run(const std::vector<WarpReferenceVertex>& vertices,
                                        const WarpUniformObservation& uniforms, bool legacy)
    {
        GLint previousProgram{}, previousVao{}, previousArray{}, previousFeedback{}, previousIndexed{};
        glGetIntegerv(GL_CURRENT_PROGRAM,&previousProgram); glGetIntegerv(GL_VERTEX_ARRAY_BINDING,&previousVao);
        glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&previousArray);
        glGetIntegerv(GL_TRANSFORM_FEEDBACK_BUFFER_BINDING,&previousFeedback);
        glGetIntegeri_v(GL_TRANSFORM_FEEDBACK_BUFFER_BINDING,0,&previousIndexed);
        const bool discard = glIsEnabled(GL_RASTERIZER_DISCARD);
        glUseProgram(program); glBindVertexArray(vao); glBindBuffer(GL_ARRAY_BUFFER,input);
        glBufferData(GL_ARRAY_BUFFER,vertices.size()*sizeof(WarpReferenceVertex),vertices.data(),GL_STREAM_DRAW);
        const int sizes[]{2,2,2,1}; const size_t offsets[]{0,2,4,6};
        for(GLuint i=0;i<4;++i) {
            glEnableVertexAttribArray(i);
            glVertexAttribPointer(i,sizes[i],GL_FLOAT,GL_FALSE,sizeof(WarpReferenceVertex),
                                  reinterpret_cast<void*>(offsets[i]*sizeof(float)));
        }
        glUniform1f(glGetUniformLocation(program,"clockValue"),uniforms.time);
        glUniform4fv(glGetUniformLocation(program,"frequencies"),1,uniforms.factors.data());
        glUniform1i(glGetUniformLocation(program,"legacyPhysicalY"),legacy);
        glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER,output);
        glBufferData(GL_TRANSFORM_FEEDBACK_BUFFER,vertices.size()*sizeof(WarpReferenceResult),nullptr,GL_STREAM_READ);
        glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,output);
        glEnable(GL_RASTERIZER_DISCARD); glBeginTransformFeedback(GL_POINTS);
        glDrawArrays(GL_POINTS,0,static_cast<GLsizei>(vertices.size())); glEndTransformFeedback();
        const auto* mapped = static_cast<const WarpReferenceResult*>(glMapBufferRange(
            GL_TRANSFORM_FEEDBACK_BUFFER,0,vertices.size()*sizeof(WarpReferenceResult),GL_MAP_READ_BIT));
        Check(mapped,"independent GPU reference readback failed");
        std::vector<WarpReferenceResult> result(mapped,mapped+vertices.size()); glUnmapBuffer(GL_TRANSFORM_FEEDBACK_BUFFER);
        glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,previousIndexed);
        glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER,previousFeedback);
        if (!discard) glDisable(GL_RASTERIZER_DISCARD);
        glBindVertexArray(previousVao); glBindBuffer(GL_ARRAY_BUFFER,previousArray); glUseProgram(previousProgram);
        Check(glGetError()==GL_NO_ERROR,"independent GPU reference GL error");
        return result;
    }
    WarpArithmeticBudget budget;
private:
    static GLuint Compile(GLenum type,const std::string& source)
    {
        const auto shader=glCreateShader(type); const char* text=source.c_str();
        glShaderSource(shader,1,&text,nullptr); glCompileShader(shader);
        GLint ok{}; glGetShaderiv(shader,GL_COMPILE_STATUS,&ok);
        char log[4096]{}; glGetShaderInfoLog(shader,sizeof(log),nullptr,log);
        Check(ok,std::string("independent GPU reference compile: ")+log); return shader;
    }
    GLuint program{}, vao{}, input{}, output{};
};
#endif
