"""Integrated source31 admission and resolved path policies; no reference frames."""
import json
from pathlib import Path
import subprocess
import numpy as np
import pytest
from engine_profiles import CORE_2331_ENGINE,CORE_2331_DISPLAY,CORE_2331_LEGACY_WARP,matches
from test_core2331_warp import BINARIES,read_source


def test_exact31_profile_and_reader_lookup(tmp_path):
    from forecast import read_source as declared_read,PRODUCTION_EQUATION_ENGINES
    path=tmp_path/'named.milk';path.write_text('[preset00]\nfWaveAlpha=.3\n')
    source=declared_read(path,reader=BINARIES/'milk-native-reader')
    assert matches(CORE_2331_ENGINE)
    assert PRODUCTION_EQUATION_ENGINES['projectmtv-core-2.3.31-cold-thread-v1']==CORE_2331_ENGINE
    assert source['parser_inputs']['setting_lookup_policy']=='native-case-insensitive-v1'
    assert source['values'].get('fWaveAlpha')=='.3'
    assert not matches({**CORE_2331_ENGINE,'patches_sha256':'0'*64})


def audio(tmp_path,count=3):
    pcm=tmp_path/'audio.f32';np.zeros(count*2940,dtype='<f4').tofile(pcm)
    output=tmp_path/'audio.json';request=tmp_path/'request.json'
    request.write_text(json.dumps({'pcm_path':str(pcm),'output':str(output),'fps':15,'frames':count,'channels':1}))
    result=subprocess.run([str(BINARIES/'milk-audio-inputs'),str(request)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    return json.loads(output.read_text())


@pytest.mark.parametrize('work_policy',['full-grid-v1','uniform-proof-v1'])
def test_source31_default_and_opt_in_forecast_export_migrated_policies(tmp_path,work_policy):
    from forecast import forecast_source,read_source as declared_read
    path=tmp_path/'legacy.milk'
    path.write_text('[preset00]\nwarp=.8\nfWaveAlpha=0\nfDecay=1\nfGammaAdj=1.0005\n'
                    'per_pixel_1=q1=q1+1;dx=q1*.0001;\n')
    source=declared_read(path,reader=BINARIES/'milk-native-reader')
    domain={'width':16,'height':8,'mesh_x':8,'mesh_y':8,'profile':'gles300',
            'initial_rgba':[.1,.2,.3,1],'hue_offsets':[0]*4,'equation_seed':0x4141f00d,
            'equation_rng_policy':'projectmtv-core-2.3.31-cold-thread-v1',
            'blur_levels':0,'quantize':True}
    if work_policy!='full-grid-v1':domain['shader_work_policy']=work_policy
    result=forecast_source(source,audio=audio(tmp_path),binaries=BINARIES,domain=domain,compatibility={})
    assert result['status']=='computed'
    assert result['uses_rendered_reference'] is False
    assert result['appearance_accuracy_verified'] is False
    assert result['provenance']['legacy_control_policy']==CORE_2331_DISPLAY
    assert result['provenance']['legacy_warp_policy']==CORE_2331_LEGACY_WARP
    assert result['provenance']['builtin_wave_appearance_policy']=='projectmtv-core-2.3.31-original-wave-appearance-v1'
    assert result['provenance']['motion_map_policy']=='projectmtv-core-2.3.31-continuous-motion-v1'
    assert result['provenance']['motion_uv_backend']=='conditional'
    assert len(result['source_features']['features'])==47
    assert result['provenance']['shader_work_policy']==work_policy


def test_source31_named_constants_are_double_legacy_values(tmp_path):
    from scene_equations import execute_scene
    from test_core2331_warp import inputs
    source,reader=read_source(tmp_path,'per_frame_1=q1=$pi;q2=$E;q3=$phi;q4=above($PI,3.1415927);\n')
    main=execute_scene(source,inputs(),reader=reader,mesh_x=8,mesh_y=8)['frames'][0]['main']
    assert [main['q1'],main['q2'],main['q3']]==[3.141592653589793,2.71828183,1.61803399]
    assert main['q4']==0
