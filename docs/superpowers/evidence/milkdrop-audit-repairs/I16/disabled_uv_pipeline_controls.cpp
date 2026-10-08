// Source-only CGL proposal. Reuse ignored test-only TF support without modifying that file.
#define main motion_style_support_not_executed
#include "../motion-style-policy/motion_style_controls.cpp"
#undef main
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <ProjectM.hpp>
#include <filesystem>
#include <fstream>

namespace libprojectM {
class FeedbackDetailTestAccess {
public:
    static MilkdropPreset::MilkdropPreset& Active(ProjectM& engine){
        auto* preset=dynamic_cast<MilkdropPreset::MilkdropPreset*>(engine.m_activePreset.get());
        Require(preset,"actual active preset is not Milkdrop");return *preset;
    }
    static uint32_t EngineFrame(const ProjectM& engine){return engine.m_frameCount;}
    static std::shared_ptr<Renderer::Texture> PublishedTexture(MilkdropPreset::MilkdropPreset& p){return p.m_motionVectorUVMap->Texture();}
    static MilkdropPreset::PresetState& State(MilkdropPreset::MilkdropPreset& p){return p.m_state;}
    static MilkdropPreset::PerFrameContext& Frame(MilkdropPreset::MilkdropPreset& p){return p.m_perFrameContext;}
};
}
using Access=libprojectM::FeedbackDetailTestAccess;
struct Publication {uint32_t frame;GLuint program,drawFbo,texture;GLint viewport[4];};
static std::vector<Publication> publications;
static uint32_t observedFrame{};static GLuint expectedUV{};
static libprojectM::MilkdropPreset::MilkdropPreset* observedPreset{};
static PFNGLDRAWELEMENTSPROC inheritedElements{};
static void PipelineElements(GLenum mode,GLsizei count,GLenum type,const void* indices){
    GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    if(observe&&mode==GL_TRIANGLES&&glGetUniformLocation(program,"warpTime")>=0){
        GLint fbo{},attachment{},drawBuffer{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);
        if(fbo){
            glGetFramebufferAttachmentParameteriv(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT1,
                                                  GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&attachment);
            glGetIntegerv(GL_DRAW_BUFFER1,&drawBuffer);
            const GLuint actualUV=observedPreset?Access::PublishedTexture(*observedPreset)->TextureID():expectedUV;
            if(attachment==static_cast<GLint>(actualUV)&&drawBuffer==GL_COLOR_ATTACHMENT1){
                Publication p{};p.frame=observedFrame;p.program=program;p.drawFbo=fbo;p.texture=attachment;
                glGetIntegerv(GL_VIEWPORT,p.viewport);publications.push_back(p);
            }
        }
    }
    inheritedElements(mode,count,type,indices);
}
class PublicationObserver {
public:
    PublicationObserver(){inheritedElements=glad_glDrawElements;glad_glDrawElements=PipelineElements;}
    ~PublicationObserver(){glad_glDrawElements=inheritedElements;}
};
// Test-only actual texture storage readback. This is not a production GetUV API.
static std::array<float,2> ReadPublishedCentre(const std::shared_ptr<Texture>& texture){
    Require(texture&&texture->Width()>=2&&texture->Height()>=2,"published map dimensions invalid");
    GLint oldRead{},oldDraw{};glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&oldRead);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&oldDraw);
    GLuint probe{};glGenFramebuffers(1,&probe);glBindFramebuffer(GL_FRAMEBUFFER,probe);
    glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture->TextureID(),0);
    Require(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"actual RG16F map readback target incomplete");
    glReadBuffer(GL_COLOR_ATTACHMENT0);std::array<float,8> texels{};
    glReadPixels(texture->Width()/2-1,texture->Height()/2-1,2,2,GL_RG,GL_FLOAT,texels.data());
    std::array<float,2> center{};for(int i=0;i<4;++i){center[0]+=texels[i*2]*.25f;center[1]+=texels[i*2+1]*.25f;}
    glBindFramebuffer(GL_READ_FRAMEBUFFER,oldRead);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,oldDraw);glDeleteFramebuffers(1,&probe);
    Require(glGetError()==GL_NO_ERROR,"actual published-map readback GL error");return center;
}
static std::string Preset(bool disabled,bool custom){
    std::ostringstream s;
    s<<"MILKDROP_PRESET_VERSION=201\nPSVERSION=2\nPSVERSION_WARP="<<(custom?2:0)<<"\nPSVERSION_COMP=0\n[preset00]\n"
      <<"fDecay=1\nfGammaAdj=1\nfShader=0\nfVideoEchoAlpha=0\nfWaveAlpha=0\nob_size=0\nib_size=0\nbDarkenCenter=0\n"
      <<"bBrighten=0\nbDarken=0\nbSolarize=0\nbInvert=0\nfWarpScale=1\nnMotionVectorsX=2\nnMotionVectorsY=2\n"
      <<"mv_dx=.3\nmv_dy=-.3\nmv_l=1\nmv_a=1\nmv_r=0\nmv_g=0\nmv_b=1\n"
      <<"per_frame_init_1=reg00=0;\n"
      <<"per_frame_1=dx=-.0625*max(1,min(4,frame));dy=0;zoom=1;zoomexp=1;sx=1;sy=1;rot=0;warp=0;\n"
      <<"per_frame_2=mv_a="<<(disabled?"if(equal(frame,2),0,1)":"1")<<";mv_r=equal(frame,3);mv_g=0;mv_b=1-mv_r;\n"
      <<"per_pixel_1=reg00+=1;\n";
    for(int i=0;i<4;++i)s<<"wavecode_"<<i<<"_enabled=0\nshapecode_"<<i<<"_enabled=0\n";
    if(custom)s<<"warp_1=`shader_body { ret=GetPixel(uv); }\n";
    return s.str();
}
static void RunSequence(bool eager,bool disabled,bool custom,bool detail){
    Target output(3840,2160);libprojectM::ProjectM engine;
    const int w=detail?3840:256,h=detail?2160:144;
    engine.SetWindowSize(w,h);engine.SetMeshSize(48,32);engine.SetTargetFramesPerSecond(30);engine.SetDirectOutput(false);
    engine.SetFeedbackDetail(detail?0.f:-1.f);engine.SetLineReferenceSize(detail?1280:0,detail?720:0);
    engine.SetPresetLocked(true);engine.SetHardCutEnabled(false);engine.SetEasterEgg(0);engine.SetPresetStartClean(true);
    std::istringstream source(Preset(disabled,custom));engine.LoadPresetData(source,false);
    auto& active=Access::Active(engine);observedPreset=&active;std::size_t publishedCount=0;int lastPublished=-1;
    std::array<std::array<float,2>,5> storedCenters{};
    for(uint32_t frame=0;frame<5;++frame){
        Require(Access::EngineFrame(engine)==frame,"engine frame protocol differs; do not infer labels");
        const auto textureBefore=Access::PublishedTexture(active);expectedUV=textureBefore->TextureID();observedFrame=frame;
        const auto previousCentre=frame?ReadPublishedCentre(textureBefore):std::array<float,2>{};
        const int consumedGeneration=lastPublished;
        records.clear();publications.clear();observe=true;engine.SetFrameTime(frame/30.0);engine.RenderFrame(
            [&](){output.Bind(w,h);GLint fbo{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);return GLuint(fbo);}());observe=false;
        auto& state=Access::State(active);const auto& pf=Access::Frame(active);
        Require(state.renderContext.frame==static_cast<int>(frame),"actual preset frame label differs");
        Require(state.globalRegisters[0]==double(frame+1)*1617,"fullpipeline repeated/omitted per-pixel execution");
        const bool off=disabled&&frame==2;const bool shouldPublish=eager||!off;
        Require(publications.size()==std::size_t(shouldPublish?1:0),"unexpected actual UV MRT publication count");
        if(shouldPublish){lastPublished=static_cast<int>(frame);++publishedCount;}
        const auto textureAfter=Access::PublishedTexture(active);
        if(frame>0)Require(textureAfter==textureBefore,"map lease changed in fixed-generation sequence");
        const auto published=ReadPublishedCentre(textureAfter);
        const float field=.5f+.0625f*std::max(1,std::min(4,int(frame)));
        const float expectedPublished=off&&!eager?.5625f:field;
        // Actual RG16F raster storage can introduce backend-dependent bias. Do not fake a half oracle.
        Near(published[0],expectedPublished,"actual published UV generation field",6e-4f);Near(published[1],.5f,"actual published UV y",6e-4f);
        storedCenters[frame]=published;
        const int expectedDraws=(frame==0||off)?0:(detail?2:1);
        Require(records.size()==std::size_t(expectedDraws),"motion consumer/replay count changed");
        for(const auto& draw:records){
            Require(draw.texture==static_cast<GLint>(textureBefore->TextureID()),"motion sampled a different texture lease");
            const auto endpoint=MotionEnd(draw);
            Near(endpoint[0],previousCentre[0],"actual motion did not query pre-warp published texture",2e-5f);
            Near(endpoint[1],previousCentre[1],"actual motion queried incorrect UV row",2e-5f);
            Require(std::abs(endpoint[0]-.5f)>.04f,"biased witness entered I15 minimum branch");
            if(frame==3){const int wantedGeneration=disabled&&!eager?1:2;
                Require(consumedGeneration==wantedGeneration,"reenabled motion publication provenance is wrong");
                Near(endpoint[0],storedCenters[wantedGeneration][0],"reenabled motion consumed wrong stored frame",2e-5f);
                Require(std::abs(endpoint[0]-.6875f)>.04f,"reenabled motion used current C instead of previous B");}
            if(frame==4){Require(consumedGeneration==3,"successor provenance is not C");Near(endpoint[0],storedCenters[3][0],"successor did not consume current C publication",2e-5f);}
            std::cout<<"consumer frame="<<frame<<" viewport="<<draw.viewport[2]<<'x'<<draw.viewport[3]
                     <<" sampled_texture="<<draw.texture<<" sampled_publication_generation="<<consumedGeneration
                     <<" endpoint="<<endpoint[0]<<','<<endpoint[1]<<'\n';
        }
        std::cout<<"field frame="<<frame<<" alpha="<<*pf.mv_a<<" prior="<<previousCentre[0]<<','<<previousCentre[1]
                 <<" published="<<published[0]<<','<<published[1]<<" observed_publication_generation="<<lastPublished
                 <<" mesh_evaluations="<<state.globalRegisters[0]<<" UV="<<textureAfter->Width()<<'x'<<textureAfter->Height()
                 <<" custom="<<custom<<" detail="<<detail<<" eager_oracle="<<eager<<'\n';
    }
    Require(publishedCount==std::size_t(eager||!disabled?5:4),"publication schedule cost differs");
    observedPreset=nullptr;
}
int main(int argc,char** argv){try{
    Require(argc==2,"usage: disabled-uv-controls current|eager-oracle");const std::string role(argv[1]);
    Require(role=="current"||role=="eager-oracle","invalid role");
    GLContext gl;Hooks tf;PublicationObserver publication;std::cout<<std::setprecision(9);
    for(bool custom:{false,true})for(bool detail:{false,true})for(bool disabled:{false,true})RunSequence(role=="eager-oracle",disabled,custom,detail);
    std::cout<<"Fullpipeline temporal controls pass for declared role; generic lazy repair/Native gates remain open\n";return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
