"""Original typed-graph query port; native semantics remain authoritative."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import pytest
from shader_fields import Field
from test_effect_families import read, shader

ROOT=Path(__file__).resolve().parents[2]
CANDIDATE=ROOT/'tools/milk-analyzer/source_field_index.py'


def module():
    assert CANDIDATE.is_file(), 'original typed Field index port missing'
    if 'source_field_index_candidate' not in sys.modules:
        spec=importlib.util.spec_from_file_location('source_field_index_candidate',CANDIDATE)
        loaded=importlib.util.module_from_spec(spec);sys.modules[spec.name]=loaded;spec.loader.exec_module(loaded)
    return sys.modules['source_field_index_candidate']


def literal(value, dtype='float'):return Field('constant',dtype=dtype,detail={'value':value})
def variable(name='phase'):return Field('input',detail={'name':name})
def binary(op,a,b, dtype='float'):return Field(op,(a,b),dtype)
def fold(phase):return Field('abs',(binary('subtract',binary('multiply',literal(2),Field('frac',(phase,),phase.dtype)),literal(1)),),phase.dtype)
def analysis(kind='custom_composite'):
    return SimpleNamespace(stages={'composite':{'kind':kind,'conditional_on_native_profile':True}},
                           source={'preset_sha256':'0'*64})


def report(field, *, kind='custom_composite', max_nodes=4096):
    m=module();index=m.TypedFieldIndex(field,max_nodes=max_nodes)
    return m.outer_fold_evidence(field,analysis(kind),stage='composite',index=index)


def test_capture_large_phase_without_scalar_reconstruction():
    leaves=[binary('add',variable(),literal(.01)) for _ in range(512)]
    while len(leaves)>1:leaves=[binary('add',leaves[i],leaves[i+1]) for i in range(0,len(leaves),2)]
    phase=leaves[0]
    row=report(fold(phase))
    assert row['status']=='structural_candidates'
    assert len(row['candidates'])==1
    capture=row['candidates'][0]
    assert capture['function']=='triangular_frac_structure'
    assert capture['phase_is_opaque'] is True
    assert capture['phase_scalar_projection_performed'] is False
    assert capture['phase_node_id'] is not None
    assert row['index']['complete'] is True
    assert row['index']['unique_nodes']>700
    assert row['phase_value_range'] is None
    assert row['visible_motion_speed'] is None
    assert row['fundamental_cell_area_uv2'] is None


def test_index_is_analysis_local_reuses_dag_nodes_and_retains_reverse_use_edges():
    m=module();kernel=fold(variable());root=binary('add',kernel,kernel)
    index=m.TypedFieldIndex(root)
    assert len(index.query('abs',dtype='float'))==1
    assert index.node_id(kernel)==index.query('abs',dtype='float')[0]
    assert len(index.parents(index.node_id(kernel)))==2
    assert index.summary()['root_node_id']==index.node_id(root)
    assert index.summary()['unique_nodes']<10


def test_incomplete_index_can_find_structure_but_cannot_prove_absence_or_ranges():
    row=report(fold(variable()),max_nodes=3)
    assert row['index']['complete'] is False
    assert row['status']=='unknown'
    assert row['unknown_reasons']
    assert row['absence_proved'] is False


@pytest.mark.parametrize('field',[literal(.5),binary('multiply',fold(variable()),literal(0)),Field('select',(literal(0,'bool'),fold(variable()),literal(.5)))])
def test_semantically_dead_or_absent_folds_do_not_supply_candidates(field):
    row=report(field)
    assert not row['candidates']


def test_cast_between_fold_operators_is_not_transparent():
    wrapped=Field('frac',(variable(),))
    converted=Field('cast',(Field('cast',(wrapped,),'int'),),'float')
    expression=Field('abs',(binary('subtract',converted,literal(.5)),))
    assert not report(expression)['candidates']


def test_reversed_triangle_sign_is_qualified_by_structure_without_phase_expansion():
    expression=Field('abs',(binary('subtract',literal(1),binary('multiply',literal(2),Field('frac',(variable(),)))),))
    row=report(expression)
    assert row['candidates'][0]['function']=='triangular_frac_structure'
    assert row['candidates'][0]['fraction_scale']==-2
    assert row['candidates'][0]['bias']==1


def test_abs_frac_cooccurrence_without_nested_fold_is_not_a_triangle():
    expression=binary('add',Field('abs',(variable(),)),Field('frac',(variable(),)))
    assert not report(expression)['candidates']


def test_native_selection_unknown_and_rejected_are_distinct():
    unknown=report(fold(variable()),kind='unknown')
    assert unknown['candidates']
    assert unknown['candidates'][0]['native_selection_verified'] is False
    assert unknown['quantitative_bounds_eligible'] is False
    rejected=report(fold(variable()),kind='default_composite')
    assert rejected['status']=='not_contributing'
    assert not rejected['candidates']


def test_known_invalid_phase_domain_is_retained_and_never_eligible():
    phase=binary('divide',variable('bass'),literal(0))
    row=report(fold(phase))
    assert row['candidates'][0]['phase_domain_status']=='known_invalid'
    assert row['candidates'][0]['quantitative_bounds_eligible'] is False
    assert row['phase_value_range'] is None


def test_unknown_nodes_and_loops_cannot_supply_absence_proof():
    row=report(Field('unknown',detail={'reason':'unresolved source'}))
    assert row['status']=='unknown'
    assert row['absence_proved'] is False


def test_frozen_grind231_recovers_typed_outer_folds_after_old_projection_budget_failure():
    from effect_families import _Analysis,_CACHE,_walk
    from source_folded_sampling import folded_coordinate_map
    path=ROOT/'core/src/main/assets/presets/flexi - grind my glitch up [231].milk'
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='3a6e50e87b46df7ce4fd910c756be5f7520348b2d97fc1f67cc93ef1272c227a'
    source=read(raw)
    compatibility=json.loads((ROOT/'build/preset-corpus/source-shape-flash-size-2000-2026-10-10/compatibility/flexi - grind my glitch up [231].json').read_text())['reports']
    a=_Analysis(source,'gles300',compatibility);token=_CACHE.set({})
    try:
        a.main_equations();a.shader('composite','comp_')
        field=a.outputs['composite']
        sample_fields=[n.args[0] for n,p in _walk(field) if n.op=='sample']
        old=[folded_coordinate_map(n,a) for n in sample_fields]
        assert any('fold scalar projection budget exceeded' in r['unknown_reasons'] for r in old)
        m=module();index=m.TypedFieldIndex(field)
        result=m.outer_fold_evidence(field,a,stage='composite',index=index)
        assert result['status']=='structural_candidates'
        assert len(result['candidates'])==6  # Three native vector source kernels lower to six scalar lanes.
        assert all(c['phase_is_opaque'] and not c['phase_scalar_projection_performed'] for c in result['candidates'])
        assert result['source_sha256']==source['preset_sha256']
        assert result['index']['complete'] is True
        assert result['quantitative_bounds_eligible'] is False
        assert result['phase_value_range'] is None
        assert result['fundamental_cell_area_uv2'] is None
    finally:_CACHE.reset(token)


def test_existing_deep_source_child_limit_stays_unknown_without_bypassing_semantics():
    phase=variable()
    for _ in range(700):phase=binary('add',phase,literal(.01))
    row=report(fold(phase))
    assert row['index']['complete'] is False
    assert row['status']=='unknown'
    assert row['absence_proved'] is False
    assert row['quantitative_bounds_eligible'] is False
    assert any('semantic child selection unresolved' in reason for reason in row['unknown_reasons'])


def test_opaque_phase_capture_keeps_original_reference_when_semantic_zero_pruning_hides_children():
    m=module()
    phase=binary('multiply',binary('divide',variable('bass'),literal(0)),literal(0))
    field=fold(phase);index=m.TypedFieldIndex(field)
    row=m.outer_fold_evidence(field,analysis(),stage='composite',index=index)
    capture=row['candidates'][0]
    assert capture['phase_node_id'] is not None
    assert index.node(capture['phase_node_id']) is phase
    assert capture['phase_domain_status']=='known_invalid'
    assert capture['quantitative_bounds_eligible'] is False


def test_discarded_float4_lane_keeps_semantic_slicing_and_no_fold_candidate():
    colour=Field('construct',(literal(1),literal(0),literal(0),fold(variable())), 'float4')
    displayed=Field('cast',(colour,), 'float3')
    assert not report(displayed)['candidates']


def test_integrated_original_export_retains_old_unknowns_and_adds_only_structural_facts():
    from test_effect_families import analyze
    source=read((ROOT/'core/src/main/assets/presets/flexi - grind my glitch up [231].milk').read_bytes())
    compatibility=json.loads((ROOT/'build/preset-corpus/source-shape-flash-size-2000-2026-10-10/compatibility/flexi - grind my glitch up [231].json').read_text())['reports']
    description=analyze(source,compatibility=compatibility)['visual_description']
    maps=description['sampling_geometry']['stages']['composite']
    metadata=[r['folded_coordinate_map']['outer_fold_structure'] for r in maps]
    assert any(r['candidates'] for r in metadata)
    assert all(r['source_model']=='unknown' and r['repeat_lattice_basis_uv'] is None for r in (m['folded_coordinate_map'] for m in maps))
    assert all(r['quantitative_bounds_eligible'] is False for r in metadata)
    assert all(r['stage']=='composite' and r['source_sha256']==source['preset_sha256'] for r in metadata)
    schema=json.loads((ROOT/'tools/milk-analyzer/export-contract/source-appearance.schema.json').read_text())
    assert schema['$defs']['outerFoldStructure']['properties']['quantitative_bounds_eligible']['const'] is False
    json.dumps(description,allow_nan=False)


def test_unknown_native_original_preserves_selection_guard_and_dead_output_removes_metadata():
    from test_effect_families import analyze
    source=read((ROOT/'core/src/main/assets/presets/flexi - grind my glitch up [231].milk').read_bytes())
    description=analyze(source)['visual_description']
    metadata=[r['folded_coordinate_map']['outer_fold_structure'] for r in description['sampling_geometry']['stages']['composite']]
    candidates=[c for r in metadata for c in r['candidates']]
    assert candidates and all(c['native_selection_verified'] is False and c['native_source_branch']=='unknown' for c in candidates)
    dead=analyze(shader('shader_body {ret=GetPixel(abs(2*frac(uv)-1))*0;}'))['visual_description']
    assert not dead['sampling_geometry']['stages']['composite']


def test_stage_root_bound_cache_does_not_persist_between_analyses():
    from effect_families import _CACHE
    m=module();field=fold(variable());token=_CACHE.set({})
    try:
        first=m.field_index(field,stage='composite')
        assert m.field_index(field,stage='composite') is first
        assert m.field_index(field,stage='warp') is not first
    finally:_CACHE.reset(token)
    token=_CACHE.set({})
    try:assert m.field_index(field,stage='composite') is not first
    finally:_CACHE.reset(token)


@pytest.mark.parametrize('failure',[ValueError('inspection value budget'),RecursionError('inspection depth budget'),OverflowError('inspection math overflow')])
def test_optional_inspection_failure_cannot_replace_existing_fold_result(monkeypatch,failure):
    from source_folded_sampling import folded_coordinate_map
    import source_field_index
    from effect_families import _SemanticBudget
    for error in (failure,_SemanticBudget('optional semantic budget')):
        def fail(*args,**kwargs):raise error
        monkeypatch.setattr(source_field_index,'field_index',fail)
        a=analysis();field=fold(variable())
        result=folded_coordinate_map(field,a,stage='composite')
        assert result['source_model']=='unknown'
        assert result['axes']==[None,None]
        assert result['visible_motion_speed'] is None
        assert result['outer_fold_structure']['status']=='unknown'
        assert result['outer_fold_structure']['unknown_reasons']
        assert result['outer_fold_structure']['quantitative_bounds_eligible'] is False


def test_local_rule_budget_failure_is_retained_as_inspection_unknown(monkeypatch):
    m=module()
    def fail(*args,**kwargs):raise OverflowError('local coefficient overflow')
    monkeypatch.setattr(m,'_outer_match',fail)
    result=report(fold(variable()))
    assert result['status']=='unknown'
    assert not result['candidates']
    assert result['unknown_reasons']
    assert result['phase_value_range'] is None


def test_supported_numeric_fold_does_not_depend_on_optional_inspection(monkeypatch):
    import source_field_index
    from test_source_folded_sampling import folded
    def forbidden(*args,**kwargs):raise ValueError('optional backend unavailable')
    monkeypatch.setattr(source_field_index,'outer_fold_evidence',forbidden)
    result=folded('ret=GetPixel(abs(2*frac(uv*2)-1));')
    assert result['source_model']=='planar_periodic_folds'
    assert result['fundamental_cell_area_uv2']==pytest.approx(.25)
    assert 'outer_fold_structure' not in result


def test_unrelated_optional_programming_error_is_not_silently_swallowed(monkeypatch):
    import source_field_index
    from source_folded_sampling import folded_coordinate_map
    def fail(*args,**kwargs):raise TypeError('unexpected programming error')
    monkeypatch.setattr(source_field_index,'outer_fold_evidence',fail)
    with pytest.raises(TypeError,match='unexpected programming error'):
        folded_coordinate_map(fold(variable()),analysis(),stage='composite')


def test_optional_inspection_cannot_charge_or_reset_parent_work_budget(monkeypatch):
    import effect_families as f
    import source_field_index as m
    field=fold(variable())
    parent={'field_visits':f.MAX_FIELD_VISITS-1,'normalized_term_nodes':19,'traversal_budget_exhausted':False}
    token=f._CACHE.set(parent)
    try:
        result=m.outer_fold_evidence(field,analysis(),stage='composite')
        assert result['candidates']
        assert parent['field_visits']==f.MAX_FIELD_VISITS-1
        assert parent['normalized_term_nodes']==19
        assert parent['traversal_budget_exhausted'] is False
        # Ordinary analytical work still observes exactly its original remaining budget.
        list(f._walk(variable('time')))
        with pytest.raises(f._SemanticBudget):list(f._walk(variable('other')))
    finally:f._CACHE.reset(token)


def test_optional_inspection_failure_stays_in_private_budget_and_keeps_parent_flag(monkeypatch):
    import effect_families as f
    import source_field_index as m
    field=fold(variable());parent={'field_visits':5,'normalized_term_nodes':11,'traversal_budget_exhausted':True}
    token=f._CACHE.set(parent)
    try:
        monkeypatch.setattr(f,'MAX_FIELD_VISITS',1)
        result=m.outer_fold_evidence(field,analysis(),stage='composite')
        assert result['quantitative_bounds_eligible'] is False
        assert parent['field_visits']==5 and parent['normalized_term_nodes']==11
        assert parent['traversal_budget_exhausted'] is True
        assert m.field_index(field,stage='composite') is m.field_index(field,stage='composite')
    finally:f._CACHE.reset(token)
