"""Matching source34 CPU adapters preserve exact attribution and old math."""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from engine_profiles import CORE_2331_ENGINE,CORE_2334_ENGINE
from test_native_wave import frame
from test_corpus15_audio import run_audio
from test_core2331_noise import generate,NAMES

ROOT=Path(__file__).resolve().parents[2]
NEW=ROOT/'build/preset-corpus/source34/adapters'
OLD=ROOT/'build/preset-corpus/source31/adapters'


def execute_wave(folder,tmp_path,mode):
    output=tmp_path/(folder.parent.name+'-wave.json');request=tmp_path/'wave-request.json'
    request.write_text(json.dumps({'mode':mode,'mode_policy':'evaluated-live-v1',
        'width':512,'height':288,'output':str(output),'frames':[frame(time=1,wave_mode=mode)]}))
    process=subprocess.run([str(folder/'milk-wave-inputs'),str(request)],capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    return json.loads(output.read_text())


@pytest.mark.parametrize('mode',[0,1,3,6,9,15])
def test_source34_live_wave_math_matches_source31_with_distinct_identity(tmp_path,mode):
    new=execute_wave(NEW,tmp_path,mode)
    old=execute_wave(OLD,tmp_path,mode)
    assert new['engine_identity']==CORE_2334_ENGINE
    assert old['engine_identity']==CORE_2331_ENGINE
    assert new['frames']==old['frames']


def test_source34_cold_audio_has_separate_policy_and_engine(tmp_path):
    options={'clock_policy':'projectmtv-jni-rounded-nanoseconds30-v1',
             'preset_progress_policy':'projectmtv-core-2.3.34-cold-jni-v1','entropy_seed':12345}
    result,new=run_audio(NEW,tmp_path,np.zeros(2*1470),fps=30,frames=2,**options)
    assert result.returncode==0,result.stderr
    options['preset_progress_policy']='projectmtv-core-2.3.31-cold-jni-v1'
    result,old=run_audio(OLD,tmp_path,np.zeros(2*1470),fps=30,frames=2,**options)
    assert result.returncode==0,result.stderr
    assert new['engine_identity']==CORE_2334_ENGINE
    assert new['frames']==old['frames']
    assert new['preset_timing']['sampled_duration_seconds']==old['preset_timing']['sampled_duration_seconds']
    result,bad=run_audio(NEW,tmp_path,np.zeros(2*1470),fps=30,frames=2,**options)
    assert result.returncode!=0 and bad is None


def test_source34_noise_keeps_production_seed_and_exact_identity(tmp_path):
    result,new=generate(NEW,tmp_path,'new34')
    assert result.returncode==0,result.stderr
    result,old=generate(OLD,tmp_path,'old31')
    assert result.returncode==0,result.stderr
    data=json.loads((new/'manifest.json').read_text())
    assert data['engine_identity']==CORE_2334_ENGINE
    for name in NAMES:
        assert (new/(name+'.u32le')).read_bytes()==(old/(name+'.u32le')).read_bytes()
