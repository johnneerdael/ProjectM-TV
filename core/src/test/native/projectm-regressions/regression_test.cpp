#include "gl_context.hpp"
#include <GLSLGenerator.h>
#include <HLSLParser.h>
#include <HLSLTree.h>
#include "Renderer/Shader.hpp"
// Exercise the patched engine itself, including the evaluator and real GL drawing.
#include <HLSLParser.h>
#include <HLSLTree.h>
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/MilkdropShader.hpp>
#include <ProjectM.hpp>
#include <projectM-4/projectM.h>
#include <Renderer/ShaderCache.hpp>

#ifdef __APPLE__
#include <OpenGL/OpenGL.h>
#else
#include <EGL/egl.h>
#endif

#include <cmath>
#include <algorithm>
#include <iostream>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

static void Check(bool ok, const char* message)
{
    if (!ok) throw std::runtime_error(message);
}

static void TestMacros()
{
    for (const auto& source : {
             "#define sampler_rand00 sampler_rand00\nsampler2D sampler_rand00;\n",
             "#define value value\nfloat value;\n#define alias value\nfloat result = alias;\n",
             "#define value 2\n#define twice(x) x * 2\nfloat result = twice(value);\n"})
    {
        M4::Allocator allocator;
        M4::HLSLTree tree(&allocator);
        M4::HLSLParser parser(&allocator, &tree);
        std::string input(source), output;
        Check(parser.ApplyPreprocessor("regression.hlsl", input.data(), input.size(), output),
              "macro preprocessing failed");
        Check(parser.Parse("regression.hlsl", output.data(), output.size()),
              "preprocessed shader did not parse");
        Check(tree.FindGlobalDeclaration(input.find("sampler_rand00") != std::string::npos
                                            ? "sampler_rand00" : "result") != nullptr,
              "macro preprocessing lost a declaration");
    }
}

static void TestImplicitInputBindings()
{
    GLContext context;
    using namespace M4;
    const char* vertex=
#ifdef USE_GLES
        "#version 300 es\n"
#else
        "#version 330\n"
#endif
        "void main(){ vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2); gl_Position=vec4(p*2.-1.,0,1); }";
    struct Case { const char* source; const char* input; int components; int boundRed; };
    for(const auto& test:{
        Case{"float3 mus; void PS(out float4 r:COLOR0){r=float4(mus+.25,1);}","mus",3,115},
        Case{"float dist_c; void PS(out float4 r:COLOR0){float before=dist_c;dist_c=.4;r=float4(before+.25,before,before,1);}","dist_c",1,115},
        Case{"float2 uv3; void PS(out float4 r:COLOR0){uv3+=.25;r=float4(uv3,0,1);}","uv3",2,115}})
    {
        Allocator allocator;HLSLTree tree(&allocator);HLSLParser parser(&allocator,&tree);
        const std::string source=test.source;
        Check(parser.Parse("binding",source.data(),source.size()),"implicit binding source rejected");
        GLSLGenerator generator;
        Check(generator.Generate(&tree,GLSLGenerator::Target_FragmentShader,
#ifdef USE_GLES
            GLSLGenerator::Version_300_ES,
#else
            GLSLGenerator::Version_330,
#endif
            "PS"),"implicit binding translation rejected");
        libprojectM::Renderer::Shader program;
        program.CompileProgram(vertex,generator.GetResult());program.Bind();
        GLuint framebuffer,texture,vao;
        glGenFramebuffers(1,&framebuffer);glBindFramebuffer(GL_FRAMEBUFFER,framebuffer);
        glGenTextures(1,&texture);glBindTexture(GL_TEXTURE_2D,texture);
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,16,16,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture,0);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"binding framebuffer incomplete");
        glGenVertexArrays(1,&vao);glBindVertexArray(vao);glViewport(0,0,16,16);
        glDisable(GL_BLEND);
        for(int invocation=0;invocation<3;++invocation)
        {
            if(invocation==1)
            {
                if(test.components==1)program.SetUniformFloat(test.input,.2f);
                else if(test.components==2)program.SetUniformFloat2(test.input,{.2f,.2f});
                else program.SetUniformFloat3(test.input,{.2f,.2f,.2f});
            }
            glDrawArrays(GL_TRIANGLES,0,3);
            unsigned char pixel[4]{};glReadPixels(8,8,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel);
            const int want=invocation==0?64:test.boundRed;
            Check(std::abs(int(pixel[0])-want)<=2,"implicit input value or invocation reset mismatch");
            Check(glGetError()==GL_NO_ERROR,"implicit binding driver error");
        }
        glDeleteVertexArrays(1,&vao);glDeleteTextures(1,&texture);glDeleteFramebuffers(1,&framebuffer);
        std::cout<<"bound and unbound implicit input: "<<test.input<<std::endl;
    }
}

