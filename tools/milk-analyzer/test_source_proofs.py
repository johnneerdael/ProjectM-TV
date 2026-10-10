"""Solver additions consume actual typed/source programs without native credit."""
import os
from pathlib import Path
import pytest
from shader_fields import Field


def backend(**kwargs):
    from source_proofs import ProofSession
    python = os.environ.get('MILK_PROOF_PYTHON')
    if python is None:
        pytest.skip('set MILK_PROOF_PYTHON to the pinned optional Z3 environment')
    assert Path(python).is_file()
    return ProofSession(python, **kwargs)


def var(name): return Field('input', dtype='float', detail={'name':name})
def const(value): return Field('constant', dtype='float', detail={'value':value})
def op(name, *args): return Field(name, tuple(args), 'float')
def pred(name, *args): return Field(name, tuple(args), 'bool')


def test_relational_polynomial_predicate_and_value_bounds():
    from source_proofs import predicate_evidence, scalar_value_evidence
    x=var('bass'); square=op('multiply',x,x)
    with backend():
        p=predicate_evidence(pred('greater_equal',square,const(0)),input_domains={'bass':[-2,2]})
        v=scalar_value_evidence(op('subtract',square,square),input_domains={'bass':[-2,2]})
    assert p['status']=='proven' and p['truth_value'] is True
    assert v['nominal_value_range']==[0.,0.]
    assert not p['native_numeric_certified'] and not v['native_numeric_certified']


def test_real_identity_and_explicit_float32_rounding_counterexample_stay_separate():
    from source_proofs import predicate_evidence
    x=var('x'); formula=pred('equal',op('subtract',op('add',const(1),x),x),const(1))
    with backend():
        real=predicate_evidence(formula,input_domains={'x':[16777216,16777216]})
        fp=predicate_evidence(formula,input_domains={'x':[16777216,16777216]},numeric_model='ieee754-binary32-rne')
    assert real['truth_value'] is True and fp['truth_value'] is False
    assert real['numeric_model']!=fp['numeric_model']
    assert fp['native_numeric_certified'] is False


@pytest.mark.parametrize('original',[
    Field('cast',(var('x'),),'float'), Field('sample',(var('x'),),'float'),
    Field('input',dtype='float',detail={'name':'x','phase':'init'}),
    const(float('inf')), Field('input',dtype='int',detail={'name':'x'})])
def test_cancelled_unsupported_or_qualified_original_is_rejected(original):
    from source_proofs import scalar_value_evidence
    with backend():r=scalar_value_evidence(op('subtract',original,original),input_domains={'x':[0,1]})
    assert r['status']=='unsupported' and r['nominal_value_range'] is None


def test_missing_or_invalid_input_domains_do_not_assume_zero_or_finite_storage():
    from source_proofs import scalar_value_evidence
    with backend():
        for domains in (None, {'x':[1,0]}, {'x':[0,float('inf')]}, {'x':[False,1]}):
            assert scalar_value_evidence(var('x'),input_domains=domains)['status']=='unsupported'


def native_source(initial,frame,extra=''):
    import test_native_reader
    return test_native_reader.NativeReaderTest().read(
        'per_frame_init_1='+initial+'\nper_frame_1='+frame+'\n'+extra)


def test_actual_source_recurrence_proves_init_and_transition_without_changing_native_domains():
    from equation_domains import main_q_domains, main_q_domain_evidence
    source=native_source('counter=0;','counter=min(1,counter+.25);q29=counter;')
    native=main_q_domains(source,policy='projectmtv-core-2.2.6-v1')
    with backend():r=main_q_domain_evidence(source,policy='projectmtv-core-2.2.6-v1',candidates={'counter':[0,1]})
    assert r['native_domains']==native
    assert r['nominal_proof']['status']=='proven'
    assert r['nominal_proof']['obligations']=={'initialization':'proven','transition':'proven'}
    assert r['nominal_proof']['frame_output_domains']['q29']==[.25,1.]


