import pytest
from analyzer_test_profiles import historical_source, historical_shader
import copy,hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def inputs():
    evidence=json.loads((ROOT/'tools/milk-analyzer/fixtures/random-binding-host-context-37.json').read_text())
    rows=evidence['bindings'];preset=rows[0]['preset_sha256']
    source={'preset_sha256':preset}
    import cv2,numpy as np
    assets={}
    for row in rows:
        path=ROOT/row['asset_path']
        image=cv2.imdecode(np.frombuffer(path.read_bytes(),dtype=np.uint8),cv2.IMREAD_UNCHANGED)
        height,width=image.shape[:2]
        assets[row['asset_path']]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'width':width,'height':height,'loading_policy':'soil2-multiply-alpha-pot-ceil'}
    patch=hashlib.sha256((ROOT/'tools/projectm-patches/0037-random-texture-alias-bindings.patch').read_bytes()).hexdigest()
    return source,evidence,assets,patch


def test_host_context_preserves_verified_aliases_and_selected_assets():
    from random_binding_context import verified_context
    source,evidence,assets,patch=inputs()
    result=verified_context(source,stage='composite',profile='glsl330',evidence=evidence,asset_metadata=assets,policy_patch_sha256=patch)
    assert result['samplers']=={'sampler_rand00':'sampler2D','sampler_rand01':'sampler2D'}
    assert result['selected_assets']['sampler_rand00']['asset_sha256']==evidence['bindings'][0]['asset_sha256']
    assert result['full_render_gl_error']==0
    assert result['appearance_verified'] is False


def test_stale_source_assets_or_policy_do_not_clear_context():
    from random_binding_context import verified_context
    source,evidence,assets,patch=inputs()
    for mutation in ['source','asset','patch','alias']:
        s=copy.deepcopy(source);e=copy.deepcopy(evidence);a=copy.deepcopy(assets);p=patch
        if mutation=='source':s['preset_sha256']='0'*64
        elif mutation=='asset':a[e['bindings'][0]['asset_path']]['sha256']='0'*64
        elif mutation=='patch':p='0'*64
        else:e['bindings'][0]['uniform']='sampler_rand99'
        assert verified_context(s,stage='composite',profile='glsl330',evidence=e,asset_metadata=a,policy_patch_sha256=p) is None


def test_host_evidence_does_not_claim_android_profile_validation():
    from random_binding_context import verified_context
    source,evidence,assets,patch=inputs()
    assert verified_context(source,stage='composite',profile='gles300',evidence=evidence,asset_metadata=assets,policy_patch_sha256=patch) is None


def test_framebuffer_error_is_retained_with_valid_binding_identity():
    from random_binding_context import verified_context
    source,evidence,assets,patch=inputs();source['preset_sha256']=evidence['preset_results'][2]['preset_sha256']
    result=verified_context(source,stage='composite',profile='glsl330',evidence=evidence,asset_metadata=assets,policy_patch_sha256=patch)
    assert result['samplers']=={'sampler_rand00':'sampler2D','sampler_rand01':'sampler2D'}
    assert result['full_render_gl_error']==1286
    assert result['appearance_verified'] is False


@pytest.mark.historical_profile("merged37")
def test_exact_three_shader_sections_lower_only_with_valid_context():
    from coverage_audit import audit_source
    source_stub,evidence,assets,patch=inputs()
    for outcome in evidence['preset_results']:
        path=ROOT/outcome['preset_path'];raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==outcome['preset_sha256']
        # Read exact archived source evidence; no ignored corpus cache.
        source=historical_source('merged37',raw)
        section=source['sections']['comp_']
        declarations=[v for n in section['tree'] if n['kind']=='declarations' for v in n['values']]
        compat=historical_shader('merged37',section['source'],stage='composite',profile='glsl330',
            samplers={v['name']:v['type']['name'] for v in declarations if v['type']['name'] in {'sampler2D','sampler3D'}},
            texture_sizes=[v['name'] for v in declarations if v['name'].startswith('texsize_') and v['type']['name']=='float4'])
        kwargs=dict(cache=source,reader_sha=source['reader_sha256'],equation_loader_policy='projectmtv-core-2.2.8-v1',
                    shader_profile='glsl330',shader_compatibility={'composite':compat})
        absent=audit_source(raw,**kwargs)
        observed=audit_source(raw,**kwargs,random_binding_evidence=evidence,asset_metadata=assets,random_policy_patch_sha256=patch)
        unit=lambda result:next(u for u in result['units'] if u['section']=='comp_' and u['loader_numbering_reachable'])
        assert not unit(absent)['lowering_complete']
        assert unit(observed)['lowering_complete'],unit(observed)['lowering_unknowns']
        assert unit(observed)['random_binding_context']['full_render_gl_error']==outcome['full_render_gl_error']
        assert observed['visual_gate']['eligible'] is False


def test_unit_collisions_cross_stage_slot_conflicts_and_wrong_dimensions_reject():
    from random_binding_context import verified_context
    source,evidence,assets,patch=inputs()
    for mutation in ['unit','slot','dimensions']:
        e=copy.deepcopy(evidence)
        if mutation=='unit':e['bindings'][1]['unit']=e['bindings'][0]['unit']
        elif mutation=='slot':
            row=copy.deepcopy(e['bindings'][1]);row.update(stage='warp',slot=0,requested_alias='rand00',uniform='sampler_rand00',texsize_uniform='texsize_rand00');e['bindings'].append(row)
        else:e['bindings'][0]['width']=1
        assert verified_context(source,stage='composite',profile='glsl330',evidence=e,asset_metadata=assets,policy_patch_sha256=patch) is None


def test_missing_source_and_policy_hashes_are_not_a_valid_identity():
    from random_binding_context import verified_context
    _,evidence,assets,_=inputs();evidence['patch_sha256']=None
    assert verified_context({},stage='composite',profile='glsl330',evidence=evidence,asset_metadata=assets,policy_patch_sha256=None) is None
