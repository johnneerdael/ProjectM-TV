"""Conditional language understanding must not fabricate selected images."""
from analyzer_test_profiles import historical_source, historical_shader, FIXTURES
import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from coverage_audit import audit_source
from field_math import evaluate, UnresolvedMath
from shader_fields import ShaderFields
from random_binding_contract import native_contract, METHODS, SOURCE_FILES

ROOT = Path(__file__).resolve().parents[2]
POLICY = 'projectmtv-random-slot-inputs-v1'
CASES = [
    ('EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3 2.milk',
     '5dd383cf79e1aacbed944ded85d70a365dde2c51f2ca7646ed0b7fde0cf4c79f'),
    ('EoS - glowsticks v2 04 music minimal - swim  - dictatutorial rt roam3.milk',
     '06b84ff69c3aeeb88eff3dea63dd3c1f5b146b4c2afb9df204f5f2561e7aee15'),
    ('midgitstraights of majillaen - featy sweet.milk',
     'd4cd997dedc57ab34c7247fee1ba94d4061528d12d16cde5a468145fb216ebba')]


def inputs(path):
    raw = path.read_bytes()
    source = historical_source('random_contract',raw)
    section = source['sections']['comp_']
    declarations = [v for node in section['tree'] if node['kind'] == 'declarations'
                    for v in node['values']]
    samplers = {v['name']: 'sampler2D' if v['type']['name']=='sampler' else v['type']['name']
                for v in declarations if v['type']['name'] in {'sampler', 'sampler2D', 'sampler3D'}}
    compatibility = historical_shader('random_contract',section['source'], stage='composite', profile='gles300',
        samplers=samplers,
        texture_sizes=[v['name'] for v in declarations
                       if v['name'].startswith('texsize_') and v['type']['name'] == 'float4'])
    assert compatibility['offline_accepted'], compatibility
    return raw, source, compatibility


def audit(raw, source, compatibility, **kwargs):
    return audit_source(raw, cache=source, reader_sha=source['reader_sha256'],
        equation_loader_policy='projectmtv-core-2.2.8-v1', shader_profile='gles300',
        shader_compatibility={'composite': compatibility}, **kwargs)


def composite(report):
    return next(u for u in report['units'] if u['section'] == 'comp_' and
                u['loader_numbering_reachable'])


@pytest.mark.parametrize('name,digest', CASES)
def test_exact_gles_sections_need_contract_and_retain_runtime_obligations(name, digest):
    raw, source, compatibility = inputs(ROOT / 'core/src/main/assets/presets' / name)
    assert hashlib.sha256(raw).hexdigest() == digest
    strict = audit(raw, source, compatibility)
    conditional = audit(raw, source, compatibility, random_binding_policy=POLICY)
    assert not composite(strict)['lowering_complete']
    assert composite(conditional)['lowering_complete'], composite(conditional)['lowering_unknowns']
    context = composite(conditional)['random_binding_context']
    assert context['basis'] == 'native source contract; conditional runtime inputs'
    assert context['selected_assets'] is None
    assert context['runtime_requirements']
    assert context['appearance_verified'] is False
    assert conditional['visual_gate']['eligible'] is False
    for key in ['source_tokens', 'code_tokens', 'parsed_code_tokens', 'unvisited_code_tokens']:
        assert strict[key] == conditional[key]


@pytest.mark.parametrize('mutation', ['missing', 'body', 'archive', 'scan', 'profile', 'type', 'size'])
def test_missing_or_contradictory_provenance_keeps_the_guard(mutation):
    raw, source, compatibility = inputs(ROOT / 'core/src/main/assets/presets' / CASES[0][0])
    source, compatibility = copy.deepcopy(source), copy.deepcopy(compatibility)
    if mutation == 'missing':
        source['parser_inputs'].pop('random_binding_contract', None)
    elif mutation == 'body':
        source['parser_inputs']['random_binding_contract']['body_sha256']['TextureManager.GetRandomTexture'] = '0'*64
    elif mutation == 'archive':
        source['parser_inputs']['engine_archive_sha256'] = '0'*64
    elif mutation == 'scan':
        compatibility['translation']['referenced_samplers'] = ['main']
    elif mutation == 'profile':
        compatibility['request']['profile'] = 'glsl330'
    elif mutation == 'type':
        compatibility['request']['samplers']['sampler_rand00'] = 'sampler3D'
    else:
        compatibility['request']['texture_sizes'].append('texsize_pc_rand00')
    result = audit(raw, source, compatibility, random_binding_policy=POLICY)
    assert not composite(result)['lowering_complete']
    assert 'random_binding_context' not in composite(result)


