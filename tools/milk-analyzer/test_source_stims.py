"""Stims dependency fixtures adapted to native ProjectM phase boundaries."""
import importlib.util
import json
from pathlib import Path

import pytest

from shader_fields import Field
from test_effect_families import read


def evidence(body, **kwargs):
    assert importlib.util.find_spec('source_stims'), 'Stims dependency component is missing'
    from source_stims import source_phase_dependency_evidence
    return source_phase_dependency_evidence(read(body), **kwargs)


def test_read_before_later_write_recovers_previous_frame_audio_ancestry():
    record = evidence('per_frame_init_1=a=0;b=0;\n'
                      'per_frame_1=a=b*.5;b=a+treb;rot=a;\n')
    row = record['outputs']['rot']
    assert row['baseline_input_dependencies'] == ['state:per_frame_:b']
    assert row['newly_exposed_input_dependencies'] == ['treb']
    assert row['may_input_dependencies'] == ['treb']
    assert row['predecessor_inputs'] == ['state:per_frame_:b']
    assert row['quantitative_value_preserved_unknown'] is True
    assert record['numeric_bounds_changed'] is False
    assert record['uses_equation_execution'] is False


def test_overwriting_local_after_read_breaks_accumulator_but_keeps_previous_audio():
    record = evidence('per_frame_init_1=k=0;\n'
                      'per_frame_1=rot=k;k=bass;k=mid;\n')
    assert record['outputs']['rot']['may_input_dependencies'] == ['mid']
    assert record['outputs']['k']['may_input_dependencies'] == ['mid']


@pytest.mark.parametrize('body', [
    'per_frame_1=rot=if(0,bass,.1);\n',
    'per_frame_1=rot=bass;rot=.1;\n',
    'per_frame_1=k=bass;rot=k*0;\n',
])
def test_dead_branch_overwrite_and_zero_mask_do_not_gain_audio(body):
    assert evidence(body)['outputs']['rot']['may_input_dependencies'] == []


def test_main_q_reloads_initial_snapshot_and_custom_q_writes_remain_isolated():
    record = evidence('per_frame_init_1=q1=.1;\n'
                      'per_frame_1=q1=q1+.1;rot=q1;\n'
                      'shapecode_0_enabled=1\nshape_0_per_frame1=q1=bass;\n')
    assert record['outputs']['rot']['may_input_dependencies'] == []
    assert record['state_count'] == 0


def test_initial_audio_is_a_distinct_unknown_input_not_silence():
    record = evidence('per_frame_init_1=k=bass;\nper_frame_1=k=k+treb;rot=k;\n')
    assert record['outputs']['rot']['may_input_dependencies'] == [
        'init:per_frame_init_:bass', 'treb']


def test_native_negative_sqrt_does_not_hide_audio_route():
    assert evidence('per_frame_1=rot=sqrt(-1)*bass;\n')['outputs']['rot'][
        'may_input_dependencies'] == ['bass']


def test_memory_aliases_and_shared_registers_are_not_resolved_as_private_locals():
    record = evidence('per_frame_1=reg00=reg00+bass;rot=reg00;dx=megabuf(0);\n')
    assert 'shared:reg00' in record['outputs']['rot']['may_input_dependencies']
    assert record['outputs']['dx']['unresolved_reasons']
    assert any('shared memory' in reason for reason in record['unresolved_reasons'])


def test_native_expression_pointer_aliases_remain_unknown():
    record = evidence('per_frame_1=rot=k+(k=bass);\n')
    assert record['outputs']['rot']['unresolved_reasons']
    assert record['status'] == 'partial'


def test_random_stream_call_count_dependence_is_explicitly_unqualified():
    record = evidence('per_frame_1=rot=rand(1);\n'
                      'shapecode_0_enabled=1\nshape_0_per_frame1=if(bass,rand(1),0);\n')
    assert record['status'] == 'partial'
    assert any('random stream' in reason for reason in record['outputs']['rot']['unresolved_reasons'])


def test_state_budget_does_not_emit_partial_successful_closure():
    record = evidence('per_frame_1=k=k+bass;rot=k;\n', max_states=0)
    assert record['status'] == 'unresolved'
    assert record['outputs'] == {}


def test_typed_graph_closure_preserves_initial_unknown_and_converges_long_chain():
    assert importlib.util.find_spec('source_stims'), 'Stims dependency component is missing'
    from source_stims import dependency_fixpoint
    state = {f'prev:{i}': Field('input', detail={'name': f'prev:{i+1}'})
             for i in range(20)}
    state['prev:20'] = Field('input', detail={'name': 'bass'})
    initial = {'prev:0': Field('unknown', detail={'reason': 'initial state not supplied'})}
    result = dependency_fixpoint({'rot': Field('input', detail={'name': 'prev:0'})},
                                 state, initial=initial)
    assert result['outputs']['rot']['may_input_dependencies'] == ['bass']
    assert 'initial state not supplied' in result['outputs']['rot']['unresolved_reasons']
    assert result['converged'] is True