static void TestFloatLiteralRendering(const std::string& preset, const std::string& capture)
{
    GLContext gl;
    GLuint framebuffer, texture;
    glGenFramebuffers(1, &framebuffer);
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 256, 144, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "float control framebuffer incomplete");
    libprojectM::ProjectM engine;
    engine.SetWindowSize(256, 144);
    engine.SetMeshSize(48, 32);
    engine.SetPresetLocked(true);
    engine.SetHardCutEnabled(false);
    engine.SetEasterEgg(0);
    engine.LoadPresetFile(preset, false);
    engine.RenderFrame(framebuffer);
    Check(glGetError() == GL_NO_ERROR, "float control rendering GL error");
    glBindFramebuffer(GL_READ_FRAMEBUFFER, framebuffer);
    glReadBuffer(GL_COLOR_ATTACHMENT0);
    // RGBA/UNSIGNED_BYTE is guaranteed for normalized GLES framebuffers; RGB is optional.
    std::vector<unsigned char> pixels(256 * 144 * 4);
    glReadPixels(0, 0, 256, 144, GL_RGBA, GL_UNSIGNED_BYTE, pixels.data());
    Check(glGetError() == GL_NO_ERROR, "float control RGBA readback GL error");
    if (!capture.empty())
    {
        std::vector<unsigned char> rgb(256 * 144 * 3);
        for (size_t i = 0; i < pixels.size(); i += 4)
            std::copy_n(pixels.data() + i, 3, rgb.data() + (i / 4) * 3);
        std::ofstream out(capture, std::ios::binary);
        out << "P6\n256 144\n255\n";
        out.write(reinterpret_cast<const char*>(rgb.data()), rgb.size());
        Check(out.good(), "float control capture failed");
    }
    std::cout << "float control RGB=" << int(pixels[0]) << ',' << int(pixels[1]) << ',' << int(pixels[2])
              << " expected=128,96,0" << std::endl;
    for (size_t i = 0; i < pixels.size(); i += 4)
        Check(pixels[i] == 128 && pixels[i + 1] == 96 && pixels[i + 2] == 0,
              "float literal one-frame result mismatch (including fallback markers)");
    glDeleteTextures(1, &texture);
    glDeleteFramebuffers(1, &framebuffer);
}

