// Proposal only. Parent integrates into a real-GL test observer; never clone the RGB producer.
#pragma once
#include <MilkdropPreset/PerFrameContext.hpp>
#include <Renderer/OpenGL.h>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <vector>

namespace I18SubmissionContract {
inline void Require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}
using RawRGB = std::array<std::array<unsigned char,sizeof(PRJM_EVAL_F)>,3>;
inline RawRGB Snapshot(const libprojectM::MilkdropPreset::PerFrameContext& frame) {
    RawRGB bytes{};
    const PRJM_EVAL_F* channels[]={frame.wave_r,frame.wave_g,frame.wave_b};
    for(int i=0;i<3;++i) std::memcpy(bytes[i].data(),channels[i],sizeof(PRJM_EVAL_F));
    return bytes;
}
inline void AssertRawRGBUnchanged(const RawRGB& before,
                                 const libprojectM::MilkdropPreset::PerFrameContext& frame) {
    Require(before==Snapshot(frame),"wave submission mutated raw frame RGB bits");
}
struct Submission {
    GLenum mode{};
    GLsizei count{}, instances{1};
    GLint framebuffer{}, viewport[4]{}, blendSource{}, blendDestination{};
    bool indexed{};
    std::array<float,2> passOffset{};
    float halfWidth{}, pointSize{};
    std::vector<std::array<float,4>> rgba;
    std::vector<unsigned char> submittedGeometry; // Parent records active positions/indices.
};
inline void CheckRGBA(const std::array<float,4>& actual,
                      const std::array<float,3>& expectedRGB, float expectedAlpha) {
    for(int c=0;c<3;++c) {
        if(std::isnan(expectedRGB[c])) Require(std::isnan(actual[c]),"submitted NaN RGB was replaced");
        else Require(std::abs(actual[c]-expectedRGB[c])<1e-6f,"wrong submitted RGB");
    }
    Require(actual[3]==expectedAlpha,"submitted alpha changed");
}
// Capture every actual A/B color attribute consumed by every Native line instance.
// Invoke from the draw hook before forwarding glDrawArraysInstanced to the real API.
inline std::vector<std::array<float,4>> CaptureInstanceRGBA(GLsizei instances) {
    std::vector<std::array<float,4>> values;
    GLint previous{};glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&previous);
    for(GLuint location:{4u,5u}) {
        GLint enabled{},buffer{},size{},stride{},type{},divisor{};
        glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);
        glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);
        glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_SIZE,&size);
        glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
        glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_TYPE,&type);
        glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_DIVISOR,&divisor);
        Require(enabled&&buffer&&size==4&&stride>0&&type==GL_FLOAT&&divisor==1,
                "Native line endpoint RGBA attribute contract changed");
        void* pointer{};glGetVertexAttribPointerv(location,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);
        const auto offset=reinterpret_cast<std::uintptr_t>(pointer);
        glBindBuffer(GL_ARRAY_BUFFER,buffer);GLint length{};
        glGetBufferParameteriv(GL_ARRAY_BUFFER,GL_BUFFER_SIZE,&length);
        Require(instances>0&&offset+std::size_t(instances-1)*stride+sizeof(float)*4<=std::size_t(length),
                "submitted RGBA range exceeds production VBO");
        const auto* bytes=static_cast<const unsigned char*>(glMapBufferRange(GL_ARRAY_BUFFER,0,length,GL_MAP_READ_BIT));
        Require(bytes!=nullptr,"production RGBA VBO map failed");
        for(GLsizei i=0;i<instances;++i) {
            std::array<float,4> rgba{};std::memcpy(rgba.data(),bytes+offset+std::size_t(i)*stride,sizeof(rgba));
            values.push_back(rgba);
        }
        Require(glUnmapBuffer(GL_ARRAY_BUFFER)==GL_TRUE,"production VBO became invalid");
    }
    glBindBuffer(GL_ARRAY_BUFFER,previous);
    Require(glGetError()==GL_NO_ERROR,"submission observer GL error");
    return values;
}
inline std::vector<std::array<float,4>> CaptureConstantRGBA() {
    GLint enabled{};glGetVertexAttribiv(1,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);
    Require(!enabled,"constant RGBA observation used an enabled attribute array");
    std::array<float,4> rgba{};glGetVertexAttribfv(1,GL_CURRENT_VERTEX_ATTRIB,rgba.data());
    return {rgba};
}
inline void AssertSameStyleAndSubmission(const std::vector<Submission>& a,
                                        const std::vector<Submission>& b) {
    Require(!a.empty()&&a.size()==b.size(),"RGB repair changed draw count or rendered nothing");
    for(std::size_t i=0;i<a.size();++i) {
        Require(a[i].mode==b[i].mode&&a[i].count==b[i].count&&a[i].instances==b[i].instances&&
                a[i].indexed==b[i].indexed,"RGB repair changed primitives/count/instances");
        // FBO numeric IDs differ between independent engines; compare declared target roles outside.
        Require(std::memcmp(a[i].viewport,b[i].viewport,sizeof(a[i].viewport))==0&&
                a[i].blendSource==b[i].blendSource&&a[i].blendDestination==b[i].blendDestination&&
                a[i].passOffset==b[i].passOffset&&a[i].halfWidth==b[i].halfWidth&&
                a[i].pointSize==b[i].pointSize,"RGB repair changed alpha/style/blend configuration");
        Require(a[i].submittedGeometry==b[i].submittedGeometry,"RGB repair changed submitted geometry");
        Require(!a[i].submittedGeometry.empty(),"observer omitted active position/index bytes");
        Require(a[i].rgba.size()==b[i].rgba.size(),"RGB repair changed endpoint observations");
        for(std::size_t j=0;j<a[i].rgba.size();++j)
            Require(a[i].rgba[j][3]==b[i].rgba[j][3],"RGB repair changed actual submitted alpha");
    }
}
}
