// Preparation only: actual engine pipeline, producer MRT, stored UV and consumer vertex output.
// Reuse the production GLContext and the extracted existing TF observer; no public GetUV API.
#include "motion_tf_support.hpp"
#include <MilkdropPreset/MilkdropPreset.hpp>
#include <ProjectM.hpp>
#include <functional>

namespace libprojectM {
class FeedbackDetailTestAccess {
public:
    static MilkdropPreset::MilkdropPreset& Active(ProjectM& e) {
        auto* p=dynamic_cast<MilkdropPreset::MilkdropPreset*>(e.m_activePreset.get());
        Require(p,"active preset type changed");return *p;
    }
    static MilkdropPreset::MilkdropPreset* Incoming(ProjectM& e) {
        return dynamic_cast<MilkdropPreset::MilkdropPreset*>(e.m_transitioningPreset.get());
    }
    static std::shared_ptr<Renderer::Texture> UV(MilkdropPreset::MilkdropPreset& p) {return p.m_motionVectorUVMap->Texture();}
    static MilkdropPreset::PresetState& State(MilkdropPreset::MilkdropPreset& p) {return p.m_state;}
    static MilkdropPreset::PerFrameContext& Frame(MilkdropPreset::MilkdropPreset& p) {return p.m_perFrameContext;}
    static bool First(MilkdropPreset::MilkdropPreset& p) {return p.m_isFirstFrame;}
    static bool Detail(MilkdropPreset::MilkdropPreset& p) {return bool(p.m_feedbackDetail);}
    static uint32_t EngineFrame(ProjectM& e) {return e.m_frameCount;}
    // Controlled fault injection into existing owner failure state, not a public renderer API.
    static void DetailFailure(MilkdropPreset::MilkdropPreset& p) {p.m_detailFailed=true;}
};
}
using Access=libprojectM::FeedbackDetailTestAccess;
using MP=libprojectM::MilkdropPreset::MilkdropPreset;
static std::vector<MP*> owners;
struct Publication {MP* owner;GLuint program,fbo,color,uv;GLint viewport[4];std::array<float,2> center,right;std::array<float,4> colorCenter;};
static std::vector<Publication> published;
static unsigned warpInvalidations{};
static PFNGLDRAWELEMENTSPROC nextElements{};
#ifdef USE_GLES
static PFNGLINVALIDATEFRAMEBUFFERPROC nextInvalidate{};
#endif

// Temporary read-FBO probes retain old read/draw bindings. The old FBO's read-buffer state is
// never changed. Float RG16F readback is a backend gate; do not silently substitute a fake field.
static std::array<float,2> ReadUV(GLuint texture,int w,int h,int x) {
    GLint oldRead{},oldDraw{};glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&oldRead);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&oldDraw);
    GLuint fbo{};glGenFramebuffers(1,&fbo);glBindFramebuffer(GL_FRAMEBUFFER,fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture,0);
    Require(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"UV probe FBO incomplete");
    glReadBuffer(GL_COLOR_ATTACHMENT0);
#ifdef USE_GLES
    static bool logged=false;
    if(!logged){GLint format{},type{};glGetIntegerv(GL_IMPLEMENTATION_COLOR_READ_FORMAT,&format);glGetIntegerv(GL_IMPLEMENTATION_COLOR_READ_TYPE,&type);std::cout<<"RG16F readback implementation format="<<format<<" type="<<type<<'\n';logged=true;}
