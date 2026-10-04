import unittest
from test_scene_equations import native,frames
from test_native_reader import READER
from scene_equations import execute_scene


def audio_frames():
    return [{**values,'waveform_left':[0]*480,'waveform_right':[0]*480,
             'spectrum_left':[1]*512,'spectrum_right':[1]*512} for values in frames()]


class CustomWaveSceneTest(unittest.TestCase):
    def test_invalid_separation_does_not_read_outside_native_audio(self):
        source=native('wavecode_0_enabled=1\nwavecode_0_samples=512\nwavecode_0_sep=10\n')
        with self.assertRaisesRegex(ValueError,'index out of bounds'):
            execute_scene(source,audio_frames()[:1],reader=READER,mesh_x=8,mesh_y=8)

    def test_wave_init_frame_point_contexts_and_qt_boundaries_are_native(self):
        source=native('wavecode_0_enabled=1\nwavecode_0_samples=3\n'
                      'per_frame_init_1=q1=10;\nper_frame_1=q1+=bass;bass=99;\n'
                      'wave_0_init1=t1=2;counter=0;\nwave_0_per_frame1=t1+=1;r=bass;counter+=1;\n'
                      'wave_0_per_point1=q1+=1;t1+=1;pc+=1;x=q1;y=t1;g=bass;b=pc;\n')
        result=execute_scene(source,audio_frames(),reader=READER,mesh_x=8,mesh_y=8)
        first,second=[f['waves'][0] for f in result['frames']]
        self.assertEqual([p['x'] for p in first['points']],[12,13,14])
        self.assertEqual([p['y'] for p in first['points']],[4,5,6])
        self.assertEqual([p['r'] for p in first['points']],[1]*3)
        self.assertEqual([p['g'] for p in first['points']],[99]*3)
        self.assertEqual([p['b'] for p in second['points']],[4,5,6])
        self.assertEqual([p['x'] for p in second['points']],[12,13,14])
        self.assertEqual([p['y'] for p in second['points']],[4,5,6])
        self.assertEqual(first['frame']['counter'],1)
        self.assertEqual(second['frame']['counter'],2)

    def test_negative_enabled_integer_and_dynamic_sample_count_are_not_bool_flags(self):
        source=native('wavecode_0_enabled=-1\nwavecode_0_samples=512\n'
                      'wave_0_per_frame1=samples=3+frame;\nwave_0_per_point1=x=sample;\n')
        result=execute_scene(source,audio_frames(),reader=READER,mesh_x=8,mesh_y=8)
        self.assertEqual([f['waves'][0]['sample_count'] for f in result['frames']],[4,5])
        self.assertEqual(result['frames'][0]['waves'][0]['points'][-1]['x'],1)

    def test_shape_memory_changes_precede_wave_and_wave_changes_reach_next_frame(self):
        source=native('wavecode_0_enabled=1\nwavecode_0_samples=2\n'
                      'shapecode_0_enabled=1\nshape_0_per_frame1=gmegabuf(0)+=10;\n'
                      'per_frame_1=q1=gmegabuf(0);\nwave_0_per_point1=gmegabuf(0)+=1;x=gmegabuf(0);\n')
        result=execute_scene(source,audio_frames(),reader=READER,mesh_x=8,mesh_y=8)
        self.assertEqual([p['x'] for p in result['frames'][0]['waves'][0]['points']],[11,12])
        self.assertEqual(result['frames'][1]['main']['q1'],12)


if __name__=='__main__':unittest.main()
