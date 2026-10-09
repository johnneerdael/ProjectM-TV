#include "scalar_attribute_sink.hpp"
#include <MilkdropPreset/MilkdropShader.hpp>
#include <MilkdropPreset/PerPixelMesh.hpp>
#include <MilkdropPreset/PerPixelContext.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <cmath>
#include <iostream>
#include <stdexcept>
#include <array>
#include <fstream>
#include <MilkdropPreset/PresetFileParser.hpp>
using namespace libprojectM::MilkdropPreset;
static int failures=0;
static void Check(bool value,const std::string&why){if(!value){++failures;std::cerr<<"FAIL "<<why<<'\n';}}
static float Attribute(GLuint attr,int vertex,int component,int width){const auto&bytes=uploaded.at(attributeBuffers.at(attr));float result;std::memcpy(&result,bytes.data()+(vertex*width+component)*sizeof(float),sizeof(float));return result;}
static void Prepare(PerPixelMesh&mesh,PresetState&state,PerFrameContext&frame,PerPixelContext&pixel){pixel.LoadStateReadOnlyVariables(state,frame);pixel.LoadPerFrameQVariables(state,frame);mesh.Prepare(state,frame,pixel);}
static void Control(int gx,int gy,float ax,float ay,bool custom){
 PresetState state;auto&rc=state.renderContext;rc.viewportSizeX=256;rc.viewportSizeY=144;rc.perPixelMeshX=gx;rc.perPixelMeshY=gy;rc.aspectX=ax;rc.aspectY=ay;rc.invAspectX=1/ax;rc.invAspectY=1/ay;rc.fps=30;
 PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);
 PerPixelContext pixel(state.globalMemory,&state.globalRegisters);pixel.RegisterBuiltinVariables();
 pixel.CompilePerPixelCode("dx=above(ang,0);dy=ang;rot=ang;zoom=-1;zoomexp=1;reg00+=1;");
 PerPixelMesh mesh;if(custom){state.warpShaderVersion=2;state.warpShader="shader_body {ret=float3(0,0,0);}";mesh.LoadWarpShader(state);}
 Prepare(mesh,state,frame,pixel);
 const int n=(gx+1)*(gy+1);const int count=state.globalRegisters[0];Check(count==n,"one evaluation per mesh node");
 const auto positions=uploaded.at(attributeBuffers.at(0));const auto radiusAngles=uploaded.at(attributeBuffers.at(3));
 for(int row=0;row<=gy;++row)for(int column=0;column<=gx;++column){
  const int index=row*(gx+1)+column;const float x=Attribute(0,index,0,2),y=Attribute(0,index,1,2),cached=Attribute(3,index,1,2);
  const bool center=row==gy/2&&column==gx/2;
  const float raw=center?0.f:atan2f(y*ay,x*ax);Check(cached==raw,"cached shader angle altered");
  const bool seam=!custom&&y==0.f&&x<0.f;
  const float expected=seam?raw:-raw;const float actual=Attribute(6,index,1,2);
  Check(actual==expected,"equation ang "+std::to_string(gx)+"x"+std::to_string(gy)+" node="+std::to_string(index)+" custom="+std::to_string(custom));
  Check(Attribute(6,index,0,2)==(expected>0?1.f:0.f),"above(ang,0) discriminator");
  Check(Attribute(4,index,2,4)==std::sin(actual)&&Attribute(8,index,0,1)==std::cos(actual),"retained CPU float rotation trig");
  Check(Attribute(9,index,0,1)==-1.f,"retained signed zoom power");
 }
 const GLuint positionBuffer=attributeBuffers.at(0);const int staticCount=uploads[positionBuffer];
 const int indexCount=uploads[bound[GL_ELEMENT_ARRAY_BUFFER]];
 Prepare(mesh,state,frame,pixel);Check(uploads[positionBuffer]==staticCount,"static position cache uploaded on unchanged frame");Check(uploads[bound[GL_ELEMENT_ARRAY_BUFFER]]==indexCount,"static topology cache uploaded on unchanged frame");
 Check(uploaded.at(positionBuffer)==positions&&uploaded.at(attributeBuffers.at(3))==radiusAngles,"cache/repeated frame changed static data");
 Check(state.globalRegisters[0]==2*n,"repeated Prepare equation count changed");
 // Inject a frozen signed-zero cache pair into real CPU storage exposed to the
 // upload sink. This exercises CalculateMesh consumption, not mesh generation.
 const int left=(gy/2)*(gx+1);const GLuint angleBuffer=attributeBuffers.at(3);
 auto*vertices=const_cast<unsigned char*>(static_cast<const unsigned char*>(cpuPointers.at(positionBuffer)));
 auto*angles=const_cast<unsigned char*>(static_cast<const unsigned char*>(cpuPointers.at(angleBuffer)));
 const float pi=atan2f(+0.f,-1.f);
 for(float signedZero:{+0.f,-0.f}){
  const float frozenAngle=atan2f(signedZero,-ax);
  std::memcpy(vertices+(left*2+1)*sizeof(float),&signedZero,sizeof(float));
  std::memcpy(angles+(left*2+1)*sizeof(float),&frozenAngle,sizeof(float));
  Prepare(mesh,state,frame,pixel);const float expected=custom?-frozenAngle:frozenAngle;
  const float actual=Attribute(6,left,1,2);Check(actual==expected,"signed-zero left-axis equation consumption");
  Check(std::signbit(Attribute(3,left,1,2))==std::signbit(signedZero),"signed-zero raw shader angle changed");
  Check(actual==(custom?(std::signbit(signedZero)?pi:-pi):(std::signbit(signedZero)?-pi:pi)),"signed-zero atan2 branch contract");
 }
 // Ordinary periodic expressions keep their bounded sine/cosine values.
 projectm_eval_code_destroy(pixel.perPixelCodeHandle);pixel.perPixelCodeHandle=nullptr;
 pixel.CompilePerPixelCode("dx=sin(ang);dy=cos(ang);");Prepare(mesh,state,frame,pixel);
 Check(std::abs(Attribute(6,left,0,2))<2e-7f&&std::abs(Attribute(6,left,1,2)+1)<2e-7f,"bounded periodic left-axis controls");
 // Rounded float pi is not mathematical pi: sine's tiny sign can still
 // change a strict predicate. Do not certify all periodic uses unchanged.
 const float positiveZero=+0.f;
 std::memcpy(vertices+(left*2+1)*sizeof(float),&positiveZero,sizeof(float));
 std::memcpy(angles+(left*2+1)*sizeof(float),&pi,sizeof(float));
 projectm_eval_code_destroy(pixel.perPixelCodeHandle);pixel.perPixelCodeHandle=nullptr;
 pixel.CompilePerPixelCode("dx=above(sin(ang),0);dy=sin(ang);");Prepare(mesh,state,frame,pixel);
 *frame.q_vars[0]=custom?-pi:pi;
 frame.CompilePerFrameCode("q2=sin(q1);");frame.ExecutePerFrameCode();
 const double expectedSine=*frame.q_vars[1];
 Check(Attribute(6,left,0,2)==(expectedSine>0?1.f:0.f),"rounded-pi sine predicate source contract");
 Check(std::abs(Attribute(6,left,1,2)-expectedSine)<1e-12,"rounded-pi sine original-input producer");
 Check(std::abs(Attribute(6,left,1,2))<2e-7f,"rounded-pi finite sine bound");
 std::cout<<"grid="<<gx<<"x"<<gy<<" custom="<<custom<<" generated raw pi="<<pi<<" evaluations="<<n<<'\n';
}
static void Stock(const char* path){
 PresetFileParser parsed;Check(parsed.Read(path),"stock preset parse");PresetState state;state.Initialize(parsed);
 Check(state.warpShaderVersion==0,"selected stock witness is configured legacy");
 auto&rc=state.renderContext;rc.viewportSizeX=256;rc.viewportSizeY=144;rc.perPixelMeshX=48;rc.perPixelMeshY=32;rc.aspectX=1;rc.aspectY=.5625f;rc.invAspectX=1;rc.invAspectY=1/.5625f;rc.fps=30;
 PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);
 PerPixelContext pixel(state.globalMemory,&state.globalRegisters);pixel.RegisterBuiltinVariables();pixel.CompilePerPixelCode(state.perPixelCode);PerPixelMesh mesh;Prepare(mesh,state,frame,pixel);
 const int node=16*49;const float expected=float(*frame.sy)-.1f;const float actual=Attribute(7,node,1,2);
 std::cout<<"stock_file_default_stage left-axis sy="<<actual<<" expected="<<expected<<" raw_angle="<<Attribute(3,node,1,2)<<'\n';Check(std::abs(actual-expected)<1e-6f,"exact stock per-pixel code at file-default left-axis stage");
}
static void Inventory(const char* input){std::ifstream in(input);std::string path;int i=0;while(std::getline(in,path)){PresetFileParser parsed;Check(parsed.Read(path),"candidate parse");PresetState state;state.Initialize(parsed);std::cout<<i++<<'\t'<<state.warpShaderVersion<<'\t'<<state.warpShader.empty()<<'\t'<<state.perPixelCode.empty()<<'\n';}}
int main(int argc,char**argv){ScalarSink();try{if(argc>2&&std::string(argv[1])=="stock"){Stock(argv[2]);std::cout<<"failures="<<failures<<'\n';return failures?1:0;}if(argc>2&&std::string(argv[1])=="inventory"){Inventory(argv[2]);return failures?1:0;}for(bool custom:{false,true})for(const auto grid:{std::array<int,2>{8,8},{48,32}})for(const auto aspect:{std::array<float,2>{1,1},{1,.5625f}})Control(grid[0],grid[1],aspect[0],aspect[1],custom);}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<'\n';return 2;}std::cout<<"failures="<<failures<<'\n';return failures?1:0;}