#endif
    // RG is not a required GLES read format. RGBA/FLOAT reads the same real
    // floating attachment; unused B/A channels are ignored, never modeled.
    std::array<float,16> pixels{};
    glReadPixels(x-1,h/2-1,2,2,GL_RGBA,GL_FLOAT,pixels.data());
    std::array<float,2> result{};for(int i=0;i<4;++i){result[0]+=.25f*pixels[4*i];result[1]+=.25f*pixels[4*i+1];}
    glBindFramebuffer(GL_READ_FRAMEBUFFER,oldRead);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,oldDraw);glDeleteFramebuffers(1,&fbo);
    Require(glGetError()==GL_NO_ERROR,"backend does not admit actual RG16F readback");return result;
}
static std::array<float,2> ReadUV(const std::shared_ptr<Texture>& t) {return ReadUV(t->TextureID(),t->Width(),t->Height(),t->Width()/2);}
static std::array<float,4> ReadColor(GLuint fbo,int w,int h) {
    GLint oldRead{};glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&oldRead);glBindFramebuffer(GL_READ_FRAMEBUFFER,fbo);
    GLint oldBuffer{};glGetIntegerv(GL_READ_BUFFER,&oldBuffer);glReadBuffer(GL_COLOR_ATTACHMENT0);
    std::array<unsigned char,4> rgba{};glReadPixels(w/2,h/2,1,1,GL_RGBA,GL_UNSIGNED_BYTE,rgba.data());
    glReadBuffer(oldBuffer);glBindFramebuffer(GL_READ_FRAMEBUFFER,oldRead);
    std::array<float,4> out{};for(int i=0;i<4;++i)out[i]=rgba[i]/255.f;
    Require(glGetError()==GL_NO_ERROR,"actual color attachment readback failed");return out;
}
static void ProducerElements(GLenum mode,GLsizei count,GLenum type,const void* indices) {
    GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
    Publication p{};bool capture=false;
    // Constant-output custom warps can optimize every warp uniform away.
    // Actual owned attachment1 + enabled MRT is the producer contract.
    if(observe&&mode==GL_TRIANGLES) {
        GLint fbo{},uv{},color{},buffer{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);
        if(fbo) {
            glGetFramebufferAttachmentParameteriv(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT1,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&uv);
            glGetFramebufferAttachmentParameteriv(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&color);
            glGetIntegerv(GL_DRAW_BUFFER1,&buffer);
            for(auto* owner:owners)if(uv==static_cast<GLint>(Access::UV(*owner)->TextureID())&&buffer==GL_COLOR_ATTACHMENT1) {
                Require(color!=uv&&color!=0,"producer routing aliases color and UV");
                p.owner=owner;p.program=program;p.fbo=fbo;p.uv=uv;p.color=color;glGetIntegerv(GL_VIEWPORT,p.viewport);capture=true;
            }
        }
    }
    nextElements(mode,count,type,indices); // exactly one real fragment invocation
    if(capture) {
        auto texture=Access::UV(*p.owner);
        Require(p.viewport[2]==texture->Width()&&p.viewport[3]==texture->Height(),"published UV dimensions differ from actual producer viewport");
        p.center=ReadUV(texture);p.right=ReadUV(p.uv,texture->Width(),texture->Height(),texture->Width()*3/4);
        p.colorCenter=ReadColor(p.fbo,p.viewport[2],p.viewport[3]);published.push_back(p);
    }
}
#ifdef USE_GLES
static void Invalidate(GLenum target,GLsizei n,const GLenum* attachments) {
    if(observe&&target==GL_DRAW_FRAMEBUFFER) {
        GLint fbo{},uv{},buffer{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);
        if(fbo) {
            glGetFramebufferAttachmentParameteriv(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT1,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&uv);
            glGetIntegerv(GL_DRAW_BUFFER1,&buffer);
            bool hasUV=false;for(int i=0;i<n;++i)hasUV|=attachments[i]==GL_COLOR_ATTACHMENT1;
            for(auto* owner:owners)if(hasUV&&buffer==GL_COLOR_ATTACHMENT1&&uv==GLint(Access::UV(*owner)->TextureID()))++warpInvalidations;
        }
    }
    nextInvalidate(target,n,attachments);
}
#endif
class ProducerObserver {
public:
    ProducerObserver(){nextElements=glad_glDrawElements;glad_glDrawElements=ProducerElements;
#ifdef USE_GLES
        nextInvalidate=glad_glInvalidateFramebuffer;glad_glInvalidateFramebuffer=Invalidate;
#endif
    }
    ~ProducerObserver(){glad_glDrawElements=nextElements;
#ifdef USE_GLES
        glad_glInvalidateFramebuffer=nextInvalidate;
#endif
    }
};

