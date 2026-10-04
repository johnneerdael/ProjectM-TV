import test_native_reader
from pytest import approx
from shader_fields import ShaderFields
from field_math import evaluate


def lower(code,domains=None):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\nwarp_1=`'+code+'\n')
    model=ShaderFields(stage='warp',frame=1,warp_reads_blur=False,
        known_uniform_component_domains=domains or {})
    return model,model.lower(source['sections']['warp_']['tree'])


CODE='shader_body {int k=int(q29)%4;float x;if(k==0){x=.1;}else if(k==1){x=.2;}else if(k==2){x=.3;}else if(k==3){x=.4;}ret=x;}'


def test_selector_cover_is_proven_and_preserves_runtime_choice():
    model,result=lower(CODE,{'_qh':{0:(0,7)}})
    assert model.complete,model.unknown
    for q in range(8):
        assert evaluate(result,inputs={'_qh':[q,0,0,0]}).tolist()==approx([.1*(q%4+1)]*3)


def test_no_bound_or_negative_selector_keeps_unassigned_path_unknown():
    for domains in [{},{'_qh':{0:(-7,7)}}]:
        model,_=lower(CODE,domains)
        assert not model.complete


def test_missing_selector_case_remains_uninitialized():
    model,_=lower(CODE.replace('else if(k==3){x=.4;}',''),{'_qh':{0:(0,7)}})
    assert not model.complete


def test_selector_mutation_does_not_reuse_an_old_branch_constraint():
    code='shader_body {int k=int(q29)%4;float x;if(k==0){x=.1;}else {k=int(q30);if(k==1){x=.2;}}ret=x;}'
    model,_=lower(code,{'_qh':{0:(0,7)}})
    assert not model.complete


def test_local_uniform_name_shadowing_cannot_borrow_input_bounds():
    model,_=lower('shader_body {float4 _qh;int k=int(_qh.x)%4;float x;if(k==0){x=.1;}ret=x;}',{'_qh':{0:(0,7)}})
    assert not model.complete


def test_folded_branch_keeps_runtime_domain_guard_scalar_and_grid():
    import numpy as np
    from pytest import raises
    from field_math import UnresolvedMath
    from grid_math import evaluate_grid
    model,result=lower('shader_body {int k=int(q29);float x;if(k==0){x=.4;}ret=x;}',{'_qh':{0:(0,0)}})
    assert model.complete,model.unknown
    with raises(UnresolvedMath,match='source domain'):
        evaluate(result,inputs={'_qh':[1,0,0,0]})
    with raises(UnresolvedMath,match='source domain'):
        evaluate_grid(result,batch_shape=(2,),inputs={'_qh':np.array([[0,0,0,0],[1,0,0,0]])})


def test_int_conversion_domain_overflow_cannot_prove_branch_cover():
    model,_=lower(CODE,{'_qh':{0:(0,2147483647)}})
    assert not model.complete


def test_float32_boundary_is_narrowed_before_selector_proof():
    from pytest import raises
    from field_math import UnresolvedMath
    code='shader_body {int k=int(q29);float x;if(k==16777216){x=.2;}ret=x;}'
    model,result=lower(code,{'_qh':{0:(16777216,16777217)}})
    assert model.complete,model.unknown
    assert evaluate(result,inputs={'_qh':[16777217,0,0,0]}).tolist()==approx([.2]*3)
    with raises(UnresolvedMath,match='source domain'):
        evaluate(result,inputs={'_qh':[16777218,0,0,0]})
