#include "gl_context.hpp"
#include <MilkdropPreset/GeometryTargets.hpp>
#include <Renderer/Framebuffer.hpp>
#include <Renderer/ShaderCache.hpp>
#include <algorithm>
#include <MilkdropPreset/PresetFileParser.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/CustomWaveform.hpp>
#include <MilkdropPreset/CustomShape.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <Renderer/OpenGL.h>
#include <climits>
#include <filesystem>
#include <set>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace libprojectM::MilkdropPreset;
static int failures=0;
static void Check(bool value,const std::string& why){if(!value){++failures;std::cerr<<"FAIL "<<why<<'\n';}}
static PresetFileParser Parse(const std::string& text){PresetFileParser p;std::istringstream in(text);Check(p.Read(in),"fixture parse");return p;}
static void Parser(){
 const char* flags[]={"bRedBlueStereo","bBrighten","bDarken","bSolarize","bInvert",
 "bAdditiveWaves","bWaveDots","bWaveThick","bModWaveAlphaByVolume","bMaximizeWaveColor",
 "bMotionVectorsOn","bTexWrap","bDarkenCenter","wavecode_0_enabled","wavecode_0_bSpectrum",
 "wavecode_0_bUseDots","wavecode_0_bDrawThick","wavecode_0_bAdditive","shapecode_0_enabled",
 "shapecode_0_additive","shapecode_0_thickOutline","shapecode_0_textured"};
 for(int value:{INT_MIN,-2,-1,0,1,2,INT_MAX})for(const auto* flag:flags){
  auto parser=Parse(std::string(flag)+"="+std::to_string(value)+"\n");
  Check(parser.GetBool(flag,false)==(value!=0),std::string(flag)+"="+std::to_string(value));
 }
 for(const auto* text:{"invalid","nan","inf","2147483648","-2147483649","999999999999999999999999"}){
  auto parser=Parse(std::string("bTexWrap=")+text+"\n");
  Check(!parser.GetBool("bTexWrap",false),std::string(text)+" false default");
  Check(parser.GetBool("bTexWrap",true),std::string(text)+" true default");
 }
 auto missing=Parse("zoom=1\n");Check(!missing.GetBool("absent",false)&&missing.GetBool("absent",true),"missing defaults");
 // Preserve existing integer-prefix parsing, rather than adding a new lexer.
 for(const auto* text:{"-1junk","-1.5","  -1"}){auto p=Parse(std::string("bTexWrap=")+text+"\n");Check(p.GetBool("BTEXWRAP",false),"negative integer prefix");}
 auto negativeFirst=Parse("BTEXWRAP=-1\nbTexWrap=0\n");Check(negativeFirst.GetBool("bTeXwRaP",false),"normalized first negative occurrence");
 auto zeroFirst=Parse("bTexWrap=0\nBTEXWRAP=-1\n");Check(!zeroFirst.GetBool("BTEXWRAP",true),"normalized first zero occurrence");
 auto invalidFirst=Parse("bTexWrap=invalid\nBTEXWRAP=-1\n");Check(!invalidFirst.GetBool("bTexWrap",false)&&invalidFirst.GetBool("BTEXWRAP",true),"first invalid occurrence retains defaults");
 for(int value:{-2,-1,0,1,2}){
  auto p=Parse("bTexWrap="+std::to_string(value)+"\nbInvert="+std::to_string(value)+"\nbMotionVectorsOn="+std::to_string(value)+"\nwavecode_0_enabled="+std::to_string(value)+"\nwavecode_0_bSpectrum="+std::to_string(value)+"\nwavecode_0_bUseDots="+std::to_string(value)+"\nwavecode_0_bDrawThick="+std::to_string(value)+"\nwavecode_0_bAdditive="+std::to_string(value)+"\nshapecode_0_enabled="+std::to_string(value)+"\nshapecode_0_additive="+std::to_string(value)+"\nshapecode_0_thickOutline="+std::to_string(value)+"\nshapecode_0_textured="+std::to_string(value)+"\n");
  bool enabled=value!=0;PresetState state;state.Initialize(p);
  Check(state.texWrap==enabled&&state.invert==enabled&&state.mvA==(enabled?1.f:0.f),"effective main flags "+std::to_string(value));
 }
}
static void Wave(){
 for(int value:{-2,-1,0,1,2}){
  auto p=Parse("wavecode_0_enabled="+std::to_string(value)+"\nwavecode_0_samples=0\nwave_0_init1=reg01+=1;t1=.5;\nwave_0_per_frame1=reg00+=1;t1+=.25;\nwave_0_per_point1=reg02+=1;\nper_frame_1=q1=reg00;\n");
  PresetState state;state.Initialize(p);state.renderContext.fps=30;
  state.customWaveInitCode[0]=p.GetCode("wave_0_init");state.customWavePerFrameCode[0]=p.GetCode("wave_0_per_frame");state.customWavePerPointCode[0]=p.GetCode("wave_0_per_point");
  PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);frame.CompilePerFrameCode(p.GetCode("per_frame_"));
  CustomWaveform wave(state);wave.Initialize(p,0);std::vector<std::string>warnings;wave.CompileCodeAndRunInitExpressions(frame,warnings);
  Check(warnings.empty(),"real EEL compilation");Check(state.globalRegisters[1]==1,"unconditional init "+std::to_string(value));
  frame.ExecutePerFrameCode();Check(*frame.q_vars[0]==0,"first main frame sees pre-wave state");
  wave.Draw(frame);Check(state.globalRegisters[0]==(value!=0?1:0),"actual wave-frame gate "+std::to_string(value));
  frame.LoadStateVariables(state);frame.ExecutePerFrameCode();Check(*frame.q_vars[0]==(value!=0?1:0),"second main frame visibility "+std::to_string(value));
  wave.Draw(frame);Check(state.globalRegisters[0]==(value!=0?2:0),"one frame evaluation per Draw "+std::to_string(value));
  Check(state.globalRegisters[1]==1&&state.globalRegisters[2]==0,"init once/no points with zero samples");
 }
}
// Exercise the real two-point renderer and one-evaluation Native replay.
static void WaveRendering(libprojectM::Renderer::ShaderCache& cache){
 using namespace libprojectM::Renderer;
 for(int value:{-2,-1,0,1,2}){
  auto p=Parse("wavecode_0_enabled="+std::to_string(value)+"\nwavecode_0_samples=2\nwavecode_0_smoothing=0\n"
    "wave_0_init1=reg01+=1;\nwave_0_per_frame1=reg00+=1;\n"
    "wave_0_per_point1=reg02+=1;x=.25+.5*sample;y=.5;r=1;g=0;b=0;a=1;\nper_frame_1=q1=reg00;\n");
  PresetState state;state.Initialize(p);auto& rc=state.renderContext;
  rc.shaderCache=&cache;rc.viewportSizeX=rc.viewportSizeY=128;
  rc.lineReferenceWidth=rc.lineReferenceHeight=64;
  rc.aspectX=rc.aspectY=rc.invAspectX=rc.invAspectY=1;rc.fps=30;state.LoadShaders();
  state.customWaveInitCode[0]=p.GetCode("wave_0_init");
  state.customWavePerFrameCode[0]=p.GetCode("wave_0_per_frame");
  state.customWavePerPointCode[0]=p.GetCode("wave_0_per_point");
  PerFrameContext frame(state.globalMemory,&state.globalRegisters);
  frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);frame.CompilePerFrameCode(p.GetCode("per_frame_"));
  CustomWaveform wave(state);wave.Initialize(p,0);std::vector<std::string> warnings;
  wave.CompileCodeAndRunInitExpressions(frame,warnings);Check(warnings.empty(),"render EEL compilation");
  Framebuffer canvas(1),native(1);
  canvas.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);
  native.CreateColorAttachment(0,0,GL_RGBA8,GL_RGBA,GL_UNSIGNED_BYTE);
  canvas.SetSize(64,64);native.SetSize(128,128);
  GeometryTargets targets(state,canvas,0,64,64,{},native,0);
  for(int n=0;n<2;++n){
   frame.LoadStateVariables(state);frame.ExecutePerFrameCode();
   Check(*frame.q_vars[0]==(value!=0?n:0),"following main frame visibility");
   native.Bind(0);glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
   targets.Authored();glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);
   wave.Draw(frame,&targets);Check(glGetError()==GL_NO_ERROR,"two-point replay GL error");
   Check(state.globalRegisters[0]==(value!=0?n+1:0),"one wave frame per render");
   Check(state.globalRegisters[1]==1,"init exactly once including disabled wave");
   Check(state.globalRegisters[2]==(value!=0?2*(n+1):0),"two points once despite Native replay");
   for(int pass=0;pass<2;++pass){
    auto& target=pass==0?canvas:native;const int size=pass==0?64:128;
    target.BindRead(0);std::vector<unsigned char> pixels(size*size*4);
    glReadPixels(0,0,size,size,GL_RGBA,GL_UNSIGNED_BYTE,pixels.data());
    bool visible=false;for(size_t i=0;i<pixels.size();i+=4){visible|=pixels[i]!=0;Check(pixels[i+1]==0&&pixels[i+2]==0,"two-point red palette");}
    Check(visible==(value!=0),"negative/positive enabled geometry and zero absence");
    Check(glGetError()==GL_NO_ERROR,"two-point read framebuffer error");
   }
  }
 }
}
static void Corpus(const char* directory){
 std::set<std::string> keys={"bredbluestereo","bbrighten","bdarken","bsolarize","binvert","badditivewaves","bwavedots","bwavethick","bmodwavealphabyvolume","bmaximizewavecolor","bmotionvectorson","btexwrap","bdarkencenter"};
 for(int i=0;i<4;++i){for(const auto* key:{"enabled","bspectrum","busedots","bdrawthick","badditive"})keys.insert("wavecode_"+std::to_string(i)+"_"+key);for(const auto* key:{"enabled","additive","thickoutline","textured"})keys.insert("shapecode_"+std::to_string(i)+"_"+key);}
 int files=0,candidates=0;for(const auto& entry:std::filesystem::directory_iterator(directory)){
  if(entry.path().extension()!=".milk")continue;++files;PresetFileParser parser;Check(parser.Read(entry.path().string()),"stock parse "+entry.path().string());
  for(const auto& key:keys)if(parser.GetInt(key,0)<0){++candidates;std::cout<<"CANDIDATE\t"<<entry.path().string()<<'\t'<<key<<'\t'<<parser.PresetValues().at(key)<<'\n';}
 }
 std::cout<<"stock_files="<<files<<" negative_recognized_first_values="<<candidates<<'\n';
}
int main(int argc,char**argv){try{GLContext gl;libprojectM::Renderer::ShaderCache cache;if(argc>2&&std::string(argv[1])=="corpus")Corpus(argv[2]);else if(argc>1&&std::string(argv[1])=="render")WaveRendering(cache);else if(argc>1&&std::string(argv[1])=="wave")Wave();else Parser();}catch(const std::exception&e){std::cerr<<"ERROR "<<e.what()<<'\n';return 2;}std::cout<<"failures="<<failures<<'\n';return failures?1:0;}