static void TestShaderRendering()
{
    GLContext gl;
    GLuint framebuffer, texture;
    glGenFramebuffers(1, &framebuffer);
    glGenTextures(1, &texture);
    glBindTexture(GL_TEXTURE_2D, texture);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, 16, 16, 0, GL_RGBA, GL_UNSIGNED_BYTE, nullptr);
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER) == GL_FRAMEBUFFER_COMPLETE, "incomplete framebuffer");
    struct Case { const char* name; const char* shader; int red; };
    for (const auto& test : {
        Case{"mixed-reverse", "float a,b=.25;\nshader_body { ret=a+b; }", 64},
        Case{"mixed-alternating", "float a,b=.1,c,d=.15;\nshader_body { ret=a+b+c+d; }", 64},
        Case{"implicit-mus", "float3 mus;\nshader_body { ret = mus+.25; }", 64},
        Case{"implicit-dist", "float dist_c;\nshader_body { float before=dist_c; dist_c=.4; ret=before+.25; }", 64},
        Case{"implicit-uv3", "float2 uv3;\nshader_body { uv3=.4*cos(42*uv3); ret=float3(uv3,0); }", 102},
        Case{"explicit-zero-control", "float2 uv3=0;\nshader_body { uv3=.4*cos(42*uv3); ret=float3(uv3,0); }", 102},
        Case{"nonzero-control", "float2 uv3=.1;\nshader_body { ret=float3(uv3,0); }", 26},
        Case{"local-assigned-control", "shader_body { float3 mus; mus=.25; ret=mus; }", 64},
        Case{"control", "shader_body { ret = .25; }", 64},
        Case{"sample", "shader_body { float3 sample = .5; ret = sample*sample*sample; }", 32},
        Case{"sample-shadow", "float sample = .1;\nshader_body { float sample = .25; { float sample = .5; sample *= .5; } ret = sample; }", 64},
        Case{"macro-declaration", "#define decl float3 value;\ndecl\nshader_body { value = .25; ret = value; }", 64},
        Case{"macro-statement", "#define texx float3(.25,.5,.75);\nshader_body { float3 add=texx; ret = add; }", 64},
        Case{"macro-precedence", "#define sum .1+.2\nshader_body { ret = sum*2; }", 128},
        Case{"macro-authored-parentheses", "#define sum (.1+.2)\nshader_body { ret = sum*2; }", 153},
        Case{"macro-function", "#define add(x) x+.2\nshader_body { ret = add(.1)*2; }", 128},
        Case{"postfix", "shader_body { ret = (float3(.1,.2,.3)*2).zyx; }", 153},
        Case{"postfix-precedence", "shader_body { ret = .1+(float3(.1,.2,.3)*2).zyx*.5; }", 102},
        Case{"postfix-nested", "shader_body { ret = (((float3(.1,.2,.3)*2))).zyx.xyy; }", 153},
        Case{"parenthesized-binary", "shader_body { ret = (float3(.1,.2,.3))*2+.1; }", 77}})
    {
        std::string preset = "MILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=3\nPSVERSION_COMP=3\n"
            "[preset00]\nfDecay=1\nfGammaAdj=1\nfWaveAlpha=0\nfVideoEchoAlpha=0\n"
            "fShader=0\nzoom=1\nwarp=0\nrot=0\nwarp_1=`shader_body { ret = 0; }\n";
        std::istringstream lines(test.shader);
        std::string line;
        for (int number = 1; std::getline(lines, line); ++number)
            preset += "comp_" + std::to_string(number) + "=`" + line + "\n";
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer);
        glClearColor(0, 0, 0, 1);
        glClear(GL_COLOR_BUFFER_BIT);
        libprojectM::ProjectM engine;
        engine.SetWindowSize(16, 16);
        engine.SetPresetLocked(true);
        engine.SetHardCutEnabled(false);
        engine.SetEasterEgg(0);
        std::istringstream data(preset);
        engine.LoadPresetData(data, false);
        for (int frame = 0; frame < 2; ++frame) engine.RenderFrame(framebuffer);
        unsigned char pixel[4]{};
        glBindFramebuffer(GL_READ_FRAMEBUFFER, framebuffer);
        glReadBuffer(GL_COLOR_ATTACHMENT0);
        glReadPixels(8, 8, 1, 1, GL_RGBA, GL_UNSIGNED_BYTE, pixel);
        Check(glGetError() == GL_NO_ERROR, "shader render GL error");
        std::cout << test.name << " red=" << int(pixel[0]) << " expected=" << test.red << std::endl;
        Check(std::abs(int(pixel[0]) - test.red) <= 2, "authored shader result mismatch (including fallback)");
    }
    glDeleteTextures(1, &texture);
    glDeleteFramebuffers(1, &framebuffer);
}

static void TestParserPresets(const std::string& assets, const std::string& manifest, int expected=16)
{
    GLContext gl;
    using namespace libprojectM;
    Renderer::ShaderCache shaders;
    Renderer::TextureManager textures({assets + "/textures"});
    auto mainTexture = std::make_shared<Renderer::Texture>("main", 16, 16, false);
    std::ifstream list(manifest);
    Check(list.good(), "cannot open parser preset manifest");
    std::string line;
    int count = 0;
    int failures = 0;
    while (std::getline(list, line))
    {
        const auto firstTab = line.find('\t');
        const auto lastTab = line.find('\t', firstTab + 1);
        Check(firstTab != std::string::npos && lastTab != std::string::npos, "invalid preset manifest");
        const std::string stage = line.substr(firstTab + 1, lastTab - firstTab - 1);
        Check(stage == "warp" || stage == "composite", "invalid preset stage");
        const std::string filename = line.substr(lastTab + 1);
        MilkdropPreset::PresetFileParser preset;
        Check(preset.Read(assets + "/presets/" + filename), "cannot read witness preset");
        MilkdropPreset::PresetState state;
        state.renderContext.viewportSizeX = 16;
        state.renderContext.viewportSizeY = 16;
        state.renderContext.textureManager = &textures;
        state.renderContext.shaderCache = &shaders;
        state.mainTexture = mainTexture;
        MilkdropPreset::MilkdropShader shader(stage == "warp"
            ? MilkdropPreset::MilkdropShader::ShaderType::WarpShader
            : MilkdropPreset::MilkdropShader::ShaderType::CompositeShader);
        // Invoke the real shader compiler directly: exceptions are failures,
        // rather than successful preset loads that silently choose fallback.
        try
        {
            shader.LoadCode(preset.GetCode(stage == "warp" ? "warp_" : "comp_"));
            shader.LoadTexturesAndCompile(state);
            std::cout << "custom shader compiled: " << filename << std::endl;
        }
        catch (const std::exception& error)
        {
            std::cout << "custom shader rejected: " << filename << ": " << error.what() << std::endl;
            ++failures;
        }
        ++count;
    }
    Check(count == expected, "wrong number of unchanged witness presets");
    Check(failures == 0, "original shader rejected by production compiler");
}

