import unittest
import importlib
import test_native_reader
import numpy as np


def native(body):return test_native_reader.NativeReaderTest().read(body)
def frames():
    return [{'time':(i+1)/30,'frame':i+1,'fps':30,'progress':0,
             'bass':1,'mid':1,'treb':1,'bass_att':1,'mid_att':1,'treb_att':1} for i in range(2)]


def test_scene_reader_rebuild_during_request_cannot_change_producer(tmp_path,monkeypatch):
    import shutil
    import pytest
    import scene_equations
    source=native('per_frame_1=q1=42;\n')
    binary=tmp_path/'reader';shutil.copy2(test_native_reader.READER,binary)
    original=scene_equations.mesh_inputs
    def replace(*args,**kwargs):
        binary.write_text('#!/bin/sh\nexit 7\n');binary.chmod(0o755)
        return original(*args,**kwargs)
    monkeypatch.setattr(scene_equations,'mesh_inputs',replace)
    with pytest.raises(ValueError,match='reader.*changed'):
        scene_equations.execute_scene(source,frames()[:1],reader=binary,mesh_x=8,mesh_y=8)


def test_scene_reader_replacement_after_execution_rejects_wrong_credit(tmp_path,monkeypatch):
    import shutil
    import subprocess
    import pytest
    import scene_equations
    source=native('per_frame_1=q1=42;\n')
    binary=tmp_path/'reader';shutil.copy2(test_native_reader.READER,binary)
    original=subprocess.run
    def replace(*args,**kwargs):
        result=original(*args,**kwargs)
        binary.write_bytes(b'replacement did not produce these equations')
        return result
    monkeypatch.setattr(subprocess,'run',replace)
    with pytest.raises(ValueError,match='reader.*changed'):
        scene_equations.execute_scene(source,frames()[:1],reader=binary,mesh_x=8,mesh_y=8)


def test_scene_reader_cwd_identity_cannot_execute_path_shadow(tmp_path,monkeypatch):
    import shutil,os,hashlib
    from pathlib import Path
    import scene_equations
    source=native('per_frame_1=q1=42;\n')
    binary=tmp_path/'reader';shutil.copy2(test_native_reader.READER,binary)
    expected=hashlib.sha256(binary.read_bytes()).hexdigest()
    other=tmp_path/'path-bin';other.mkdir();shadow=other/'reader'
    shadow.write_text('#!/bin/sh\nexit 7\n');shadow.chmod(0o755)
    monkeypatch.chdir(tmp_path);monkeypatch.setenv('PATH',str(other)+os.pathsep+os.environ['PATH'])
    result=scene_equations.execute_scene(source,frames()[:1],reader=Path('reader'),mesh_x=8,mesh_y=8)
    assert result['frames'][0]['main']['q1']==42
    assert result['reader_sha256']==expected


def test_scene_reader_rejects_stale_source_identity(tmp_path):
    import shutil,pytest
    import scene_equations
    source=native('per_frame_1=q1=42;\n')
    binary=tmp_path/'reader';shutil.copy2(test_native_reader.READER,binary)
    with pytest.raises(ValueError,match='reader.*identity'):
        scene_equations.execute_scene(source,frames()[:1],reader=binary,mesh_x=8,mesh_y=8,expected_reader_sha256='0'*64)


