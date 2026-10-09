// Source preparation only: root owns compilation and all GL execution.
#include "gl_context.hpp"
#include <MilkdropPreset/Waveform.hpp>
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <Renderer/TextureManager.hpp>
#include <Renderer/Texture.hpp>
#include <sstream>
#include <MilkdropPreset/WaveformMode.hpp>
#include <MilkdropPreset/Waveforms/Factory.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Audio/PCM.hpp>
#include <projectM-4/audio.h>
#include <cstdint>
#include <array>
#include <vector>
#include <string>
#include <fstream>
#include <iostream>
#include <cmath>
#include <limits>
#include <algorithm>
#include <stdexcept>
using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool ok,const std::string& why){if(!ok)throw std::runtime_error(why);}
struct Submission { GLenum mode{}; int count{},instances{}; float halfWidth{}; std::vector<std::array<float,2>> a,b; std::array<float,4> color{}; };
static std::vector<Submission> submitted;
static PFNGLDRAWELEMENTSPROC realElements;
static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced;
static std::vector<std::array<float,2>> Attribute(GLuint location,int count)
{
    GLint buffer{},previous{},stride{};void* pointer{};
    glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);
    glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
    glGetVertexAttribPointerv(location,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
    Check(buffer!=0 && stride>0,"missing production position buffer");
    glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&previous);glBindBuffer(GL_ARRAY_BUFFER,buffer);
    GLint bytes{};glGetBufferParameteriv(GL_ARRAY_BUFFER,GL_BUFFER_SIZE,&bytes);
    const auto offset=reinterpret_cast<uintptr_t>(pointer);
    Check(offset+size_t(count-1)*stride+sizeof(float)*2<=size_t(bytes),"position capture exceeds buffer");
    const auto* data=static_cast<const unsigned char*>(glMapBufferRange(GL_ARRAY_BUFFER,0,bytes,GL_MAP_READ_BIT));
    Check(data!=nullptr,"production position mapping failed");
    std::vector<std::array<float,2>> result;
    for(int i=0;i<count;++i){const auto* xy=reinterpret_cast<const float*>(data+offset+size_t(i)*stride);result.push_back({xy[0],xy[1]});}
    glUnmapBuffer(GL_ARRAY_BUFFER);glBindBuffer(GL_ARRAY_BUFFER,previous);return result;
}
static void ActiveProgram() { GLint program{},linked{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);Check(program!=0,"no actual production GL program");glGetProgramiv(program,GL_LINK_STATUS,&linked);Check(linked==GL_TRUE,"actual production GL program not linked"); }
static void Elements(GLenum mode,GLsizei count,GLenum type,const void* indices)
{
    ActiveProgram();
    Check(type==GL_UNSIGNED_INT && indices==nullptr,"changed waveform index contract");
    Submission s;s.mode=mode;s.count=count;s.a=Attribute(0,count);
    glGetVertexAttribfv(1,GL_CURRENT_VERTEX_ATTRIB,s.color.data());submitted.push_back(std::move(s));
    realElements(mode,count,type,indices);
}
static void Instanced(GLenum mode,GLint first,GLsizei count,GLsizei instances)
{
    ActiveProgram();
    Check(mode==GL_TRIANGLE_STRIP && first==0 && count==4 && instances>0,"changed Native quad contract");
    Submission s;s.mode=mode;s.count=count;s.instances=instances;s.a=Attribute(1,instances);s.b=Attribute(2,instances);
    GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);const GLint widthLocation=glGetUniformLocation(program,"half_width");Check(widthLocation>=0,"Native line half-width uniform missing");glGetUniformfv(program,widthLocation,&s.halfWidth);
    // Attribute4 points at RGBA of segment A; position capture helper is intentionally not used here.
    GLint buffer{},previous{},stride{};void* pointer{};
    glGetVertexAttribiv(4,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);glGetVertexAttribiv(4,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
    glGetVertexAttribPointerv(4,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&previous);
    glBindBuffer(GL_ARRAY_BUFFER,buffer);const auto offset=reinterpret_cast<uintptr_t>(pointer);
    const auto* rgba=static_cast<const float*>(glMapBufferRange(GL_ARRAY_BUFFER,offset,sizeof(float)*4,GL_MAP_READ_BIT));
    Check(rgba!=nullptr,"Native color mapping failed");std::copy_n(rgba,4,s.color.begin());glUnmapBuffer(GL_ARRAY_BUFFER);glBindBuffer(GL_ARRAY_BUFFER,previous);
    submitted.push_back(std::move(s));realInstanced(mode,first,count,instances);
}
struct Hooks { Hooks(){realElements=glad_glDrawElements;realInstanced=glad_glDrawArraysInstanced;glad_glDrawElements=Elements;glad_glDrawArraysInstanced=Instanced;}
~Hooks(){glad_glDrawElements=realElements;glad_glDrawArraysInstanced=realInstanced;} };
static void Configure(PresetState& state,ShaderCache& cache)
{
    auto& c=state.renderContext;c.shaderCache=&cache;c.viewportSizeX=1280;c.viewportSizeY=720;
    c.aspectX=1;c.aspectY=.5625f;c.invAspectX=1;c.invAspectY=1/.5625f;c.time=1.5f;c.fps=30;c.frame=45;c.perPixelMeshX=48;c.perPixelMeshY=32;
    state.LoadShaders();state.waveMode=0;state.waveScale=1;state.waveSmoothing=0;state.waveAlpha=.8f;
    state.waveR=.2f;state.waveG=.7f;state.waveB=1;state.waveParam=.25f;state.waveX=state.waveY=.5f;
    state.audioData.vol=state.audioData.treb=1;
    for(size_t i=0;i<state.audioData.waveformLeft.size();++i){state.audioData.waveformLeft[i]=32*std::sin(i*.13f);state.audioData.waveformRight[i]=24*std::cos(i*.17f);}
    for(size_t i=0;i<state.audioData.spectrumLeft.size();++i){state.audioData.spectrumLeft[i]=64+float(i%17);state.audioData.spectrumRight[i]=48+float(i%11);}
}
static void SamePoint(const std::array<float,2>& actual,const Point& expected,float dx=0,float dy=0)
{Check(std::abs(actual[0]-expected.X()-dx)<2e-6f && std::abs(actual[1]-expected.Y()-dy)<2e-6f,"wrong selected factory geometry or replay producer");}
static void Validate(PresetState& state,PerFrameContext& frame,Waveform& wave,int expectedMode,bool replay,bool dots,bool thick,Framebuffer& canvas,Framebuffer& native)
{
    state.renderContext.viewportSizeX=3840;state.renderContext.viewportSizeY=2160;
    state.renderContext.lineReferenceWidth=1280;state.renderContext.lineReferenceHeight=720;
    GeometryTargets targets(state,canvas,0,1280,720,{},native,0);targets.Authored();
    *frame.wave_usedots=dots;*frame.wave_thick=thick;submitted.clear();
    auto factory=Waveforms::Factory::Create(static_cast<WaveformMode>(expectedMode));
    std::array<Waveforms::WaveformMath::VertexList,2> expected;
    const bool valid=bool(factory);if(valid)expected=factory->GetVertices(state,frame);
    wave.Draw(frame,replay?&targets:nullptr);
    Check(glGetError()==GL_NO_ERROR,"waveform GL error");
    if(!valid){Check(submitted.empty(),"invalid mode retained/submitted prior geometry");return;}
    const GLenum primitive=dots?GL_POINTS:factory->IsLoop()?GL_LINE_LOOP:GL_LINE_STRIP;
    size_t index=0;const int authoredPasses=(dots||thick)?4:1;
    for(const auto& strip:expected)if(!strip.empty())for(int pass=0;pass<authoredPasses;++pass){
        Check(index<submitted.size(),"missing authored draw");const auto& s=submitted[index++];
        Check(s.mode==primitive && s.count==int(strip.size()),"wrong selected factory primitive/count");
        const float dx=(pass==1||pass==2)?2.f/1280:0;const float dy=pass>=2?2.f/720:0;
        for(size_t i=0;i<strip.size();++i)SamePoint(s.a[i],strip[i],dx,dy);
        if(expectedMode==1)Check(std::abs(s.color[3]-1)<1e-6,"mode1 opacity boost changed");
    }
    if(replay)for(const auto& strip:expected)if(!strip.empty()){
        const int passes=dots?1:thick?4:1;
        for(int pass=0;pass<passes;++pass){Check(index<submitted.size(),"missing Native replay draw");const auto& s=submitted[index++];
            if(dots){Check(s.mode==GL_POINTS&&s.count==int(strip.size()),"Native dot style/count changed");for(size_t i=0;i<strip.size();++i)SamePoint(s.a[i],strip[i]);}
            else{Check(std::abs(s.halfWidth-1.5f)<1e-6,"Native line width changed at3xreference scale");if(expectedMode==1)Check(std::abs(s.color[3]-1)<1e-6,"Native mode1 opacity boost changed");const int segments=int(strip.size())-(factory->IsLoop()?0:1);Check(s.mode==GL_TRIANGLE_STRIP&&s.instances==segments,"Native segment/pass count changed");
                for(int i=0;i<segments;++i){SamePoint(s.a[i],strip[i]);SamePoint(s.b[i],strip[(i+1)%strip.size()]);}}
        }
    }
    Check(index==submitted.size(),"unexpected extra mode/replay draws");
    for(const auto& s:submitted){for(float c:s.color)Check(std::isfinite(c),"nonfinite submitted color");for(const auto& xy:s.a)for(float x:xy)Check(std::isfinite(x),"nonfinite submitted geometry");}
    Check(state.renderContext.viewportSizeX==1280&&state.renderContext.lineReferenceWidth==0,"replay lost authored context");
}
static void Bounded(ShaderCache& cache)
{
    Framebuffer canvas(1),native(1);canvas.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);native.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);canvas.SetSize(1280,720);native.SetSize(3840,2160);
    for(bool replay:{false,true})for(bool dots:{false,true})for(bool thick:{false,true}){
        PresetState state;Configure(state,cache);PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);Waveform wave(state);
        for(int mode=0;mode<16;++mode){*frame.wave_mode=mode;Validate(state,frame,wave,mode,replay,dots,thick,canvas,native);}
        struct Alias{double input;int mode;};
        for(const auto& a:{Alias{8.9,8},Alias{9.9,9},Alias{16,0},Alias{17,1},Alias{24,8},Alias{25,9},Alias{31,15},Alias{-.9,0},Alias{-8,-8},Alias{-16,0},Alias{-17,-1}}){*frame.wave_mode=a.input;Validate(state,frame,wave,a.mode,replay,dots,thick,canvas,native);}
        for(double bad:{std::numeric_limits<double>::quiet_NaN(),std::numeric_limits<double>::infinity(),-std::numeric_limits<double>::infinity(),2147483648.,-2147483649.,-1.}){
            *frame.wave_mode=9;Validate(state,frame,wave,9,replay,dots,thick,canvas,native);
            *frame.wave_mode=bad;submitted.clear();
            state.renderContext.viewportSizeX=3840;state.renderContext.viewportSizeY=2160;state.renderContext.lineReferenceWidth=1280;state.renderContext.lineReferenceHeight=720;
            GeometryTargets invalidTargets(state,canvas,0,1280,720,{},native,0);invalidTargets.Authored();
            GLint programBefore{},drawBefore{},readBefore{};glGetIntegerv(GL_CURRENT_PROGRAM,&programBefore);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&drawBefore);glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&readBefore);
            wave.Draw(frame,replay?&invalidTargets:nullptr);Check(submitted.empty(),"invalid input submitted stale geometry");Check(glGetError()==GL_NO_ERROR,"invalid input GL error");
            GLint programAfter{},drawAfter{},readAfter{};glGetIntegerv(GL_CURRENT_PROGRAM,&programAfter);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&drawAfter);glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&readAfter);
            Check(programBefore==programAfter&&drawBefore==drawAfter&&readBefore==readAfter,"invalid mode changed GL program/targets");
            *frame.wave_mode=1;Validate(state,frame,wave,1,replay,dots,thick,canvas,native);
        }
    }
    std::cout<<"bounded production GL modes/aliases/recovery/replay PASS\n";
}
static bool Selected(int frame){return frame==120||frame==150||frame==180||frame==210||frame==239||frame==300||frame==390||frame==479;}
static bool CommonPCM(ShaderCache& cache,const std::string& path,const std::string& log)
{
    std::ifstream input(path,std::ios::binary);Check(bool(input),"missing frozen PCM");std::ofstream output(log);Check(bool(output),"cannot write input trace");
    libprojectM::Audio::PCM pcm;bool qualified=true;std::array<uint8_t,1470> block{};
    const unsigned feedSamples=projectm_pcm_get_max_samples();Check(feedSamples>0&&feedSamples<=block.size(),"unsupported production PCM tail count");
    std::cout<<"production projectm_pcm_get_max_samples="<<feedSamples<<"; spectrum bins="<<libprojectM::Audio::SpectrumSamples<<'\n';
    PresetState state;Configure(state,cache);PerFrameContext context(state.globalMemory,&state.globalRegisters);context.RegisterBuiltinVariables();
    std::array<std::unique_ptr<Waveforms::WaveformMath>,16> producers;for(int mode=0;mode<16;++mode)producers[mode]=Waveforms::Factory::Create(static_cast<WaveformMode>(mode));
    for(int frame=0;frame<480;++frame){input.read(reinterpret_cast<char*>(block.data()),block.size());Check(input.gcount()==int(block.size()),"PCM does not contain480complete1470-byteblocks");
        // Exact API-backed FeedAudio tail transport; Add(float) would be a different contract.
        pcm.Add(block.data()+block.size()-feedSamples,1,feedSamples);pcm.UpdateFrameAudioData(frame==0?0.:frame/30.-(frame-1)/30.,frame);state.audioData=pcm.GetFrameAudioData();state.renderContext.time=frame/30.f;state.renderContext.frame=frame;
        state.renderContext.viewportSizeX=3840;state.renderContext.viewportSizeY=2160;state.renderContext.lineReferenceWidth=1280;state.renderContext.lineReferenceHeight=720;context.LoadStateVariables(state);
        float pairMin=std::numeric_limits<float>::infinity();int badPairs=0;
        for(int i=0;i<256;++i){const float sum=state.audioData.spectrumLeft[2*i]/128.f+state.audioData.spectrumLeft[2*i+1]/128.f;pairMin=std::min(pairMin,sum);if(!std::isfinite(sum)||sum<=0)++badPairs;}
        float lassoMin=std::numeric_limits<float>::infinity();int badLassoArguments=0,badLassoTan=0;
        for(int i=0;i<240;++i){const float angle=state.audioData.waveformLeft[i+32]/128.f*1.57f+state.renderContext.time*2.f;
            if(std::isfinite(angle))lassoMin=std::min(lassoMin,std::abs(angle));
            if(!std::isfinite(angle)||angle==0){++badLassoArguments;continue;}
            const float argument=state.renderContext.time/angle;if(!std::isfinite(argument)){++badLassoArguments;continue;}if(!std::isfinite(std::tan(argument)))++badLassoTan;}
        for(int mode=0;mode<16;++mode){auto vertices=producers[mode]->GetVertices(state,context);size_t count=0,bad=0;
            for(const auto& strip:vertices)for(const auto& xy:strip){++count;if(!std::isfinite(xy.X())||!std::isfinite(xy.Y()))++bad;}
            output<<"{\"feedTailSamples\":"<<feedSamples<<",\"frame\":"<<frame<<",\"time\":"<<state.renderContext.time<<",\"mode\":"<<mode<<",\"smoothedPoints\":"<<count<<",\"nonfinitePoints\":"<<bad<<",\"nonpositiveOrNonfiniteSpectrumPairs\":"<<badPairs<<",\"minimumScaledPairSum\":";
            if(std::isfinite(pairMin))output<<pairMin;else output<<"null";output<<",\"nonfiniteLassoArguments\":"<<badLassoArguments<<",\"nonfiniteLassoTan\":"<<badLassoTan<<",\"minimumLassoAbsAngle\":";if(std::isfinite(lassoMin))output<<lassoMin;else output<<"null";output<<",\"selected\":"<<(Selected(frame)?"true":"false")<<"}\n";
            if(Selected(frame)&&(bad||(mode==8&&badPairs)||(mode==15&&(badLassoArguments||badLassoTan))))qualified=false;
        }
    }
    Check(output.good(),"PCM trace write failed");std::cout<<"common-PCM selected finite qualification="<<qualified<<" (host source producer only)\n";return qualified;
}