static void TestWaveforms()
{
    GLContext gl;
    using namespace libprojectM::MilkdropPreset;
    libprojectM::Renderer::ShaderCache shaders;
    PresetState state;
    state.renderContext.shaderCache = &shaders;
    state.LoadShaders();
    state.renderContext.viewportSizeX = 16;
    state.renderContext.viewportSizeY = 16;
    state.renderContext.invAspectX = 1;
    state.renderContext.invAspectY = 1;
    PerFrameContext frame(state.globalMemory, &state.globalRegisters);
    frame.RegisterBuiltinVariables();
    for (size_t i = 0; i < state.audioData.waveformLeft.size(); ++i)
    {
        state.audioData.waveformLeft[i] = static_cast<float>(i);
        state.audioData.waveformRight[i] = -static_cast<float>(i);
    }
    for (size_t i = 0; i < state.audioData.spectrumLeft.size(); ++i)
    {
        state.audioData.spectrumLeft[i] = static_cast<float>(i);
        state.audioData.spectrumRight[i] = -static_cast<float>(i);
    }
    // Per-point code reports how many points ran and the final audio values through real
    // evaluator registers, independently of the GL driver's rasterization.
    state.customWavePerPointCode[0] = "reg00=reg00+1;reg01=value1;reg02=value2;reg03=sample;";
    struct Case { bool spectrum; int samples; int separation; int points; float last; };
    for (const auto& test : {
             Case{false, 480, 0, 480, 1.916f},
             Case{false, 480, 1000000, 480, 1.916f},
             Case{false, 480, -1000000, 480, 1.916f},
             Case{false, 512, 0, 512, 1.916f},
             Case{false, 1000000, 0, 512, 1.916f},
             // MilkDrop's centered two-point window ends at input index240.
             Case{false, 2, 0, 2, 0.96f},
             Case{true, 512, 0, 512, 76.65f},
             Case{true, 512, 1000000, 512, 0.0f},
             Case{true, 512, -1000000, 512, 76.65f},
             Case{true, 2, 1, 2, 38.25f},
             Case{false, -1, 0, 0, 0.0f},
             Case{false, 0, 0, 0, 0.0f},
             Case{false, 1, 0, 0, 0.0f},
             Case{true, 0, 1000000, 0, 0.0f}})
    {
        std::cout << "waveform spectrum=" << test.spectrum << " samples=" << test.samples
                  << " sep=" << test.separation << std::endl;
        std::ostringstream text;
        text << "[preset00]\nwavecode_0_enabled=1\nwavecode_0_samples=" << test.samples
             << "\nwavecode_0_sep=" << test.separation
             << "\nwavecode_0_bSpectrum=" << test.spectrum << "\nwavecode_0_smoothing=0\n";
        std::istringstream input(text.str());
        PresetFileParser preset;
        Check(preset.Read(input), "fixture preset did not parse");
        CustomWaveform wave(state);
        wave.Initialize(preset, 0);
        std::vector<std::string> warnings;
        wave.CompileCodeAndRunInitExpressions(frame, warnings);
        Check(warnings.empty(), "fixture waveform code did not compile");
        for (auto& value : state.globalRegisters) value = 0;
        wave.Draw(frame);
        Check(state.globalRegisters[0] == test.points, "wrong number of waveform points");
        if (test.points)
        {
            Check(std::abs(state.globalRegisters[1] - test.last) < 0.0001,
                  "wrong left-channel sample");
            Check(std::abs(state.globalRegisters[2] + test.last) < 0.0001,
                  "wrong right-channel sample");
            Check(state.globalRegisters[3] == 1.0, "waveform did not reach its endpoint");
        }
    }
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc >= 2, "expected test mode");
        const std::string mode(argv[1]);
        if (mode == "macro") TestMacros();
        else if (mode == "float-render" && (argc == 3 || argc == 4)) TestFloatLiteralRendering(argv[2], argc == 4 ? argv[3] : "");
        else if (mode == "shader-render") TestShaderRendering();
        else if (mode == "implicit-bindings") TestImplicitInputBindings();
        else if (mode == "parser-presets" && argc == 4) TestParserPresets(argv[2], argv[3]);
        else if (mode == "float-presets" && argc == 4) TestParserPresets(argv[2], argv[3],95);
        else if (mode == "initialization-presets" && argc == 4) TestParserPresets(argv[2], argv[3],4);
        else if (mode == "waveform") TestWaveforms();
        else throw std::runtime_error("unknown test mode");
        std::cout << mode << " regressions passed\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
