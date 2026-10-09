// Production RGB contract: original MilkDrop 2.25c milkdropfs.cpp:2822-2845.
#include "gl_context.hpp"
#include "wave_colour_submission.hpp"
#include <MilkdropPreset/GeometryTargets.hpp>
#include <Renderer/Framebuffer.hpp>
#include <array>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/Waveform.hpp>
#include <Renderer/Color.hpp>
#include <Renderer/ShaderCache.hpp>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool ok, const std::string& message)
{
    if (!ok) throw std::runtime_error(message);
}
static void Configure(PresetState& state, ShaderCache& cache)
{
    state.renderContext.shaderCache = &cache;
    state.renderContext.viewportSizeX = state.renderContext.viewportSizeY = 64;
    state.renderContext.aspectX = state.renderContext.aspectY = 1;
    state.renderContext.invAspectX = state.renderContext.invAspectY = 1;
    state.renderContext.time = .5f;
    state.LoadShaders();
    state.hueRandomOffsets.fill(0);
}

// Observe the production engine without replacing its color producer.
// Keep GL context/platform flags identical to legacy-compatibility-regressions.
static PFNGLDRAWELEMENTSPROC realElements;
static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced;
static std::vector<std::array<float,4>> colors;
static std::vector<I18SubmissionContract::Submission> submissions;
static I18SubmissionContract::Submission Submission(GLenum mode,GLsizei count,GLsizei instances,bool indexed){
 I18SubmissionContract::Submission row;row.mode=mode;row.count=count;row.instances=instances;row.indexed=indexed;
 glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&row.framebuffer);glGetIntegerv(GL_VIEWPORT,row.viewport);
 glGetIntegerv(GL_BLEND_SRC_RGB,&row.blendSource);glGetIntegerv(GL_BLEND_DST_RGB,&row.blendDestination);
 GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
 for(auto named:{std::pair<const char*,float*>{"half_width",&row.halfWidth},{"vertex_point_size",&row.pointSize}}){
  GLint location=glGetUniformLocation(program,named.first);if(location>=0)glGetUniformfv(program,location,named.second);
 }
 const GLint offset=glGetUniformLocation(program,"pass_offset");if(offset>=0)glGetUniformfv(program,offset,row.passOffset.data());
 GLint previous{};glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&previous);
 for(GLuint loc=0;loc<(indexed?1u:4u);++loc){
  GLint buffer{},stride{};glGetVertexAttribiv(loc,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);glGetVertexAttribiv(loc,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
  GLint size{},type{},enabled{};glGetVertexAttribiv(loc,GL_VERTEX_ATTRIB_ARRAY_SIZE,&size);glGetVertexAttribiv(loc,GL_VERTEX_ATTRIB_ARRAY_TYPE,&type);glGetVertexAttribiv(loc,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);Check(enabled&&size==2&&type==GL_FLOAT,"wave position attribute changed");if(stride==0)stride=2*sizeof(float);
  void* pointer{};glGetVertexAttribPointerv(loc,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
  glBindBuffer(GL_ARRAY_BUFFER,buffer);GLint bytes{};glGetBufferParameteriv(GL_ARRAY_BUFFER,GL_BUFFER_SIZE,&bytes);
  const auto* data=static_cast<const unsigned char*>(glMapBufferRange(GL_ARRAY_BUFFER,0,bytes,GL_MAP_READ_BIT));Check(data,"geometry map failed");
  for(int i=0;i<(indexed?count:instances);++i){const size_t at=reinterpret_cast<uintptr_t>(pointer)+size_t(i)*stride;Check(at+2*sizeof(float)<=size_t(bytes),"geometry range failed");row.submittedGeometry.insert(row.submittedGeometry.end(),data+at,data+at+2*sizeof(float));}
  glUnmapBuffer(GL_ARRAY_BUFFER);
 }
 glBindBuffer(GL_ARRAY_BUFFER,previous);return row;
}
static void Elements(GLenum mode,GLsizei count,GLenum type,const void* indices){
 auto row=Submission(mode,count,1,true);row.rgba=I18SubmissionContract::CaptureConstantRGBA();colors.insert(colors.end(),row.rgba.begin(),row.rgba.end());
 Check(type==GL_UNSIGNED_INT&&indices==nullptr,"wave index type/offset changed");
 const auto* index=static_cast<const unsigned char*>(glMapBufferRange(GL_ELEMENT_ARRAY_BUFFER,0,count*sizeof(uint32_t),GL_MAP_READ_BIT));Check(index,"index readback failed");row.submittedGeometry.insert(row.submittedGeometry.end(),index,index+count*sizeof(uint32_t));glUnmapBuffer(GL_ELEMENT_ARRAY_BUFFER);
 submissions.push_back(std::move(row));realElements(mode,count,type,indices);
}
static void Instanced(GLenum mode,GLint first,GLsizei count,GLsizei instances){
 Check(first==0&&count==4,"Native quad primitive changed");auto row=Submission(mode,count,instances,false);row.rgba=I18SubmissionContract::CaptureInstanceRGBA(instances);colors.insert(colors.end(),row.rgba.begin(),row.rgba.end());submissions.push_back(std::move(row));realInstanced(mode,first,count,instances);
}
struct Hooks {
    Hooks() { realElements=glad_glDrawElements;realInstanced=glad_glDrawArraysInstanced;
              glad_glDrawElements=Elements;glad_glDrawArraysInstanced=Instanced; }
    ~Hooks() { glad_glDrawElements=realElements;glad_glDrawArraysInstanced=realInstanced; }
};
static void WaveColors(ShaderCache& cache)
{
    struct Case { std::array<float,3> raw,unbrightened,brightened; };
    const Case cases[]={{{2,1,0},{1,1,0},{1,1,0}},
        {{1,.5f,0},{1,.5f,0},{1,.5f,0}},
        {{-1,.5f,2},{0,.5f,1},{0,.5f,1}},
        {{.2f,.1f,.05f},{.2f,.1f,.05f},{1,.5f,.25f}},
        {{-2,-1,-.5f},{0,0,0},{0,0,0}},
        {{.01f,.005f,0},{.01f,.005f,0},{.01f,.005f,0}},
        {{INFINITY,.5f,-INFINITY},{1,.5f,0},{1,.5f,0}},
        {{NAN,1,.5f},{NAN,1,.5f},{NAN,1,.5f}},
        {{1,NAN,.5f},{1,NAN,.5f},{1,NAN,.5f}},
        {{1,.5f,NAN},{1,.5f,NAN},{1,.5f,NAN}}};
    // Line, Native quad line, dots, thick dots and authored/Native prepared replay.
    for(bool replay:{false,true}) for(bool dots:{false,true}) for(bool thick:{false,true})
    for(const auto& c:cases) for(double brighten:{0.,1.,-1.})
    for(bool additive:{false,true}) for(float alpha:{.0039f,.0041f,.5f}) {
        PresetState state;Configure(state,cache);
        auto& rc=state.renderContext;rc.viewportSizeX=rc.viewportSizeY=128;
        rc.lineReferenceWidth=rc.lineReferenceHeight=64;
        state.waveMode=6;state.waveAlpha=alpha;state.waveScale=1;state.waveParam=0;
        state.waveX=state.waveY=.5f;state.waveR=c.raw[0];state.waveG=c.raw[1];state.waveB=c.raw[2];
        state.waveDots=dots;state.waveThick=thick;
        PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();
        frame.LoadStateVariables(state);*frame.wave_brighten=brighten;*frame.wave_additive=additive;
        Waveform wave(state);Framebuffer canvas(1),native(1);
        canvas.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);
        native.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);
        canvas.SetSize(64,64);native.SetSize(128,128);
        GeometryTargets targets(state,canvas,0,64,64,{},native,0);
        colors.clear();submissions.clear();targets.Authored();glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
        const auto raw=I18SubmissionContract::Snapshot(frame);
        wave.Draw(frame,replay?&targets:nullptr);
        I18SubmissionContract::AssertRawRGBUnchanged(raw,frame);
        const int authoredPasses=dots||thick?4:1;
        const int nativePasses=dots?1:thick?4:1;
        Check(int(submissions.size())==(alpha<.004f?0:authoredPasses+(replay?nativePasses:0)),"wave pass count/opacity threshold changed");
        for(size_t pass=0;pass<submissions.size();++pass){
            const bool native=pass>=size_t(authoredPasses);const auto& row=submissions[pass];
            Check(row.mode==(dots?GL_POINTS:native?GL_TRIANGLE_STRIP:GL_LINE_STRIP),"wave primitive changed");
            // Authored width64: approved I19 cap is21 raw /41 smoothed points.
            Check(row.count==(native&&!dots?4:41)&&row.instances==(native&&!dots?40:1),"wave point/segment count changed");
            for(const auto& rgba:row.rgba)Check(rgba[3]==alpha,"wave submitted opacity changed");
        }
        const auto signature=submissions;
        *frame.wave_r=1;*frame.wave_g=.5;*frame.wave_b=0;
        submissions.clear();colors.clear();targets.Authored();
        wave.Draw(frame,replay?&targets:nullptr);
        if(!signature.empty())I18SubmissionContract::AssertSameStyleAndSubmission(signature,submissions);else Check(submissions.empty(),"suppressed wave submitted geometry");
        submissions=signature;colors.clear();for(const auto& row:submissions)colors.insert(colors.end(),row.rgba.begin(),row.rgba.end());
        Check(glGetError()==GL_NO_ERROR,"wave color draw GL error");
        Check(colors.empty()==(alpha<.004f),"wave color control submission threshold changed");
        const auto expected=brighten==0?c.unbrightened:c.brightened;
        for(const auto& actual:colors) {
            for(int channel=0;channel<3;++channel)
                Check(std::isnan(expected[channel])?std::isnan(actual[channel]):std::abs(actual[channel]-expected[channel])<1e-6f,"wrong production wave RGB producer");
            Check(actual[3]==alpha,"opacity or Native dot gain changed");
        }
        // Compare count/alpha/primitive/style to same-profile baseline separately;
        // RGB clamp must not add draw calls or change replay equation evaluation.
    }
}
int main(){try{GLContext gl;ShaderCache cache;Hooks hooks;WaveColors(cache);std::cout<<"Production wave RGB, raw values, style and replay controls pass\n";}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