def test_independently_sourced_supporting_fixture_lineage_and_native_routes():
    path = Path(__file__).with_name('fixtures')/'stims-supporting-source-controls.json'
    assert path.is_file(), 'independent EEL/preset-utils fixtures are missing'
    fixture = json.loads(path.read_text())
    assert all(component['commit'] for component in fixture['lineage'])
    for case in fixture['native_route_controls']:
        row = evidence(case['source'])['outputs']['rot']
        assert row['may_input_dependencies'] == case['native_may_input_dependencies'], case['name']
    from scene_equations import MAIN, SHAPE
    assert MAIN['mv_a'][1] == fixture['native_default_controls']['mv_a']
    assert SHAPE['border_a'][0] == fixture['native_default_controls']['shape_border_a']


def test_dependency_comparison_ignores_output_order_and_unknown_annotations():
    import source_stims_validate
    assert hasattr(source_stims_validate, 'dependency_signature'), 'order-independent census comparison missing'
    change = {'control': 'rot', 'new_current_audio_ancestry': ['bass'],
              'baseline_input_dependencies': ['previous:k'], 'may_input_dependencies': ['bass'],
              'newly_exposed_input_dependencies': ['bass'], 'predecessor_inputs': ['previous:k']}
    other = {**change, 'control': 'dx'}
    before = {'changes': [change, other]}
    after = {'changes': [{**other, 'unresolved_reasons': ['RNG stream unknown']}, change]}
    assert source_stims_validate.dependency_signature(before) == source_stims_validate.dependency_signature(after)
    after['changes'][1] = {**change, 'may_input_dependencies': ['mid']}
    assert source_stims_validate.dependency_signature(before) != source_stims_validate.dependency_signature(after)


def test_public_entrypoint_interns_shared_dag_and_restores_ambient_context(monkeypatch):
    import effect_families
    assert effect_families._CACHE.get() is None
    original = effect_families._key
    calls = 0
    def bounded_key(field):
        nonlocal calls
        calls += 1
        assert calls < 1000, 'shared DAG identity expanded without phase cache'
        return original(field)
    monkeypatch.setattr(effect_families, '_key', bounded_key)
    record = evidence('per_frame_1=k=bass;' + 'k=k+k;'*14 + 'rot=if(mid,k,k+1);\n')
    assert record['outputs']['rot']['may_input_dependencies'] == ['bass', 'mid']
    assert effect_families._CACHE.get() is None


def test_public_entrypoint_reuses_existing_cache_without_resetting_its_owner():
    from effect_families import _CACHE
    cache = {'caller-owned': True}; token = _CACHE.set(cache)
    try:
        record = evidence('per_frame_1=rot=if(bass,mid,treb);\n')
        assert record['outputs']['rot']['may_input_dependencies'] == ['bass', 'mid', 'treb']
        assert _CACHE.get() is cache
        assert cache['caller-owned'] is True
    finally:
        _CACHE.reset(token)


def test_public_entrypoint_resets_its_context_when_lowering_raises(monkeypatch):
    from effect_families import _CACHE, _EEL
    def failed(*args):
        assert _CACHE.get() is not None, 'public phase cache missing'
        raise RuntimeError('fixture lowering failure')
    monkeypatch.setattr(_EEL, 'lower', failed)
    with pytest.raises(RuntimeError, match='fixture lowering failure'):
        evidence('per_frame_1=rot=bass;\n')
    assert _CACHE.get() is None


def test_public_entrypoint_semantic_budget_is_explicit_unknown(monkeypatch):
    from effect_families import _CACHE, _EEL, _SemanticBudget
    def failed(*args):
        raise _SemanticBudget('fixture semantic budget exhausted')
    monkeypatch.setattr(_EEL, 'lower', failed)
    record = evidence('per_frame_1=rot=bass;\n')
    assert record['status'] == 'unresolved'
    assert record['outputs'] == {}
    assert record['converged'] is False
    assert record['numeric_bounds_changed'] is False
    assert record['unresolved_reasons'] == ['fixture semantic budget exhausted']
    assert _CACHE.get() is None


def test_exact_alien_web_bouncer_public_entrypoint_has_scoped_cache(monkeypatch):
    from effect_families import _CACHE, _EEL
    from forecast import read_source
    from engine_profiles import CORE_2334_ENGINE
    from source_stims import source_phase_dependency_evidence
    root = Path(__file__).resolve().parents[2]
    path = root/'core/src/main/assets/presets/Flexi - alien web bouncer [39].milk'
    source = read_source(path, reader=root/'build/preset-corpus/source34/adapters/milk-native-reader')
    assert source['parser_inputs']['engine'] == CORE_2334_ENGINE
    original = _EEL.lower
    def guarded(model, tree):
        assert _CACHE.get() is not None, 'exact preset requires public phase cache'
        return original(model, tree)
    monkeypatch.setattr(_EEL, 'lower', guarded)
    standalone = source_phase_dependency_evidence(source)
    assert _CACHE.get() is None
    cache = {}; token = _CACHE.set(cache)
    try:
        combined_context = source_phase_dependency_evidence(source)
        assert _CACHE.get() is cache
    finally:
        _CACHE.reset(token)
    assert standalone == combined_context
    assert standalone['status'] in {'partial', 'source_may_dependencies'}
