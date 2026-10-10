"""Optional symbolic source maths preserves native/unknown boundaries."""
import os
from pathlib import Path
import pytest
from shader_fields import Field


def backend(**kwargs):
    import source_symbolic
    python=os.environ.get('MILK_SYMBOLIC_PYTHON')
    if python is None:
        pytest.skip('set MILK_SYMBOLIC_PYTHON to the prepared optional component environment')
    assert Path(python).is_file(),'prepared symbolic component Python missing'
    return source_symbolic.SymbolicSession(Path(python),**kwargs)


def control(op,*args):return Field(op,tuple(args),'float')
def variable(name):return Field('input',dtype='float',detail={'name':name})
def constant(value):return Field('constant',dtype='float',detail={'value':value})


def test_correlated_derivative_refines_baseline_without_execution():
    from source_control_bounds import scalar_response_envelope
    x=variable('bass');formula=control('add',control('multiply',x,x),control('negate',control('multiply',x,x)))
    ordinary=scalar_response_envelope(formula,input_names={'bass'})
    assert ordinary['maximum_absolute_control_change_per_audio_unit'] is None
    with backend():
        refined=scalar_response_envelope(formula,input_names={'bass'})
    assert refined['maximum_absolute_control_change_per_audio_unit']==0
    assert refined['baseline_absolute_control_change_per_audio_unit'] is None
    assert refined['native_numeric_certified'] is False
    assert refined['assumed_finite_input_names']==['bass']


def test_derivative_program_uses_existing_declared_range_calculator():
    from source_control_bounds import scalar_response_envelope
    x=variable('bass');formula=control('multiply',control('sin',x),control('sin',x))
    with backend():r=scalar_response_envelope(formula,input_names={'bass'})
    assert r['maximum_absolute_control_change_per_audio_unit']<=1.000001
    assert r['symbolic_refinement']['status']=='bounded'


@pytest.mark.parametrize('op',['cast','narrow','sample','sequence','floor','eel_divide'])
def test_unsupported_original_operation_cannot_be_simplified_away(op):
    from source_control_bounds import scalar_response_envelope
    original=control(op,variable('bass'));formula=control('subtract',original,original)
    with backend():r=scalar_response_envelope(formula,input_names={'bass'})
    assert r['symbolic_refinement']['status']=='unsupported'
    assert r['native_numeric_certified'] is False


def test_unknown_state_gain_remains_unbounded():
    from source_control_bounds import scalar_response_envelope
    with backend():r=scalar_response_envelope(control('multiply',variable('bass'),variable('private_state')),input_names={'bass'})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None
    assert r['symbolic_refinement']['status']=='unbounded'


def test_no_backend_leaves_response_contract_unchanged():
    from source_control_bounds import scalar_response_envelope
    r=scalar_response_envelope(variable('bass'),input_names={'bass'})
    assert 'symbolic_refinement' not in r


def test_session_caches_same_query_and_releases_worker():
    from source_control_bounds import scalar_response_envelope
    session=backend()
    with session:
        a=scalar_response_envelope(control('sin',variable('bass')),input_names={'bass'})
        b=scalar_response_envelope(control('sin',variable('bass')),input_names={'bass'})
        assert a==b
        assert session.stats['queries']==1
        process=session.process
    assert process.poll() is not None


def test_timeout_disables_worker_without_repeating_the_failure(tmp_path, monkeypatch):
    import source_symbolic
    from source_control_bounds import scalar_response_envelope
    worker=tmp_path/'slow.py'
    worker.write_text('import json,sys,time\nprint(json.dumps({"protocol":1,"sympy_version":"1.14.0"}),flush=True)\nsys.stdin.readline()\ntime.sleep(30)\n')
    monkeypatch.setattr(source_symbolic,'WORKER',worker)
    with backend(timeout=.02) as session:
        a=scalar_response_envelope(variable('bass'),input_names={'bass'})
        b=scalar_response_envelope(variable('mid'),input_names={'mid'})
        assert a['symbolic_refinement']['status']==b['symbolic_refinement']['status']=='unavailable'
        assert session.stats['queries']==1
        assert session.stats['timeouts']==1
        assert session.process.poll() is not None


