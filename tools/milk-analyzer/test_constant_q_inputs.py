import test_native_reader
from shader_fields import ShaderFields


def test_unused_q_bank_is_zero_but_referenced_bank_is_not_assumed():
    from equation_loading import constant_q_banks
    source=test_native_reader.NativeReaderTest().read('per_frame_1=q1=time;\n')
    banks=constant_q_banks(source,policy='projectmtv-core-2.2.6-v1')
    assert '_qa' not in banks
    assert banks['_qh']==[0,0,0,0]


def test_rejected_equations_cannot_establish_zero_q_inputs():
    from equation_loading import constant_q_banks
    source=test_native_reader.NativeReaderTest().read('per_pixel_1=q1=is_\nper_pixel_2=beat;\n')
    assert constant_q_banks(source,policy='projectmtv-core-2.2.6-v1')=={}


def test_missing_raw_tree_cannot_establish_zero_q_inputs():
    from equation_loading import constant_q_banks
    source=test_native_reader.NativeReaderTest().read('per_frame_1=q29=time;\n')
    source['sections']['per_frame_'].pop('projectm_raw_tree')
    assert constant_q_banks(source,policy='projectmtv-core-2.2.6-v1')=={}


def test_known_q_input_resolves_only_selected_initialization_branch():
    source=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\n'
        'warp_1=`shader_body {float x;if(q29==0){x=.4;}ret=x;}\n')
    model=ShaderFields(stage='warp',frame=1,warp_reads_blur=False,known_uniforms={'_qh':[0,0,0,0]})
    model.lower(source['sections']['warp_']['tree'])
    assert model.complete,model.unknown


def test_known_uniform_does_not_initialize_generated_writable_replacement():
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
        'comp_1=`shader_body {q18=1;ret=q19;}\n')
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,known_uniforms={'_qe':[0,0,0,0]})
    model.lower(source['sections']['comp_']['tree'])
    assert not model.complete
