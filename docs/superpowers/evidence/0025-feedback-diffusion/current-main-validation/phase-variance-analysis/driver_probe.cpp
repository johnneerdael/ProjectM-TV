#include <MilkdropPreset/FeedbackDiffusion.hpp>
#include <Renderer/Sampler.hpp>
#include <Renderer/Shader.hpp>
#include <Renderer/Texture.hpp>
#include <OpenGL/OpenGL.h>
#include <algorithm>
#include <cmath>
#include <iostream>
#include <memory>
#include <numeric>
#include <vector>

using libprojectM::Renderer::Sampler;
using libprojectM::Renderer::Shader;
using libprojectM::Renderer::Texture;
constexpr int Width = 200, Height = 200;

const char* Vertex = R"(#version 330
void main() {
    vec2 p = gl_VertexID == 0 ? vec2(-1,-1) : gl_VertexID == 1 ? vec2(3,-1) : vec2(-1,3);
    gl_Position = vec4(p,0,1);
})";
const char* Fragment = R"(#version 330
precision highp float;
uniform sampler2D source;
uniform vec2 render_size;
uniform vec2 reference_size;
uniform int reaction;
out vec4 color;
void main() {
    vec2 uv = gl_FragCoord.xy / render_size;
    vec2 pixel = 1.0 / reference_size;
    vec3 c = texture(source, uv).rgb;
    if (reaction == 1) c = texture(source, uv + vec2(pixel.x,0)).rgb;
    if (reaction == 2) {
        c = max(texture(source,uv+vec2(pixel.x,0)).rgb, texture(source,uv-vec2(pixel.x,0)).rgb);
        c = max(c,texture(source,uv+vec2(0,pixel.y)).rgb);
        c = max(c,texture(source,uv-vec2(0,pixel.y)).rgb);
        c = c*.94-.04;
    }
    color = vec4(c,1);
})";
const char* Boundary = R"(#version 330
precision highp float;
uniform sampler2D source;
uniform vec2 render_size;
out vec4 color;
void main() {
    vec2 uv=gl_FragCoord.xy/render_size;
    vec2 step=vec2(.75)/render_size;
    color=(texture(source,uv+vec2(0,-step.y))+
           texture(source,uv+vec2(step.x,step.y*.5))+
           texture(source,uv+vec2(-step.x,step.y*.5)))/3.0;
})";

