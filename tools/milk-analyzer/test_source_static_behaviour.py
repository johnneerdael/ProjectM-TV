"""End-to-end source behaviour uses native selection and declared context."""
import pytest


def analysis(raw, *, qualified=True):
    from test_effect_families import read
    from effect_families import _Analysis
    import hashlib
    source=read(raw)
    compatibility={}
    if qualified:
        for stage,prefix in [('warp','warp_'),('composite','comp_')]:
            if source['sections'].get(prefix,{}).get('source'):
                code=source['sections'][prefix]['source']
                compatibility[stage]={'source_sha256':hashlib.sha256(code.encode()).hexdigest(),
                    'request':{'code':code,'stage':stage,'profile':'gles300'},
                    'translation':{'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256']},
                    'offline_accepted':True}
    a=_Analysis(source,'gles300',compatibility if qualified else None)
    a.input_scenario=None
    a.main_equations();a.primitives();a.shader('warp','warp_');a.shader('composite','comp_');a.contribution_gates()
    return a


def test_declared_context_rejects_invalid_viewport_and_fps():
    from source_static_behaviour import validate_context
    with pytest.raises(ValueError):validate_context({'viewport':[0,1080],'feedback_fps':30})
    with pytest.raises(ValueError):validate_context({'viewport':[1920,1080],'feedback_fps':float('nan')})


def test_constant_qualified_composite_can_have_complete_calm_model():
    from source_appearance import appearance_from_analysis
    from source_static_behaviour import static_behaviour
    a=analysis('PSVERSION_COMP=2\nfWaveAlpha=0\ncomp_1=`shader_body {ret=float3(.1,.2,.3);}\n')
    result=static_behaviour(a,appearance_from_analysis(a),{'viewport':[1920,1080],'feedback_fps':30})
    assert result['uses_rendered_images'] is False
    assert result['uses_equation_execution'] is False
    assert result['output_model_complete'] is True
    assert 'Chill' in result['classification']['eligible_bands']


def test_unqualified_composite_cannot_certify_chill():
    from source_appearance import appearance_from_analysis
    from source_static_behaviour import static_behaviour
    a=analysis('PSVERSION_COMP=2\nfWaveAlpha=0\ncomp_1=`shader_body {ret=float3(.1,.2,.3);}\n',qualified=False)
    result=static_behaviour(a,appearance_from_analysis(a),{'viewport':[1920,1080],'feedback_fps':30})
    assert result['output_model_complete'] is False
    assert result['classification']['eligible_bands']==[]


def test_activity_domain_changes_context_identity():
    from source_appearance import appearance_from_analysis
    from source_static_behaviour import static_behaviour
    a=analysis('fWaveAlpha=0\nfRot=.01\nwarp=0\nzoom=1\n')
    desc=appearance_from_analysis(a)
    first=static_behaviour(a,desc,{'viewport':[1920,1080],'feedback_fps':15})
    second=static_behaviour(a,desc,{'viewport':[1920,1080],'feedback_fps':30})
    assert first['context_sha256']!=second['context_sha256']


def test_normal_static_export_includes_behaviour_without_execution(tmp_path):
    from effect_family_export import export_preset
    from test_core2331_warp import BINARIES
    path=tmp_path/'behaviour.milk';path.write_text('[preset00]\nfWaveAlpha=0\n')
    result,_=export_preset(path,reader=BINARIES/'milk-native-reader')
    report=result['analysis']['visual_description']['static_behaviour']
    assert report['uses_shader_execution'] is False
    assert report['uses_equation_execution'] is False
    assert report['uses_rendered_images'] is False
    assert report['context']['feedback_fps']==30


def test_changed_behaviour_context_separates_export_cache(tmp_path):
    from effect_family_export import export_preset
    from test_core2331_warp import BINARIES
    path=tmp_path/'behaviour.milk';path.write_text('[preset00]\nfWaveAlpha=0\n')
    kwargs={'reader':BINARIES/'milk-native-reader','cache':tmp_path/'cache'}
    first,_=export_preset(path,behaviour_context={'viewport':[1920,1080],'feedback_fps':15},**kwargs)
    second,hit=export_preset(path,behaviour_context={'viewport':[1920,1080],'feedback_fps':30},**kwargs)
    assert hit is False and first['cache_key']!=second['cache_key']


def test_static_report_joins_hue_candidates_and_hashes_colour_model():
    from source_appearance import appearance_from_analysis
    a=analysis('PSVERSION_COMP=2\nfWaveAlpha=0\ncomp_1=`shader_body {ret=float3(.1,.2,.3);}\n')
    report=appearance_from_analysis(a)['static_behaviour']
    assert report['colour']['uses_rendered_images'] is False
    assert report['colour']['components']
    assert 'source_colour_character.py' in report['model_sources']


@pytest.mark.parametrize('body',[
    'while(bass>0){}ret=float3(.1,.2,.3);',
    'float x[1]={0};x[int(time)]=1;ret=float3(.1,.2,.3);',
])
def test_unresolved_execution_cannot_certify_constant_output_as_chill(body):
    from source_appearance import appearance_from_analysis
    a=analysis('PSVERSION_COMP=2\nfWaveAlpha=0\ncomp_1=`shader_body {'+body+'}\n')
    result=appearance_from_analysis(a)['static_behaviour']
    assert result['output_model_complete'] is False
    assert result['classification']['eligible_bands']==[]


def test_discard_shader_retains_partial_report_without_crashing():
    from source_appearance import appearance_from_analysis
    a=analysis('PSVERSION_COMP=2\nfWaveAlpha=0\ncomp_1=`shader_body {clip(-1);ret=float3(.1,.2,.3);}\n')
    result=appearance_from_analysis(a)['static_behaviour']
    assert result['output_model_complete'] is False
    assert result['classification']['eligible_bands']==[]
