import test_native_reader


def source(initial,frame):
    return test_native_reader.NativeReaderTest().read(
        'per_frame_init_1='+initial+'\nper_frame_1='+frame+'\n')


def test_modulo_counter_proves_q_range_for_all_frames():
    from equation_domains import main_q_domains
    d=source('index4=rand(12);',
        'is_beat=above(bass,avg)*above(time,t0);'
        'index4=(index4+is_beat*bnot(index)*bnot(index2)*bnot(index3))%8;q29=index4;')
    assert main_q_domains(d,policy='projectmtv-core-2.2.6-v1')['q29']==(0,7)


def test_negative_seed_cannot_prove_nonnegative_q_range():
    from equation_domains import main_q_domains
    d=source('index4=-12;', 'index4=(index4+above(bass,avg))%8;q29=index4;')
    assert 'q29' not in main_q_domains(d,policy='projectmtv-core-2.2.6-v1')


def test_unbounded_recurrence_cannot_prove_finite_q_range():
    from equation_domains import main_q_domains
    d=source('index4=rand(12);', 'index4=index4+1;q29=index4;')
    assert 'q29' not in main_q_domains(d,policy='projectmtv-core-2.2.6-v1')


def test_nested_assignment_or_missing_tree_blocks_range_inference():
    from equation_domains import main_q_domains
    d=source('index4=rand(12);', 'q29=exec2(index4=-1,index4%8);')
    assert main_q_domains(d,policy='projectmtv-core-2.2.6-v1')=={}
    d=source('index4=rand(12);', 'index4=index4%8;q29=index4;')
    d['sections']['per_frame_'].pop('projectm_raw_tree')
    assert main_q_domains(d,policy='projectmtv-core-2.2.6-v1')=={}


def test_frame_audio_and_builtin_resets_cannot_inherit_init_values():
    from equation_domains import main_q_domains
    d=source('bass=0;zoom=2;', 'q29=bass;q30=zoom;')
    domains=main_q_domains(d,policy='projectmtv-core-2.2.6-v1')
    assert 'q29' not in domains
    assert 'q30' not in domains


def test_frame_q_inputs_reset_to_init_values_instead_of_accumulating():
    from equation_domains import main_q_domains
    d=source('q29=2;', 'q29=q29+1;')
    assert main_q_domains(d,policy='projectmtv-core-2.2.6-v1')['q29']==(3,3)


def test_shared_register_dependency_cannot_ignore_other_phase_initialization():
    from equation_domains import main_q_domains
    d=test_native_reader.NativeReaderTest().read('per_frame_init_1=reg00=2;\n'
        'per_frame_1=q29=reg00;\nshapecode_0_enabled=0\nshape_0_init1=reg00=9;\n')
    assert main_q_domains(d,policy='projectmtv-core-2.2.6-v1')=={}


def test_native_ieee_constant_export_stays_unknown_without_crashing():
    from equation_domains import main_q_domains
    d=source('x=exp(1000);', 'q29=x;')
    assert 'q29' not in main_q_domains(d,policy='projectmtv-core-2.2.6-v1')
