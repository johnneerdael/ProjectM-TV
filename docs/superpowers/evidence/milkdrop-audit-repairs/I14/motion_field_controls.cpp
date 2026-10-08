#include <MilkdropPreset/MilkdropShader.hpp>
// Preparation only. Production CGL components; no canonical source mutations.
#include "gl_context.hpp"
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PerPixelContext.hpp>
#include <MilkdropPreset/PerPixelMesh.hpp>
#include <MilkdropPreset/MotionVectors.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/TextureManager.hpp>
#include <Renderer/Texture.hpp>
#include <array>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <iostream>
#include <iomanip>
#include <stdexcept>
using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool ok,const std::string& message){if(!ok)throw std::runtime_error(message);}
static PFNGLLINKPROGRAMPROC realLink;
static PFNGLDRAWELEMENTSPROC realElements;
static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced;
static GLuint feedbackBuffer;
static std::vector<float> warpVertices,motionVertices;
static std::vector<uint32_t> warpIndices;
static GLenum requestedFilter=GL_LINEAR;
static bool IsMotion(GLuint program){return glGetUniformLocation(program,"warp_coordinates")>=0;}
static void Link(GLuint program)
{
    GLint count{};glGetProgramiv(program,GL_ATTACHED_SHADERS,&count);std::vector<GLuint> attached(count);glGetAttachedShaders(program,count,nullptr,attached.data());
    for(GLuint shader:attached){GLint type{},length{};glGetShaderiv(shader,GL_SHADER_TYPE,&type);if(type!=GL_VERTEX_SHADER)continue;
        glGetShaderiv(shader,GL_SHADER_SOURCE_LENGTH,&length);std::string source(length,'\0');glGetShaderSource(shader,length,nullptr,source.data());
        const char* varying=nullptr;
        if(source.find("warp_coordinates")!=std::string::npos)varying="gl_Position";
        else if(source.find("uniform vec4 warpFactors")!=std::string::npos)varying="frag_TEXCOORD0";
        if(varying)glTransformFeedbackVaryings(program,1,&varying,GL_INTERLEAVED_ATTRIBS);
    }
    realLink(program);
}
template<class Draw>static void Capture(GLenum primitive,int vertices,bool motion,Draw draw)
{
    GLint sampler{};GLint min{},mag{};
    if(motion){GLint previousActive{};glGetIntegerv(GL_ACTIVE_TEXTURE,&previousActive);glActiveTexture(GL_TEXTURE0);glGetIntegerv(GL_SAMPLER_BINDING,&sampler);glActiveTexture(previousActive);Check(sampler!=0,"production motion sampler missing");
        glGetSamplerParameteriv(sampler,GL_TEXTURE_MIN_FILTER,&min);glGetSamplerParameteriv(sampler,GL_TEXTURE_MAG_FILTER,&mag);
        Check(min==GL_LINEAR&&mag==GL_LINEAR,"production sampler changed from linear");
        glSamplerParameteri(sampler,GL_TEXTURE_MIN_FILTER,requestedFilter);glSamplerParameteri(sampler,GL_TEXTURE_MAG_FILTER,requestedFilter);}
    glBindBuffer(GL_TRANSFORM_FEEDBACK_BUFFER,feedbackBuffer);glBufferData(GL_TRANSFORM_FEEDBACK_BUFFER,vertices*4*sizeof(float),nullptr,GL_STREAM_READ);
    glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,feedbackBuffer);glBeginTransformFeedback(primitive);draw();glEndTransformFeedback();
    const auto* output=static_cast<const float*>(glMapBufferRange(GL_TRANSFORM_FEEDBACK_BUFFER,0,vertices*4*sizeof(float),GL_MAP_READ_BIT));Check(output,"transform feedback mapping failed");
    auto& destination=motion?motionVertices:warpVertices;destination.assign(output,output+vertices*4);glUnmapBuffer(GL_TRANSFORM_FEEDBACK_BUFFER);glBindBufferBase(GL_TRANSFORM_FEEDBACK_BUFFER,0,0);
    if(motion){glSamplerParameteri(sampler,GL_TEXTURE_MIN_FILTER,min);glSamplerParameteri(sampler,GL_TEXTURE_MAG_FILTER,mag);}
    Check(glGetError()==GL_NO_ERROR,"production transform feedback GL error");
}
static void Elements(GLenum mode,GLsizei count,GLenum type,const void* indices)
{
    GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    if(IsMotion(program)){Check(mode==GL_LINES&&count==2,"fixture did not produce one GL motion vector");Capture(GL_LINES,count,true,[&]{realElements(mode,count,type,indices);});}
    else if(glGetUniformLocation(program,"warpFactors")>=0){Check(mode==GL_TRIANGLES&&type==GL_UNSIGNED_INT&&indices==nullptr,"unexpected warp primitive/index type");
        const auto* data=static_cast<const uint32_t*>(glMapBufferRange(GL_ELEMENT_ARRAY_BUFFER,0,count*sizeof(uint32_t),GL_MAP_READ_BIT));Check(data,"warp index readback failed");warpIndices.assign(data,data+count);glUnmapBuffer(GL_ELEMENT_ARRAY_BUFFER);Capture(GL_TRIANGLES,count,false,[&]{realElements(mode,count,type,indices);});}
    else realElements(mode,count,type,indices);
}
static void Instanced(GLenum mode,GLint first,GLsizei count,GLsizei instances)
{
    GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    if(IsMotion(program)){Check(mode==GL_TRIANGLE_STRIP&&first==0&&count==4&&instances==1,"fixture did not produce one Native motion quad");Capture(GL_TRIANGLES,6,true,[&]{realInstanced(mode,first,count,instances);});}
    else realInstanced(mode,first,count,instances);
}
struct Hooks{Hooks(){realLink=glad_glLinkProgram;realElements=glad_glDrawElements;realInstanced=glad_glDrawArraysInstanced;glad_glLinkProgram=Link;glad_glDrawElements=Elements;glad_glDrawArraysInstanced=Instanced;glGenBuffers(1,&feedbackBuffer);}
~Hooks(){glad_glLinkProgram=realLink;glad_glDrawElements=realElements;glad_glDrawArraysInstanced=realInstanced;glDeleteBuffers(1,&feedbackBuffer);}};
using UV=std::array<float,2>;
static UV OriginalBilerp(){
    // Original source accumulates A, then B, C, D in float32; final inversion is explicit.
    constexpr UV a{.375f,.75f},b{.5f,.75f},c{.375f,.625f},d{.75f,.875f};
    constexpr float s=.25f,t=.375f;UV result{};
    for(int channel=0;channel<2;++channel){result[channel]=a[channel]*(1-s)*(1-t);result[channel]+=b[channel]*s*(1-t);result[channel]+=c[channel]*(1-s)*t;result[channel]+=d[channel]*s*t;}
    result[1]=1-result[1];return result;
}
static UV FromClip(int vertex){return {motionVertices[vertex*4]*.5f+.5f,motionVertices[vertex*4+1]*.5f+.5f};}
struct Control
{
    ShaderCache cache;TextureManager textures{std::vector<std::string>{}};PresetState state;
    PerFrameContext frame{state.globalMemory,&state.globalRegisters};PerPixelContext pixel{state.globalMemory,&state.globalRegisters};PerPixelMesh mesh;MotionVectors motion{state};
    std::shared_ptr<Texture> source=std::make_shared<Texture>("field-source",GL_TEXTURE_2D,256,256,1,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
    std::shared_ptr<Texture> color=std::make_shared<Texture>("field-color",GL_TEXTURE_2D,256,256,1,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
    std::shared_ptr<Texture> nativeColor=std::make_shared<Texture>("motion-native-output",GL_TEXTURE_2D,3840,2160,1,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
    std::shared_ptr<Texture> uv;GLuint framebuffer{},authoredMotion{},nativeMotion{};
    Control(GLenum format,int path):uv(std::make_shared<Texture>("field-uv",GL_TEXTURE_2D,256,256,1,format,GL_RG,GL_FLOAT,false))
    {
        auto& rc=state.renderContext;rc.shaderCache=&cache;rc.textureManager=&textures;rc.viewportSizeX=rc.viewportSizeY=256;rc.perPixelMeshX=rc.perPixelMeshY=8;
        rc.aspectX=rc.aspectY=rc.invAspectX=rc.invAspectY=1;rc.texelOffsetX=rc.texelOffsetY=0;rc.fps=30;rc.time=1.5f;state.LoadShaders();state.mainTexture=source;
        glBindTexture(GL_TEXTURE_2D,source->TextureID());std::vector<unsigned char> input(256*256*4,0);for(size_t i=0;i<input.size();i+=4){input[i+2]=191;input[i+3]=255;}
        glTexSubImage2D(GL_TEXTURE_2D,0,0,0,256,256,GL_RGBA,GL_UNSIGNED_BYTE,input.data());
        frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);*frame.zoom=*frame.zoomexp=*frame.sx=*frame.sy=1;*frame.rot=*frame.warp=*frame.dx=*frame.dy=0;*frame.decay=1;*frame.cx=*frame.cy=.5;
        pixel.RegisterBuiltinVariables();pixel.CompilePerPixelCode("d=equal(x,.375)*equal(y,.375);dx=-.125-.25*d;dy=.25*d;reg00+=1;");Check(pixel.perPixelCodeHandle,"finite field EEL compile failed");
        if(path){state.warpShaderVersion=2;state.warpShader=path==1?"shader_body { ret=float3(uv.x,uv.y,.25); }":"shader_body { ret=missing_function_that_must_fail(uv); }";}
        mesh.LoadWarpShader(state);mesh.CompileWarpShader(state);
        glGenFramebuffers(1,&framebuffer);glGenFramebuffers(1,&authoredMotion);glGenFramebuffers(1,&nativeMotion);
        glBindFramebuffer(GL_FRAMEBUFFER,authoredMotion);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,color->TextureID(),0);Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"authored motion target incomplete");
        glBindFramebuffer(GL_FRAMEBUFFER,nativeMotion);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,nativeColor->TextureID(),0);Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"Native motion target incomplete");
        glBindFramebuffer(GL_FRAMEBUFFER,framebuffer);
        glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,color->TextureID(),0);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT1,GL_TEXTURE_2D,uv->TextureID(),0);
        const GLenum buffers[]={GL_COLOR_ATTACHMENT0,GL_COLOR_ATTACHMENT1};glDrawBuffers(2,buffers);Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"field framebuffer incomplete");glViewport(0,0,256,256);
    }
    ~Control(){glDeleteFramebuffers(1,&framebuffer);glDeleteFramebuffers(1,&authoredMotion);glDeleteFramebuffers(1,&nativeMotion);}
    std::vector<UV> Publish(){pixel.LoadStateReadOnlyVariables(state,frame);pixel.LoadPerFrameQVariables(state,frame);warpVertices.clear();mesh.Prepare(state,frame,pixel);mesh.DrawAgain(state,frame);
        Check(state.globalRegisters[0]==81,"prepared field equations not once per node");const auto calls=state.globalRegisters[0];const auto first=warpVertices;mesh.DrawAgain(state,frame);Check(calls==state.globalRegisters[0]&&first==warpVertices,"field replay reevaluated/changed vertices");
        Check(warpVertices.size()==8*8*6*4&&warpIndices.size()==8*8*6,"warp capture count changed");
        for(size_t i=0;i<warpIndices.size();++i){const auto node=warpIndices[i];const float x=float(node%9)/8,y=float(node/9)/8;const float d=(node%9==3&&node/9==3)?1.f:0.f;
            Check(std::abs(warpVertices[i*4]-(x+.125f+.25f*d))<1e-6f&&std::abs(warpVertices[i*4+1]-(y-.25f*d))<1e-6f,"actual warp node producer differs from injected final corners");
            Check(warpVertices[i*4+2]==x&&warpVertices[i*4+3]==y,"original UV varying changed");}
        std::vector<UV> field(256*256);glReadBuffer(GL_COLOR_ATTACHMENT1);glReadPixels(0,0,256,256,GL_RG,GL_FLOAT,field.data());Check(glGetError()==GL_NO_ERROR,"actual UV storage read failed");return field;}
    UV Sample(const std::vector<UV>& field,bool nearest){
        const float x=.28125f*256-.5f,y=(1-.296875f)*256-.5f;
        if(nearest)return field[int(std::floor(y+.5f))*256+int(std::floor(x+.5f))];
        const int ix=int(std::floor(x)),iy=int(std::floor(y));const float sx=x-ix,sy=y-iy;UV result{};
        const UV a=field[iy*256+ix],b=field[iy*256+ix+1],c=field[(iy+1)*256+ix],d=field[(iy+1)*256+ix+1];
        for(int k=0;k<2;++k){result[k]=a[k]*(1-sx)*(1-sy);result[k]+=b[k]*sx*(1-sy);result[k]+=c[k]*(1-sx)*sy;result[k]+=d[k]*sx*sy;}return result;}
    UV Draw(bool native){
        // Same256-square UV owner; physical4K is a declared component-stage override.
        auto& rc=state.renderContext;rc.viewportSizeX=native?3840:256;rc.viewportSizeY=native?2160:256;rc.lineReferenceWidth=native?1280:0;rc.lineReferenceHeight=native?720:0;
        *frame.mv_a=1;*frame.mv_x=*frame.mv_y=2;*frame.mv_dx=.08125;*frame.mv_dy=-.096875;*frame.mv_l=1;*frame.mv_r=*frame.mv_g=*frame.mv_b=1;
        glBindFramebuffer(GL_FRAMEBUFFER,native?nativeMotion:authoredMotion);const GLenum buffer=GL_COLOR_ATTACHMENT0;glDrawBuffers(1,&buffer);glViewport(0,0,rc.viewportSizeX,rc.viewportSizeY);motionVertices.clear();
        Check(motion.Draw(frame,uv,false),"production motion fixture drew nothing");Check(motionVertices.size()==(native?24:8),"motion feedback vertex count changed");
        if(!native)return FromClip(1);
        // Triangle-strip TF emits0,1,2 /2,1,3; end-center average cancels style width.
        const UV a=FromClip(2),b=FromClip(5);return {(a[0]+b[0])*.5f,(a[1]+b[1])*.5f};
    }
};
int main(){
 try{GLContext gl;Hooks hooks;glDisable(GL_DITHER);
    const UV original=OriginalBilerp();Check(original==UV{.4296875f,.2734375f},"independent original bilerp source witness changed");
    for(int path:{0,1,2})for(GLenum format:{GL_RG16F,GL_RG32F}){
        Control control(format,path);auto field=control.Publish();
        glReadBuffer(GL_COLOR_ATTACHMENT0);std::array<unsigned char,4> color{};glReadPixels(8,8,1,1,GL_RGBA,GL_UNSIGNED_BYTE,color.data());Check(std::abs(int(color[2])-(path==1?64:191))<=1,"actual compiled custom/fallback marker missing");
        const UV triangle=path==1?UV{.40625f,.296875f}:UV{.46875f,.234375f};
        const UV actualLinear=control.Sample(field,false);Check(std::abs(actualLinear[0]-triangle[0])<4e-6&&std::abs(actualLinear[1]-triangle[1])<4e-6,"actual raster storage does not match declared AD/BC model");
        for(bool native:{false,true})for(bool nearest:{false,true}){
            requestedFilter=nearest?GL_NEAREST:GL_LINEAR;const UV expected=control.Sample(field,nearest),endpoint=control.Draw(native);
            Check(std::abs(endpoint[0]-expected[0])<4e-6&&std::abs(endpoint[1]-expected[1])<4e-6,"actual production motion endpoint differs from sampled stored field");
            std::cout<<std::setprecision(9)<<"path="<<path<<" format="<<format<<" native="<<native<<" nearest="<<nearest<<" endpoint="<<endpoint[0]<<','<<endpoint[1]<<" original="<<original[0]<<','<<original[1]<<'\n';
        }
    }
    // Uniform fractional storage isolates half conversion from triangles/filtering.
    for(float value:{.173f,.17309f,.25f,.5f})for(GLenum format:{GL_RG16F,GL_RG32F}){
        Control control(format,1);
        // Explicit authored COLOR1 override isolates actual fragment -> attachment conversion.
        // It is a finite test producer, not an original custom-shader semantic claim.
        control.state.warpShader="shader_body { ret=float3(uv.x,uv.y,.25); _mv_tex_coords.xy=float2("+std::to_string(value)+",.5); }";
        control.mesh.LoadWarpShader(control.state);control.mesh.CompileWarpShader(control.state);control.Publish();
        for(bool uploadWrite:{false,true}){
            if(uploadWrite){std::vector<UV> upload(256*256,UV{value,.5f});glBindTexture(GL_TEXTURE_2D,control.uv->TextureID());glTexSubImage2D(GL_TEXTURE_2D,0,0,0,256,256,GL_RG,GL_FLOAT,upload.data());}
            glBindFramebuffer(GL_FRAMEBUFFER,control.framebuffer);glReadBuffer(GL_COLOR_ATTACHMENT1);UV stored{};glReadPixels(72,180,1,1,GL_RG,GL_FLOAT,stored.data());Check(glGetError()==GL_NO_ERROR,"uniform storage conversion failed");
            requestedFilter=GL_LINEAR;for(bool native:{false,true}){const UV endpoint=control.Draw(native);Check(std::abs(endpoint[0]-stored[0])<4e-6&&std::abs(endpoint[1]-stored[1])<4e-6,"motion storage/query conversion mismatch");}
            if(format==GL_RG32F)Check(stored[0]==value,"float32 storage changed input");
            if(value==.25f||value==.5f)Check(stored[0]==value,"exact half control changed");
            std::cout<<std::setprecision(9)<<"storage format="<<format<<" write="<<(uploadWrite?"upload":"render-target")<<" input="<<value<<" stored="<<stored[0]<<'\n';
        }
    }
    std::cout<<"production field/raster/filter/storage/motion controls PASS\n";
 }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}return 0;
}