def test_slot_input_identity_preserves_alias_modes_and_requires_texture_values(tmp_path):
    from random_binding_contract import verified_contract
    path = tmp_path / 'aliases.milk'
    path.write_text('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=3\ncomp_1=`'
        'sampler sampler_pc_rand00=sampler_state {AddressU=WRAP;};'
        'sampler sampler_fw_rand00=sampler_state {AddressU=CLAMP;};'
        'shader_body {ret=(tex2D(sampler_pc_rand00,uv)+tex2D(sampler_fw_rand00,uv)).rgb*.5;}\n')
    raw, source, compatibility = inputs(path)
    compatibility = historical_shader('random_contract',source['sections']['comp_']['source'], stage='composite',
        profile='gles300',
        samplers={'sampler_pc_rand00': 'sampler2D', 'sampler_fw_rand00': 'sampler2D'}, texture_sizes=[])
    context = verified_contract(source, stage='composite', profile='gles300', compatibility=compatibility)
    assert context is not None
    aliases = context['random_inputs']
    assert aliases['sampler_pc_rand00']['slot'] == aliases['sampler_fw_rand00']['slot'] == 0
    model = ShaderFields(stage='composite', frame=3, warp_reads_blur=False)
    result = model.lower(source['sections']['comp_']['tree'], native_samplers=context['samplers'],
                         random_texture_inputs=aliases)
    assert model.complete, model.unknown
    with pytest.raises(UnresolvedMath):
        evaluate(result, inputs={'_uv': [.5, .5]})
    calls = []
    def sample(detail, coordinates):
        calls.append(detail)
        assert detail['random_texture_input']['slot'] == 0
        return np.array([.2, .4, .6, 1])
    np.testing.assert_allclose(evaluate(result, inputs={'_uv': [.5, .5]}, sample=sample), [.2, .4, .6])
    assert len(calls) == 2
    assert {c['sampling_policy']['linear'] for c in calls} == {True, False}
    assert {c['sampling_policy']['wrap'] for c in calls} == {True, False}


def test_texsize_aliases_need_one_explicit_uploaded_dimension_input(tmp_path):
    from random_binding_contract import verified_contract
    path = tmp_path/'size.milk'
    path.write_text('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=3\ncomp_1=`'
        'sampler sampler_rand00_red=sampler_state {AddressU=WRAP;};'
        'shader_body {ret=texsize_rand00_red.x+texsize_rand00.x;}\n')
    _, source, compatibility = inputs(path)
    context = verified_contract(source, stage='composite', profile='gles300', compatibility=compatibility)
    assert context is not None
    assert context['texsize_inputs']['texsize_rand00_red'] == context['texsize_inputs']['texsize_rand00']
    model = ShaderFields(stage='composite', frame=3, warp_reads_blur=False)
    result = model.lower(source['sections']['comp_']['tree'], native_samplers=context['samplers'],
        random_texture_inputs=context['random_inputs'], random_texsize_inputs=context['texsize_inputs'])
    assert model.complete, model.unknown
    with pytest.raises(UnresolvedMath):
        evaluate(result)
    np.testing.assert_allclose(evaluate(result, inputs={'texsize_rand00': [16,16,1/16,1/16]}), [32]*3)
    np.testing.assert_allclose(evaluate(result, inputs={'texsize_rand00': [32,16,1/32,1/16]}), [64]*3)


@pytest.mark.parametrize('container', ['source', 'sections', 'section', 'parser', 'compatibility', 'translation', 'request'])
@pytest.mark.parametrize('invalid', [None, [], 'invalid'])
def test_direct_verifier_fails_closed_on_malformed_containers(container, invalid):
    from random_binding_contract import verified_contract
    _, source, compatibility = inputs(ROOT/'core/src/main/assets/presets'/CASES[0][0])
    if container == 'source': source = invalid
    elif container == 'sections': source['sections'] = invalid
    elif container == 'section': source['sections']['comp_'] = invalid
    elif container == 'parser': source['parser_inputs'] = invalid
    elif container == 'compatibility': compatibility = invalid
    else: compatibility[container] = invalid
    assert verified_contract(source, stage='composite', profile='gles300', compatibility=compatibility) is None


def test_changed_warp_sampler_initializer_or_dispatcher_revokes_contract(tmp_path):
    # Reconstruct only the files the policy stamps; never edit a shared engine.
    cache = historical_source('random_contract',(ROOT/'core/src/main/assets/presets'/CASES[0][0]).read_bytes())
    assert cache['parser_inputs']['random_binding_contract']['policy'] == POLICY
    engine = FIXTURES/'random_contract'/'source'
    manifest=json.loads((engine/'sha256.json').read_text())
    for relative,digest in manifest.items():
        assert hashlib.sha256((engine/relative).read_bytes()).hexdigest()==digest
    for name in {row[0] for row in METHODS.values()} | set(SOURCE_FILES):
        relative = Path('src/libprojectM')/name
        (tmp_path/relative).parent.mkdir(parents=True,exist_ok=True)
        (tmp_path/relative).write_bytes((engine/relative).read_bytes())
    assert native_contract(tmp_path) is not None
    header = tmp_path/'src/libprojectM/MilkdropPreset/PerPixelMesh.hpp'
    original = header.read_text()
    assert 'm_perPixelSampler{GL_CLAMP_TO_EDGE, GL_LINEAR}' in original
    header.write_text(original.replace('m_perPixelSampler{GL_CLAMP_TO_EDGE, GL_LINEAR}',
                                       'm_perPixelSampler{GL_CLAMP_TO_EDGE, GL_NEAREST}'))
    assert native_contract(tmp_path) is None
    header.write_text(original)
    shader = tmp_path/'src/libprojectM/MilkdropPreset/MilkdropShader.cpp'
    shader.write_text(shader.read_text().replace('desc.Bind(textureUnit, m_shader);',
                                                 'desc.Bind(textureUnit + 1, m_shader);'))
    assert native_contract(tmp_path) is None

# Recognized pre43 random-slot source contract; newer source remains fail-closed.
pytestmark = pytest.mark.historical_profile("random_contract")
