import unittest
import importlib
import numpy as np
import test_field_math


class FeedbackFieldTest(unittest.TestCase):
    def test_unknown_sampler_filter_cannot_silently_become_nearest_sampling(self):
        module=importlib.import_module('feedback_field')
        from shader_fields import ShaderFields
        model=ShaderFields(stage='warp',frame=4,warp_reads_blur=False)
        sample=model.expression({'kind':'call','function':'tex2D','type':{'name':'float4'},
            'args':[{'kind':'variable','name':'sampler_fc_main','type':{'name':'sampler2D'}},
                    {'kind':'variable','name':'uv','type':{'name':'float2'}}]})
        transfer=module.affine_main_transfer(sample)
        with self.assertRaisesRegex(ValueError,'filtering'):
            module.apply_affine_transfer(np.zeros((2,2,4)),[[.5,.5]],transfer,wrap=True)

    def test_affine_colour_transfer_is_extracted_from_native_shader_tree(self):
        module=importlib.import_module('feedback_field')
        model,result=test_field_math.lower('ret=tex2D(sampler_main,uv).xyz*.85-.022;')
        self.assertTrue(model.complete)
        transfer=module.affine_main_transfer(result)
        self.assertIsNotNone(transfer)
        np.testing.assert_allclose(transfer.matrix,np.eye(4,dtype=np.float32)[:3]*.85)
        np.testing.assert_allclose(transfer.bias,[-.022]*3)
        self.assertEqual(transfer.sample.detail['frame'],2)

    def test_nonlinear_and_distinct_coordinate_feedback_are_not_claimed_affine(self):
        module=importlib.import_module('feedback_field')
        for body in ['float3 a=GetPixel(uv);ret=a*a;',
                     'ret=GetPixel(uv)+GetPixel(uv+float2(.01,0));']:
            _,result=test_field_math.lower(body)
            self.assertIsNone(module.affine_main_transfer(result))

    def test_feedback_fields_create_wrapped_layers_from_a_declared_source(self):
        module=importlib.import_module('feedback_field')
        _,result=test_field_math.lower('ret=GetPixel(uv)*.75;')
        transfer=module.affine_main_transfer(result)
        uv=np.stack(np.meshgrid((np.arange(8)+.5)/8,(np.arange(2)+.5)/2),axis=-1)
        uv[...,0]-=.25
        wrap=np.zeros((2,8,3),dtype=np.float32);clamp=wrap.copy()
        for _ in range(4):
            wrap=module.apply_affine_transfer(wrap,uv,transfer,wrap=True,quantize=False)
            clamp=module.apply_affine_transfer(clamp,uv,transfer,wrap=False,quantize=False)
            wrap[:,6]=.8;clamp[:,6]=.8
        np.testing.assert_allclose(wrap[0,:,0],[.6,0,.45,0,.3375,0,.8,0],atol=1e-6)
        self.assertEqual(np.count_nonzero(clamp[0,:,0]),1)

    def test_framebuffer_conversion_clips_and_quantizes_without_silent_nan(self):
        module=importlib.import_module('feedback_field')
        np.testing.assert_allclose(module.unorm8(np.array([-.1,.5,1.5])),[0,128/255,1],atol=1e-7)
        with self.assertRaises(ValueError):module.unorm8([np.nan])

    def test_unorm_conversion_preserves_represented_float32_values_above_half_bytes(self):
        from feedback_field import unorm8
        # The represented f32 inputs are above their half-byte boundaries. A f32
        # multiply by255 prematurely collapses them onto an exact halfway value.
        for half_byte, expected_byte in [(.5,1),(2.5,3),(80.5,81)]:
            with self.subTest(half_byte=half_byte):
                result=unorm8(np.float32(half_byte/255))
                self.assertEqual(result.dtype,np.dtype(np.float32))
                self.assertEqual(result,np.float32(expected_byte)/np.float32(255))

    def test_unorm_conversion_handles_rgb_channel_arrays_and_bounded_values(self):
        from feedback_field import unorm8
        k=np.arange(60,dtype=np.float32)[:,None]
        inputs=(k+np.array([.5,.25,.75],np.float32))/np.float32(255)
        expected_bytes=np.stack((np.arange(1,61),np.arange(60),np.arange(1,61)),axis=-1)
        np.testing.assert_array_equal(np.rint(unorm8(inputs)*255).astype(np.uint8),expected_bytes)
        bounded=unorm8([[-1,0,1,2],[-.001,.5,1.001,255]])
        np.testing.assert_array_equal(bounded,np.array([[0,0,1,1],[0,128/255,1,1]],np.float32))

    def test_unorm_conversion_casts_to_source_float32_before_quantization(self):
        from feedback_field import unorm8
        below_half=np.nextafter(np.float64(.5/255),-np.inf)
        self.assertLess(below_half*255,.5)
        # Input narrowing is the existing contract, even when the f64 value lies below half.
        self.assertEqual(unorm8(below_half),np.float32(1)/np.float32(255))

    def test_unorm_conversion_rejects_nonfinite_scalar_and_array_inputs(self):
        from feedback_field import unorm8
        for value in [np.nan,np.inf,-np.inf,[[0,np.nan],[1,2]]]:
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,'nonfinite framebuffer'):
                unorm8(value)

    def test_alpha_dependent_transfer_requires_explicit_alpha_state(self):
        module=importlib.import_module('feedback_field')
        _,result=test_field_math.lower('ret=float3(tex2D(sampler_main,uv).w);')
        transfer=module.affine_main_transfer(result)
        with self.assertRaises(ValueError):
            module.apply_affine_transfer(np.zeros((2,2,3)),[[.5,.5]],transfer,wrap=False)


if __name__=='__main__':unittest.main()
