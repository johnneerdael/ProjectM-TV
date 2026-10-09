#include <Audio/PCM.hpp>
#include <Audio/Loudness.hpp>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <vector>
using namespace libprojectM::Audio;
using Bands=std::array<Loudness,3>;
static Bands NewBands(){return {Loudness(Loudness::Band::Bass),Loudness(Loudness::Band::Middles),Loudness(Loudness::Band::Treble)};}
static void Require(bool b,const char* m){if(!b)throw std::runtime_error(m);}
static void Verify(PCM& pcm,Bands& avg,Bands& left,unsigned frame,bool equal,double& maxDelta){
 pcm.UpdateFrameAudioData(1./30,frame);auto d=pcm.GetFrameAudioData();SpectrumBuffer s{};
 for(unsigned i=0;i<SpectrumSamples;++i){Require(std::isfinite(d.spectrumLeft[i])&&std::isfinite(d.spectrumRight[i]),"nonfinite spectrum");s[i]=.5f*(d.spectrumLeft[i]+d.spectrumRight[i]);if(equal)Require(d.spectrumLeft[i]==d.spectrumRight[i]&&s[i]==d.spectrumLeft[i],"mono spectra not identical");}
 const float values[]={d.bass,d.mid,d.treb},atten[]={d.bassAtt,d.midAtt,d.trebAtt};
 for(unsigned b=0;b<3;++b){avg[b].Update(s,1./30,frame);left[b].Update(d.spectrumLeft,1./30,frame);Require(values[b]==avg[b].CurrentRelative()&&atten[b]==avg[b].AverageRelative(),"production band not averaged spectrum");double delta=std::abs(double(values[b])-left[b].CurrentRelative());maxDelta=std::max(maxDelta,delta);if(equal)Require(delta==0&&atten[b]==left[b].AverageRelative(),"mono differs from left-only stage");}
 Require(d.vol==(d.bass+d.mid+d.treb)*.333f&&d.volAtt==(d.bassAtt+d.midAtt+d.trebAtt)*.333f,"immutable all-band fields changed");
}
int main(int argc,char**argv){try{
 Require(argc==2,"expected common uint8 PCM path");std::ifstream file(argv[1],std::ios::binary);Require(bool(file),"PCM missing");std::vector<uint8_t> data((std::istreambuf_iterator<char>(file)),{});Require(data.size()==480*1470,"PCM size mismatch");
 PCM mono;auto avg=NewBands(),left=NewBands();double delta=0;
 for(unsigned f=0;f<480;++f){mono.Add(data.data()+(f+1)*1470-AudioBufferSamples,1,AudioBufferSamples);Verify(mono,avg,left,f,true,delta);}std::cout<<"common-JNI uint8 mono 480 frames, effective tail="<<AudioBufferSamples<<", averaged/left-only bands exact; maxdelta="<<delta<<'\n';
 for(int kind=0;kind<4;++kind){PCM pcm;auto a=NewBands(),l=NewBands();double maximum=0;std::array<float,AudioBufferSamples*2> samples{};
  for(unsigned f=0;f<120;++f){for(unsigned i=0;i<AudioBufferSamples;++i){double tone=std::sin(6.283185307179586*(f*AudioBufferSamples+i)*7./AudioBufferSamples);float x=float(.05*tone),y=float((f<60?.05:.15)*tone);if(kind==1)std::swap(x,y);if(kind==2)x=0;if(kind==3)y=x;samples[2*i]=x;samples[2*i+1]=y;}pcm.Add(samples.data(),2,AudioBufferSamples);Verify(pcm,a,l,f,kind==3,maximum);if(kind==0&&f==60){auto d=pcm.GetFrameAudioData();std::cout.precision(10);std::cout<<"STAGE frame60 average_bass="<<d.bass<<" left_only_bass="<<l[0].CurrentRelative()<<" average_bass_att="<<d.bassAtt<<" left_only_bass_att="<<l[0].AverageRelative()<<'\n';}}
  if(kind!=3)Require(maximum>1e-3,"asymmetric stereo did not differ from left-only stage");std::cout<<"stereo kind="<<kind<<" frames=120 max relative-band difference="<<maximum<<'\n';
 }
 std::cout<<"production PCM averaged-policy/mono-invariance controls passed; same-FFT left-only combination oracle, not Windows PCM equivalence\n";
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
