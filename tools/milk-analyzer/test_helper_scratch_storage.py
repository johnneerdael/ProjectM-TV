from pytest import approx
import test_native_reader
from shader_fields import ShaderFields
from field_math import evaluate


def lower(code):
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`'+code+'\n')
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False)
    result=model.lower(source['sections']['comp_']['tree'])
    return model,result


def test_exclusive_helper_scratch_is_independent_across_unordered_calls():
    model,result=lower('float scratch;float h(float x){scratch=x*2;return scratch;} '
                       'shader_body {ret=h(.1)+h(.2);}')
    assert model.complete,model.unknown
    assert evaluate(result).tolist()==approx([.6]*3)


def test_external_read_keeps_shared_helper_state_order_unresolved():
    model,_=lower('float scratch;float h(float x){scratch=x*2;return scratch;} '
                  'shader_body {ret=h(.1)+h(.2);ret+=scratch;}')
    assert not model.complete
    assert 'arithmetic/comparison side-effect order not established' in model.unknown


def test_exclusive_scratch_read_before_write_remains_unresolved():
    model,_=lower('float scratch;float h(float x){scratch+=x;return scratch;} '
                  'shader_body {ret=h(.1)+h(.2);}')
    assert not model.complete
    assert 'uninitialized shader value reaches a read' in model.unknown


def test_two_helpers_sharing_storage_are_not_localized():
    model,_=lower('float scratch;float h(float x){scratch=x;return scratch;} '
                  'float g(float x){return scratch+x;} '
                  'shader_body {ret=h(.1)+g(.2);}')
    assert not model.complete


def test_initialized_helper_global_retains_its_declared_value():
    model,result=lower('float scratch=.3;float h(float x){return scratch+x;} '
                       'shader_body {ret=h(.1)+h(.2);}')
    assert model.complete,model.unknown
    assert evaluate(result).tolist()==approx([.9]*3)
