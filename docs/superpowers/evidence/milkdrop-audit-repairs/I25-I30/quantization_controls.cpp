// Prepared source-only controls; not compiled/run during owner preparation.
#include "Color.hpp"
#include <cmath>
#include <iostream>
#include <stdexcept>
using libprojectM::Renderer::Color;
static void Check(bool value,const char*why){if(!value)throw std::runtime_error(why);}
static unsigned GeometryByte(double value){if(!std::isfinite(value)||value<0||value>1)throw std::invalid_argument("bounded original geometry domain");return unsigned(int(value*255.0))&255u;}
static unsigned DisplayByte(float value){if(!std::isfinite(value)||value<0||value>1)throw std::invalid_argument("bounded original display domain");float scaled=value*255.f;return unsigned(int(scaled))&255u;}
int main(){try{
 Check(GeometryByte(.5)==127,"original half channel truncates");Check(GeometryByte(.123456)==31,"original fractional channel truncates");
 Check(GeometryByte(.003)==0,"original sub-byte alpha becomes zero");Check(DisplayByte(.75f)==191,"original gamma diffuse byte");
 Check(GeometryByte(0)==0&&GeometryByte(1)==255,"original endpoints");
 for(double value:{0.,1./255.,31./255.,127./255.,191./255.,1.})Check(std::abs(Color::Modulo(value)-value)<2e-7,"retain bounded current float modulo, including byte-fraction controls");
 Check(std::abs(Color::Modulo(.5)-.5)<2e-7&&std::abs(Color::Modulo(.5)-127./255.)>1e-4,"current half channel retains fraction");
 Check(std::abs(Color::Modulo(.123456)-.123456)<2e-7&&std::abs(Color::Modulo(.123456)-31./255.)>1e-4,"current fractional channel retains fraction");
 Check(Color::Modulo(.003)>0,"current sub-byte alpha survives producer");
 Color raw(1.25f,.5f,.25f,.123456f);Check(raw.R()==1.25f&&raw.A()==.123456f,"raw display/border colour remains floating; not a framebuffer HDR proof");
 std::cout<<"bounded colour source controls passed\n";
}catch(const std::exception&e){std::cerr<<"FAIL "<<e.what()<<'\n';return 1;}return 0;}