static void CompiledWarpMarker(ShaderCache& cache)
{
    TextureManager manager(std::vector<std::string>{});RenderContext render;
    render.shaderCache=&cache;render.textureManager=&manager;render.viewportSizeX=256;render.viewportSizeY=144;
    render.perPixelMeshX=48;render.perPixelMeshY=32;render.time=1.5f;render.fps=30;
    auto initial=std::make_shared<Texture>("compile-seed",GL_TEXTURE_2D,256,144,1,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
    auto output=std::make_shared<Texture>("compile-output",GL_TEXTURE_2D,256,144,1,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
    GLuint seed{},target{};glGenFramebuffers(1,&seed);glGenFramebuffers(1,&target);
    glBindFramebuffer(GL_FRAMEBUFFER,seed);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,initial->TextureID(),0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"compile seed incomplete");
    glViewport(0,0,256,144);glClearColor(.75f,.125f,0,1);glClear(GL_COLOR_BUFFER_BIT);
    std::istringstream source("MILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=2\n[preset00]\nfDecay=1\nfGammaAdj=1\nfShader=0\nfVideoEchoAlpha=0\nfWaveAlpha=0\nob_size=0\nib_size=0\nmv_a=0\nbDarkenCenter=0\nwarp_1=`shader_body { ret=float3(0,0,.25); }\n");
    libprojectM::MilkdropPreset::MilkdropPreset preset(source);preset.Initialize(render);
    Check(preset.InitializationWarnings().empty(),"compiled marker initialization warnings");preset.DrawInitialImage(initial,render);
    glBindFramebuffer(GL_FRAMEBUFFER,target);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,output->TextureID(),0);
    Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"compile output incomplete");Check(preset.SetOutputTarget(true,target),"compile output target rejected");
    preset.RenderFrame({},render);glBindFramebuffer(GL_READ_FRAMEBUFFER,target);std::array<unsigned char,4> pixel{};
    glReadPixels(128,72,1,1,GL_RGBA,GL_UNSIGNED_BYTE,pixel.data());Check(glGetError()==GL_NO_ERROR,"compiled marker GL error");
    Check(pixel[0]<=1&&pixel[1]<=1&&std::abs(int(pixel[2])-64)<=1,"actual full pipeline custom warp marker missing/fallback active");
    glDeleteFramebuffers(1,&seed);glDeleteFramebuffers(1,&target);
    std::cout<<"actual full pipeline constant-blue custom warp marker PASS (256x144 source CGL)\n";
}

int main(int argc,char** argv)
{
    try{GLContext gl;ShaderCache cache;{Hooks hooks;Bounded(cache);}CompiledWarpMarker(cache);if(argc==3)return CommonPCM(cache,argv[1],argv[2])?0:2;Check(argc==1,"usage:extended-mode-controls [PCM_U8 TRACE_JSONL]");}
    catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}return 0;
}
