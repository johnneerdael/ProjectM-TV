// Source-only proposal until the parent compiles/runs it against an identified production engine.
// Use actual HLSL transpilation, MilkdropShader::LoadVariables and live GL uniforms/draws.
#include "gl_context.hpp"
#include <Audio/PCM.hpp>
#include <MilkdropPreset/MilkdropShader.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/Texture.hpp>
#include <Renderer/TextureManager.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
using AudioData = libprojectM::Audio::FrameAudioData;
static void Check(bool ok,const std::string& message) {
    if(!ok) throw std::runtime_error(message);
}
static void Near(float actual,float expected,const std::string& name,float tolerance=2e-6f) {
    Check(std::isfinite(actual)&&std::abs(actual-expected)<=tolerance,name+" mismatch");
}

// Shader.cpp detaches/deletes shaders after link. Record submitted source at the real GL boundary.
struct ShaderSource { GLenum type{}; std::string text; };
static std::map<GLuint,ShaderSource> sourceByShader;
static std::map<GLuint,std::vector<ShaderSource>> sourceByProgram;
static PFNGLSHADERSOURCEPROC actualShaderSource{};
static PFNGLLINKPROGRAMPROC actualLinkProgram{};
static void ObserveSource(GLuint shader,GLsizei count,const GLchar* const* strings,const GLint* lengths) {
    GLint type{};glGetShaderiv(shader,GL_SHADER_TYPE,&type);
    ShaderSource record;record.type=static_cast<GLenum>(type);
    for(GLsizei i=0;i<count;++i) {
        if(lengths&&lengths[i]>=0)record.text.append(strings[i],static_cast<std::size_t>(lengths[i]));
        else record.text.append(strings[i]);
    }
    sourceByShader[shader]=std::move(record);
    actualShaderSource(shader,count,strings,lengths);
}
static void ObserveLink(GLuint program) {
    GLint count{};glGetProgramiv(program,GL_ATTACHED_SHADERS,&count);
    std::vector<GLuint> attached(static_cast<std::size_t>(count));GLsizei written{};
    glGetAttachedShaders(program,count,&written,attached.data());
    std::vector<ShaderSource> sources;
    for(GLsizei i=0;i<written;++i) {
        const auto found=sourceByShader.find(attached[static_cast<std::size_t>(i)]);
        Check(found!=sourceByShader.end(),"linked shader has no captured source");
        GLint compiled{};glGetShaderiv(attached[static_cast<std::size_t>(i)],GL_COMPILE_STATUS,&compiled);
        Check(compiled==GL_TRUE,"linked shader did not compile");sources.push_back(found->second);
    }
    actualLinkProgram(program);
    GLint linked{};glGetProgramiv(program,GL_LINK_STATUS,&linked);
    if(linked==GL_TRUE)sourceByProgram[program]=std::move(sources);
}
class CompileObserver {
public:
    CompileObserver() {
        actualShaderSource=glad_glShaderSource;actualLinkProgram=glad_glLinkProgram;
        glad_glShaderSource=ObserveSource;glad_glLinkProgram=ObserveLink;
    }
    ~CompileObserver(){glad_glShaderSource=actualShaderSource;glad_glLinkProgram=actualLinkProgram;}
};
static GLuint CompiledProgram(const std::string& label,const std::filesystem::path& proofDir) {
    GLint program{},linked{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    Check(program!=0,label+": no bound production program");glGetProgramiv(program,GL_LINK_STATUS,&linked);
    Check(linked==GL_TRUE,label+": program did not link");
    const auto found=sourceByProgram.find(static_cast<GLuint>(program));
    Check(found!=sourceByProgram.end(),label+": source/link proof absent (binary-cache path unqualified)");
    bool vertex=false,fragment=false;
    for(const auto& source:found->second) {
        vertex|=source.type==GL_VERTEX_SHADER;fragment|=source.type==GL_FRAGMENT_SHADER;
        const auto suffix=source.type==GL_VERTEX_SHADER?".vert": ".frag";
        std::ofstream file(proofDir/(label+suffix));file<<source.text;
        Check(file.good(),label+": could not retain actual submitted GLSL");
    }
    Check(vertex&&fragment,label+": shader stages missing");
    return static_cast<GLuint>(program);
}
static std::array<float,4> Uniform(GLuint program,const char* name) {
    const GLint location=glGetUniformLocation(program,name);
    Check(location>=0,std::string("required active production uniform missing: ")+name);
    std::array<float,4> value{};glGetUniformfv(program,location,value.data());
    Check(glGetError()==GL_NO_ERROR,"uniform readback GL error");
    std::cout<<"uniform "<<name<<' '<<value[0]<<' '<<value[1]<<' '<<value[2]<<' '<<value[3]<<'\n';
    return value;
}
struct Surface {
    std::shared_ptr<Texture> texture;
    GLuint fbo{},vao{},vbo{};
    Surface():texture(std::make_shared<Texture>("shader-input-control",GL_TEXTURE_2D,16,16,1,
                                             GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false)) {
        glGenFramebuffers(1,&fbo);glBindFramebuffer(GL_FRAMEBUFFER,fbo);
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture->TextureID(),0);
        Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"control FBO incomplete");
        glGenVertexArrays(1,&vao);glBindVertexArray(vao);glGenBuffers(1,&vbo);glBindBuffer(GL_ARRAY_BUFFER,vbo);
        const float vertices[]{-1,-1,3,-1,-1,3};glBufferData(GL_ARRAY_BUFFER,sizeof(vertices),vertices,GL_STATIC_DRAW);
        glEnableVertexAttribArray(0);glVertexAttribPointer(0,2,GL_FLOAT,GL_FALSE,0,nullptr);
    }
    ~Surface(){glDeleteBuffers(1,&vbo);glDeleteVertexArrays(1,&vao);glDeleteFramebuffers(1,&fbo);}
    void Expect(const std::array<float,3>& color,const std::string& label) {
        // This small target tests uniform-driven production composite output, not Native4K presentation.
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER,fbo);glViewport(0,0,16,16);
        glBindVertexArray(vao);glDisable(GL_BLEND);glDisable(GL_DEPTH_TEST);glDisable(GL_SCISSOR_TEST);
        glDisable(GL_CULL_FACE);glDisable(GL_STENCIL_TEST);
        glDisable(GL_DITHER);glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE);
        for(GLuint attribute:{1u,2u,3u})glDisableVertexAttribArray(attribute);
        glVertexAttrib4f(1,1,1,1,1);glVertexAttrib2f(2,.5f,.5f);glVertexAttrib2f(3,0,0);
        glDrawArrays(GL_TRIANGLES,0,3);
        glBindFramebuffer(GL_READ_FRAMEBUFFER,fbo);glReadBuffer(GL_COLOR_ATTACHMENT0);
        std::array<unsigned char,16*16*4> pixels{};
        glReadPixels(0,0,16,16,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());
        Check(glGetError()==GL_NO_ERROR,label+": actual composite draw/readback error");
        for(std::size_t i=0;i<pixels.size();i+=4) {
            for(int c=0;c<3;++c) {
                const int expected=static_cast<int>(std::lround(std::clamp(color[c],0.f,1.f)*255));
                Check(std::abs(static_cast<int>(pixels[i+c])-expected)<=1,label+": compiled composite color mismatch");
            }
            Check(pixels[i+3]==255,label+": composite alpha changed");
        }
        std::cout<<"pixel "<<label<<' '<<int(pixels[0])<<' '<<int(pixels[1])<<' '<<int(pixels[2])
                 <<" read_fbo="<<fbo<<" sample_target=16x16\n";
    }
};
struct Control {
    TextureManager textures;
    ShaderCache cache;
    Surface input;
    PresetState state;
    PerFrameContext frame;
    Control():textures(std::vector<std::string>{}),frame(state.globalMemory,&state.globalRegisters) {
        auto& rc=state.renderContext;rc.textureManager=&textures;rc.shaderCache=&cache;
        rc.viewportSizeX=rc.viewportSizeY=16;rc.aspectX=rc.aspectY=rc.invAspectX=rc.invAspectY=1;
        rc.fps=30;rc.time=.25f;rc.frame=7;rc.progress=.1f;
        state.mainTexture=input.texture;state.hueRandomOffsets.fill(0);
        state.blurTexture.Initialize(rc);state.LoadShaders();
        state.audioData.waveformLeft.fill(0);state.audioData.waveformRight.fill(0);
        state.audioData.spectrumLeft.fill(0);state.audioData.spectrumRight.fill(0);
        frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);
    }
    void CoherentFields(const std::array<float,3>& bands,const std::array<float,3>& attenuated) {
        // Explicit injection only. Actual PCM producer is executed separately in ColdMonoProducer().
        auto& a=state.audioData;a.bass=bands[0];a.mid=bands[1];a.treb=bands[2];
        a.bassAtt=attenuated[0];a.midAtt=attenuated[1];a.trebAtt=attenuated[2];
        a.vol=(a.bass+a.mid+a.treb)*.333f;a.volAtt=(a.bassAtt+a.midAtt+a.trebAtt)*.333f;
        frame.LoadStateVariables(state);
    }
};
static void Compile(MilkdropShader& shader,Control& control,const std::string& code) {
    shader.LoadCode(code);shader.LoadTexturesAndCompile(control.state);
}
static float OriginalComma(float bass,float mid,float treb) {
    (void)bass;(void)mid;return .3333f*treb; // Independent original comma-expression scalar expectation.
}
static void CheckVolumeUniforms(MilkdropShader& shader,Control& control,const std::string& label,
                               const std::filesystem::path& proofDir) {
    shader.LoadVariables(control.state,control.frame);const auto program=CompiledProgram(label,proofDir);
    const auto c3=Uniform(program,"_c3"),c4=Uniform(program,"_c4");const auto& a=control.state.audioData;
    const std::array<float,4> expected3{a.bass,a.mid,a.treb,a.vol},expected4{a.bassAtt,a.midAtt,a.trebAtt,a.volAtt};
    for(int i=0;i<4;++i){Near(c3[i],expected3[i],"_c3 component");Near(c4[i],expected4[i],"_c4 component");}
    control.input.Expect({a.vol/4,a.volAtt/4,0},label);
    std::cout<<"original_comma "<<label<<' '<<OriginalComma(a.bass,a.mid,a.treb)<<' '
             <<OriginalComma(a.bassAtt,a.midAtt,a.trebAtt)<<" current="<<a.vol<<','<<a.volAtt<<'\n';
}
static void ColdMonoProducer(const std::filesystem::path& proofDir) {
    libprojectM::Audio::PCM pcm;std::array<uint8_t,libprojectM::Audio::AudioBufferSamples> silence{};silence.fill(128);
    pcm.Add(silence.data(),1,silence.size());pcm.UpdateFrameAudioData(1.0/30.0,0);
    const auto audio=pcm.GetFrameAudioData();
    for(float value:{audio.bass,audio.mid,audio.treb,audio.bassAtt,audio.midAtt,audio.trebAtt})Near(value,1,"cold silence relative fallback");
    Near(audio.vol,.999f,"actual PCM volume");Near(audio.volAtt,.999f,"actual PCM attenuated volume");
    Check(audio.waveformLeft==audio.waveformRight,"mono production buffers diverged");
    Control control;control.state.audioData=audio;control.frame.LoadStateVariables(control.state);
    MilkdropShader shader(MilkdropShader::ShaderType::CompositeShader);
    Compile(shader,control,"shader_body { ret=float3(vol/4,vol_att/4,0); }");
    CheckVolumeUniforms(shader,control,"I26-real-cold-mono",proofDir);
}
static void VolumeControls(const std::filesystem::path& proofDir) {
    const std::array<std::array<float,3>,6> cases{{{1,2,3},{1,1,1},{1,0,0},{0,1,0},{0,0,1},{0,0,0}}};
    Control control;MilkdropShader shader(MilkdropShader::ShaderType::CompositeShader);
    Compile(shader,control,"shader_body { ret=float3(vol/4,vol_att/4,0); }");
    for(std::size_t i=0;i<cases.size();++i) {
        const auto attenuated=i==0?std::array<float,3>{.5f,1,2}:cases[i];
        control.CoherentFields(cases[i],attenuated);
        CheckVolumeUniforms(shader,control,"I26-injected-"+std::to_string(i),proofDir);
    }
    control.CoherentFields({1,2,3},{.5f,1,2});
    control.frame.CompilePerFrameCode("vol=7;vol_att=9;bass=11;mid=12;treb=13;q1=vol;q2=vol_att;q6=q6+1;");
    control.frame.ExecutePerFrameCode();
    Check(*control.frame.q_vars[0]==7&&*control.frame.q_vars[1]==9&&*control.frame.q_vars[5]==1,
          "mutable EEL control did not execute");
    CheckVolumeUniforms(shader,control,"I26-mutated-EEL",proofDir);
    CheckVolumeUniforms(shader,control,"I26-same-frame-rebind",proofDir);
    Check(*control.frame.q_vars[5]==1,"shader uniform replay executed EEL again");
    Near(control.state.audioData.vol,1.998f,"mutable EEL altered immutable audioData");
}
struct Profile {const char* name;int width,height,referenceWidth,referenceHeight,canvasWidth,canvasHeight;};
static const std::array<Profile,5> profiles{{
    {"square",256,256,0,0,256,256},{"landscape",256,144,0,0,256,144},
    {"portrait",144,256,0,0,144,256},{"native-reference",3840,2160,1280,720,1280,720},
    {"native-no-reference",3840,2160,0,0,3840,2160}}};