class SceneEquationsTest(unittest.TestCase):
    def test_main_init_shader_dimensions_are_separate_from_frame_dimensions(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_init_1=q1=pixelsx;q2=pixelsy;\n'
                      'per_frame_1=q3=pixelsx;q4=pixelsy;\n'
                      'shapecode_0_enabled=1\nshape_0_init1=t1=pixelsx;t2=q1;\n'
                      'shape_0_per_frame1=x=t1;y=t2;\n')
        result=module.execute_scene(source,frames(),reader=test_native_reader.READER,
                                    width=960,height=540,mesh_x=8,mesh_y=8,
                                    initial_shader_canvas=(1280,720))
        self.assertEqual(result['viewport'],[960,540])
        for frame in result['frames']:
            self.assertEqual([frame['main'][f'q{i}'] for i in range(1,5)],
                             [1280,720,960,540])
            # Custom contexts never receive main-only pixelsx/y builtins.
            self.assertEqual(frame['shapes'][0]['values']['x'],0)
            self.assertEqual(frame['shapes'][0]['values']['y'],1280)

    def test_main_init_aspect_comes_from_actual_viewport_not_reported_shader_size(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_init_1=q1=aspectx;q2=aspecty;\n')
        result=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                                    width=1296,height=720,mesh_x=8,mesh_y=8,
                                    initial_shader_canvas=(1288,716))
        main=result['frames'][0]['main']
        self.assertEqual(main['q1'],1)
        self.assertEqual(main['q2'],float(np.float32(1)/np.float32(720/1296)))

    def test_main_init_shader_canvas_requires_positive_int32_dimensions(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_1=q1=1;\n')
        for dimensions in [[],[8],(0,8),(8,-1),(True,8),(8.,8),(2**31,8)]:
            with self.subTest(dimensions=dimensions):
                with self.assertRaisesRegex(ValueError,'initial shader canvas'):
                    module.execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                                         initial_shader_canvas=dimensions)

    def test_legacy_motion_enable_is_the_fallback_for_missing_or_invalid_alpha(self):
        module=importlib.import_module('scene_equations')
        for text,expected in [('bMotionVectorsOn=1\n',1),
                              ('bMotionVectorsOn=1\nmv_a=0\n',0),
                              ('bMotionVectorsOn=1\nmv_a=invalid\n',1)]:
            source=native(text)
            result=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER,mesh_x=8,mesh_y=8)
            self.assertEqual(result['frames'][0]['main']['mv_a'],expected)

    def test_external_render_and_audio_values_enter_eel_as_native_float32(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_1=q1=time;q2=bass;gamma=20;echo_zoom=-1;\nper_pixel_1=zoom=time;\n')
        inputs=frames()[:1];inputs[0]['time']=.123456789;inputs[0]['bass']=1.23456789
        result=module.execute_scene(source,inputs,reader=test_native_reader.READER,mesh_x=8,mesh_y=8)['frames'][0]
        self.assertEqual(result['main']['q1'],float(np.float32(.123456789)))
        self.assertEqual(result['main']['q2'],float(np.float32(1.23456789)))
        self.assertEqual(result['mesh'][0]['zoom'],float(np.float32(.123456789)))
        self.assertEqual(result['main']['gamma'],8)
        self.assertEqual(result['main']['echo_zoom'],.001)

    def test_pixel_state_runs_in_row_order_with_q_carry_and_separate_main_locals(self):
        module=importlib.import_module('scene_equations')
        source=native('warp=0\nper_frame_init_1=q1=4;counter=100;\n'
                      'per_frame_1=q1+=bass;bass=99;zoom=2;\n'
                      'per_pixel_1=q1+=1;counter+=1;dx=q1*.01;dy=counter*.001;zoom+=x;rot=bass;\n'
                      'shapecode_0_enabled=1\nshape_0_per_frame1=rad=q1;\n')
        result=module.execute_scene(source,frames(),reader=test_native_reader.READER,mesh_x=8,mesh_y=8)
        first,second=[f['mesh'] for f in result['frames']]
        self.assertEqual(len(first),81)
        self.assertAlmostEqual(first[0]['dx'],.06)
        self.assertAlmostEqual(first[-1]['dx'],.86)
        self.assertAlmostEqual(second[0]['dx'],.06)
        self.assertAlmostEqual(second[0]['dy'],.082)
        self.assertEqual(first[0]['zoom'],2)
        self.assertEqual(first[1]['zoom'],2.125)
        self.assertEqual(first[0]['rot'],1) # Inputs loaded before main code writes bass.
        self.assertEqual(result['frames'][0]['main_custom']['counter'],100)
        self.assertEqual(result['frames'][0]['shapes'][0]['values']['rad'],5)

    def test_pixel_shared_memory_precedes_shape_execution_and_uses_direct_aspect(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_1=q1=aspecty;\n'
                      'per_pixel_1=gmegabuf(0)+=1;zoom=aspecty;dx=y;dy=ang;\n'
                      'shapecode_0_enabled=1\nshape_0_per_frame1=rad=gmegabuf(0);\n')
        frame=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER,
                                   width=128,height=72,mesh_x=8,mesh_y=8)['frames'][0]
        self.assertEqual(frame['main']['q1'],float(np.float32(1)/np.float32(.5625)))
        self.assertEqual(frame['mesh'][0]['zoom'],.5625)
        self.assertEqual(frame['mesh'][0]['dx'],.21875)
        self.assertAlmostEqual(frame['mesh'][8*9+4]['dy'],-np.pi/2,places=6)
        self.assertEqual(frame['shapes'][0]['values']['rad'],81)

    def test_seeded_scene_randomness_is_repeatable_and_reported(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_init_1=q1=rand(10000);\nper_frame_1=q2=rand(10000);\n')
        first=module.execute_scene(source,frames(),reader=test_native_reader.READER,seed=12345)
        second=module.execute_scene(source,frames(),reader=test_native_reader.READER,seed=12345)
        other=module.execute_scene(source,frames(),reader=test_native_reader.READER,seed=98765)
        self.assertEqual(first['frames'],second['frames'])
        self.assertNotEqual(first['frames'],other['frames'])
        self.assertEqual(first['equation_rng_seed'],12345)

    def test_production_rng_draws_carry_across_33_shape_instances_and_60_frames(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_init_1=q1=rand(1);\n'
                      'per_frame_1=q2=rand(1);\n'
                      'shapecode_0_enabled=1\nshapecode_0_num_inst=33\n'
                      'shape_0_per_frame1=x=rand(1);y=rand(1);rad=rand(1);\n')
        inputs=[{**frames()[0],'time':(i+1)/30,'frame':i+1} for i in range(60)]
        result=module.execute_scene(source,inputs,reader=test_native_reader.READER,
                                    mesh_x=8,mesh_y=8,seed=0x4141f00d)
        generator=np.random.RandomState(0x4141f00d)
        expected=generator.randint(0,2**32,size=1+60*(1+33*3),dtype=np.uint32).astype(np.float64)*(1.0/(2**32-1))
        self.assertEqual(result['frames'][0]['main']['q1'],expected[0])
        for index,frame in enumerate(result['frames']):
            first=1+index*100
            self.assertEqual(frame['main']['q2'],expected[first])
            actual=[[shape['values'][key] for key in ['x','y','rad']] for shape in frame['shapes']]
            np.testing.assert_array_equal(actual,expected[first+1:first+100].reshape(33,3))

    def test_native_scalar_parsing_keeps_positive_bool_and_float_prefix_rules(self):
        module=importlib.import_module('scene_equations')
        source=native('zoom=1.2trailing\nshapecode_0_enabled=-1\n')
        result=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER)
        self.assertEqual(result['frames'][0]['shapes'],[])
        self.assertAlmostEqual(result['frames'][0]['main']['zoom'],1.2000000476837158,places=12)

    def test_out_of_range_scalar_values_use_native_constructor_defaults(self):
        module=importlib.import_module('scene_equations')
        source=native('zoom=1e100\nshapecode_0_enabled=1\nshapecode_0_sides=999999999999999999999\n')
        result=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER)
        self.assertEqual(result['frames'][0]['main']['zoom'],1)
        self.assertEqual(result['frames'][0]['shapes'][0]['values']['sides'],4)

    def test_main_init_and_shape_state_transfer_is_automatic_from_source(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_init_1=q1=10;ma=0;\n'
            'per_frame_1=q1+=bass;ma+=1;\n'
            'shapecode_0_enabled=1\nshapecode_0_num_inst=2\n'
            'shape_0_init1=t1=2;ma=0;\n'
            'shape_0_per_frame1=ma+=1;x=ma*.1;rad=q1*.01;t1+=1;\n')
        result=module.execute_scene(source,frames(),reader=test_native_reader.READER)
        self.assertEqual([f['main']['q1'] for f in result['frames']],[11,11])
        self.assertEqual([f['main_custom']['ma'] for f in result['frames']],[1,2])
        shapes=[s['values'] for f in result['frames'] for s in f['shapes']]
        self.assertEqual([round(s['x'],6) for s in shapes],[.1,.2,.3,.4])
        self.assertEqual([s['t1'] for s in shapes],[3,3,3,3])
        for shape in shapes:self.assertAlmostEqual(shape['rad'],.11)

    def test_disabled_component_init_can_affect_shared_memory_without_drawing(self):
        module=importlib.import_module('scene_equations')
        source=native('shapecode_0_enabled=0\nshape_0_init1=gmegabuf(2)=.7;\n'
                      'shapecode_1_enabled=1\nshape_1_per_frame1=rad=gmegabuf(2);\n')
        result=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER)
        self.assertEqual([s['index'] for s in result['frames'][0]['shapes']],[1])
        self.assertAlmostEqual(result['frames'][0]['shapes'][0]['values']['rad'],.7)

    def test_preset_float_defaults_and_shape_defaults_load_as_native_float32(self):
        module=importlib.import_module('scene_equations')
        source=native('zoom=1.2\nfDecay=.9\nshapecode_0_enabled=1\n')
        result=module.execute_scene(source,frames()[:1],reader=test_native_reader.READER)
        self.assertAlmostEqual(result['frames'][0]['main']['zoom'],1.2000000476837158,places=12)
        self.assertAlmostEqual(result['frames'][0]['main']['decay'],.8999999761581421,places=12)
        self.assertEqual(result['frames'][0]['shapes'][0]['values']['r'],1)
        self.assertEqual(result['frames'][0]['shapes'][0]['values']['g'],0)

    def test_original_dialect_accepted_but_target_rejected_code_is_not_executed_as_native(self):
        module=importlib.import_module('scene_equations')
        source=native('per_frame_1=is_beat=1;\nper_frame_2=q1=is_\nper_frame_3=beat;\n')
        with self.assertRaisesRegex(ValueError,'target'):
            module.execute_scene(source,frames()[:1],reader=test_native_reader.READER)

    def test_active_wave_requires_explicit_native_audio_arrays(self):
        module=importlib.import_module('scene_equations')
        with self.assertRaisesRegex(ValueError,'wave'):
            module.execute_scene(native('wavecode_0_enabled=1\n'),frames()[:1],reader=test_native_reader.READER)


if __name__=='__main__':unittest.main()
