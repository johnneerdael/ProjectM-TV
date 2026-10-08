// Prepared production-parser contract controls. Not built/run in owner preparation.
// Link with the byte-identical parser snapshot; no GL, mocks or policy implementation.
#include "PresetFileParser.hpp"
#include <sstream>
#include <iostream>
#include <stdexcept>
#include <cmath>
using libprojectM::MilkdropPreset::PresetFileParser;
static void Check(bool value,const std::string&why){if(!value)throw std::runtime_error(why);}
static PresetFileParser Parse(const std::string&text){PresetFileParser parsed;std::istringstream input(text);Check(parsed.Read(input),"fixture parse");return parsed;}
static void Contract(){
 for(const auto* key:{"zoom","ZOOM","zOoM"}){auto p=Parse(std::string(key)+"=2\n");for(const auto*lookup:{"zoom","ZOOM","ZoOm"})Check(p.GetFloat(lookup,1)==2,"tolerant float key lookup");}
 auto absent=Parse("fGammaAdj=1\n");Check(absent.GetFloat("zoom",1)==1,"missing float default");
 auto intKey=Parse("nWaVeMoDe=4\n");Check(intKey.GetInt("NWAVEMODE",0)==4,"tolerant integer lookup");
 auto boolKey=Parse("bWaVeDoTs=1\n");Check(boolKey.GetBool("BWAVEDOTS",false),"tolerant bool key lookup");
 auto invalid=Parse("ZOOM=invalid\nzoom=2\n");Check(invalid.GetFloat("zoom",1)==1,"first invalid occurrence retains default");
 auto firstUpper=Parse("ZOOM=2\nzoom=1\n");Check(firstUpper.GetFloat("zoom",1)==2,"normalized first upper occurrence");Check(firstUpper.PresetValues().size()==1,"duplicate keys normalize into one entry");
 auto firstLower=Parse("zoom=1\nZOOM=2\n");Check(firstLower.GetFloat("ZOOM",2)==1,"normalized first lower occurrence");
 auto values=Parse("LaBeL=Sampler_Noise_LQ\n");Check(values.GetString("LABEL","")=="Sampler_Noise_LQ","preserve value casing");
 auto code=Parse("PeR_FrAmE_1=q1=MiXeD_Value;\nper_frame_1=q1=overwritten;\nPER_FRAME_2=q2=Second;\n");
 Check(code.GetCode("PER_FRAME_")=="q1=MiXeD_Value;\nq2=Second;\n","code prefix normalization, first occurrence and unchanged contents");
 auto shaders=Parse("WaRp_1=`shader_body {\nWARP_2=`ret = tex2D(Sampler_Noise, UV).rgb;\nwarp_3=`}\n");
 Check(shaders.GetCode("WARP_")=="shader_body {\nret = tex2D(Sampler_Noise, UV).rgb;\n}\n","shader source casing preserved while backticks stripped");
 auto prefixes=Parse("wave_0_per_point1=x=.25;\nWaVe_0_PeR_PoInT1=x=.75;\n");Check(prefixes.GetCode("WAVE_0_PER_POINT")=="x=.25;\n","normalized custom-code duplicate first occurrence");
 // Finite fixture producer values. Rendering is deliberately a separate gate.
 Check(firstUpper.GetFloat("zoom",1)*.05f==.1f,"retained diagnostic width");
 Check(firstLower.GetFloat("zoom",1)*.05f==.05f,"explicit strict-source-oracle diagnostic width");
}
static void Candidate(const std::string&path){PresetFileParser p;Check(p.Read(path),"exact candidate parse");
 Check(p.GetInt("PSVERSION_COMP",2)==3,"candidate tolerant composite version");
 Check(std::abs(p.GetFloat("fWarpAnimSpeed",1)-.5f)<1e-6f,"candidate tolerant warp speed");
 Check(std::abs(p.GetFloat("fWarpScale",1)-2.331f)<1e-6f,"candidate tolerant warp scale");
 Check(p.GetFloat("warp",1)==0,"candidate declares warp0");
 Check(!p.GetCode("warp_").empty()&&!p.GetCode("comp_").empty(),"candidate retains authored custom shaders");
 const auto pixel=p.GetCode("per_pixel_");Check(pixel.find("q5 * q5 * q5 * q5")!=std::string::npos,"exact duplicate per_pixel1 keeps first authored expression");Check(pixel.find("sin(q5 * (100 * q5)")==std::string::npos,"later duplicate per_pixel1 must not replace first");
}
int main(int argc,char**argv){try{Contract();for(int i=1;i<argc;++i)Candidate(argv[i]);std::cout<<"production parser casing/first-occurrence controls passed\n";}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}return 0;}