static void SetProfile(Control& control,const Profile& p) {
    auto& rc=control.state.renderContext;rc.viewportSizeX=p.width;rc.viewportSizeY=p.height;
    rc.lineReferenceWidth=p.referenceWidth;rc.lineReferenceHeight=p.referenceHeight;
    rc.aspectX=p.height>p.width?float(p.width)/p.height:1;rc.aspectY=p.width>p.height?float(p.height)/p.width:1;
    rc.invAspectX=1/rc.aspectX;rc.invAspectY=1/rc.aspectY;
    rc.feedbackDetailAlpha=0; // Same-frame uniform reuse admission; no actual detail target is allocated here.
}
static std::array<float,3> ExpectedMip(const Profile& p) {
    // Independent double log2 oracle with tolerance for the production float logf/divide producer.
    const float x=static_cast<float>(std::log2(double(p.canvasWidth)));
    const float y=static_cast<float>(std::log2(double(p.canvasHeight)));return {x,y,(x+y)/2};
}
static void MipControls(const std::filesystem::path& proofDir) {
    Control control;MilkdropShader shader(MilkdropShader::ShaderType::CompositeShader);
    Compile(shader,control,"shader_body { ret=float3(mip_x,mip_y,mip_avg)/16; }");
    for(const auto& profile:profiles) {
        SetProfile(control,profile);control.frame.LoadStateVariables(control.state);
        shader.LoadVariables(control.state,control.frame);
        const auto program=CompiledProgram("I27-"+std::string(profile.name),proofDir);
        const auto c12=Uniform(program,"_c12");const auto expected=ExpectedMip(profile);
        for(int i=0;i<3;++i)Near(c12[i],expected[i],"mip component",1e-5f);Near(c12[3],0,"mip padding");
        control.input.Expect({expected[0]/16,expected[1]/16,expected[2]/16},profile.name);
        std::cout<<"profile "<<profile.name<<" reported_canvas="<<profile.canvasWidth<<'x'<<profile.canvasHeight
                 <<" context_viewport="<<profile.width<<'x'<<profile.height<<" reference="
                 <<profile.referenceWidth<<'x'<<profile.referenceHeight<<" original_duplicate="<<expected[0]<<'\n';
        if(profile.canvasWidth!=profile.canvasHeight)Check(std::abs(c12[1]-c12[0])>.1f,"nonsquare height was replaced by width");
        shader.LoadVariables(control.state,control.frame);
        const auto repeated=Uniform(program,"_c12");Check(repeated==c12,"same-frame mip rebind changed tuple");
    }
}
static void FixtureControls(const std::filesystem::path& fixtures,const std::filesystem::path& proofDir) {
    struct Case {const char* file;std::array<float,3> color;int profile;};
    const float currentVol=(1.f+2.f+3.f)*.333f,currentAtt=(.5f+1.f+2.f)*.333f;
    const auto landscape=ExpectedMip(profiles[1]),reference=ExpectedMip(profiles[3]);
    const std::vector<Case> cases{
        {"I26-live.milk",{currentVol/4,currentAtt/4,0},1},
        {"I26-mutable-eel-live.milk",{currentVol/4,currentAtt/4,0},1},
        {"I26-current-oracle.milk",{currentVol/4,currentAtt/4,0},1},
        {"I26-comma-oracle.milk",{OriginalComma(1,2,3)/4,OriginalComma(.5f,1,2)/4,0},1},
        {"I26-direct-bands.milk",{.25f,.5f,.75f},1},
        {"I26-direct-attenuated.milk",{.125f,.25f,.5f},1},
        {"I27-live.milk",{landscape[0]/16,landscape[1]/16,landscape[2]/16},1},
        {"I27-256x144-current-oracle.milk",{landscape[0]/16,landscape[1]/16,landscape[2]/16},1},
        {"I27-256x144-duplicate-oracle.milk",{.5f,.5f,.5f},1},
        {"I27-256x256-current-oracle.milk",{.5f,.5f,.5f},0},
        {"I27-256x256-duplicate-oracle.milk",{.5f,.5f,.5f},0},
        {"I27-1280x720-current-oracle.milk",{reference[0]/16,reference[1]/16,reference[2]/16},3},
        {"I27-1280x720-duplicate-oracle.milk",{reference[0]/16,reference[0]/16,reference[0]/16},3}};
    for(const auto& c:cases) {
        PresetFileParser parser;Check(parser.Read((fixtures/c.file).string()),"fixture parser failed");
        Check(parser.GetInt("PSVERSION_COMP",0)==2,"fixture composite version missing");
        Control control;SetProfile(control,profiles[c.profile]);control.CoherentFields({1,2,3},{.5f,1,2});
        const auto equations=parser.GetCode("per_frame_");
        if(!equations.empty()){control.frame.CompilePerFrameCode(equations);control.frame.ExecutePerFrameCode();}
        MilkdropShader shader(MilkdropShader::ShaderType::CompositeShader);
        Compile(shader,control,parser.GetCode("comp_"));shader.LoadVariables(control.state,control.frame);
        CompiledProgram(c.file,proofDir);control.input.Expect(c.color,c.file);
    }
}
int main(int argc,char** argv) {
    try {
        Check(argc==3,"usage: shader-input-controls FIXTURE_DIRECTORY GLSL_PROOF_DIRECTORY");
        const std::filesystem::path fixtures(argv[1]),proofDir(argv[2]);std::filesystem::create_directories(proofDir);
        GLContext context;CompileObserver observer;std::srand(12345);std::cout<<std::setprecision(9);
        std::cout<<"backend "<<glGetString(GL_VENDOR)<<' '<<glGetString(GL_RENDERER)<<' '<<glGetString(GL_VERSION)<<'\n';
        ColdMonoProducer(proofDir);VolumeControls(proofDir);MipControls(proofDir);FixtureControls(fixtures,proofDir);
        std::cout<<"Production shader input CGL controls pass; Native4K output and unchanged-library gates remain separate\n";
        return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}
