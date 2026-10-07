import json
import subprocess
import tempfile
import unittest
import os
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
BINARY=ROOT/'build/milk-analyzer/native/milk-audio-inputs'
CLOCK_BINARY=Path(os.environ.get('MILK_NATIVE_CLOCK_AUDIO_BINARY', BINARY))


class NativeAudioTest(unittest.TestCase):
    def run_audio(self,data,channels=1,frames=2,fps=30,clock_policy=None,binary=None,
                  preset_progress_policy=None,entropy_seed=None):
        binary=BINARY if binary is None else binary
        self.assertTrue(binary.is_file(),'native CPU audio bridge has not been built')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);pcm=root/'samples.f32';pcm.write_bytes(np.asarray(data,dtype='<f4').tobytes())
            request=root/'request.json';output=root/'audio.json'
            settings={'pcm_path':str(pcm),'output':str(output),'fps':fps,'frames':frames,'channels':channels}
            if clock_policy is not None:settings['clock_policy']=clock_policy
            if preset_progress_policy is not None:settings['preset_progress_policy']=preset_progress_policy
            if entropy_seed is not None:settings['entropy_seed']=entropy_seed
            request.write_text(json.dumps(settings))
            result=subprocess.run([str(binary),str(request)],capture_output=True,text=True)
            report=json.loads(output.read_text()) if output.exists() else None
            return result,report

    def test_silent_pcm_exports_native_arrays_and_relative_band_defaults(self):
        process,report=self.run_audio(np.zeros(1470*2))
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertFalse(report['uses_rendered_reference'])
        self.assertEqual(len(report['frames']),2)
        first=report['frames'][0]
        self.assertEqual(first['frame'],0)
        self.assertEqual(first['time'],1/30)
        self.assertEqual(first['bass'],1)
        self.assertEqual(len(first['waveform_left']),480)
        self.assertEqual(len(first['spectrum_left']),512)
        self.assertEqual(max(first['waveform_left']),0)
        self.assertEqual(max(first['spectrum_left']),0)
        self.assertEqual(report['engine_archive_sha256'].__len__(),64)

    def test_stereo_channels_stay_separate_and_execution_is_repeatable(self):
        t=np.arange(2940)/44100
        samples=np.stack((.1*np.sin(2*np.pi*80*t),np.zeros_like(t)),axis=-1)
        first,report=self.run_audio(samples,channels=2)
        self.assertEqual(first.returncode,0,first.stderr)
        second,again=self.run_audio(samples,channels=2)
        self.assertEqual(second.returncode,0,second.stderr)
        self.assertEqual(report['frames'],again['frames'])
        self.assertGreater(max(np.abs(report['frames'][-1]['waveform_left'])),0)
        self.assertEqual(max(np.abs(report['frames'][-1]['waveform_right'])),0)

    def test_invalid_or_truncated_pcm_does_not_export_success(self):
        for samples in [np.zeros(1470),np.full(2940,np.nan),np.full(2940,2)]:
            process,report=self.run_audio(samples)
            self.assertNotEqual(process.returncode,0)
            self.assertIsNone(report)

    def test_noninteger_schedule_fields_are_not_silently_truncated(self):
        for settings in [{'fps':30.5},{'frames':2.1},{'channels':1.2}]:
            process,report=self.run_audio(np.zeros(2940),**settings)
            self.assertNotEqual(process.returncode,0)
            self.assertIsNone(report)

    def test_jni_clock_uses_rounded_nanoseconds_for_time_and_band_updates(self):
        policy='projectmtv-jni-rounded-nanoseconds30-v1'
        process,report=self.run_audio(np.zeros(4410),frames=3,clock_policy=policy,binary=CLOCK_BINARY)
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertEqual([f['time'] for f in report['frames']],
                         [33333333/1e9,66666667/1e9,.1])
        self.assertEqual(report['render_clock_policy'],policy)
        self.assertEqual([f['clock_nanoseconds'] for f in report['frames']],
                         [33333333,66666667,100000000])

    def test_jni_clock_rejects_an_incompatible_cadence_or_unknown_policy(self):
        for fps,policy in [(60,'projectmtv-jni-rounded-nanoseconds30-v1'),
                           (30,'unknown-clock')]:
            process,report=self.run_audio(np.zeros(2*(44100//fps)),fps=fps,clock_policy=policy,binary=CLOCK_BINARY)
            self.assertNotEqual(process.returncode,0)
            self.assertIsNone(report)

    def test_rounded_clock_changes_nonzero_loudness_decay_not_only_reported_time(self):
        t=np.arange(2940)/44100
        samples=.1*np.sin(2*np.pi*80*t)
        process,rounded=self.run_audio(samples,clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',binary=CLOCK_BINARY)
        baseline,ideal=self.run_audio(samples,binary=CLOCK_BINARY)
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertEqual(baseline.returncode,0,baseline.stderr)
        self.assertNotEqual(rounded['frames'][0]['bass_att'],ideal['frames'][0]['bass_att'])

    def test_cold_jni_progress_matches_qualified_context_or_rejects_other_producers(self):
        baseline,identity=self.run_audio(np.zeros(2940),binary=CLOCK_BINARY)
        self.assertEqual(baseline.returncode,0,baseline.stderr)
        process,report=self.run_audio(np.zeros(44100),frames=30,binary=CLOCK_BINARY,
            clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
            preset_progress_policy='projectmtv-core-2.3.16-cold-jni-v1',entropy_seed=12345)
        if identity.get('duration_distribution_model')!='libcxx-200100-fresh-normal-v1':
            self.assertNotEqual(process.returncode,0)
            self.assertIn('qualified libcxx-200100',process.stderr)
            self.assertIsNone(report)
            return
        if identity['engine_identity']['patches_sha256']!='cd01f0f3cce4f6be05d781b06192dadadbd8254a6fa1c03ea52394d3e48f9ded':
            self.assertNotEqual(process.returncode,0)
            self.assertIn('pinned 2.3.16',process.stderr)
            self.assertIsNone(report)
            return
        self.assertEqual(process.returncode,0,process.stderr)
        self.assertEqual(report['preset_timing']['sampled_duration_seconds'],29.618844229502262)
        self.assertEqual(np.float32(report['frames'][0]['progress']),np.float32(.001125409617088735))
        self.assertEqual(np.float32(report['frames'][-1]['progress']),np.float32(.03376229107379913))

    def test_cold_jni_progress_requires_known_clock_and_uint32_seed(self):
        for options in [dict(),dict(entropy_seed=-1),dict(entropy_seed=True),
                        dict(entropy_seed=.5),dict(entropy_seed=2**32),
                        dict(entropy_seed=12345,frames=31),dict(entropy_seed=12345,channels=2),
                        dict(entropy_seed=12345,clock_policy='ideal-frame-fractions-v1'),
                        dict(entropy_seed=12345,preset_progress_policy='unknown')]:
            settings=dict(binary=CLOCK_BINARY,clock_policy='projectmtv-jni-rounded-nanoseconds30-v1',
                          preset_progress_policy='projectmtv-core-2.3.16-cold-jni-v1')
            settings.update(options)
            frames=settings.get('frames',2);channels=settings.get('channels',1)
            process,report=self.run_audio(np.zeros(frames*1470*channels),**settings)
            self.assertNotEqual(process.returncode,0)
            self.assertIsNone(report)


if __name__=='__main__':unittest.main()
