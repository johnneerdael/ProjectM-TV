import unittest
import tempfile
import subprocess
import json
import hashlib
from pathlib import Path
import numpy as np
import importlib


ROOT=Path(__file__).resolve().parents[2]
BINARY=ROOT/'build/milk-analyzer/native/milk-noise-inputs'


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

    def generate(self,names,seed=12345):
        self.assertTrue(BINARY.is_file(),'native noise input exporter has not been built')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);request=root/'request.json'
            request.write_text(json.dumps({'names':names,'seed':seed,'output':str(root/'inputs')}))
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
