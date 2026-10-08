// Source-only prepared CGL production controls. Not built or executed by the owner.
// Uses the existing projectm-regressions gl_context.hpp and patched engine APIs.
#include "gl_context.hpp"
#include <MilkdropPreset/CustomShape.hpp>
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/VideoEcho.hpp>
#include <MilkdropPreset/FinalComposite.hpp>
#include <MilkdropPreset/GeometryTargets.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/LineGeometry.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <Renderer/Texture.hpp>
#include <Renderer/TextureManager.hpp>
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <limits>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
using RGBA=std::array<float,4>;
static void Check(bool value,const std::string&message){if(!value)throw std::runtime_error(message);}
static bool Near(float a,float b){return std::abs(a-b)<=2e-6f;}
static unsigned GeometryByte(double channel){Check(std::isfinite(channel)&&channel>=0&&channel<=1,"bounded original geometry channel");return unsigned(int(channel*255.0))&255u;}
static unsigned DisplayByte(float channel){const float scaled=channel*255.f;Check(std::isfinite(scaled)&&double(scaled)>=double(std::numeric_limits<int>::min())&&double(scaled)<=double(std::numeric_limits<int>::max()),"defined int32 original display product");return unsigned(int(scaled))&255u;}
static float Normalized(unsigned byte){return float(byte)/255.f;}
static RGBA QuantGeometry(const RGBA&rgba){RGBA out{};for(size_t i=0;i<4;++i)out[i]=Normalized(GeometryByte(rgba[i]));return out;}
struct Surface {
 std::shared_ptr<Texture> texture;GLuint fbo{};int size;
 explicit Surface(int pixels):texture(std::make_shared<Texture>("owner",GL_TEXTURE_2D,pixels,pixels,1,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE,false)),size(pixels){glGenFramebuffers(1,&fbo);Bind();glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture->TextureID(),0);Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"owner FBO");}
 ~Surface(){glDeleteFramebuffers(1,&fbo);}
 void Bind(){glBindFramebuffer(GL_FRAMEBUFFER,fbo);glViewport(0,0,size,size);}
 void Clear(float r=0,float g=0,float b=0){Bind();glClearColor(r,g,b,1);glClear(GL_COLOR_BUFFER_BIT);}
 std::vector<unsigned char> Pixels()const{GLint previous{};glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&previous);glBindFramebuffer(GL_READ_FRAMEBUFFER,fbo);glPixelStorei(GL_PACK_ALIGNMENT,1);std::vector<unsigned char> out(size*size*4);glReadPixels(0,0,size,size,GL_RGBA,GL_UNSIGNED_BYTE,out.data());glBindFramebuffer(GL_READ_FRAMEBUFFER,GLuint(previous));Check(glGetError()==GL_NO_ERROR,"explicit owner read target");return out;}
 void Ppm(const std::filesystem::path&path)const{const auto data=Pixels();std::ofstream out(path,std::ios::binary);Check(bool(out),"PPM open");out<<"P6\n"<<size<<" "<<size<<"\n255\n";for(int y=size-1;y>=0;--y)for(int x=0;x<size;++x)out.write(reinterpret_cast<const char*>(data.data()+(y*size+x)*4),3);Check(bool(out),"PPM write");}
};
static std::vector<unsigned char> BufferBytes(GLenum target,GLuint id){GLint previous{};glGetIntegerv(target==GL_ARRAY_BUFFER?GL_ARRAY_BUFFER_BINDING:GL_ELEMENT_ARRAY_BUFFER_BINDING,&previous);glBindBuffer(target,id);GLint size{};glGetBufferParameteriv(target,GL_BUFFER_SIZE,&size);Check(size>0,"nonempty producer buffer");const auto*data=static_cast<const unsigned char*>(glMapBufferRange(target,0,size,GL_MAP_READ_BIT));Check(data,"producer buffer mapping");std::vector<unsigned char> out(data,data+size);Check(glUnmapBuffer(target)==GL_TRUE,"producer buffer unmap");glBindBuffer(target,GLuint(previous));return out;}
struct Attribute {
 GLuint buffer{};size_t offset{},stride{};GLint components{},divisor{};
 std::vector<unsigned char> bytes;
 Attribute(GLuint location){GLint enabled{},type{},bufferId{},strideBytes{};void*pointer{};glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_ENABLED,&enabled);Check(enabled==GL_TRUE,"producer attribute must be enabled");glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_TYPE,&type);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_SIZE,&components);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_STRIDE,&strideBytes);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_BUFFER_BINDING,&bufferId);glGetVertexAttribiv(location,GL_VERTEX_ATTRIB_ARRAY_DIVISOR,&divisor);glGetVertexAttribPointerv(location,GL_VERTEX_ATTRIB_ARRAY_POINTER,&pointer);Check(type==GL_FLOAT&&bufferId>0,"float producer attribute buffer");buffer=GLuint(bufferId);offset=reinterpret_cast<uintptr_t>(pointer);stride=strideBytes?size_t(strideBytes):size_t(components)*sizeof(float);bytes=BufferBytes(GL_ARRAY_BUFFER,buffer);}
 float Component(size_t row,size_t column)const{Check(column<size_t(components)&&offset+row*stride+(column+1)*sizeof(float)<=bytes.size(),"producer attribute bounds");float value;std::memcpy(&value,bytes.data()+offset+row*stride+column*sizeof(float),sizeof(float));return value;}
 RGBA Color(size_t row)const{Check(components==4,"RGBA producer components");return{Component(row,0),Component(row,1),Component(row,2),Component(row,3)};}
};
struct Record {GLenum primitive{};GLint target{};bool instanced{};std::vector<uint32_t> indices;std::vector<RGBA> colors;};
static PFNGLDRAWARRAYSPROC realArrays{};
static PFNGLDRAWELEMENTSPROC realElements{};
static PFNGLDRAWARRAYSINSTANCEDPROC realInstanced{};
static std::vector<Record>*records{};
struct GridReplay {Surface*output{};std::filesystem::path csv;bool done{};};
static GridReplay*gridReplay{};
static GLint DrawTarget(){GLint target{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&target);return target;}
static Record ArraysRecord(GLenum mode,GLint first,GLsizei count){Record r;r.primitive=mode;r.target=DrawTarget();Attribute color(1);for(int i=0;i<count;++i)r.colors.push_back(color.Color(size_t(first+i)));return r;}
static std::vector<uint32_t> ElementIndices(GLsizei count,GLenum type,const void*offset){Check(count>0,"positive producer index count");Check(type==GL_UNSIGNED_INT,"uint32 engine indices");GLint id{};glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING,&id);const auto bytes=BufferBytes(GL_ELEMENT_ARRAY_BUFFER,GLuint(id));const size_t start=reinterpret_cast<uintptr_t>(offset);Check(start+size_t(count)*4<=bytes.size(),"index range");std::vector<uint32_t> out(count);std::memcpy(out.data(),bytes.data()+start,size_t(count)*4);return out;}
static void Arrays(GLenum mode,GLint first,GLsizei count){if(records)records->push_back(ArraysRecord(mode,first,count));realArrays(mode,first,count);}
static void Instanced(GLenum mode,GLint first,GLsizei count,GLsizei instances){if(records){Record r;r.primitive=mode;r.target=DrawTarget();r.instanced=true;Attribute a(4),b(5);Check(a.divisor==1&&b.divisor==1,"production line colour divisors");for(int i=0;i<instances;++i){r.colors.push_back(a.Color(i));r.colors.push_back(b.Color(i));}records->push_back(std::move(r));}realInstanced(mode,first,count,instances);}
static void Elements(GLenum mode,GLsizei count,GLenum type,const void*offset){
 const auto indices=ElementIndices(count,type,offset);Attribute color(1);
 if(records){Record r;r.primitive=mode;r.target=DrawTarget();r.indices=indices;for(auto i:indices)r.colors.push_back(color.Color(i));records->push_back(std::move(r));}
 if(!gridReplay){realElements(mode,count,type,offset);return;}
 Check(!gridReplay->done&&mode==GL_TRIANGLES,"one completed composite grid draw");
 GLint program{},linked{};glGetIntegerv(GL_CURRENT_PROGRAM,&program);glGetProgramiv(program,GL_LINK_STATUS,&linked);Check(linked==GL_TRUE&&glGetAttribLocation(program,"vertex_color")==1,"hue probe compiled and consumes vertex colour; reject fallback");
 Attribute positions(0),uv(2),radiusAngle(3);Check(positions.components==2&&color.components==4&&color.divisor==0,"composite attribute layout");
 const size_t vertices=*std::max_element(indices.begin(),indices.end())+1;
 std::vector<unsigned char> quantized=color.bytes;bool changed=false;
 std::ofstream csv(gridReplay->csv);Check(bool(csv),"grid CSV open");csv<<std::setprecision(9)<<"vertex,x,y,u,v,rad,ang,r,g,b,a,byte_r,byte_g,byte_b,byte_a\n";
 for(size_t i=0;i<vertices;++i){const auto c=color.Color(i);csv<<i<<','<<positions.Component(i,0)<<','<<positions.Component(i,1)<<','<<uv.Component(i,0)<<','<<uv.Component(i,1)<<','<<radiusAngle.Component(i,0)<<','<<radiusAngle.Component(i,1);for(float v:c)csv<<','<<v;for(size_t channel=0;channel<4;++channel){const auto byte=DisplayByte(c[channel]);const float normalized=Normalized(byte);csv<<','<<byte;changed|=normalized!=c[channel];std::memcpy(quantized.data()+color.offset+i*color.stride+channel*sizeof(float),&normalized,sizeof(float));}csv<<'\n';}
 Check(changed,"completed producer grid has non-byte-exact values");
 std::ofstream topology(gridReplay->csv.string()+".indices.csv");for(auto index:indices)topology<<index<<'\n';Check(bool(topology),"topology CSV write");
 // Baseline uses the real production draw. Replay alters ONLY completed colour
 // vertices, before interpolation; positions/UV/rad/indices/program/uniforms stay.
 realElements(mode,count,type,offset);
 const auto positionBefore=positions.bytes,uvBefore=uv.bytes,angleBefore=radiusAngle.bytes;
 GLint draw{},array{};glGetIntegerv(GL_DRAW_FRAMEBUFFER_BINDING,&draw);glGetIntegerv(GL_ARRAY_BUFFER_BINDING,&array);
 glBindBuffer(GL_ARRAY_BUFFER,color.buffer);glBufferSubData(GL_ARRAY_BUFFER,0,quantized.size(),quantized.data());
 glBindFramebuffer(GL_DRAW_FRAMEBUFFER,gridReplay->output->fbo);realElements(mode,count,type,offset);
 glBindBuffer(GL_ARRAY_BUFFER,color.buffer);glBufferSubData(GL_ARRAY_BUFFER,0,color.bytes.size(),color.bytes.data());glBindBuffer(GL_ARRAY_BUFFER,GLuint(array));glBindFramebuffer(GL_DRAW_FRAMEBUFFER,GLuint(draw));
 Check(BufferBytes(GL_ARRAY_BUFFER,positions.buffer)==positionBefore&&BufferBytes(GL_ARRAY_BUFFER,uv.buffer)==uvBefore&&BufferBytes(GL_ARRAY_BUFFER,radiusAngle.buffer)==angleBefore,"quantized replay changed non-colour data");
 Check(ElementIndices(count,type,offset)==indices,"quantized replay changed index topology");Check(BufferBytes(GL_ARRAY_BUFFER,color.buffer)==color.bytes,"restore production colour buffer after replay");
 gridReplay->done=true;
}
struct Hook {
 Hook(std::vector<Record>*out=nullptr,GridReplay*replay=nullptr){Check(!records&&!gridReplay,"no nested producer hook");realArrays=glad_glDrawArrays;realElements=glad_glDrawElements;realInstanced=glad_glDrawArraysInstanced;records=out;gridReplay=replay;glad_glDrawArrays=Arrays;glad_glDrawElements=Elements;glad_glDrawArraysInstanced=Instanced;}
 ~Hook(){glad_glDrawArrays=realArrays;glad_glDrawElements=realElements;glad_glDrawArraysInstanced=realInstanced;records=nullptr;gridReplay=nullptr;}
};
static void Configure(PresetState&state,ShaderCache&cache,int size=128){auto&rc=state.renderContext;rc.shaderCache=&cache;rc.viewportSizeX=rc.viewportSizeY=size;rc.lineReferenceWidth=rc.lineReferenceHeight=64;rc.aspectX=rc.aspectY=rc.invAspectX=rc.invAspectY=1;rc.perPixelMeshX=48;rc.perPixelMeshY=32;rc.fps=30;rc.time=.5f;state.hueRandomOffsets.fill(0);state.LoadShaders();Check(state.lineRenderer.Usable(),"requires actual production Native line program");}
static std::vector<unsigned char> FramebufferPixels(Framebuffer&fbo,int size){GLint previous{};glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&previous);fbo.BindRead(0);std::vector<unsigned char> pixels(size*size*4);glReadPixels(0,0,size,size,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());glBindFramebuffer(GL_READ_FRAMEBUFFER,GLuint(previous));Check(glGetError()==GL_NO_ERROR,"geometry explicit read target");return pixels;}
static void Ppm(const std::filesystem::path&file,const std::vector<unsigned char>&pixels,int size){std::ofstream out(file,std::ios::binary);Check(bool(out),"geometry PPM open");out<<"P6\n"<<size<<" "<<size<<"\n255\n";for(int y=size-1;y>=0;--y)for(int x=0;x<size;++x)out.write(reinterpret_cast<const char*>(pixels.data()+(y*size+x)*4),3);Check(bool(out),"geometry PPM write");}
static void Dump(const std::filesystem::path&file,const std::vector<Record>&out){std::ofstream csv(file);Check(bool(csv),"producer CSV open");csv<<std::setprecision(9)<<"draw,target,primitive,instanced,row,r,g,b,a\n";for(size_t draw=0;draw<out.size();++draw)for(size_t row=0;row<out[draw].colors.size();++row){csv<<draw<<','<<out[draw].target<<','<<out[draw].primitive<<','<<out[draw].instanced<<','<<row;for(float v:out[draw].colors[row])csv<<','<<v;csv<<'\n';}Check(bool(csv),"producer CSV write");}
static void Compare(const RGBA&actual,const RGBA&expected,const std::string&label){for(size_t c=0;c<4;++c)Check(Near(actual[c],expected[c]),label+" channel="+std::to_string(c));}
struct Material {std::string name;RGBA center,edge,border;bool wave{},dots{};};
static const std::vector<Material> materials={
 {"shape-flat",{.5f,.123456f,.75f,.123456f},{.5f,.123456f,.75f,.123456f},{1,1,1,0}},
 {"shape-gradient",{.5f,.123456f,.75f,.5f},{.123456f,.75f,.5f,.123456f},{1,1,1,0}},
 {"shape-border",{0,0,0,0},{0,0,0,0},{.5f,.123456f,.75f,.123456f}},
 {"shape-subbyte-alpha",{1,1,1,.003f},{1,1,1,.003f},{1,1,1,0}},
 {"wave-line",{.5f,.123456f,.75f,.123456f},{},{},true,false},
 {"wave-dots",{.5f,.123456f,.75f,.123456f},{},{},true,true},
 {"shape-border-hdr",{0,0,0,0},{0,0,0,0},{1.25f,.5f,.25f,1}}
};
static void Geometry(const std::filesystem::path&packet,ShaderCache&cache,const std::filesystem::path&out){
 for(const auto&m:materials)for(bool oracle:{false,true}){
  if(m.name=="shape-border-hdr"&&oracle)continue;
  const auto label=m.name=="shape-border-hdr"?std::string("i25-shape-border-hdr-current-probe"):"i25-"+m.name+"-"+(oracle?"byte-source-oracle":"float-current");PresetFileParser parsed;Check(parsed.Read((packet/"fixtures"/(label+".milk")).string()),"real fixture parser");PresetState state;state.Initialize(parsed);Configure(state,cache);
  PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);
  Framebuffer canvas(1),native(1);canvas.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);native.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);canvas.SetSize(64,64);native.SetSize(128,128);GeometryTargets targets(state,canvas,0,64,64,{},native,0);
  native.Bind(0);const GLint nativeId=DrawTarget();glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);targets.Authored();const GLint canvasId=DrawTarget();glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
  std::vector<Record> captured;std::vector<std::string>warnings;
  if(m.wave){state.customWaveInitCode[0]+="reg02+=1;";state.customWavePerFrameCode[0]+="reg00+=1;";state.customWavePerPointCode[0]+="reg01+=1;";CustomWaveform wave(state);wave.Initialize(parsed,0);wave.CompileCodeAndRunInitExpressions(frame,warnings);Check(warnings.empty(),"actual wave compilation");{Hook hook(&captured);wave.Draw(frame,&targets);}Check(state.globalRegisters[0]==1&&state.globalRegisters[1]==2&&state.globalRegisters[2]==1,"wave frame/point/init once despite Native replay");}
  else{state.customShapeInitCode[0]+="reg02+=1;";state.customShapePerFrameCode[0]+="reg00+=1;";CustomShape shape(state);shape.Initialize(parsed,0);shape.CompileCodeAndRunInitExpressions(warnings);Check(warnings.empty(),"actual shape compilation");{Hook hook(&captured);shape.Draw(&targets);}Check(state.globalRegisters[0]==1&&state.globalRegisters[2]==1,"shape frame/init once despite Native replay");}
  Check(!captured.empty(),"actual geometry draws");bool sawCanvas=false,sawNative=false;
  for(const auto&r:captured){const bool isNative=r.target==nativeId;Check(isNative||r.target==canvasId,"only owned target draws");sawNative|=isNative;sawCanvas|=!isNative;Check(!r.colors.empty(),"actual emitted RGBA rows");
   if(m.wave){RGBA expected=oracle?QuantGeometry(m.center):m.center;if(isNative&&m.dots)expected[3]*=DotStyleFor(LineKind::CustomWave,false,2).alphaScale;for(const auto&c:r.colors)Compare(c,expected,label+" wave emitted source fraction/style");}
   else if(r.primitive==GL_TRIANGLE_FAN){const auto center=oracle?QuantGeometry(m.center):m.center;const auto edge=oracle?QuantGeometry(m.edge):m.edge;Compare(r.colors.front(),center,label+" actual fill center");for(size_t i=1;i<r.colors.size();++i)Compare(r.colors[i],edge,label+" actual fill edge");}
   else{const auto border=oracle?QuantGeometry(m.border):m.border;for(const auto&c:r.colors)Compare(c,border,label+" actual border");}
  }
  Check(sawCanvas&&sawNative,"both production targets observed");const int expectedDraws=m.wave?2:m.border[3]>0?4:2;Check(int(captured.size())==expectedDraws,"retained thin/dot/fill/border pass count");
  Dump(out/(label+".attributes.csv"),captured);const auto a=FramebufferPixels(canvas,64),n=FramebufferPixels(native,128);Check(a.size()==64*64*4&&n.size()==128*128*4,"read both real targets");Ppm(out/(label+".authored.ppm"),a,64);Ppm(out/(label+".native.ppm"),n,128);Check(glGetError()==GL_NO_ERROR,"production geometry GL state");
  std::cout<<label<<" actual RGBA/pass/replay controls passed\n";
 }
}
static void Display(ShaderCache&cache,const std::filesystem::path&out){
 struct Case{const char*name;float gamma,echo;std::vector<float>gain;};const std::vector<Case> cases={{"gamma075",.75f,0,{.75f}},{"gamma09",.9f,0,{.9f}},{"gamma1",1,0,{1}},{"echoHalf",1,.5f,{.5f,.5f}}};
 Surface input(64),output(64);input.Clear(1,1,1);
 for(const auto&c:cases){PresetState state;Configure(state,cache,64);state.mainTexture=input.texture;state.shader=0;state.gammaAdj=c.gamma;state.videoEchoAlpha=c.echo;state.videoEchoZoom=1;state.videoEchoOrientation=0;
  PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);VideoEcho echo(state);output.Clear();std::vector<Record> captured;{Hook hook(&captured);echo.Draw(frame);}Check(captured.size()==c.gain.size(),"actual display pass count");
  std::ofstream expected(out/(std::string(c.name)+".source-byte.csv"));expected<<"pass,channel,current,original_byte,original_normalized\n";
  for(size_t i=0;i<captured.size();++i){Check(captured[i].colors.size()==4,"actual display quad attributes");for(const auto&rgba:captured[i].colors){Compare(rgba,{c.gain[i],c.gain[i],c.gain[i],1},"actual white-tint display producer");}for(int channel=0;channel<3;++channel){const auto byte=DisplayByte(c.gain[i]);expected<<i<<','<<channel<<','<<std::setprecision(9)<<c.gain[i]<<','<<byte<<','<<Normalized(byte)<<'\n';}}
  Dump(out/(std::string(c.name)+".attributes.csv"),captured);output.Ppm(out/(std::string(c.name)+".actual.ppm"));Check(glGetError()==GL_NO_ERROR,"actual display GL state");std::cout<<c.name<<" actual display attributes/passes passed\n";
 }
}
static void Composite(ShaderCache&cache,const std::filesystem::path&out){
 Surface input(64),current(64),quantized(64);input.Clear(1,1,1);current.Clear();quantized.Clear();TextureManager textures(std::vector<std::string>{});
 PresetState state;Configure(state,cache,64);state.renderContext.textureManager=&textures;state.mainTexture=input.texture;state.compositeShaderVersion=2;state.compositeShader="shader_body { ret = hue_shader; }";
 PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);FinalComposite composite;composite.LoadCompositeShader(state);composite.CompileCompositeShader(state);Check(composite.HasCompositeShader(),"actual shader composite path");
 GridReplay replay{&quantized,out/"composite-completed-vertices.csv",false};current.Bind();{Hook hook(nullptr,&replay);composite.Draw(state,frame);}Check(replay.done,"completed vertex-byte replay executed");Check(glGetError()==GL_NO_ERROR,"actual composite producer/replay GL state");current.Ppm(out/"composite-float-current.ppm");quantized.Ppm(out/"composite-vertex-byte-oracle.ppm");
 // Equality after final RGBA8/interpolation is admitted; producer rows establish
 // the source difference. This is not a Windows raster or old-grid oracle.
 std::cout<<"actual completed composite vertices/indices captured and pre-interpolation byte replay passed\n";
}
int main(int argc,char**argv){try{Check(argc>=3,"usage: producer-attributes PACKET_DIR OUTPUT_DIR [geometry|display|composite|all]");const std::filesystem::path packet=argv[1],out=argv[2];std::filesystem::create_directories(out);const std::string mode=argc>3?argv[3]:"all";GLContext gl;ShaderCache cache;if(mode=="geometry"||mode=="all")Geometry(packet,cache,out);if(mode=="display"||mode=="all")Display(cache,out);if(mode=="composite"||mode=="all")Composite(cache,out);Check(mode=="geometry"||mode=="display"||mode=="composite"||mode=="all","unknown case");}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}return 0;}
