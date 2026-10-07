import unittest
import os
import pytest
import tempfile
import subprocess
import json
import hashlib
from pathlib import Path
import numpy as np
import importlib


ROOT=Path(__file__).resolve().parents[2]
BINARY=Path(os.environ.get('MILK_NATIVE_NOISE_BINARY',ROOT/'build/milk-analyzer/native/milk-noise-inputs'))


class NoiseInputsTest(unittest.TestCase):
    def test_packed_channels_follow_declared_upload_format(self):
        module=importlib.import_module('noise_inputs')
        word=np.array([0x44332211],dtype='<u4').tobytes()
        np.testing.assert_allclose(module.decode_words(word,[1,1,1],'BGRA')[0,0],[.2,34/255,17/255,68/255],atol=1e-7)
        np.testing.assert_allclose(module.decode_words(word,[1,1,1],'RGBA')[0,0],[17/255,34/255,.2,68/255],atol=1e-7)

    def test_native_input_bank_supplies_texture_sizes_and_samples(self):
        module=importlib.import_module('noise_inputs')
        manifest,payloads=self.generate(['noise_lq_lite','noisevol_hq'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'manifest.json').write_text(json.dumps(manifest))
            for name,row in manifest['textures'].items():(root/row['file']).write_bytes(payloads[name])
            bank=module.NoiseBank(root)
            self.assertEqual(bank.uniforms()['texsize_noisevol_hq'],[32,32,1/32,1/32])
            for name,coordinates in [('noise_lq_lite',[[.5,.5]]),('noisevol_hq',[[.5,.5,.5]])]:
                values=bank.sample({'canonical_texture':name,'sampling_policy':{'wrap':True,'linear':True}},np.array(coordinates))
                self.assertEqual(values.shape,(1,4));self.assertTrue(np.all((values>=0)&(values<=1)))

    def test_corrupt_native_input_cannot_silently_become_a_texture(self):
        module=importlib.import_module('noise_inputs')
        manifest,payloads=self.generate(['noise_lq_lite'])
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'manifest.json').write_text(json.dumps(manifest))
            row=manifest['textures']['noise_lq_lite'];(root/row['file']).write_bytes(bytes(len(payloads['noise_lq_lite'])))
            with self.assertRaisesRegex(ValueError,'hash'):module.NoiseBank(root)

    def generate(self,names,seed=12345,seed_policy=None):
        self.assertTrue(BINARY.is_file(),'native noise input exporter has not been built')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);request=root/'request.json'
            settings={'names':names,'seed':seed,'output':str(root/'inputs')}
            if seed_policy is not None:settings['seed_policy']=seed_policy
            request.write_text(json.dumps(settings))
            process=subprocess.run([str(BINARY),str(request)],capture_output=True,text=True,timeout=30)
            self.assertEqual(process.returncode,0,process.stderr)
            manifest=json.loads(process.stdout)
            payloads={name:(root/'inputs'/row['file']).read_bytes() for name,row in manifest['textures'].items()}
            return manifest,payloads

    def test_native_noise_inputs_have_physical_dimensions_without_rendering(self):
        manifest,payloads=self.generate(['noise_lq_lite','noise_hq','noisevol_hq'])
        expected={'noise_lq_lite':[32,32,1],'noise_hq':[256,256,1],'noisevol_hq':[32,32,32]}
        for name,dims in expected.items():
            self.assertEqual(manifest['textures'][name]['dimensions'],dims)
            self.assertEqual(len(payloads[name]),int(np.prod(dims))*4)
        self.assertFalse(manifest['uses_rendered_reference'])
        self.assertEqual(manifest['basis'],'pinned native procedural texture generation')

    def test_same_seed_is_byte_repeatable_and_changed_seed_changes_input(self):
        _,first=self.generate(['noise_lq_lite'],12345)
        _,second=self.generate(['noise_lq_lite'],12345)
        _,other=self.generate(['noise_lq_lite'],12346)
        self.assertEqual(first,second)
        self.assertNotEqual(first,other)

    def test_generation_is_independent_of_requested_texture_order(self):
        _,a=self.generate(['noise_lq_lite','noisevol_hq'])
        _,b=self.generate(['noisevol_hq','noise_lq_lite'])
        self.assertEqual(a,b)

    def test_manifest_retains_engine_provenance_and_actual_upload_format(self):
        manifest,payloads=self.generate(['noise_lq_lite'])
        self.assertEqual(len(manifest['engine_archive_sha256']),64)
        self.assertIn(manifest['native_upload_format'],['RGBA','BGRA'])
        self.assertEqual(manifest['packed_word_encoding'],'uint32 little endian')
        self.assertEqual(manifest['textures']['noise_lq_lite']['sha256'],hashlib.sha256(payloads['noise_lq_lite']).hexdigest())


