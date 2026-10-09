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
    auto r=Begin(mode,count,1,first);realArrays(mode,first,count);Capture(r,[&](){realArrays(mode,first,count);});records.push_back(std::move(r));
}
static void Instanced(GLenum mode,GLint first,GLsizei count,GLsizei instances){
    if(!observe){realInstanced(mode,first,count,instances);return;}
    Require(mode==GL_TRIANGLE_STRIP&&count==4,"unexpected production line instancing");
    auto r=Begin(mode,count,instances);realInstanced(mode,first,count,instances);Capture(r,[&](){realInstanced(mode,first,count,instances);});records.push_back(std::move(r));
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

static std::array<float,2> Normalized(const std::array<float,4>& p){return {(p[0]/p[3]+1)/2,(p[1]/p[3]+1)/2};}
static std::array<float,2> MotionEnd(const Record& r){
    Require(!r.clipPositions.empty(),"production vertex shader output absent");
    if(r.mode==GL_LINES){Require(r.clipPositions.size()==2,"motion line primitive count changed");return Normalized(r.clipPositions[1]);}
    Require(r.clipPositions.size()==6,"motion quad must capture two triangles");
    std::array<float,4> centre{};for(int c=0;c<4;++c)centre[c]=(r.clipPositions[2][c]+r.clipPositions[5][c])*.5f;
    return Normalized(centre);
}
