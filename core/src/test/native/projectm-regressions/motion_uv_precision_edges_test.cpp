// TEST-ONLY proposal. Include immutable controls-v2 for real pipeline/TF observation.
#ifndef COMPATIBILITY_CONTROL_SOURCE
#define COMPATIBILITY_CONTROL_SOURCE "motion_uv_freshness_test.cpp"
#endif
#define main projectmtvOriginalCompatibilityMain
#include COMPATIBILITY_CONTROL_SOURCE
#undef main
#include <limits>

static std::array<uint16_t,2> ReadWords(const std::shared_ptr<Texture>& t,int x,int y) {
    Require(allocatedFormats[t->TextureID()]==GL_RG16UI,"precision control requires actual RG16UI storage");
    GLint read{},draw{};glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);
    GLuint fbo{};glGenFramebuffers(1,&fbo);glBindFramebuffer(GL_FRAMEBUFFER,fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,t->TextureID(),0);
    Require(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"integer read FBO incomplete");
    glReadBuffer(GL_COLOR_ATTACHMENT0);std::array<GLuint,4> words{};
    glReadPixels(x,y,1,1,GL_RGBA_INTEGER,GL_UNSIGNED_INT,words.data());
    glBindFramebuffer(GL_READ_FRAMEBUFFER,read);glBindFramebuffer(GL_DRAW_FRAMEBUFFER,draw);glDeleteFramebuffers(1,&fbo);
    Require(glGetError()==GL_NO_ERROR,"actual integer-word read GL error");
    Require(words[0]<=65535u&&words[1]<=65535u,"integer storage exceeded half-word range");
    return {uint16_t(words[0]),uint16_t(words[1])};
}
static std::string CoordinatesFixture(const std::string& coordinates,bool disabled=true) {
    auto text=Fixture(disabled?"1":"0","output");text.erase(text.find("warp_1="));
    text+="warp_1=`shader_body { _mv_tex_coords.xy="+coordinates+";ret=float3(.25,.5,.75); }\n";return text;
}
class CoordinateUniform {
public:
    explicit CoordinateUniform(std::array<float,2> xy):values(xy){Require(!active,"nested uniform injection");active=this;saved=glad_glUniform4fv;glad_glUniform4fv=Set;}
    ~CoordinateUniform(){glad_glUniform4fv=saved;active=nullptr;}
    unsigned submitted{};
private:
    static void Set(GLint location,GLsizei count,const GLfloat* input){
        GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);
        if(count==1&&location>=0&&location==glGetUniformLocation(program,"_qa")){
            std::array<GLfloat,4> value{active->values[0],active->values[1],input[2],input[3]};
            active->saved(location,count,value.data());++active->submitted;
            // Query the real submitted values; NaN payload/sign is deliberately not required.
            std::array<GLfloat,4> actual{};glGetUniformfv(program,location,actual.data());
            for(int i=0;i<2;++i)Require(std::isnan(active->values[i])?std::isnan(actual[i]):actual[i]==active->values[i],"driver did not receive requested real coordinate uniform");
        }else active->saved(location,count,input);
    }
    std::array<float,2> values;
    PFNGLUNIFORM4FVPROC saved{};
    static CoordinateUniform* active;
};
CoordinateUniform* CoordinateUniform::active{};
static void FinitePrecision() {
    struct Case{std::array<float,2> values;std::array<uint16_t,2> expected;};
    // Precomputed IEEE binary16 words: distinct from the production GLSL codec.
    const std::array<Case,5> cases{{{{.50048828125f,-2.001953125f},{0x3801,0xc001}},
                                  {{.1234567f,-3.1415925f},{0x2fe7,0xc248}},
                                  {{1.0007f,-.0001234f},{0x3c01,0x880b}},
                                  {{65504.f,-65504.f},{0x7bff,0xfbff}},
                                  {{0.f,-0.f},{0x0000,0x8000}}}};
    for(bool detail:{false,true})for(const auto& test:cases){
        Target out(768,432);libprojectM::ProjectM e;Configure(e,detail);Load(e,CoordinatesFixture("float2(q1,q2)"));auto& p=Access::Active(e);owners={&p};
        CoordinateUniform values(test.values);Render(e,out,detail?768:256,detail?432:144);
        Require(values.submitted>0&&records.empty()&&published.size()==1,"actual finite uniform/producer/first-frame guard absent");
        auto texture=Access::UV(p);auto words=ReadWords(texture,texture->Width()/2,texture->Height()/2);
        Require(words==test.expected,"actual packed fragment lost binary16 precision/rounding/range/sign");
        Near(published[0].colorCenter[0],.25f,"finite coordinate words changed primary color",.005f);
        std::cout<<"actual finite-half detail="<<detail<<" words="<<words[0]<<','<<words[1]<<'\n';owners.clear();
    }
}
static void NonfiniteClasses(){
    uint32_t nanBits=0x7fc12345u;float nan{};std::memcpy(&nan,&nanBits,4);
    for(bool detail:{false,true})for(float infinity:{std::numeric_limits<float>::infinity(),-std::numeric_limits<float>::infinity()}){
        Target out(768,432);libprojectM::ProjectM e;Configure(e,detail);Load(e,CoordinatesFixture("float2(q1,q2)"));auto& p=Access::Active(e);owners={&p};
        // Set real actual-program uniforms instead of using undefined GLSL division/sqrt.
        CoordinateUniform values({infinity,nan});Render(e,out,detail?768:256,detail?432:144);
        Require(values.submitted>0&&records.empty()&&published.size()==1,"actual nonfinite uniform/producer absent");
        auto texture=Access::UV(p);auto words=ReadWords(texture,texture->Width()/2,texture->Height()/2);
        Require(words[0]==uint16_t(std::signbit(infinity)?0xfc00:0x7c00),"actual infinity sign/class was sanitized or clipped");
        Require((words[1]&0x7c00u)==0x7c00u&&(words[1]&0x03ffu)!=0,"actual NaN class was sanitized or clipped");
        Near(published[0].colorCenter[0],.25f,"nonfinite coordinate words changed primary color",.005f);
        std::cout<<"actual nonfinite-half detail="<<detail<<" words="<<words[0]<<','<<words[1]<<'\n';owners.clear();
    }
}
struct ExpectedEdge{GLint program{};GLuint texture{};std::array<float,2> start{},endpoint{};};
static std::vector<ExpectedEdge> expectedEdges;
static std::shared_ptr<Texture> previousEdgeTexture;
static std::array<float,2> SubmittedStart(GLint first){
    GLint enabled{},buffer{},stride{},length{},old{};void* pointer{};
    glGetVertexAttribiv(0,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);Require(enabled,"actual motion start attribute disabled");
    glGetVertexAttribiv(0,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&buffer);glGetVertexAttribiv(0,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&stride);
    glGetVertexAttribPointerv(0,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&old);
    Require(buffer&&stride>0,"actual motion start VBO absent");glBindBuffer(GL_ARRAY_BUFFER,buffer);glGetBufferParameteriv(GL_ARRAY_BUFFER,GL_BUFFER_SIZE,&length);
    const size_t offset=reinterpret_cast<std::uintptr_t>(pointer)+static_cast<size_t>(first)*stride;
    Require(offset+2*sizeof(float)<=static_cast<size_t>(length),"actual motion start outside submitted VBO");
    const auto* bytes=static_cast<const unsigned char*>(glMapBufferRange(GL_ARRAY_BUFFER,0,length,GL_MAP_READ_BIT));Require(bytes,"actual start VBO read failed");
    std::array<float,2> start{};std::memcpy(start.data(),bytes+offset,2*sizeof(float));Require(glUnmapBuffer(GL_ARRAY_BUFFER)==GL_TRUE,"actual start VBO invalidated");
    glBindBuffer(GL_ARRAY_BUFFER,old);return start;
}
static void ObserveEdge(GLint first){
    GLint program{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);if(glGetUniformLocation(program,"warp_coordinates")<0)return;
    Require(bool(previousEdgeTexture),"previous completed UV lease missing");
    ExpectedEdge expected;expected.program=program;expected.texture=previousEdgeTexture->TextureID();expected.start=SubmittedStart(first);
    GLint bound{};glGetIntegerv(GL_TEXTURE_BINDING_2D,&bound);Require(bound==GLint(expected.texture),"edge consumer did not bind previous completed storage");
    // Expected values come exclusively from actual stored integer texels before this consumer,
    // using the actual submitted start. This CPU interpolation does not generate a UV field.
    const int w=previousEdgeTexture->Width(),h=previousEdgeTexture->Height();
    const double px=double(expected.start[0])*w-.5,py=(1.0-double(expected.start[1]))*h-.5;
    const int x=int(std::floor(px)),y=int(std::floor(py));const double fx=px-x,fy=py-y;
    Require(px<0||px>w-1||py<0||py>h-1,"edge fixture did not reach CLAMP_TO_EDGE interval");
    std::array<std::array<float,2>,4> texels{};
    for(int j=0;j<2;++j)for(int i=0;i<2;++i){auto words=ReadWords(previousEdgeTexture,std::max(0,std::min(w-1,x+i)),std::max(0,std::min(h-1,y+j)));texels[j*2+i]={HalfValue(words[0]),HalfValue(words[1])};}
    for(int c=0;c<2;++c)expected.endpoint[c]=float((1-fy)*((1-fx)*texels[0][c]+fx*texels[1][c])+fy*((1-fx)*texels[2][c]+fx*texels[3][c]));
    float minimum{};glGetUniformfv(program,glGetUniformLocation(program,"minimum_length"),&minimum);
    Require(std::hypot(expected.endpoint[0]-expected.start[0],expected.endpoint[1]-expected.start[1])>minimum,"edge oracle reached minimum-length adjustment");
    expectedEdges.push_back(expected);
}
class EdgeObserver{
public:
    EdgeObserver(){Require(!active,"nested edge observer");active=this;elements=glad_glDrawElements;instanced=glad_glDrawArraysInstanced;glad_glDrawElements=ElementsEdge;glad_glDrawArraysInstanced=InstancedEdge;}
    ~EdgeObserver(){glad_glDrawElements=elements;glad_glDrawArraysInstanced=instanced;active=nullptr;}
private:
    static void ElementsEdge(GLenum mode,GLsizei count,GLenum type,const void* indices){if(observe&&mode==GL_LINES){Require(count==2,"edge fixture must submit one real line");ObserveEdge(0);}active->elements(mode,count,type,indices);}
    static void InstancedEdge(GLenum mode,GLint first,GLsizei count,GLsizei instances){if(observe){Require(mode==GL_TRIANGLE_STRIP&&instances==1,"edge fixture must submit one real quad");ObserveEdge(first);}active->instanced(mode,first,count,instances);}
    PFNGLDRAWELEMENTSPROC elements{};PFNGLDRAWARRAYSINSTANCEDPROC instanced{};static EdgeObserver* active;
};
EdgeObserver* EdgeObserver::active{};
static void ClampEdges(){
    const std::array<std::array<float,2>,4> positions{{{.0002f,.4375f},{.9998f,.4375f},{.4375f,.0002f},{.4375f,.9998f}}};
    EdgeObserver edge;
    for(bool detail:{false,true})for(const auto& position:positions){
        auto text=CoordinatesFixture("float2(-2.0+6.0*uv_orig.x,-4.0+10.0*uv_orig.y)",false);
        std::ostringstream grid;grid<<std::setprecision(9)<<"per_frame_3=mv_x=1;mv_y=1;mv_dx="<<position[0]-1.f<<";mv_dy="<<1.f-position[1]<<";\n";text+=grid.str();
        Target out(768,432);libprojectM::ProjectM e;Configure(e,detail);Load(e,text);auto& p=Access::Active(e);owners={&p};
        expectedEdges.clear();Render(e,out,detail?768:256,detail?432:144);Require(expectedEdges.empty(),"first-frame edge consumer not suppressed");previousEdgeTexture=Access::UV(p);
        expectedEdges.clear();Render(e,out,detail?768:256,detail?432:144);Require(records.size()==size_t(detail?2:1)&&expectedEdges.size()==records.size(),"actual edge consumer/expectation count changed");
        for(size_t i=0;i<records.size();++i){const auto& expected=expectedEdges[i];Require(records[i].program==expected.program&&records[i].texture==GLint(expected.texture),"edge expectation paired to different production shader/storage");const auto actual=MotionEnd(records[i]);Near(actual[0],expected.endpoint[0],"actual decoded CLAMP_TO_EDGE/bilinear U changed",.002f);Near(actual[1],expected.endpoint[1],"actual decoded CLAMP_TO_EDGE/bilinear V changed",.002f);std::cout<<"actual edge detail="<<detail<<" start="<<expected.start[0]<<','<<expected.start[1]<<" expected="<<expected.endpoint[0]<<','<<expected.endpoint[1]<<" TF="<<actual[0]<<','<<actual[1]<<'\n';}
        previousEdgeTexture.reset();owners.clear();
    }
}
class GLES30Capability {
public:
    GLES30Capability(){Require(!active,"nested GLES version mask");active=this;saved=glad_glGetIntegerv;glad_glGetIntegerv=Get;}
    ~GLES30Capability(){glad_glGetIntegerv=saved;active=nullptr;}
private:
    static void Get(GLenum name,GLint* value){active->saved(name,value);if(name==GL_MAJOR_VERSION)*value=3;if(name==GL_MINOR_VERSION)*value=0;}
    PFNGLGETINTEGERVPROC saved{};static GLES30Capability* active;
};
GLES30Capability* GLES30Capability::active{};
int main(int argc,char** argv){try{
    Require(argc==2,"usage: motion-uv-precision-edges fractional|nonfinite|edge");const std::string mode=argv[1];
#ifndef USE_GLES
    throw std::runtime_error("supplementary packed controls require actual GLES3");
#endif
    GLContext gl;Hooks tf;FormatObserver formats;ProducerObserver producer;GLES30Capability gles30;hideFloatExtensions=true;rejectFloatMRT=false;requirePacked=true;
    if(mode=="fractional")FinitePrecision();else if(mode=="nonfinite")NonfiniteClasses();else if(mode=="edge")ClampEdges();else throw std::runtime_error("unknown mode");
    std::cout<<"actual packed motion UV "<<mode<<" supplementary controls pass\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