if __name__=='__main__':unittest.main()



def test_declared_android_noise_clock_rejects_first_frame_seed_for_surface_init():
    from noise_inputs import validate_noise_clock
    from types import SimpleNamespace
    import pytest
    bank=SimpleNamespace(manifest={'seed':3567620661,'seed_policy':'production-clock-seed-v1'})
    contract={'policy':'core-thread-inputs-v1','noise_initialization_clock_ns':1000000000000000,
              'noise_clock_period':'android-libcxx-microseconds-v1'}
    with pytest.raises(ValueError,match='noise.*seed'):
        validate_noise_clock(bank,contract,profile='gles300')


def test_declared_android_noise_clock_matches_surface_init_low32_microseconds():
    from noise_inputs import validate_noise_clock
    from types import SimpleNamespace
    bank=SimpleNamespace(manifest={'seed':3567587328,'seed_policy':'production-clock-seed-v1'})
    contract={'policy':'core-thread-inputs-v1','noise_initialization_clock_ns':1000000000000000,
              'noise_clock_period':'android-libcxx-microseconds-v1'}
    assert validate_noise_clock(bank,contract,profile='gles300')==3567587328


@pytest.mark.parametrize('clock',[True,-1,1.5,'1000',2**63])
def test_declared_noise_clock_requires_explicit_supported_int64_nanoseconds(clock):
    from noise_inputs import validate_noise_clock
    from types import SimpleNamespace
    import pytest
    contract={'policy':'core-thread-inputs-v1','noise_initialization_clock_ns':clock,
              'noise_clock_period':'android-libcxx-microseconds-v1'}
    with pytest.raises(ValueError,match='noise.*clock'):
        validate_noise_clock(SimpleNamespace(manifest={'seed':0}),contract,profile='gles300')


def test_noise_clock_policy_does_not_extrapolate_other_platforms_or_missing_units():
    from noise_inputs import validate_noise_clock
    from types import SimpleNamespace
    import pytest
    base={'policy':'core-thread-inputs-v1','noise_initialization_clock_ns':0,
          'noise_clock_period':'android-libcxx-microseconds-v1'}
    for contract,profile in [(base,'glsl330'),({**base,'noise_clock_period':'nanoseconds'},'gles300'),
                             ({k:v for k,v in base.items() if k!='noise_clock_period'},'gles300')]:
        with pytest.raises(ValueError,match='noise.*clock'):
            validate_noise_clock(SimpleNamespace(manifest={'seed':0}),contract,profile=profile)


def test_unpaired_noise_generation_keeps_its_explicit_seed_without_android_claim():
    from noise_inputs import validate_noise_clock
    from types import SimpleNamespace
    assert validate_noise_clock(SimpleNamespace(manifest={'seed':12345}),None,profile='glsl330') is None


@pytest.mark.parametrize('contract',[{'policy':'core-thread-inputs-v1'},
    {'policy':'core-thread-inputs-v1','noise_clock_period':'android-libcxx-microseconds-v1'}])
def test_paired_noise_clock_cannot_omit_initialization_timestamp(contract):
    from types import SimpleNamespace
    from noise_inputs import validate_noise_clock
    with pytest.raises(ValueError,match='noise.*clock'):
        validate_noise_clock(SimpleNamespace(manifest={'seed':42}),contract,profile='gles300')


def test_raw_production_noise_seed_is_not_mixed_by_lab_instrumentation():
    helper=NoiseInputsTest()
    names=['noise_lq_lite','noise_lq','noise_mq','noise_hq','noisevol_lq','noisevol_hq']
    manifest,raw=helper.generate(names,3567620661,seed_policy='production-clock-seed-v1')
    assert manifest['seed_policy']=='production-clock-seed-v1'
    for name,row in manifest['textures'].items():
        assert row['generator_seed']==3567620661
        size=row['dimensions'][0];zoom=row['zoom_factor']
        configured=3567620661^((101*0x9e3779b9)&0xffffffff)^(size*31+zoom)
        _,expected=helper.generate([name],configured)
        assert raw[name]==expected[name]


def test_legacy_noise_policy_preserves_original_bytes_and_names_its_mixed_seeds():
    helper=NoiseInputsTest();manifest,_=helper.generate(['noise_lq'],12345)
    assert manifest['seed_policy']=='lab-subsystem-seed-v1'
    assert manifest['textures']['noise_lq']['generator_seed']==12345^((101*0x9e3779b9)&0xffffffff)^(256*31+1)