std::vector<unsigned char> Read(Texture& texture, GLuint framebuffer)
{
    glBindFramebuffer(GL_READ_FRAMEBUFFER,framebuffer);
    glFramebufferTexture2D(GL_READ_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture.TextureID(),0);
    glReadBuffer(GL_COLOR_ATTACHMENT0);
    if (glCheckFramebufferStatus(GL_READ_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE) throw 1;
    std::vector<unsigned char> pixels(Width*Height*4);
    glReadPixels(0,0,Width,Height,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());
    if (glGetError()!=GL_NO_ERROR) throw 2;
    return pixels;
}

void Stats(const std::vector<unsigned char>& pixels, double& mean, double& deviation, int& peak, int& lit)
{
    mean=0; deviation=0; peak=0; lit=0;
    // Interior ROI keeps the recurrence experiment separate from boundary behavior.
    for (int y=40; y<160; ++y) for (int x=40; x<160; ++x) {
        const int value=pixels[(y*Width+x)*4]; mean+=value; deviation+=value*value;
        peak=std::max(peak,value); lit+=value!=0;
    }
    mean/=120*120; deviation=std::sqrt(std::max(0.0,deviation/(120*120)-mean*mean));
}

int main()
{
    CGLPixelFormatAttribute attributes[]={kCGLPFAOpenGLProfile,static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_3_2_Core),static_cast<CGLPixelFormatAttribute>(0)};
    CGLPixelFormatObj format{}; GLint count{}; CGLContextObj context{};
    if(CGLChoosePixelFormat(attributes,&format,&count)!=kCGLNoError||!format) return 2;
    if(CGLCreateContext(format,nullptr,&context)!=kCGLNoError) return 3;
    CGLDestroyPixelFormat(format); CGLSetCurrentContext(context);
    std::cout<<"driver="<<glGetString(GL_RENDERER)<<"\n";
    {
        Texture::SetPoolLimit(0); glDisable(GL_DITHER); glDisable(GL_BLEND);
        Shader reaction; reaction.CompileProgram(Vertex,Fragment);
        Shader boundary; boundary.CompileProgram(Vertex,Boundary);
        Sampler wrapped(GL_REPEAT,GL_LINEAR);
        GLuint vao{},drawFramebuffer{},readFramebuffer{};
        glGenVertexArrays(1,&vao); glGenFramebuffers(1,&drawFramebuffer); glGenFramebuffers(1,&readFramebuffer);
        auto first=std::make_shared<Texture>("first",Width,Height,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
        auto second=std::make_shared<Texture>("second",Width,Height,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false);
        libprojectM::MilkdropPreset::FeedbackDiffusion diffusion;
        for(int ref : {99,100,101}) for(int scene : {0,1,2}) for(bool filtered : {false,true}) {
            std::vector<unsigned char> seed(Width*Height*4,0);
            for(int y=0;y<Height;++y) for(int x=0;x<Width;++x) {
                const int value=scene==2 ? (x==100&&y==100?128:0) : ((x/4+y/4)%2?192:32);
                for(int c=0;c<3;++c) seed[(y*Width+x)*4+c]=static_cast<unsigned char>(value);
                seed[(y*Width+x)*4+3]=255;
            }
            auto current=first,output=second; current->Bind(0);
            glTexSubImage2D(GL_TEXTURE_2D,0,0,0,Width,Height,GL_RGBA,GL_UNSIGNED_BYTE,seed.data());
            diffusion.SetScale(static_cast<float>(Width)/ref);
            for(int frame=1;frame<=8;++frame) {
                glViewport(0,0,Width,Height);
                auto input=current;
                if(filtered) { diffusion.Draw(current,false); input=diffusion.Texture(); }
                glBindFramebuffer(GL_DRAW_FRAMEBUFFER,drawFramebuffer);
                glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,output->TextureID(),0);
                const GLenum draw=GL_COLOR_ATTACHMENT0;glDrawBuffers(1,&draw);
                reaction.Bind(); reaction.SetUniformInt("source",0); reaction.SetUniformInt("reaction",scene);
                reaction.SetUniformFloat2("render_size",{Width,Height}); reaction.SetUniformFloat2("reference_size",{ref,ref});
                input->Bind(0); wrapped.Bind(0); glBindVertexArray(vao); glDrawArrays(GL_TRIANGLES,0,3);
                glBindVertexArray(0); Sampler::Unbind(0);Shader::Unbind();
                auto pixels=Read(*output,readFramebuffer);double mean{},sd{};int peak{},lit{};Stats(pixels,mean,sd,peak,lit);
                int error{};
                if(scene==0) for(size_t n=0;n<pixels.size();++n) error=std::max(error,std::abs(int(pixels[n])-int(seed[n])));
                if(scene==1&&ref==100) for(int y=0;y<Height;++y) for(int x=0;x<Width;++x) for(int c=0;c<4;++c)
                    error=std::max(error,std::abs(int(pixels[(y*Width+x)*4+c])-int(seed[(y*Width+(x+2*frame)%Width)*4+c])));
                if(frame==1||frame==2||frame==4||frame==8)
                    std::cout<<"ref="<<ref<<" scene="<<scene<<" filtered="<<filtered<<" frame="<<frame
                             <<" mean_byte="<<mean<<" sd_byte="<<sd<<" peak="<<peak<<" lit="<<lit<<" exact_identity_or_integer_error="<<error<<"\n";
                std::swap(current,output);
            }
        }
        // Same stencil and variance, different boundary contract. Left half is0, right half255.
        std::vector<unsigned char> edge(Width*Height*4,255);
        for(int y=0;y<Height;++y) for(int x=0;x<Width/2;++x) for(int c=0;c<3;++c)edge[(y*Width+x)*4+c]=0;
        first->Bind(0);glTexSubImage2D(GL_TEXTURE_2D,0,0,0,Width,Height,GL_RGBA,GL_UNSIGNED_BYTE,edge.data());
        glViewport(0,0,Width,Height);diffusion.SetScale(2);diffusion.Draw(first,false);
        auto clamped=Read(*diffusion.Texture(),readFramebuffer);
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER,drawFramebuffer);glFramebufferTexture2D(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,second->TextureID(),0);
        const GLenum draw=GL_COLOR_ATTACHMENT0;glDrawBuffers(1,&draw);
        boundary.Bind();boundary.SetUniformInt("source",0);boundary.SetUniformFloat2("render_size",{Width,Height});first->Bind(0);wrapped.Bind(0);
        glBindVertexArray(vao);glDrawArrays(GL_TRIANGLES,0,3);glBindVertexArray(0);Sampler::Unbind(0);Shader::Unbind();
        auto periodic=Read(*second,readFramebuffer);
        std::cout<<"boundary_clamped_left="<<int(clamped[(100*Width)*4])<<" boundary_wrapped_left="<<int(periodic[(100*Width)*4])
                 <<" boundary_clamped_right="<<int(clamped[(100*Width+199)*4])<<" boundary_wrapped_right="<<int(periodic[(100*Width+199)*4])<<"\n";
        glDeleteFramebuffers(1,&drawFramebuffer);glDeleteFramebuffers(1,&readFramebuffer);glDeleteVertexArrays(1,&vao);
    }
    CGLSetCurrentContext(nullptr);CGLDestroyContext(context);
}
