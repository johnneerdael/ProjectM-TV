"""Exact release31 audio identity; cadence and cold-JNI scope stay distinct."""
import json
import numpy as np
import pytest
from test_corpus15_audio import run_audio
from test_core2331_warp import BINARIES,ROOT
from engine_profiles import CORE_2331_ENGINE


def test_source31_general_audio_matches_unchanged29_equations(tmp_path):
    samples=.3*np.sin(2*np.pi*80*np.arange(3*2940)/44100)
    result,new=run_audio(BINARIES,tmp_path,samples,frames=3)
    assert result.returncode==0,result.stderr
    result,old=run_audio(ROOT/'build/preset-corpus/source29/adapters',tmp_path,samples,frames=3)
    assert result.returncode==0,result.stderr
    assert new['engine_identity']==CORE_2331_ENGINE
    assert new['frames']==old['frames']


def test_source31_cold_policy_exact_identity_and_bounded_scope(tmp_path):
    options={'clock_policy':'projectmtv-jni-rounded-nanoseconds30-v1',
             'preset_progress_policy':'projectmtv-core-2.3.31-cold-jni-v1','entropy_seed':12345}
    result,report=run_audio(BINARIES,tmp_path,np.zeros(2*1470),fps=30,frames=2,**options)
    if 'qualified libcxx-200100' in result.stderr:
        pytest.skip('qualified duration distribution unavailable')
    assert result.returncode==0,result.stderr
    assert report['engine_identity']==CORE_2331_ENGINE
    assert report['preset_timing']['physical_fps']==30
    for fps,count in [(15,2),(30,31)]:
        result,report=run_audio(BINARIES,tmp_path,np.zeros(count*(44100//fps)),fps=fps,frames=count,**options)
        assert result.returncode!=0
        assert report is None
    result,report=run_audio(ROOT/'build/preset-corpus/source29/adapters',tmp_path,np.zeros(2*1470),
                             fps=30,frames=2,**options)
    assert result.returncode!=0
    assert report is None
