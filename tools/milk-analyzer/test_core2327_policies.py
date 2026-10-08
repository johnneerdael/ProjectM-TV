"""Exact PR59 input admission; rendered preset qualification is separate."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest


ENGINE = {
    'commit': '6f64807467e312034883a4389e6aa80a675458bc',
    'patches_sha256': '65313919430bd6d1531292b405463d8ec400a44bcfddfb1eb808fbaba16b5ad0',
}


@pytest.fixture
def core2327_adapters():
    variable=os.environ.get('MILK_TEST_2327_BINARIES')
    if variable is None:pytest.skip('explicit prepared PR59 source adapters required')
    folder=Path(variable)
    for name in ['milk-wave-inputs','milk-audio-inputs','milk-noise-inputs']:
        if not (folder/name).is_file():pytest.skip('missing PR59 adapter: '+name)
    return folder


def run_request(binary,path,request):
    path.write_text(json.dumps(request))
    return subprocess.run([str(binary),str(path)],capture_output=True,text=True)


def assert_identity(report,folder):
    assert report['engine_identity']==ENGINE
    archive=folder.parent/'native-build/projectm/src/libprojectM/libprojectM-4.a'
    assert archive.is_file(),'prepared PR59 archive required'
    assert report['engine_archive_sha256']==hashlib.sha256(archive.read_bytes()).hexdigest()
    assert report['uses_rendered_reference'] is False


def test_core2327_live_wave_retains_exact_source_identity(tmp_path,core2327_adapters):
    from test_native_wave import frame
    output=tmp_path/'wave.json'
    result=run_request(core2327_adapters/'milk-wave-inputs',tmp_path/'request.json',dict(
        mode=1,mode_policy='evaluated-live-v1',width=256,height=144,output=str(output),
        frames=[frame(time=1/30,wave_mode=1,wave_x=.5,wave_y=.5,wave_mystery=0,wave_a=.5,vol=1)]))
    assert result.returncode==0,result.stderr
    report=json.loads(output.read_text());assert_identity(report,core2327_adapters)
    assert report['mode_policy']=='evaluated-live-v1'
    assert report['frames'][0]['closed_loop'] is False


def test_core2327_cold_audio_uses_its_own_label_and_rejects_core2325(tmp_path,core2327_adapters):
    pcm=tmp_path/'pcm.f32';np.zeros(2*1470,dtype='<f4').tofile(pcm)
    output=tmp_path/'audio.json';path=tmp_path/'request.json'
    request=dict(pcm_path=str(pcm),output=str(output),fps=30,frames=2,channels=1,
                 clock_policy='projectmtv-jni-rounded-nanoseconds30-v1')
    binary=core2327_adapters/'milk-audio-inputs'
    probe=run_request(binary,path,request);assert probe.returncode==0,probe.stderr
    report=json.loads(output.read_text());assert_identity(report,core2327_adapters)
    # Rejecting old labels stays checked even on an unqualified host library.
    rejected=run_request(binary,path,{**request,'output':str(tmp_path/'rejected.json'),
        'preset_progress_policy':'projectmtv-core-2.3.25-cold-jni-v1','entropy_seed':12345})
    assert rejected.returncode!=0
    assert not (tmp_path/'rejected.json').exists()
    if report['duration_distribution_model']!='libcxx-200100-fresh-normal-v1':
        pytest.skip('qualified libcxx-200100 cold runtime required')
    result=run_request(binary,path,{**request,
        'preset_progress_policy':'projectmtv-core-2.3.27-cold-jni-v1','entropy_seed':12345})
    assert result.returncode==0,result.stderr
    report=json.loads(output.read_text());assert_identity(report,core2327_adapters)
    assert report['frames'][0]['fps']==35
    assert report['preset_timing']['duration_draws']==3


def test_core2327_raw_noise_requires_production_seed_policy(tmp_path,core2327_adapters):
    request=dict(names=['noise_lq_lite'],seed=3567620661,
                 seed_policy='production-clock-seed-v1',output=str(tmp_path/'noise'))
    binary=core2327_adapters/'milk-noise-inputs';path=tmp_path/'request.json'
    result=run_request(binary,path,request);assert result.returncode==0,result.stderr
    report=json.loads(result.stdout);assert_identity(report,core2327_adapters)
    assert report['seed_model']=='raw-declared-native-noise-v1'
    assert report['textures']['noise_lq_lite']['generator_seed']==3567620661
    rejected=run_request(binary,path,{**request,'seed_policy':'lab-subsystem-seed-v1',
                                     'output':str(tmp_path/'rejected')})
    assert rejected.returncode!=0
    assert not (tmp_path/'rejected').exists()
