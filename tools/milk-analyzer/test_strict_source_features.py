"""Strict extraction evaluates source math without constructing display fields."""
import importlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from test_shader_loops import lower


def query(expression, inputs, **settings):
    return importlib.import_module('strict_source_features').colour_queries(expression, inputs, **settings)


def test_uniform_shader_colour_has_whole_viewport_independence_evidence():
    model,expression=lower('shader_body {ret=float3(.8,.2,.1);}')
    assert model.complete
    result=query(expression,[{'_uv':[.1,.2]},{'_uv':[.9,.8]}])
    assert result['status']=='computed'
    assert result['uses_display_fields'] is False
    assert result['spatially_uniform'] is True
    assert result['palette']['warm_cool']==pytest.approx(1)
    assert result['query_count']==2


def test_spatial_colour_samples_are_not_called_screen_area():
    model,expression=lower('shader_body {ret=float3(uv.x,1-uv.x,0);}')
    assert model.complete
    result=query(expression,[{'_uv':[0,0]},{'_uv':[1,0]}])
    assert result['status']=='computed'
    assert result['spatially_uniform'] is False
    assert result['coverage_kind']=='isolated shader queries; screen area unproved'


def test_feedback_dependent_colour_is_unknown_without_a_source_texture_function():
    model,expression=lower('shader_body {ret=GetPixel(uv);}')
    assert model.complete
    result=query(expression,[{'_uv':[.5,.5]}])
    assert result['status']=='unknown'
    assert result['palette'] is None
    assert any('texture' in reason for reason in result['unknown_reasons'])


def test_missing_branch_inputs_and_invalid_math_are_unknown_not_black():
    for code in ['ret=bass;', 'ret=1/uv.x;']:
        model,expression=lower('shader_body {'+code+'}')
        assert model.complete
        result=query(expression,[{'_uv':[0,0]}])
        assert result['status']=='unknown'
        assert result['palette'] is None


def test_shader_float_colour_is_clamped_to_declared_unorm_output():
    model,expression=lower('shader_body {ret=float3(2,-1,.5);}')
    assert model.complete
    result=query(expression,[{}])
    assert result['rgb_queries']==[[1,0,.5]]


def test_query_budget_is_declared_and_cannot_silently_sample_a_prefix():
    model,expression=lower('shader_body {ret=1;}')
    assert model.complete
    with pytest.raises(ValueError,match='budget'):
        query(expression,[{}]*4,max_queries=3)


def test_loops_do_not_establish_spatial_independence_from_hidden_plan_inputs():
    model,expression=lower('shader_body {float v=0;int i=0;while(i<uv.x){v+=.1;i++;}ret=v;}')
    assert model.complete
    result=query(expression,[{'_uv':[1,0]}])
    assert result['status']=='computed'
    assert result['spatially_uniform'] is False


def test_uniform_input_selection_does_not_read_unused_nonfinite_q_banks():
    from shader_uniforms import source_uniforms
    scene={'viewport':[32,32],'frames':[{'render_inputs':{'time':1,'fps':30,'frame':1,'progress':0,
        'bass':2,'mid':1,'treb':1,'bass_att':1,'mid_att':1,'treb_att':1},
        'main':{f'q{i}':{'ieee':'nan'} for i in range(1,33)}}]}
    result=source_uniforms(scene,0,names={'_c3'})
    assert result['_c3'][0]==2
    assert not any(name.startswith('_q') for name in result)


def test_strict_cli_outputs_cached_evidence_without_native_frame_arrays(tmp_path):
    # Use the same prepared source49 adapter location as the policy controls.
    folder=Path(__file__).resolve().parents[2]/'build/visual-loop/source49/adapters'
    if not (folder/'milk-native-reader').is_file():pytest.skip('prepared source49 adapters required')
    from test_scene_equations import frames
    preset=tmp_path/'strict.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'
                     'comp_1=`shader_body {ret=float3(.8,.2,.1);}\n')
    audio=tmp_path/'audio.json'
    reader_output=subprocess.check_output([str(folder/'milk-native-reader'),str(preset)],text=True)
    archive=json.loads(reader_output)['parser_inputs']['engine_archive_sha256']
    audio.write_text(json.dumps({'uses_rendered_reference':False,'engine_archive_sha256':archive,
                                'pcm_sha256':'1'*64,'frames':frames()}))
    output=tmp_path/'features.json'
    command=[sys.executable,str(Path(__file__).with_name('source_extract.py')),
        '--preset',str(preset),'--audio',str(audio),'--binaries',str(folder),
        '--profile','gles300','--width','32','--height','32','--output',str(output)]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    evidence=json.loads(output.read_text())
    assert evidence['feature_basis']=='strict-source-no-display-frames'
    assert evidence['features']['palette.warm_cool']['value']==pytest.approx(1)
    assert evidence['features']['palette.coloured_support']['value']==1
    assert 'display' not in evidence and 'feedback' not in evidence


def test_unused_frame_wrap_does_not_block_uniform_composite_queries(tmp_path):
    folder=Path(__file__).resolve().parents[2]/'build/visual-loop/source49/adapters'
    if not (folder/'milk-native-reader').is_file():pytest.skip('prepared source49 adapters required')
    from forecast import read_source
    from shader_compat import check_shader
    from analyzer_test_profiles import validator_path
    from test_scene_equations import frames
    from strict_source_features import strict_features
    preset=tmp_path/'unused-wrap.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'
        'per_frame_1=wrap=exp(1000);\ncomp_1=`shader_body {ret=float3(.8,.2,.1);}\n')
    source=read_source(preset,reader=folder/'milk-native-reader')
    compatibility={'composite':check_shader(source['sections']['comp_']['source'],stage='composite',
        profile='gles300',translator=folder/'milk-shader-translate',validator=validator_path(),
        samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])}
    audio={'uses_rendered_reference':False,'pcm_sha256':'1'*64,
           'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256'],'frames':frames()}
    domain={'profile':'gles300','width':32,'height':32,'mesh_x':8,'mesh_y':8,'equation_seed':1}
    result=strict_features(source,audio=audio,binaries=folder,domain=domain,compatibility=compatibility)
    assert result['features']['palette.warm_cool']['value']==pytest.approx(1)


def test_first_direct_api_call_cannot_stamp_changed_disk_code_as_loaded_code(tmp_path):
    import shutil
    import os
    root=Path(__file__).parent
    for path in root.glob('*.py'):
        if not path.name.startswith('test_'):shutil.copyfile(path,tmp_path/path.name)
    code='''from pathlib import Path
import strict_source_features as module
path=Path('shader_uniforms.py');path.write_text(path.read_text()+'\\n# changed after strict import\\n')
try:
 module.strict_features({},audio={},binaries=Path('.'),domain={},compatibility={})
except ValueError as error:
 assert 'fresh process' in str(error),str(error)
else:raise AssertionError('changed disk code was accepted')
'''
    result=subprocess.run([sys.executable,'-c',code],cwd=tmp_path,
        env={**os.environ,'PYTHONPATH':str(tmp_path)},capture_output=True,text=True)
    assert result.returncode==0,result.stderr
