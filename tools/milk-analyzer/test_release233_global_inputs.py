import os
import test_native_reader
import json,subprocess,tempfile
from pathlib import Path
import numpy as np
from pytest import approx,raises
from shader_fields import ShaderFields
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid

READER=Path(os.environ.get("MILK_TEST_CURRENT_BINARIES",test_native_reader.READER.parent))/"milk-native-reader"
POLICY='projectmtv-implicit-extern-zero-v1'


def model(code,*,policy=POLICY):
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'control.milk'
        path.write_text('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=3\ncomp_1=`'+code+'\n')
        source=json.loads(subprocess.check_output([str(READER),str(path)]))
    section=source['sections']['comp_'];assert section['implicit_global_input_policy']==POLICY
    m=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,global_input_policy=policy)
    return m,m.lower(section['tree'])


def test_current_zero_defaults_preserve_global_read_and_write_order():
    for code,expected in [
        ('float3 mus;shader_body{ret=mus+.25;}',[.25]*3),
        ('float dist_c;shader_body{float x=dist_c;dist_c=.4;ret=x+.25;}',[.25]*3),
        ('float2 uv3;shader_body{uv3=.4*cos(42*uv3);ret=float3(uv3,0);}',[.4,.4,0])]:
        m,result=model(code);assert m.complete,m.unknown
        assert evaluate(result).tolist()==approx(expected)
        np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,)),[expected,expected],atol=1e-6)


def test_explicit_runtime_binding_overrides_unbound_default():
    m,result=model('float dist_c;shader_body{float x=dist_c;dist_c=.4;ret=x+.25;}')
    assert m.complete,m.unknown
    assert evaluate(result,inputs={'dist_c':.2}).tolist()==approx([.45]*3)
    np.testing.assert_allclose(evaluate_grid(result,batch_shape=(2,),inputs={'dist_c':np.array([.1,.2])}),[[.35]*3,[.45]*3],atol=1e-6)


def test_strict_policy_does_not_invent_external_values():
    m,result=model('float3 mus;shader_body{ret=mus+.25;}',policy='strict-v1')
    with raises(UnresolvedMath,match='missing symbolic'):evaluate(result)


def test_local_uninitialized_storage_does_not_receive_global_defaults():
    m,_=model('shader_body{float2 v;ret=float3(v,0);}')
    assert not m.complete
