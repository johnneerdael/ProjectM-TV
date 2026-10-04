#include <ProjectM.hpp>
#include <Renderer/Shader.hpp>
#include <OpenGL/OpenGL.h>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

class Engine : public libprojectM::ProjectM
{
public:
    mutable std::string failure;
    void PresetSwitchFailedEvent(const std::string&,const std::string& why) const override { failure=why; }
};

std::string Preset(int scene,bool gated)
{
    const std::string checker="(32+160*frac((floor(uv.x*texsize.x)+floor(uv.y*texsize.y))*.5)*2)/255.0";
    const std::string point="((floor(uv.x*texsize.x)==50 && floor(uv.y*texsize.y)==50)?128.0/255.0:0)";
    std::string body="if(frame<1) ret="+(scene==2?point:checker)+"; else ";
    if(scene==0) body+="ret=GetPixel(uv);";
    if(scene==1) body+="ret=GetPixel(uv+float2(texsize.z,0));";
    if(scene==2) body+="{ret=max(GetPixel(uv+float2(texsize.z,0)),GetPixel(uv-float2(texsize.z,0)));"
                     "ret=max(ret,GetPixel(uv+float2(0,texsize.w)));"
                     "ret=max(ret,GetPixel(uv-float2(0,texsize.w)));ret=ret*.94-.04;}";
    if(gated) body+="ret+=0*GetPixel(uv_orig);";
    return "MILKDROP_PRESET_VERSION=201\nPSVERSION_WARP=3\nPSVERSION_COMP=3\n[preset00]\n"
           "fDecay=1\nfGammaAdj=1\nfWaveAlpha=0\nfShader=0\nfVideoEchoAlpha=0\n"
           "fWarpAnimSpeed=1\nfWarpScale=1\nfZoomExponent=1\nzoom=1\nwarp=0\nrot=0\n"
           "dx=0\ndy=0\nsx=1\nsy=1\nbTexWrap=1\nmv_a=0\nob_size=0\nib_size=0\n"
           "warp_1=`shader_body {"+body+"}\n"
           "comp_1=`shader_body {ret=GetPixel(uv);}\n";
}

int main(int argc,char** argv)
{
    if(argc!=2)return 1;
    const std::string directory=argv[1];
    CGLPixelFormatAttribute attributes[]={kCGLPFAOpenGLProfile,static_cast<CGLPixelFormatAttribute>(kCGLOGLPVersion_3_2_Core),static_cast<CGLPixelFormatAttribute>(0)};
    CGLPixelFormatObj format{};GLint count{};CGLContextObj context{};
    if(CGLChoosePixelFormat(attributes,&format,&count)!=kCGLNoError||!format)return 2;
    if(CGLCreateContext(format,nullptr,&context)!=kCGLNoError)return 3;
    CGLDestroyPixelFormat(format);CGLSetCurrentContext(context);glDisable(GL_DITHER);
    std::cout<<"driver="<<glGetString(GL_RENDERER)<<"\n";
    for(int reference : {99,100,101}) for(int scene : {0,1,2}) for(bool off : {false,true}) for(int width : {100,200})
    {
        // Only the central100reference run is the matched reference-grid proof; the band tests use200.
        if(width==100&&reference!=100)continue;
        const std::string tag="r"+std::to_string(reference)+"-s"+std::to_string(scene)+"-off"+std::to_string(off)+"-w"+std::to_string(width);
        const auto preset=Preset(scene,off);std::ofstream(directory+"/"+tag+".milk")<<preset;
        GLuint framebuffer{},texture{};glGenFramebuffers(1,&framebuffer);glGenTextures(1,&texture);
        glBindTexture(GL_TEXTURE_2D,texture);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,width,width,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
        glBindFramebuffer(GL_FRAMEBUFFER,framebuffer);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture,0);
        if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE)return 4;
        glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
        {
            std::srand(12345);Engine engine;engine.SetWindowSize(width,width);engine.SetLineReferenceSize(reference,reference);
            engine.SetMeshSize(48,32);engine.SetPresetLocked(true);engine.SetHardCutEnabled(false);engine.SetEasterEgg(0);
            std::istringstream data(preset);engine.LoadPresetData(data,false);
            if(!engine.failure.empty()){std::cerr<<engine.failure<<"\n";return 5;}
            for(int step=0;step<=8;++step)
            {
                engine.RenderFrame(framebuffer);glBindFramebuffer(GL_READ_FRAMEBUFFER,framebuffer);glReadBuffer(GL_COLOR_ATTACHMENT0);
                std::vector<unsigned char> pixels(width*width*4);glReadPixels(0,0,width,width,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());
                if(glGetError()!=GL_NO_ERROR)return 6;
                if(step==0||step==1||step==2||step==4||step==8)
                {
                    std::ofstream output(directory+"/"+tag+"-step"+std::to_string(step)+".rgba",std::ios::binary);
                    output.write(reinterpret_cast<const char*>(pixels.data()),pixels.size());
                    double mean{},sum2{};int peak{},lit{};
                    const int lo=width/5,hi=width*4/5,n=(hi-lo)*(hi-lo);
                    for(int y=lo;y<hi;++y)for(int x=lo;x<hi;++x){int v=pixels[(y*width+x)*4];mean+=v;sum2+=v*v;peak=std::max(peak,v);lit+=v!=0;}
                    mean/=n;double sd=std::sqrt(std::max(0.0,sum2/n-mean*mean));
                    std::cout<<"tag="<<tag<<" step="<<step<<" mean_byte="<<mean<<" sd_byte="<<sd<<" peak="<<peak<<" lit="<<lit<<"\n";
                }
            }
        }
        libprojectM::Renderer::Shader::Unbind();glDeleteFramebuffers(1,&framebuffer);glDeleteTextures(1,&texture);
    }
    CGLSetCurrentContext(nullptr);CGLDestroyContext(context);
}
