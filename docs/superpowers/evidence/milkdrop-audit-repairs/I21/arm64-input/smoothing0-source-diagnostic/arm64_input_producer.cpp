#include "constructor_sink.hpp"
#include <Audio/PCM.hpp>
#include <MilkdropPreset/PresetState.hpp>
#include <MilkdropPreset/PerFrameContext.hpp>
#include <MilkdropPreset/WaveformMode.hpp>
#include <MilkdropPreset/Waveforms/Factory.hpp>
#include <projectM-4/audio.h>
#include <array>
#include <algorithm>
#include <cmath>
#include <limits>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <stdexcept>
#include <cstdlib>
using namespace libprojectM::MilkdropPreset;
static void Check(bool value,const char* reason){if(!value)throw std::runtime_error(reason);}
static bool Selected(int f){return f==120||f==150||f==180||f==210||f==239||f==300||f==390||f==479;}
static void Number(std::ostream& output,double value){if(std::isfinite(value))output<<std::setprecision(17)<<value;else output<<"null";}
int main(int argc,char** argv)
{
 try {
    Check(argc==3,"usage:arm64-input-producer PCM_U8 TRACE_JSONL");setenv("PRESET_LAB_SEED","12345",1);input_sink::Install();
    std::ifstream input(argv[1],std::ios::binary);std::ofstream output(argv[2]);Check(bool(input)&&bool(output),"cannot open input/output");
    libprojectM::Audio::PCM pcm;const unsigned feedSamples=projectm_pcm_get_max_samples();
    Check(feedSamples>0&&feedSamples<=1470,"invalid production PCM tail size");
    PresetState state;auto& rc=state.renderContext;rc.viewportSizeX=3840;rc.viewportSizeY=2160;
    rc.lineReferenceWidth=1280;rc.lineReferenceHeight=720;rc.perPixelMeshX=48;rc.perPixelMeshY=32;
    rc.aspectX=1;rc.aspectY=.5625f;rc.invAspectX=1;rc.invAspectY=1/.5625f;rc.fps=30;
    state.waveScale=1;state.waveSmoothing=0;state.waveAlpha=.8f;state.waveParam=.25f;state.waveX=state.waveY=.5f;
    state.modWaveAlphaByvolume=false;state.waveR=.2f;state.waveG=.7f;state.waveB=1;
    PerFrameContext context(state.globalMemory,&state.globalRegisters);context.RegisterBuiltinVariables();
    std::array<std::unique_ptr<Waveforms::WaveformMath>,16> producers;
    for(int m=0;m<16;++m)producers[m]=Waveforms::Factory::Create(static_cast<WaveformMode>(m));
    bool qualified=true;std::array<uint8_t,1470> block{};double previousClock=0;
    for(int frame=0;frame<480;++frame){
        input.read(reinterpret_cast<char*>(block.data()),block.size());Check(input.gcount()==int(block.size()),"missing complete480x1470PCM blocks");
        const double clock=frame/30.;const double dt=clock-previousClock;previousClock=clock;
        pcm.Add(block.data()+block.size()-feedSamples,1,feedSamples);pcm.UpdateFrameAudioData(dt,frame);
        state.audioData=pcm.GetFrameAudioData();rc.time=static_cast<float>(clock);rc.frame=frame;context.LoadStateVariables(state);
        float pairMin=std::numeric_limits<float>::infinity();int badPairs=0;
        for(int i=0;i<256;++i){const float sum=state.audioData.spectrumLeft[i*2]/128.f+state.audioData.spectrumLeft[i*2+1]/128.f;
            pairMin=std::min(pairMin,sum);if(!std::isfinite(sum)||sum<=0)++badPairs;}
        float lassoMin=std::numeric_limits<float>::infinity();int badLassoArguments=0,badLassoTan=0;
        for(int i=0;i<240;++i){const float angle=state.audioData.waveformLeft[i+32]/128.f*1.57f+rc.time*2.f;
            if(std::isfinite(angle))lassoMin=std::min(lassoMin,std::abs(angle));
            if(!std::isfinite(angle)||angle==0){++badLassoArguments;continue;}
            const float argument=rc.time/angle;if(!std::isfinite(argument)){++badLassoArguments;continue;}
            if(!std::isfinite(std::tan(argument)))++badLassoTan;}
        const auto& audio=state.audioData;const float bands[]={audio.bass,audio.mid,audio.treb,audio.bassAtt,audio.midAtt,audio.trebAtt,audio.vol,audio.volAtt};
        int badBands=0;for(float value:bands)if(!std::isfinite(value))++badBands;
        for(int mode=0;mode<16;++mode){auto vertices=producers[mode]->GetVertices(state,context);size_t count=0,bad=0;
            for(const auto& strip:vertices)for(const auto& xy:strip){++count;if(!std::isfinite(xy.X())||!std::isfinite(xy.Y()))++bad;}
            output<<"{\"frame\":"<<frame<<",\"clock\":";Number(output,clock);output<<",\"dt\":";Number(output,dt);
            output<<",\"renderTimeFloat\":";Number(output,rc.time);output<<",\"mode\":"<<mode<<",\"feedTailSamples\":"<<feedSamples
                  <<",\"waveformSamples\":"<<libprojectM::Audio::WaveformSamples<<",\"spectrumSamples\":"<<libprojectM::Audio::SpectrumSamples
                  <<",\"smoothedPoints\":"<<count<<",\"nonfinitePoints\":"<<bad<<",\"nonpositiveOrNonfiniteSpectrumPairs\":"<<badPairs<<",\"minimumScaledPairSum\":";Number(output,pairMin);
            output<<",\"nonfiniteLassoArguments\":"<<badLassoArguments<<",\"nonfiniteLassoTan\":"<<badLassoTan<<",\"minimumLassoAbsAngle\":";Number(output,lassoMin);
            const char* keys[]={"bass","mid","treb","bassAtt","midAtt","trebAtt","vol","volAtt"};
            for(int i=0;i<8;++i){output<<",\""<<keys[i]<<"\":";Number(output,bands[i]);}
            output<<",\"nonfiniteBands\":"<<badBands<<",\"constructorSinkCalls\":"<<input_sink::calls<<",\"selected\":"<<(Selected(frame)?"true":"false")<<"}\n";
            if(Selected(frame)&&(bad||badBands||(mode==8&&badPairs)||(mode==15&&(badLassoArguments||badLassoTan))))qualified=false;
        }
    }
    Check(output.good(),"trace write failed");std::cout<<"ARM64 source CPU producer:tail="<<feedSamples<<" spectrum="<<libprojectM::Audio::SpectrumSamples<<" selected_finite="<<qualified<<" no_context_no_draw=true\n";
    return qualified?0:2;
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