def test_unbounded_mutation_and_bad_initialization_return_counterexamples():
    from equation_domains import main_q_domain_evidence
    with backend():
        growth=main_q_domain_evidence(native_source('counter=0;','counter=counter+1;q29=counter;'),
            policy='projectmtv-core-2.2.6-v1',candidates={'counter':[0,1]})['nominal_proof']
        bad=main_q_domain_evidence(native_source('counter=-1;','counter=min(1,counter+.25);q29=counter;'),
            policy='projectmtv-core-2.2.6-v1',candidates={'counter':[0,1]})['nominal_proof']
    assert growth['status']=='refuted' and growth['failed_obligation']=='transition'
    assert bad['status']=='refuted' and bad['failed_obligation']=='initialization'
    assert growth['counterexample']


def test_source_order_q_reset_and_host_reset_are_preserved():
    from equation_domains import main_q_domain_evidence
    source=native_source('q29=2;counter=0;bass=0;',
        'counter=min(1,counter+.25);q30=q29;q29=q29+1;q31=bass;')
    with backend():r=main_q_domain_evidence(source,policy='projectmtv-core-2.2.6-v1',
        candidates={'counter':[0,1]},input_domains={'bass':[0,2]})['nominal_proof']
    assert r['status']=='proven'
    assert r['frame_output_domains']['q29']==[3.,3.]
    assert r['frame_output_domains']['q30']==[2.,2.]
    assert r['frame_output_domains']['q31']==[0.,2.]


@pytest.mark.parametrize('initial,frame,extra',[
    ('counter=0;','counter=min(1,counter+.25);q29=counter;','per_pixel_1=counter=9;\n'),
    ('counter=0;','q29=exec2(counter=-1,counter);',''),
    ('counter=0;','counter=min(1,counter+bass);q29=counter;',''),
    ('counter=0;','q29=reg00;','shape_0_init1=reg00=9;\n'),
    ('counter=0;','counter=;','')])
def test_source_effect_missing_domain_register_and_format_guards(initial,frame,extra):
    from equation_domains import main_q_domain_evidence
    with backend():r=main_q_domain_evidence(native_source(initial,frame,extra),
        policy='projectmtv-core-2.2.6-v1',candidates={'counter':[0,1]})['nominal_proof']
    assert r['status']=='unsupported'


def test_unknown_solver_result_is_not_a_proof():
    from source_proofs_worker import decide
    class Z3:
        unknown='unknown';sat='sat';unsat='unsat'
    class UnknownSolver:
        def check(self): return Z3.unknown
        def reason_unknown(self): return 'timeout'
    assert decide(UnknownSolver(),Z3)=={'status':'unknown','reason':'timeout'}


def test_worker_deadline_disables_session_and_reaps_child(tmp_path,monkeypatch):
    import source_proofs
    worker=tmp_path/'slow.py'
    worker.write_text('import json,sys,time\nprint(json.dumps({"protocol":1,"z3_version":"5.1.0.0"}),flush=True)\nsys.stdin.readline()\ntime.sleep(30)\n')
    monkeypatch.setattr(source_proofs,'WORKER',worker)
    with backend(timeout=.02) as session:
        a=source_proofs.scalar_value_evidence(var('x'),input_domains={'x':[0,1]})
        b=source_proofs.scalar_value_evidence(var('y'),input_domains={'y':[0,1]})
        assert a['status']==b['status']=='unavailable'
        assert session.stats['queries']==1 and session.stats['timeouts']==1
        assert session.process.poll() is not None


def test_default_off_returns_no_solver_record():
    from source_proofs import scalar_value_evidence, predicate_evidence
    assert scalar_value_evidence(var('x'),input_domains={'x':[0,1]}) is None
    assert predicate_evidence(pred('equal',var('x'),const(0)),input_domains={'x':[0,1]}) is None


