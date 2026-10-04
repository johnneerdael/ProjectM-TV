import unittest
import importlib
import test_native_reader
from shader_fields import ShaderFields


class SamplingPolicyTest(unittest.TestCase):
    def test_standalone_main_sample_does_not_invent_a_known_frame_wrap(self):
        model=ShaderFields(stage='warp',frame=4,warp_reads_blur=False)
        result=model.expression({'kind':'call','function':'tex2D','type':{'name':'float4'},
             'args':[{'kind':'variable','name':'sampler_main','type':{'name':'sampler2D'}},
                     {'kind':'variable','name':'uv','type':{'name':'float2'}}]})
        self.assertIsNone(result.detail['sampling_policy']['wrap'])

    def test_native_prefix_order_and_unknown_prefix_follow_texture_manager(self):
        module=importlib.import_module('sampling_policy')
        common={'mipmapped':False,'base_level':0}
        self.assertEqual(module.texture_settings('sampler_cp_main'),{'texture':'main','wrap':False,'linear':False,**common})
        self.assertEqual(module.texture_settings('sampler_WF_noise_hq'),{'texture':'noise_hq','wrap':True,'linear':True,**common})
        self.assertEqual(module.texture_settings('sampler_zz_main'),{'texture':'main','wrap':True,'linear':True,**common})

    def test_warp_texture_unit_zero_overrides_alias_policy_in_native_bind_order(self):
        module=importlib.import_module('sampling_policy')
        bindings=module.main_sampler_bindings(['sampler_fc_main'],stage='warp',frame_wrap=1)
        self.assertEqual(bindings['sampler_fc_main']['unit'],0)
        self.assertTrue(bindings['sampler_fc_main']['wrap'])
        self.assertEqual(bindings['sampler_main']['unit'],1)
        # Composite has no per-pixel sampler override.
        bindings=module.main_sampler_bindings(['sampler_fc_main'],stage='composite',frame_wrap=1)
        self.assertFalse(bindings['sampler_fc_main']['wrap'])

    def test_unbound_frame_wrap_stays_symbolic(self):
        module=importlib.import_module('sampling_policy')
        binding=module.main_sampler_bindings([],stage='warp',frame_wrap=None)['sampler_main']
        self.assertIsNone(binding['wrap'])
        self.assertEqual(binding['wrap_condition'],'frame_wrap > 0.0001')

    def test_prefixed_main_sampler_keeps_feedback_history_in_lowered_graph(self):
        tree=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {ret=tex2D(sampler_fc_main,uv).xyz;}\n')['sections']['comp_']['tree']
        model=ShaderFields(stage='composite',frame=4,warp_reads_blur=False)
        result=model.lower(tree)
        self.assertTrue(model.complete,model.unknown)
        sample=result.args[0]
        self.assertEqual(sample.detail['surface'],'current_warp_with_draws')
        self.assertEqual(sample.detail['frame'],4)
        self.assertFalse(sample.detail['sampling_policy']['wrap'])


if __name__=='__main__':unittest.main()