def test_rational_derivative_coefficient_is_enclosed_outwards():
    from fractions import Fraction
    from source_control_bounds import scalar_response_envelope
    formula=control('multiply',constant(.1),control('multiply',constant(.2),variable('bass')))
    with backend():r=scalar_response_envelope(formula,input_names={'bass'})
    value=r['symbolic_refinement']['maximum_absolute_control_change_per_audio_unit']
    assert Fraction(value)>=Fraction(.1)*Fraction(.2)


def test_response_names_advance_together_in_one_derivative():
    from source_control_bounds import scalar_response_envelope
    with backend():r=scalar_response_envelope(control('subtract',variable('bass'),variable('bass_alias')),input_names={'bass','bass_alias'})
    assert r['maximum_absolute_control_change_per_audio_unit']==0


def test_invalid_domain_is_not_hidden_by_symbolic_cancellation():
    from source_control_bounds import scalar_response_envelope
    formula=control('subtract',variable('bass'),variable('bass'))
    with backend():r=scalar_response_envelope(formula,input_names={'bass'},input_domains={'bass':[2,1]})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None


def test_known_original_overflow_cannot_be_removed_with_its_derivative():
    from source_control_bounds import scalar_response_envelope
    overflow=control('multiply',constant(1e308),constant(1e308))
    formula=control('add',control('sin',overflow),variable('bass'))
    with backend():r=scalar_response_envelope(formula,input_names={'bass'})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None
    assert r['unknown_reasons']


def test_derived_coefficient_name_cannot_bound_a_real_source_input():
    from source_control_bounds import scalar_response_envelope
    formula=control('multiply',variable('bass'),control('multiply',constant(.1),control('multiply',constant(.2),variable(':symbolic-rational-0'))))
    with backend():r=scalar_response_envelope(formula,input_names={'bass'})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None


def test_same_name_in_different_phases_cannot_cancel():
    from source_control_bounds import scalar_response_envelope
    snapshot=Field('input',dtype='float',detail={'name':'rad','equation_phase':'per_frame_','value_binding':'phase_scalar_snapshot'})
    mesh=Field('input',dtype='float',detail={'name':'rad','native_mesh_reset_input':True})
    formula=control('multiply',variable('bass'),control('subtract',snapshot,mesh))
    with backend():r=scalar_response_envelope(formula,input_names={'bass'})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None
    assert r['symbolic_refinement']['status']=='unsupported'


def test_request_pipe_write_is_inside_the_deadline(tmp_path, monkeypatch):
    import source_symbolic
    import time
    worker=tmp_path/'not_reading.py'
    worker.write_text('import json,time\nprint(json.dumps({"protocol":1,"sympy_version":"1.14.0"}),flush=True)\ntime.sleep(.5)\n')
    monkeypatch.setattr(source_symbolic,'WORKER',worker)
    with backend(timeout=.02) as session:
        start=time.monotonic()
        r=session.query({'root':0,'nodes':[{'op':'input','dtype':'float','args':[],
            'detail':{'name':'x','large':'z'*100000}}]}, {'x'})
        assert r['status']=='unavailable'
        assert session.stats['timeouts']==1
        assert time.monotonic()-start<.4


def test_supported_symbolic_square_preserves_declared_original_overflow():
    from source_control_bounds import scalar_response_envelope
    with backend():r=scalar_response_envelope(control('sqr',variable('bass')),input_names={'bass'},
        input_domains={'bass':[1e200,1e200]})
    assert r['maximum_absolute_control_change_per_audio_unit'] is None


def test_real_six_band_trig_sum_avoids_general_simplification_timeout():
    import json
    fixture=json.loads((Path(__file__).parent/'fixtures/symbolic-worker-trig-sum-timeout.json').read_text())
    with backend() as session:r=session.query(fixture['program'],fixture['input_names'])
    assert r['status']=='derived'


def test_unsupported_source_does_not_start_a_worker():
    from source_control_bounds import scalar_response_envelope
    with backend() as session:
        r=scalar_response_envelope(control('floor',variable('bass')),input_names={'bass'})
        assert r['symbolic_refinement']['status']=='unsupported'
        assert session.process is None