// Exercise the real constructor exception/RAII path after valid allocations.
// Only the selected status is injected; the driver and later GL checks remain real.
class DetailFramebufferFault {
public:
    explicit DetailFramebufferFault(unsigned failAt):remaining(failAt) {
        Require(!active,"nested framebuffer fault");active=this;
        saved=glad_glCheckFramebufferStatus;glad_glCheckFramebufferStatus=Check;
    }
    ~DetailFramebufferFault(){glad_glCheckFramebufferStatus=saved;active=nullptr;}
    GLuint failedFramebuffer{};
private:
    static GLenum Check(GLenum target) {
        const auto status=active->saved(target);
        if(active->remaining&&--active->remaining==0) {
            Require(status==GL_FRAMEBUFFER_COMPLETE,"fault requires a valid real framebuffer");
            GLint fbo{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);
            Require(fbo!=0,"fault reached the default framebuffer");
            active->failedFramebuffer=static_cast<GLuint>(fbo);
            return GL_FRAMEBUFFER_INCOMPLETE_ATTACHMENT;
        }
        return status;
    }
    unsigned remaining;
    PFNGLCHECKFRAMEBUFFERSTATUSPROC saved{};
    static DetailFramebufferFault* active;
};
DetailFramebufferFault* DetailFramebufferFault::active{};

