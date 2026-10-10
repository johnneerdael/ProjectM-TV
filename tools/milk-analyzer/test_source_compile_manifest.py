"""Source-bound offline compile evidence, separate from GPU/binding acceptance."""
import copy
import json
from pathlib import Path
import pytest
from test_effect_families import read
from corpus_store import digest

ROOT=Path(__file__).resolve().parents[2]
BINS=ROOT/'build/preset-corpus/source34/adapters'


def fixture(tmp_path,code='shader_body {ret=GetPixel(uv);}'):
    from forecast import read_source
    from shader_compat import check_shader
    from analyzer_test_profiles import validator_path
    p=tmp_path/'one.milk';p.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nfWaveAlpha=0\ncomp_1=`'+code+'\n')
    source=read_source(p,reader=BINS/'milk-native-reader')
    code=source['sections']['comp_']['source']
    report=check_shader(code,stage='composite',profile='gles300',translator=BINS/'milk-shader-translate',validator=validator_path(),samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_main'])
    m={'schema_version':1,'kind':'source-offline-compatibility-set','profile':'gles300',
       'engine':source['parser_inputs']['engine'],'engine_archive_sha256':source['parser_inputs']['engine_archive_sha256'],
       'compiler_inputs':{k:report[k] for k in ('translator_sha256','validator_sha256')},
       'native_driver_verified':False,'runtime_texture_bindings_verified':False,
       'binding_assumptions':'Explicit sampler declarations are conditional runtime inputs, not observed texture bindings',
       'presets':{source['preset_sha256']:{'composite':report}}}
    m['record_sha256']=digest(m)
    return p,source,m


def seal(m):
    m.pop('record_sha256',None);m['record_sha256']=digest(m);return m


def test_compile_manifest_resolves_candidate_branch_without_rendering(tmp_path):
    from effect_family_export import export_preset
    p,s,m=fixture(tmp_path)
    record,_=export_preset(p,reader=BINS/'milk-native-reader',compile_manifest=m)
    assert record['analysis']['stages']['composite']['kind']=='custom_composite'
    assert record['analysis']['stages']['composite']['conditional_on_native_profile'] is True
    assert record['analysis']['uses_rendered_images'] is False
    assert record['analysis']['uses_shader_execution'] is False
    assert record['provenance']['offline_compile_evidence']['record_sha256']==m['record_sha256']
    assert record['provenance']['offline_compile_evidence']['runtime_texture_bindings_verified'] is False


@pytest.mark.parametrize('mutation',[
 lambda m:m.update(profile='glsl330'),
 lambda m:m.update(engine_archive_sha256='0'*64),
 lambda m:m.update(native_driver_verified=True),
 lambda m:m.update(runtime_texture_bindings_verified=True),
 lambda m:m['compiler_inputs'].update(translator_sha256='0'*64),
 lambda m:next(iter(m['presets'].values()))['composite']['request'].update(code='shader_body {ret=0;}'),
 lambda m:next(iter(m['presets'].values()))['composite'].update(offline_accepted=1),
 lambda m:m.update(schema_version=True),
 lambda m:next(iter(m['presets'].values()))['composite'].update(native_driver_verified=True),
 lambda m:next(iter(m['presets'].values()))['composite'].update(request=[]),
])
def test_incompatible_manifest_cannot_select_branch(tmp_path,mutation):
    from effect_family_export import export_preset
    p,s,m=fixture(tmp_path);mutation(m);seal(m)
    with pytest.raises(ValueError):export_preset(p,reader=BINS/'milk-native-reader',compile_manifest=m)


def test_unsealed_change_is_rejected_before_cache_lookup(tmp_path):
    from effect_family_export import export_preset
    p,s,m=fixture(tmp_path);export_preset(p,reader=BINS/'milk-native-reader',compile_manifest=m,cache=tmp_path/'cache')
    m['binding_assumptions']='changed'
    with pytest.raises(ValueError,match='hash'):export_preset(p,reader=BINS/'milk-native-reader',compile_manifest=m,cache=tmp_path/'cache')


def test_missing_case_keeps_stage_unknown_instead_of_borrowing_other_shader(tmp_path):
    from effect_family_export import export_preset
    p,s,m=fixture(tmp_path);m['presets']={};seal(m)
    record,_=export_preset(p,reader=BINS/'milk-native-reader',compile_manifest=m)
    assert record['analysis']['stages']['composite']['kind']=='unknown'
    assert record['provenance']['offline_compile_evidence']['preset_record_present'] is False


def test_compile_rejection_keeps_explicit_offline_fallback_candidate(tmp_path):
    from effect_family_export import export_preset
    p,s,m=fixture(tmp_path,'shader_body {ret=unknown_function(uv);}')
    report=m['presets'][s['preset_sha256']]['composite'];assert report['offline_accepted'] is False
    r,_=export_preset(p,reader=BINS/'milk-native-reader',compile_manifest=m)
    assert r['analysis']['stages']['composite']['kind']=='default_composite'
    assert r['analysis']['stages']['composite']['conditional_on_native_profile'] is True


def test_cli_records_manifest_hash_and_paired_source_result(tmp_path):
    from effect_family_export import main
    p,s,m=fixture(tmp_path);mf=tmp_path/'compile.json';mf.write_text(json.dumps(m));out=tmp_path/'out'
    assert main([str(p),'--reader',str(BINS/'milk-native-reader'),'--output',str(out),'--compile-manifest',str(mf)])==0
    r=json.loads((out/'results/one.json').read_text());assert r['analysis']['stages']['composite']['kind']=='custom_composite'
    cfg=json.loads((out/'run-manifest.json').read_text())['configuration'];assert cfg['compile_manifest_file_sha256']


def test_manifest_change_inside_last_preset_is_rejected_before_completion(tmp_path,monkeypatch):
    import effect_family_export as export
    p,s,m=fixture(tmp_path);mf=tmp_path/'compile.json';mf.write_text(json.dumps(m));out=tmp_path/'out'
    real=export.export_preset
    def mutate(*args,**kwargs):
        result=real(*args,**kwargs);mf.write_text('{}');return result
    monkeypatch.setattr(export,'export_preset',mutate)
    assert export.main([str(p),'--reader',str(BINS/'milk-native-reader'),'--output',str(out),'--compile-manifest',str(mf)])==2
    assert not (out/'results/one.json').exists()
