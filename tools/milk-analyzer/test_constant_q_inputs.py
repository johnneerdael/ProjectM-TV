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


def test_partial_q_defaults_preserve_live_component_and_resolve_selector():
    from equation_loading import constant_q_components
    from field_math import evaluate
    source=test_native_reader.NativeReaderTest().read(
        'PSVERSION_WARP=2\nper_frame_1=q32=time;\n'
        'warp_1=`shader_body {float x;if(q29==0){x=.4;}ret=x+q32;}\n')
    known=constant_q_components(source,policy='projectmtv-core-2.2.6-v1')
    assert known['_qh']=={0:0,1:0,2:0}
    model=ShaderFields(stage='warp',frame=1,warp_reads_blur=False,known_uniform_components=known)
    result=model.lower(source['sections']['warp_']['tree'])
    assert model.complete,model.unknown
    from pytest import approx
    assert list(evaluate(result,inputs={'_qh':[9,8,7,.2]}))==approx([.6]*3)


def test_partial_q_defaults_do_not_prove_referenced_or_missing_tree_components():
    from equation_loading import constant_q_components
    source=test_native_reader.NativeReaderTest().read('per_pixel_1=q29=q30;\n')
    known=constant_q_components(source,policy='projectmtv-core-2.2.6-v1')
    assert known['_qh']=={2:0,3:0}
    source['sections']['per_pixel_'].pop('projectm_raw_tree')
    assert constant_q_components(source,policy='projectmtv-core-2.2.6-v1')=={}


def test_partial_q_defaults_do_not_replace_shader_local_storage():
    source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n'
        'comp_1=`shader_body {float4 _qh;ret=_qh.x;}\n')
    model=ShaderFields(stage='composite',frame=1,warp_reads_blur=False,
                       known_uniform_components={'_qh':{0:0}})
    model.lower(source['sections']['comp_']['tree'])
    assert not model.complete
