// Source-only proposal. Parent owns compilation/GL execution; no shipping policy modification.
#include "gl_context.hpp"
#include <MilkdropPreset/CustomShape.hpp>
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <MilkdropPreset/MotionVectors.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/Texture.hpp>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Require(bool ok,const std::string& s){if(!ok)throw std::runtime_error(s);}
static void Near(float a,float b,const char* s,float eps=3e-6f){Require(std::isfinite(a)&&std::abs(a-b)<eps,s);}
struct Record {
    GLenum mode{};GLsizei count{},instances{1};GLint viewport[4]{},fbo{},program{},texture{};
    float minimum{},length{},halfWidth{},alpha{};std::array<float,2> passOffset{};
    std::vector<std::array<float,4>> clipPositions;
};
static std::vector<Record> records;static bool observe=false;
static int fillDraws{},fillVertices{};
static PFNGLLINKPROGRAMPROC realLink{};static PFNGLDRAWELEMENTSPROC realElements{};
static PFNGLDRAWARRAYSPROC realArrays{};static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced{};
static GLuint feedbackBuffer{},primitiveQuery{};
static void Link(GLuint program){
    const char* varying="gl_Position";glTransformFeedbackVaryings(program,1,&varying,GL_INTERLEAVED_ATTRIBS);
    realLink(program);
}
static Record Begin(GLenum mode,GLsizei count,GLsizei instances,GLint first=0){
    Record r;r.mode=mode;r.count=count;r.instances=instances;
    glGetIntegerv(GL_CURRENT_PROGRAM,&r.program);glGetIntegerv(GL_VIEWPORT,r.viewport);
    glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&r.fbo);glGetIntegerv(GL_TEXTURE_BINDING_2D,&r.texture);
    GLint linked{},varyings{};glGetProgramiv(r.program,GL_LINK_STATUS,&linked);
    glGetProgramiv(r.program,GL_TRANSFORM_FEEDBACK_VARYINGS,&varyings);
    Require(linked==GL_TRUE&&varyings==1,"production program lacks linked TF proof; fallback/cache unqualified");
    auto scalar=[&](const char* name,float& value){GLint loc=glGetUniformLocation(r.program,name);if(loc>=0)glGetUniformfv(r.program,loc,&value);};
    scalar("minimum_length",r.minimum);scalar("length_multiplier",r.length);scalar("half_width",r.halfWidth);
    GLint offset=glGetUniformLocation(r.program,"pass_offset");if(offset>=0)glGetUniformfv(r.program,offset,r.passOffset.data());
    const GLuint colorAttribute=offset>=0?4:1;
    GLint enabled{};glGetVertexAttribiv(colorAttribute,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);
    if(!enabled){std::array<float,4> color{};glGetVertexAttribfv(colorAttribute,GL_CURRENT_VERTEX_ATTRIB,color.data());r.alpha=color[3];}
    else{
        GLint buffer{},stride{},old{},length{},divisor{};void* pointer{};
        glGetVertexAttribiv(colorAttribute,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);
        glGetVertexAttribiv(colorAttribute,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
        glGetVertexAttribiv(colorAttribute,GL_VERTEX_ATTRIB_ARRAY_DIVISOR,&divisor);
        glGetVertexAttribPointerv(colorAttribute,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
        glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&old);glBindBuffer(GL_ARRAY_BUFFER,buffer);
        glGetBufferParameteriv(GL_ARRAY_BUFFER,GL_BUFFER_SIZE,&length);
        Require(stride>0,"production color stride missing");
        const std::size_t byteOffset=reinterpret_cast<std::uintptr_t>(pointer)+3*sizeof(float)+
            (divisor==0?static_cast<std::size_t>(first)*stride:0);
        Require(byteOffset+sizeof(float)<=static_cast<std::size_t>(length),"submitted alpha outside VBO");
        const auto* bytes=static_cast<const unsigned char*>(glMapBufferRange(GL_ARRAY_BUFFER,0,length,GL_MAP_READ_BIT));
        Require(bytes,"alpha VBO map failed");std::memcpy(&r.alpha,bytes+byteOffset,sizeof(float));
        Require(glUnmapBuffer(GL_ARRAY_BUFFER)==GL_TRUE,"alpha VBO invalidated");glBindBuffer(GL_ARRAY_BUFFER,old);
    }
    return r;
}
template<class Draw> static void Capture(Record& r,Draw draw){
    GLenum primitive=GL_LINES;int verticesPerPrimitive=2;
    if(r.mode==GL_TRIANGLE_STRIP){primitive=GL_TRIANGLES;verticesPerPrimitive=3;}
    const std::size_t capacity=static_cast<std::size_t>(r.count)*r.instances*3*4*sizeof(float);
    GLint oldBuffer{},oldBase{};glGetIntegerv(GL_TRANSFORM_FEEDBACK_BUFFER_BINDING,&oldBuffer);
    glGetIntegeri_v(GL_TRANSFORM_FEEDBACK_BUFFER_BINDING,0,&oldBase);
    glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER,feedbackBuffer);glBufferData(GL_TRANSFORM_FEEDBACK_BUFFER,capacity,nullptr,GL_STREAM_READ);
    glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,feedbackBuffer);
    const bool discard=glIsEnabled(GL_RASTERIZER_DISCARD)==GL_TRUE;glEnable(GL_RASTERIZER_DISCARD);
    glBeginQuery(GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN,primitiveQuery);
    glBeginTransformFeedback(primitive);draw();glEndTransformFeedback();glEndQuery(GL_TRANSFORM_FEEDBACK_PRIMITIVES_WRITTEN);
    GLuint primitives{};glGetQueryObjectuiv(primitiveQuery,GL_QUERY_RESULT,&primitives);
    const std::size_t floats=static_cast<std::size_t>(primitives)*verticesPerPrimitive*4;
    Require(floats*sizeof(float)<=capacity,"TF capture overflow");
    if(floats){
        const auto* data=static_cast<const float*>(glMapBufferRange(GL_TRANSFORM_FEEDBACK_BUFFER,0,floats*sizeof(float),GL_MAP_READ_BIT));
        Require(data,"TF map failed");
        for(std::size_t i=0;i<floats;i+=4)r.clipPositions.push_back({data[i],data[i+1],data[i+2],data[i+3]});
        Require(glUnmapBuffer(GL_TRANSFORM_FEEDBACK_BUFFER)==GL_TRUE,"TF buffer invalidated");
    }
    if(!discard)glDisable(GL_RASTERIZER_DISCARD);
    glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,static_cast<GLuint>(oldBase));
    glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER,static_cast<GLuint>(oldBuffer));
    Require(glGetError()==GL_NO_ERROR,"production shader capture GL error");
}
static bool LineMode(GLenum mode){return mode==GL_LINES||mode==GL_LINE_STRIP||mode==GL_LINE_LOOP;}
static void Elements(GLenum mode,GLsizei count,GLenum type,const void* indices){
    if(!observe||!LineMode(mode)){realElements(mode,count,type,indices);return;}
    auto r=Begin(mode,count,1);
    // Indexed TF draws are not universally admitted by the GL3/GLES3 APIs. Forward production once,
    // then shadow its verified continuous indices through the same production shader/VAO for TF.
    Require(type==GL_UNSIGNED_INT&&indices==nullptr,"indexed shadow control requires continuous uint32 indices");
    GLint ebo{},length{};glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING,&ebo);Require(ebo,"indexed production draw missing EBO");
    glGetBufferParameteriv(GL_ELEMENT_ARRAY_BUFFER,GL_BUFFER_SIZE,&length);
    Require(length>=count*static_cast<int>(sizeof(uint32_t)),"production indices too short");
    const auto* index=static_cast<const uint32_t*>(glMapBufferRange(GL_ELEMENT_ARRAY_BUFFER,0,count*sizeof(uint32_t),GL_MAP_READ_BIT));
    Require(index,"index observation map failed");bool continuous=true;
    for(GLsizei i=0;i<count;++i)continuous&=index[i]==static_cast<uint32_t>(i);
    Require(glUnmapBuffer(GL_ELEMENT_ARRAY_BUFFER)==GL_TRUE&&continuous,"production index order is not shadow-equivalent");
    realElements(mode,count,type,indices);
    Capture(r,[&](){realArrays(mode,0,count);});records.push_back(std::move(r));
}
static void Arrays(GLenum mode,GLint first,GLsizei count){
    if(observe&&mode==GL_TRIANGLE_FAN){++fillDraws;fillVertices+=count;}
    if(!observe||!LineMode(mode)){realArrays(mode,first,count);return;}
    auto r=Begin(mode,count,1,first);Capture(r,[&](){realArrays(mode,first,count);});records.push_back(std::move(r));
}
static void Instanced(GLenum mode,GLint first,GLsizei count,GLsizei instances){
    if(!observe){realInstanced(mode,first,count,instances);return;}
    Require(mode==GL_TRIANGLE_STRIP&&count==4,"unexpected production line instancing");
    auto r=Begin(mode,count,instances);Capture(r,[&](){realInstanced(mode,first,count,instances);});records.push_back(std::move(r));
}
class Hooks {
public:
    Hooks(){realLink=glad_glLinkProgram;realElements=glad_glDrawElements;realArrays=glad_glDrawArrays;realInstanced=glad_glDrawArraysInstanced;
        glad_glLinkProgram=Link;glad_glDrawElements=Elements;glad_glDrawArrays=Arrays;glad_glDrawArraysInstanced=Instanced;
        glGenBuffers(1,&feedbackBuffer);glGenQueries(1,&primitiveQuery);}
    ~Hooks(){observe=false;glad_glLinkProgram=realLink;glad_glDrawElements=realElements;glad_glDrawArrays=realArrays;
        glad_glDrawArraysInstanced=realInstanced;glDeleteQueries(1,&primitiveQuery);glDeleteBuffers(1,&feedbackBuffer);}
};
struct Target {
    Framebuffer fbo{1};
    Target(int w,int h){fbo.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);fbo.SetSize(w,h);}
    void Bind(int w,int h){fbo.Bind(0);glViewport(0,0,w,h);}
};
struct Context {
    ShaderCache cache;PresetState state;PerFrameContext frame;
    Context():frame(state.globalMemory,&state.globalRegisters){
        auto& rc=state.renderContext;rc.shaderCache=&cache;rc.viewportSizeX=256;rc.viewportSizeY=144;
        rc.aspectX=1;rc.aspectY=.5625f;rc.invAspectX=1;rc.invAspectY=1/.5625f;
        rc.time=.25f;rc.frame=7;rc.fps=30;state.LoadShaders();
        state.audioData.waveformLeft.fill(0);state.audioData.waveformRight.fill(0);
        state.audioData.spectrumLeft.fill(0);state.audioData.spectrumRight.fill(0);
        frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);
    }
    void Profile(int w,int h,int rw,int rh){auto& rc=state.renderContext;rc.viewportSizeX=w;rc.viewportSizeY=h;
        rc.lineReferenceWidth=rw;rc.lineReferenceHeight=rh;rc.aspectX=h>w?float(w)/h:1;rc.aspectY=w>h?float(h)/w:1;
        rc.invAspectX=1/rc.aspectX;rc.invAspectY=1/rc.aspectY;}
};
static std::shared_ptr<Texture> Map(float u,float v){
    const std::array<float,8> data{u,v,u,v,u,v,u,v};
    return std::make_shared<Texture>("declared-prior-motion-field",data.data(),GL_TEXTURE_2D,2,2,1,GL_RG16F,GL_RG,GL_FLOAT,false);
}
static std::array<float,2> Normalized(const std::array<float,4>& p){return {(p[0]/p[3]+1)/2,(p[1]/p[3]+1)/2};}
static std::array<float,2> MotionEnd(const Record& r){
    Require(!r.clipPositions.empty(),"production vertex shader output absent");
    if(r.mode==GL_LINES){Require(r.clipPositions.size()==2,"motion line primitive count changed");return Normalized(r.clipPositions[1]);}
    Require(r.clipPositions.size()==6,"motion quad must capture two triangles");
    // A-B strip expands as 0,1,2,2,1,3. Average the B corners 2/3 to recover endpoint centre.
    std::array<float,4> centre{};for(int c=0;c<4;++c)centre[c]=(r.clipPositions[2][c]+r.clipPositions[5][c])*.5f;
    return Normalized(centre);
}
static void MotionControls(){
    Context c;MotionVectors vectors(c.state);Target target(3840,2160);
    const auto previous=Map(.5f,.5f),next=Map(.75f,.5f),small=Map(.50048828125f,.5f);
    struct P{int w,h,rw,rh;bool diffusion;};
    const std::array<P,6> profiles{{{256,144,0,0,false},{256,256,0,0,false},
        {1280,720,0,0,false},{3840,2160,1280,720,false},{3840,2160,1280,720,true},{3840,2160,0,0,false}}};
    for(const auto& p:profiles)for(int kind:{0,1,2}){
        c.Profile(p.w,p.h,p.rw,p.rh);target.Bind(p.w,p.h);c.frame.LoadStateVariables(c.state);
        *c.frame.mv_x=*c.frame.mv_y=2;*c.frame.mv_dx=.3;*c.frame.mv_dy=-.3;*c.frame.mv_l=1;*c.frame.mv_a=1;
        const auto field=kind==0?previous:kind==1?small:next;
        records.clear();observe=true;const bool drawn=vectors.Draw(c.frame,field,p.diffusion);observe=false;
        Require(drawn&&records.size()==1,"motion production submission count changed");const auto& r=records[0];
        const bool quad=p.rw>0&&p.rh>0;Require(r.mode==(quad?GL_TRIANGLE_STRIP:GL_LINES),"motion compiled quad path fell back");
        Require(r.count==(quad?4:2)&&r.instances==1,"motion primitive/instance count changed");
        Require(r.texture==static_cast<GLint>(field->TextureID()),"motion queried a different field texture");Near(r.alpha,1,"motion submission alpha changed");
        const float base=std::hypot(1.25f/p.w,1.25f/p.h);
        const float scale=quad?std::max(1.f,std::sqrt(float(p.w)*p.h/(float(p.rw)*p.rh))):0;
        const float minimum=p.diffusion?base*std::max(1.f,scale):base;
        Near(r.minimum,minimum,"wrong actual minimum uniform");Near(r.length,1,"wrong actual motion length uniform");
        const auto end=MotionEnd(r);
        const float dx=kind==0?minimum:kind==1?std::max(.00048828125f,minimum):.25f;
        Near(end[0],.5f+dx,"actual motion vertex endpoint x");Near(end[1],.5f+(kind==0?minimum:0),"actual motion vertex endpoint y");
        std::cout<<"I15 "<<p.w<<'x'<<p.h<<" reference="<<p.rw<<'x'<<p.rh<<" diffusion="<<p.diffusion
                 <<" kind="<<kind<<" minimum="<<r.minimum<<" original_threshold="<<1.f/p.w
                 <<" endpoint="<<end[0]<<','<<end[1]<<" map_generation="<<(kind==2?"next-explicit":"previous-explicit")<<'\n';
        // Allocating next did not replace the explicitly supplied previous field; test it again.
        records.clear();observe=true;vectors.Draw(c.frame,previous,p.diffusion);observe=false;
        Near(MotionEnd(records.at(0))[0],.5f+minimum,"next field replaced previous ownership");
        *c.frame.mv_a=0;records.clear();observe=true;const bool hidden=vectors.Draw(c.frame,previous,p.diffusion);observe=false;
        Require(!hidden&&records.empty(),"motion zero alpha drew geometry");
    }
}
static std::unique_ptr<CustomWaveform> Wave(Context& c,bool thick,float alpha){
    std::ostringstream text;text<<"[preset00]\nwavecode_0_enabled=1\nwavecode_0_samples=2\nwavecode_0_sep=0\n"
        <<"wavecode_0_bUseDots=0\nwavecode_0_bDrawThick="<<thick<<"\nwavecode_0_a="<<alpha<<"\n"
        <<"wave_0_per_frame1=reg00+=1;\nwave_0_per_point1=reg01+=1;x=.25+.5*sample;y=.5;r=1;g=1;b=1;\n";
    std::istringstream stream(text.str());PresetFileParser parser;Require(parser.Read(stream),"wave fixture parse failed");
    c.state.Initialize(parser);c.frame.LoadStateVariables(c.state);
    auto wave=std::make_unique<CustomWaveform>(c.state);wave->Initialize(parser,0);std::vector<std::string> warnings;
    wave->CompileCodeAndRunInitExpressions(c.frame,warnings);Require(warnings.empty(),"wave equations did not compile");return wave;
}
static std::unique_ptr<CustomShape> Shape(Context& c,bool thick,float alpha){
    std::ostringstream text;text<<"[preset00]\nshapecode_0_enabled=1\nshapecode_0_sides=4\nshapecode_0_num_inst=1\n"
        <<"shapecode_0_a=0\nshapecode_0_a2=0\nshapecode_0_border_a="<<alpha<<"\nshapecode_0_thickOutline="<<thick
        <<"\nshapecode_0_rad=.2\nshape_0_per_frame1=reg02+=1;\n";
    std::istringstream stream(text.str());PresetFileParser parser;Require(parser.Read(stream),"shape fixture parse failed");
    c.state.Initialize(parser);c.frame.LoadStateVariables(c.state);
    auto shape=std::make_unique<CustomShape>(c.state);shape->Initialize(parser,0);std::vector<std::string> warnings;
    shape->CompileCodeAndRunInitExpressions(warnings);Require(warnings.empty(),"shape equations did not compile");return shape;
}
static void StyleTrace(bool wave,bool thick,bool replay,float alpha){
    Context c;c.Profile(3840,2160,1280,720);Target authored(1280,720),native(3840,2160);
    GeometryTargets targets(c.state,authored.fbo,0,1280,720,{},native.fbo,0);targets.Authored();
    auto custom=wave?Wave(c,thick,alpha):nullptr;auto shape=wave?nullptr:Shape(c,thick,alpha);
    records.clear();fillDraws=fillVertices=0;observe=true;
    if(wave)custom->Draw(c.frame,replay?&targets:nullptr);else shape->Draw(replay?&targets:nullptr);
    observe=false;
    Require(c.state.globalRegisters[wave?0:2]==1,"geometry replay repeated frame equations");
    if(wave)Require(c.state.globalRegisters[1]==2,"geometry replay repeated point equations");
    const int passes=thick?4:1;const int lineCalls=wave?passes*(replay?2:1):(alpha>0?passes*(replay?2:1):0);
    Require(records.size()==static_cast<std::size_t>(lineCalls),"thick/thin/border submission count changed");
    Require(fillDraws==(wave?0:(replay?2:1))&&fillVertices==(wave?0:6*(replay?2:1)),"shape transparent fill submission changed");
    for(std::size_t i=0;i<records.size();++i){
        const auto& r=records[i];const bool quad=r.mode==GL_TRIANGLE_STRIP;
        Require(r.count==(quad?4:(wave?3:4))&&r.instances==(quad?(wave?2:4):1),"style source count/segments changed");
        Require(!r.clipPositions.empty(),"style shader output absent");
        Near(r.alpha,alpha,"style submitted alpha changed");
        const int pass=static_cast<int>(i)%passes;const auto& first=records[i-static_cast<std::size_t>(pass)];
        const float scale=quad?3:1;const float ex=(pass==1||pass==2)?scale/float(r.viewport[2]):0;
        const float ey=(pass==2||pass==3)?scale/float(wave?r.viewport[2]:r.viewport[3]):0;
        Near(r.clipPositions[0][0]-first.clipPositions[0][0],ex,"actual thick pass clip-x offset");
        Near(r.clipPositions[0][1]-first.clipPositions[0][1],-ey,"actual thick pass clip-y offset");
        if(quad){Near(r.passOffset[0],ex,"actual Native pass_offset.x");Near(r.passOffset[1],ey,"actual Native pass_offset.y");Near(r.halfWidth,1.5f,"Native width changed");}
        std::cout<<"I23 kind="<<(wave?"wave":"shape")<<" thick="<<thick<<" alpha="<<alpha<<" replay="<<replay
                 <<" viewport="<<r.viewport[2]<<'x'<<r.viewport[3]<<" pass="<<pass<<" mode="<<r.mode
                 <<" count="<<r.count<<" instances="<<r.instances<<" offset_pixels="<<ex*r.viewport[2]/2<<','<<ey*r.viewport[3]/2<<'\n';
    }
}
int main(){try{
    GLContext gl;Hooks hooks;std::cout<<std::setprecision(9);
    MotionControls();for(bool wave:{true,false})for(bool thick:{false,true})for(bool replay:{false,true})for(float alpha:{0.f,1.f})StyleTrace(wave,thick,replay,alpha);
    std::cout<<"Production motion/style controls pass; full Native/previous-frame renderer gates remain separate\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
