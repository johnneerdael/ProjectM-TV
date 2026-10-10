"""Auxiliary compiler inventory preserves source, conversions and profile boundaries."""
import copy
import shutil
import subprocess

import pytest

from source_shader_compiler import CompilerTools, analyze_case, sha256


GLSL = '''#version 300 es
precision highp float;
uniform sampler2D sampler_main;
uniform float bass;
in vec2 uv;
out vec4 colour;
float helper(float x) {
    int n = int(x);
    float y = 0.0;
    for (int i=0; i<3; ++i) { if (i < n) y += x; }
    return y;
}
void main() { colour = texture(sampler_main, uv) * helper(bass); }
'''


def case(glsl=GLSL):
    engine = {'commit': 'a'*40, 'patches_sha256': 'b'*64}
    request = {'code': 'shader_body { ret = bass; }', 'stage': 'composite',
               'profile': 'gles300', 'samplers': {'sampler_main': 'sampler2D'},
               'texture_sizes': []}
    return {'preset': {'sha256': 'c'*64, 'relative_path': 'test.milk'},
            'engine': engine, 'engine_archive_sha256': 'd'*64,
            'reports': {'composite': {'request': request,
                'source_sha256': sha256(request['code']),
                'translator_sha256': 'e'*64, 'validator_sha256': 'f'*64,
                'native_driver_verified': False,
                'translation': {'status': 'translated', 'glsl': glsl,
                    'profile': 'gles300', 'stage': 'composite', 'engine': engine,
                    'engine_archive_sha256': 'd'*64, 'native_driver_verified': False}}}}


@pytest.fixture
def compiler():
    if not all(shutil.which(n) for n in CompilerTools.NAMES.values()):
        pytest.skip('optional official compiler CLI tools unavailable')
    return CompilerTools()


def test_real_cli_function_loop_conversion_sample_and_resource_joins(compiler):
    result = analyze_case(case(), compiler)['stages']['composite']
    assert result['status'] == 'analyzed'
    assert result['exact_ast']['profile'] == 'gles300'
    assert result['inspection']['profile'] == 'gles310-opengl-inspection'
    assert result['inspection']['native_driver_verified'] is False
    assert result['inspection']['runtime_texture_bindings_verified'] is False
    summary = result['inspection']['original_summary']
    helper = next(f for f in summary['functions'] if f['name'].startswith('helper('))
    main = next(f for f in summary['functions'] if f['name'] == 'main')
    assert helper['loops'] and helper['selections']
    assert any(c['op'] == 'OpConvertFToS' and c['source']['line'] == 8
               for c in helper['conversions'])
    assert helper['id'] in [c['target'] for c in main['calls']]
    assert main['samples'][0]['source']['line'] == 13
    assert set(main['transitive_resource_names']) == {'bass', 'sampler_main', 'uv', 'colour'}
    assert any(t['op'] == 'OpTypeInt' and t['operands'] == ['32', '1'] for t in summary['types'])
    resource = next(r for r in result['inspection']['resources'] if r['name'] == 'sampler_main')
    assert resource['request_sampler_type'] == 'sampler2D'
    assert resource['translated_declarations'][0]['line'] == 3
    assert result['inspection']['normalized_summary']['conversion_count'] == summary['conversion_count']
    assert result['inspection']['passes'] == ['--eliminate-dead-functions', '--compact-ids']


@pytest.mark.parametrize('mutate', [
    lambda c: c['reports']['composite']['request'].update(code='different'),
    lambda c: c['reports']['composite']['translation'].update(profile='glsl330'),
    lambda c: c['reports']['composite']['translation'].update(engine_archive_sha256='0'*64),
    lambda c: c['reports']['composite'].update(native_driver_verified=True),
    lambda c: c['reports']['composite']['translation'].update(glsl=GLSL.replace('300 es', '310 es')),
    lambda c: c['reports']['composite'].update(translator_sha256='missing'),
])
def test_bad_source_profile_provenance_rejected_before_tools(mutate):
    c = case(); mutate(c)
    with pytest.raises(ValueError):
        analyze_case(c, None)


def test_mutating_arithmetic_changes_source_join(compiler):
    a = analyze_case(case(), compiler)
    b = analyze_case(case(GLSL.replace('int(x)', 'int(x + 1.0)')), compiler)
    assert a['stages']['composite']['translated_glsl_sha256'] != b['stages']['composite']['translated_glsl_sha256']
    assert a['record_sha256'] != b['record_sha256']


def test_compile_rejection_is_not_an_inspection_success(compiler):
    r = analyze_case(case(GLSL.replace('int(x)', 'missing(x)')), compiler)['stages']['composite']
    assert r['status'] == 'exact_ast_rejected'
    assert 'inspection' not in r


def test_no_aggressive_or_inline_pass_is_accepted():
    with pytest.raises(ValueError, match='pass'):
        CompilerTools(passes=['--inline-entry-points-exhaustive'])


def test_result_rejoin_rejects_changed_source_and_claimed_native_parity(compiler):
    from source_shader_compiler import validate_join
    c = case(); r = analyze_case(c, compiler)
    validate_join(r, c)
    changed = case(GLSL.replace('int(x)', 'int(x + 1.0)'))
    with pytest.raises(ValueError, match='join'):
        validate_join(r, changed)
    forged = copy.deepcopy(r)
    forged['stages']['composite']['inspection']['native_driver_verified'] = True
    with pytest.raises(ValueError, match='seal'):
        validate_join(forged, c)


def test_timeout_and_compiler_crash_remain_unknown(compiler, monkeypatch):
    def timeout(key, args):
        raise subprocess.TimeoutExpired(key, .01)
    monkeypatch.setattr(compiler, 'run', timeout)
    result = analyze_case(case(), compiler)['stages']['composite']
    assert result['status'] == 'inspection_unknown'
    assert 'inspection' not in result
    monkeypatch.setattr(compiler, 'run', lambda key, args: subprocess.CompletedProcess(args, -11, '', 'crash'))
    result = analyze_case(case(), compiler)['stages']['composite']
    assert result['status'] == 'inspection_unknown'
    assert 'AST tool failure' in result['reason']


def test_resealed_inspection_cannot_be_promoted_to_native(compiler):
    from source_shader_compiler import validate_join, _digest
    c=case(); r=analyze_case(c, compiler)
    r['stages']['composite']['inspection']['native_driver_verified'] = True
    r['record_sha256'] = _digest({k:v for k,v in r.items() if k != 'record_sha256'})
    with pytest.raises(ValueError, match='native'):
        validate_join(r,c)


def test_line_directives_keep_logical_locations_without_false_physical_text(compiler):
    glsl=GLSL.replace('void main()', '#line 5\nvoid main()')
    r=analyze_case(case(glsl),compiler)['stages']['composite']
    assert r['status']=='analyzed'
    main=next(f for f in r['inspection']['original_summary']['functions'] if f['name']=='main')
    assert main['samples'][0]['source']['line']==5
    assert main['samples'][0]['source']['text'] is None
    assert main['samples'][0]['source']['logical_file_id'] is not None
    assert main['samples'][0]['source']['reason']=='#line mapping not qualified'
    sampler=next(r for r in r['inspection']['resources'] if r['name']=='sampler_main')
    assert sampler['translated_declarations'][0]['text']=='uniform sampler2D sampler_main;'