def test_boolean_scalar_consumer_receives_relational_proof_as_supplement():
    from source_control_bounds import scalar_value_envelope
    x=var('bass');condition=pred('greater_equal',op('multiply',x,x),const(0))
    baseline=scalar_value_envelope(condition,input_domains={'bass':[-2,2]})
    with backend():result=scalar_value_envelope(condition,input_domains={'bass':[-2,2]})
    assert result['nominal_value_range']==baseline['nominal_value_range']
    assert result['solver_refinement']['nominal_value_range']==[1.,1.]
    assert result['solver_refinement']['predicate_status']=='proven'


def test_unrepresentable_fp_singleton_and_overflow_are_not_vacuous_proofs():
    from source_proofs import predicate_evidence
    with backend():
        missing=predicate_evidence(pred('equal',var('x'),var('x')),input_domains={'x':[.1,.1]},
                                   numeric_model='ieee754-binary32-rne')
        huge=op('multiply',const(1e30),const(1e30))
        overflow=predicate_evidence(pred('equal',huge,huge),numeric_model='ieee754-binary32-rne')
    assert missing['status']=='unsupported'
    assert overflow['status']=='unknown' and overflow['truth_value'] is None


def test_pinned_worker_version_mismatch_is_unavailable(tmp_path,monkeypatch):
    import source_proofs
    worker=tmp_path/'wrong.py'
    worker.write_text('import json\nprint(json.dumps({"protocol":1,"z3_version":"4.0.0.0"}),flush=True)\n')
    monkeypatch.setattr(source_proofs,'WORKER',worker)
    with backend() as session:
        result=source_proofs.scalar_value_evidence(var('x'),input_domains={'x':[0,1]})
    assert result['status']=='unavailable' and 'version/protocol mismatch' in result['reason']


def test_known_original_intermediate_overflow_cannot_cancel_into_a_proof():
    from source_control_bounds import scalar_value_envelope
    from source_proofs import scalar_value_evidence
    product=op('multiply',var('x'),var('x'));formula=op('subtract',product,product)
    with backend():
        direct=scalar_value_evidence(formula,input_domains={'x':[1e200,1e200]})
        envelope=scalar_value_envelope(formula,input_domains={'x':[1e200,1e200]})
    assert direct['status']=='unsupported' and direct['nominal_value_range'] is None
    assert 'overflow' in direct['original_value_domain']['unknown_reasons'][0]
    assert envelope['solver_refinement']['status']=='unsupported'
    assert envelope['nominal_value_range'] is None


def test_phase_qualified_input_name_requires_binding_adapter():
    from source_proofs import scalar_value_evidence
    name='init:per_frame_init_:bass'
    with backend():result=scalar_value_evidence(var(name),input_domains={name:[0,2]})
    assert result['status']=='unsupported'


def test_private_q_named_variable_does_not_reload_like_actual_q_registers():
    from equation_domains import main_q_domain_evidence
    source=native_source('counter=0;q999=0;','counter=min(1,counter+.25);q999=q999+1;q29=q999;')
    with backend():result=main_q_domain_evidence(source,policy='projectmtv-core-2.2.6-v1',
        candidates={'counter':[0,1]})['nominal_proof']
    assert result['status']=='unsupported'
    assert 'q999' in result['reason']


def test_total_solver_deadline_is_unknown_before_constructing_a_solver():
    from source_proofs_worker import Query
    query=Query(object(),1);query.deadline=0
    assert query.check([],None)=={'status':'unknown','reason':'request solver time budget exhausted'}
    assert query.unknowns==['request solver time budget exhausted']


def test_invariant_original_intermediate_overflow_is_retained():
    from equation_domains import main_q_domain_evidence
    source=native_source('counter=0;x=1e200;',
        'counter=min(1,counter+.25);q29=x*x-x*x;')
    with backend():result=main_q_domain_evidence(source,policy='projectmtv-core-2.2.6-v1',
        candidates={'counter':[0,1],'x':[1e200,1e200]})['nominal_proof']
    assert result['status']=='unsupported'