static std::string Fixture(const std::string& off="0",const std::string& shader="default",float bias=0,bool same=false) {
    std::ostringstream s;s<<"MILKDROP_PRESET_VERSION=201\nPSVERSION=2\nPSVERSION_WARP="<<(shader=="default"?0:2)<<"\nPSVERSION_COMP=0\n[preset00]\n"
        <<"fDecay=1\nfGammaAdj=1\nfShader=0\nfVideoEchoAlpha=0\nfWaveAlpha=0\nob_size=0\nib_size=0\nbDarkenCenter=0\n"
        <<"bBrighten=0\nbDarken=0\nbSolarize=0\nbInvert=0\nfWarpScale=1\nnMotionVectorsX=2\nnMotionVectorsY=2\n"
        <<"mv_dx=.3\nmv_dy=-.3\nmv_l=1\nmv_a=1\nmv_r=1\nmv_g=0\nmv_b=0\n"
        <<"per_frame_init_1=reg00=0;reg01=0;\n"
        <<"per_frame_1=q1=.5+"<<bias<<"+.0625*"<<(same?"1":"max(1,min(4,frame))")<<";q2=equal(frame,2);dx=.5-q1;dy=0;zoom=1;zoomexp=1;sx=1;sy=1;rot=0;warp=0;reg01+=1;\n"
        <<"per_frame_2=mv_a=if("<<off<<",0,1);\nper_pixel_1=reg00+=1;\n";
    for(int i=0;i<4;++i)s<<"wavecode_"<<i<<"_enabled=0\nshapecode_"<<i<<"_enabled=0\n";
    if(shader=="custom")s<<"warp_1=`shader_body { ret=GetPixel(uv);ret.z=.25; }\n";
    if(shader=="fallback")s<<"warp_1=`missing_entry_point { ret=GetPixel(uv); }\n";
    if(shader=="output")s<<"warp_1=`shader_body { _mv_tex_coords.xy=float2(q1,.5);ret=float3(.25,q1,.5); }\n";
    if(shader=="discard")s<<"warp_1=`shader_body { if(q2>.5) { clip(uv.x-.7); } _mv_tex_coords.xy=float2(q1,.5);ret=float3(.25,q1,.5); }\n";
    return s.str();
}
static void Configure(libprojectM::ProjectM& e,bool detail) {
    e.SetWindowSize(detail?768:256,detail?432:144);e.SetMeshSize(48,32);e.SetTargetFramesPerSecond(30);
    e.SetDirectOutput(false);e.SetFeedbackDetail(detail?0.f:-1.f);e.SetLineReferenceSize(detail?256:0,detail?144:0);
    e.SetPresetLocked(true);e.SetHardCutEnabled(false);e.SetEasterEgg(0);e.SetPresetStartClean(true);
}
static void Load(libprojectM::ProjectM& e,const std::string& text,bool smooth=false) {std::istringstream s(text);e.LoadPresetData(s,smooth);}
static void Render(libprojectM::ProjectM& e,Target& out,int w,int h) {
    records.clear();published.clear();warpInvalidations=0;
    e.SetFrameTime(Access::EngineFrame(e)/30.0);out.Bind(w,h);GLint fbo{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&fbo);
    observe=true;try{e.RenderFrame(fbo);}catch(...){observe=false;throw;}observe=false;
    GLint draw{},viewport[4]{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);glGetIntegerv(GL_VIEWPORT,viewport);
    Require(draw==fbo&&viewport[2]==w&&viewport[3]==h,"pipeline did not restore caller output/viewport");
    GLint attached{};glGetFramebufferAttachmentParameteriv(GL_DRAW_FRAMEBUFFER,GL_COLOR_ATTACHMENT1,GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME,&attached);
    Require(attached==0,"UV attachment leaked into caller output");
    Require(glGetError()==GL_NO_ERROR,"full pipeline GL error");
}
static void Temporal(const std::string& off,const std::string& shader,bool detail,bool same=false) {
    Target out(768,432);libprojectM::ProjectM e;Configure(e,detail);Load(e,Fixture(off,shader,0,same));auto& p=Access::Active(e);owners={&p};
    std::array<float,2> previous{};std::shared_ptr<Texture> lease;
    for(int f=0;f<7;++f) {
        Render(e,out,detail?768:256,detail?432:144);
        Require(published.size()==1,"latest completed frame did not publish exactly one real UV producer");
#ifdef USE_GLES
        Require(warpInvalidations==1,"non-discard warp changed actual UV invalidation routing");
#endif
        Require(published[0].owner==&p,"producer belongs to different preset");
        const bool hidden=*Access::Frame(p).mv_a<.0001||static_cast<int>(*Access::Frame(p).mv_x)<=0||static_cast<int>(*Access::Frame(p).mv_y)<=0;
        Require(records.size()==size_t(f==0||hidden?0:detail?2:1),"first-frame/visibility/consumer count changed");
        for(const auto& r:records) {
            Require(r.texture==GLint(lease->TextureID()),"consumer sampled wrong previous lease");
            auto end=MotionEnd(r);Near(end[0],previous[0],"consumer did not use actual previous completed UV",6e-4);
            Near(end[1],previous[1],"consumer previous UV row changed",6e-4);
        }
        const float ideal=.5f+.0625f*(same?1:std::max(1,std::min(4,f)));
        Near(published[0].center[0],ideal,"actual producer center generation changed",6e-4);
        Near(published[0].center[1],.5f,"actual producer center Y changed",6e-4);
        if(shader=="custom")Near(published[0].colorCenter[2],.25f,"requested custom warp silently fell back",.005f);
        if(shader=="fallback")Near(published[0].colorCenter[2],0.f,"malformed custom warp did not fall back to seeded black default",.005f);
        if(shader=="output") {Near(published[0].colorCenter[0],.25f,"actual custom color fragment fell back",.005f);Near(published[0].colorCenter[1],ideal,"color/UV outputs routed incorrectly",.005f);}
        Require(Access::State(p).globalRegisters[0]==double(f+1)*1617,"per-pixel equations repeated or omitted");
        Require(Access::State(p).globalRegisters[1]==f+1,"per-frame equations repeated or omitted");
        auto current=Access::UV(p);if(lease)Require(current==lease,"fixed-generation UV lease replaced");lease=current;previous=published[0].center;
        std::cout<<"temporal frame="<<f<<" shader="<<shader<<" detail="<<detail<<" off="<<off<<" uv="<<lease->Width()<<'x'<<lease->Height()<<" published="<<previous[0]<<','<<previous[1]<<" consumers="<<records.size()<<'\n';
    }
    owners.clear();
}
static void Discard(bool detail) {
    Target out(768,432);libprojectM::ProjectM e;Configure(e,detail);Load(e,Fixture("1","discard"));auto& p=Access::Active(e);owners={&p};
    std::array<float,2> prior{};
    for(int f=0;f<4;++f) {
        Render(e,out,detail?768:256,detail?432:144);Require(published.size()==1,"disabled discard warp missing real UV MRT");

#ifdef USE_GLES
        Require(warpInvalidations==0,"clip producer invalidated defined previous UV storage");
#endif
        auto& got=published[0];const float ideal=.5f+.0625f*std::max(1,std::min(4,f));
        if(f==2) {
            Near(got.center[0],prior[0],"clip-discard overwrote previously defined UV pixel",6e-4);
            Near(got.right[0],ideal,"non-discarded fragment failed to publish current custom UV",6e-4);
            // Color0 is alternating feedback storage; do not equate it to UV's single-lease age.
        } else {
            Near(got.center[0],ideal,"discard fixture custom output not active",6e-4);
            Near(got.colorCenter[0],.25f,"discard fixture color fragment fell back",.005f);
        }
        prior=got.center;Require(records.empty(),"all-disabled discard fixture drew vectors");
    }
    owners.clear();
}
static void CountsOff(bool x,bool detail,bool alpha=false) {
    auto text=Fixture();text+="per_frame_3=mv_"+std::string(alpha?"a":x?"x":"y")+
        (alpha?"=if(equal(frame,2),.00009,.0001);\n":"=if(equal(frame,2),0,2);\n");
    Target out(768,432);libprojectM::ProjectM e;Configure(e,detail);Load(e,text);auto& p=Access::Active(e);owners={&p};
    std::array<float,2> previous{};std::shared_ptr<Texture> lease;
    for(int f=0;f<4;++f) {
        Render(e,out,detail?768:256,detail?432:144);Require(published.size()==1,"count-off skipped actual producer");
        Require(records.size()==size_t(f==0||f==2?0:detail?2:1),"count-off consumer behavior changed");
        if(f==3)for(const auto& r:records){Require(r.texture==GLint(lease->TextureID()),"count reenable wrong lease");Near(MotionEnd(r)[0],previous[0],"count reenable used stale/current field",6e-4);}
        previous=published[0].center;lease=Access::UV(p);
    }
    owners.clear();
}
static void Lifecycle() {
    Target out(768,432);libprojectM::ProjectM e;Configure(e,false);Load(e,Fixture());auto& p=Access::Active(e);owners={&p};
    Render(e,out,256,144);Require(records.empty()&&published.size()==1,"initial first-frame guard failed");
    auto original=Access::UV(p);Render(e,out,256,144);Require(records.size()==1,"warm native consumer missing");
    p.DrawInitialImage(p.OutputTexture(),Access::State(p).renderContext);
    Render(e,out,256,144);Require(records.empty()&&published.size()==1,"initial image did not suppress previous UV consumer");
    Render(e,out,256,144);Require(records.size()==1,"initial image successor failed to consume completed map");
    e.SetWindowSize(512,288);Render(e,out,512,288);auto resized=Access::UV(p);
    Require(records.empty()&&resized!=original&&published.size()==1,"resize did not suppress old map consumer");
    Render(e,out,512,288);Require(records.size()==1&&records[0].texture==GLint(resized->TextureID()),"resize successor wrong map");
    e.SetLineReferenceSize(256,144);e.SetFeedbackDetail(0);Render(e,out,512,288);auto authored=Access::UV(p);
    Require(records.empty()&&authored!=resized&&published.size()==1&&Access::Detail(p),"authored entry used stale native map");
    Render(e,out,512,288);Require(records.size()==2,"authored native/canvas consumers missing");
    e.SetFeedbackDetail(.5f);Render(e,out,512,288);Require(records.empty()&&Access::Detail(p)&&published.size()==1,"gain class rebuild first-frame guard failed");
    // At unchanged canvas size the TextureAttachment legitimately retains the same UV lease.
    e.SetFeedbackDetail(-1);Render(e,out,512,288);auto native=Access::UV(p);
    Require(records.empty()&&native!=authored&&!Access::Detail(p)&&published.size()==1,"native return stale canvas consumer");
    e.SetFeedbackDetail(0);Access::DetailFailure(p);Render(e,out,512,288);
    Require(!Access::Detail(p)&&published.size()==1&&Access::UV(p)==native,"detail failure did not retain native producer");
    e.SetMeshSize(8,6);uint32_t acceptedX{},acceptedY{};e.MeshSize(acceptedX,acceptedY);
    Require(acceptedX==8&&acceptedY==8,"public mesh minimum contract changed");
    const double before=Access::State(p).globalRegisters[0];Render(e,out,512,288);
    Require(Access::State(p).globalRegisters[0]==before+(acceptedX+1)*(acceptedY+1)&&published.size()==1,"mesh resize repeated/missed equations");
    // Grid changes retain the compatible previous normalized field; no first-frame reset is
    // introduced. Consumer still precedes mesh replacement/current publication.
    auto old=&p;auto held=Access::UV(p);Load(e,Fixture("0","output",-.0625f));auto& next=Access::Active(e);owners={&next};
    Require(&next!=old&&Access::UV(next)!=held,"new preset inherited outgoing UV ownership");
    Render(e,out,512,288);Require(records.empty()&&published.size()==1,"hard-cut first-frame guard failed");
    owners.clear();
}
static void PartialFailure() {
    for(float gain:{0.0f,.5f}) {
        Target out(512,288);libprojectM::ProjectM e;Configure(e,false);Load(e,Fixture());
        auto& p=Access::Active(e);owners={&p};Render(e,out,256,144);Render(e,out,256,144);
        e.SetWindowSize(512,288);Render(e,out,512,288);Render(e,out,512,288);
        auto native=Access::UV(p);e.SetLineReferenceSize(256,144);e.SetFeedbackDetail(gain);
        GLuint failed{};
        {
            // Standard fails the first canvas check; High fails its native-detail
            // framebuffer after all three canvas checks succeeded.
            DetailFramebufferFault fault(gain>0?4:1);Render(e,out,512,288);failed=fault.failedFramebuffer;
            Require(failed&&!Access::Detail(p)&&published.size()==1&&Access::UV(p)==native,
                    "partial detail failure did not retain the native producer");
        }
        Require(glIsFramebuffer(failed)==GL_FALSE,"failed detail framebuffer survived constructor unwind");
        const auto previous=ReadUV(native);Render(e,out,512,288);
        Require(records.size()==1&&published.size()==1&&!Access::Detail(p),"failed detail did not continue native rendering");
        Near(MotionEnd(records[0])[0],previous[0],"failure successor did not consume latest completed native map",6e-4);
        Require(glGetError()==GL_NO_ERROR,"partial detail failure leaked GL error state");owners.clear();
    }
}
static void Transition(uint32_t divisor) {
    Target out(256,144);libprojectM::ProjectM e;Configure(e,false);e.SetOutgoingPresetFrameDivisor(divisor);Load(e,Fixture());auto& old=Access::Active(e);owners={&old};
    Render(e,out,256,144);Render(e,out,256,144);auto oldUV=Access::UV(old);
    Load(e,Fixture("0","output",-.0625f),true);auto* incoming=Access::Incoming(e);Require(incoming,"smooth switch did not create second instance");owners={&old,incoming};
    auto newUV=Access::UV(*incoming);Require(newUV!=oldUV,"transition shares UV storage");
    Render(e,out,256,144);Require(published.size()==2,"transition did not publish both instance fields");
    Require(records.size()==1&&records[0].texture==GLint(oldUV->TextureID()),"incoming first-frame guard or outgoing ownership failed");
    for(int i=0;i<2;++i) {
        const auto a=ReadUV(oldUV),b=ReadUV(newUV);const bool oldRenders=Access::EngineFrame(e)%divisor==0;
        const double oldFrames=Access::State(old).globalRegisters[1];
        Render(e,out,256,144);Require(published.size()==size_t(oldRenders?2:1)&&records.size()==size_t(oldRenders?2:1),"transition instance render counts changed");
        Require(Access::State(old).globalRegisters[1]==oldFrames+(oldRenders?1:0),"throttled outgoing repeated/missed frame equations");
        if(!oldRenders){const auto held=ReadUV(oldUV);Near(held[0],a[0],"throttled outgoing replaced unrendered field",6e-4);}
        for(const auto& r:records) {const auto expected=r.texture==GLint(oldUV->TextureID())?a:b;Require(r.texture==GLint(oldUV->TextureID())||r.texture==GLint(newUV->TextureID()),"transition consumer unknown lease");Near(MotionEnd(r)[0],expected[0],"transition mixed current/other-instance field",6e-4);}
    }
    owners.clear();
}
int main(int argc,char** argv) {try {
    Require(argc==2,"usage: motion-uv-freshness temporal|producer|lifecycle|transition|context");const std::string mode=argv[1];
    auto run=[&]() {GLContext gl;Hooks tf;ProducerObserver producer;
        if(mode=="temporal")for(bool detail:{false,true})for(const auto& shader:{"default","custom","fallback","output"}) {
            for(const auto& off:{"0","1","equal(frame,2)","above(frame,1)*below(frame,5)"})Temporal(off,shader,detail);
            Temporal("equal(frame,2)",shader,detail,true);CountsOff(true,detail);CountsOff(false,detail);CountsOff(false,detail,true);
        }
        else if(mode=="producer")for(bool detail:{false,true})Discard(detail);
        else if(mode=="lifecycle"){Lifecycle();PartialFailure();}
        else if(mode=="transition"){Transition(1);Transition(2);}
        else if(mode=="context")Temporal("equal(frame,2)","output",false);
        else throw std::runtime_error("unknown mode");
    };
    run();if(mode=="context")run(); // Destroy every engine/resource before destroying each GL context.
    std::cout<<"actual motion UV "<<mode<<" controls pass; Native pixels/cost remain separate\n";return 0;
} catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}}
