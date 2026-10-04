import json
import subprocess
import tempfile
import unittest
from pathlib import Path
import numpy as np
from test_native_audio import ROOT

BINARY=ROOT/'build/milk-analyzer/native/milk-wave-inputs'


def frame(**settings):
    return {'waveform_left':[0]*480,'waveform_right':[0]*480,
            'spectrum_left':[1]*512,'spectrum_right':[1]*512,**settings}


class NativeWaveTest(unittest.TestCase):
    def test_circle_time_matches_native_double_before_float_angle_storage(self):
        time=10001.123456789
        process,report=self.run_wave(0,[frame(time=time,wave_x=.5,wave_y=.5,wave_mystery=0)],wave_smoothing=0)
        self.assertEqual(process.returncode,0,process.stderr)
        angle=np.float32(time*float(np.float32(.2)))
        expected=[np.float32(.5)*np.cos(angle)*np.float32(288/512),np.float32(.5)*np.sin(angle)]
        np.testing.assert_allclose(report['frames'][0]['vertex_waves'][0][0],expected,atol=1e-7,rtol=0)

    def run_wave(self,mode,frames,**settings):
        self.assertTrue(BINARY.is_file(),'CPU waveform bridge has not been built')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);request=root/'request.json';output=root/'wave.json'
            request.write_text(json.dumps({'mode':mode,'frames':frames,'width':512,'height':288,'output':str(output),**settings}))
            process=subprocess.run([str(BINARY),str(request)],capture_output=True,text=True)
            result=json.loads(output.read_text()) if output.exists() else None
            return process,result

    def test_native_line_uses_x_for_vertical_position_and_ignores_y(self):
        process,report=self.run_wave(6,[frame(wave_x=.25,wave_y=.1),frame(wave_x=.25,wave_y=.9)])
        self.assertEqual(process.returncode,0,process.stderr)
        first,second=[np.asarray(f['vertex_waves'][0]) for f in report['frames']]
        self.assertEqual(len(first),159)
        np.testing.assert_array_equal(first,second)
        np.testing.assert_allclose(first[:,1],-.5*np.sin(np.float32(1.57)),atol=2e-7)
        self.assertFalse(report['uses_rendered_reference'])
        self.assertIn('Waveforms/Line.cpp',report['source_hashes'])

    def test_all_sixteen_native_modes_generate_finite_geometry_under_declared_safe_inputs(self):
        for mode in range(16):
            with self.subTest(mode=mode):
                process,report=self.run_wave(mode,[frame(time=1)])
                self.assertEqual(process.returncode,0,process.stderr)
                self.assertTrue(any(f for f in report['frames'][0]['vertex_waves']))
                for wave in report['frames'][0]['vertex_waves']:self.assertTrue(np.all(np.isfinite(wave)))

    def test_spectrum_zero_domain_is_unresolved_and_inputs_have_exact_native_sizes(self):
        for values in [frame(spectrum_left=[0]*512),frame(waveform_left=[0]*479)]:
            process,report=self.run_wave(8,[values])
            self.assertNotEqual(process.returncode,0)
            self.assertIsNone(report)
        process,report=self.run_wave(15,[frame(time=0)])
        self.assertNotEqual(process.returncode,0)
        self.assertIsNone(report)

    def test_stateful_smoothing_tail_affects_later_geometry(self):
        first=frame(waveform_left=[128]*480,waveform_right=[128]*480)
        second=frame()
        process,report=self.run_wave(2,[first,second],wave_smoothing=.75)
        self.assertEqual(process.returncode,0,process.stderr)
        process,fresh=self.run_wave(2,[second],wave_smoothing=.75)
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertNotEqual(report['frames'][1]['vertex_waves'],fresh['frames'][0]['vertex_waves'])


if __name__=='__main__':unittest.main()
