import unittest
import importlib
import numpy as np
import test_native_reader


def trees(warp,composite):
    native=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\nPSVERSION_COMP=2\n'
        f'warp_1=`shader_body {{ {warp} }}\ncomp_1=`shader_body {{ {composite} }}\n')
    return native['sections']['warp_']['tree'],native['sections']['comp_']['tree']


class PipelineFieldsTest(unittest.TestCase):
    def test_blur_arithmetic_profile_requires_gles_and_reaches_update(self):
        from pipeline_fields import SourcePipeline
        with self.assertRaisesRegex(ValueError,'GLES300'):
            SourcePipeline.from_source({},profile='glsl330',compatibility={},
                blur_arithmetic_profile='apple-m4pro-gles-vertical-blur-fma-v1')
        warp,comp=trees('ret=GetBlur1(uv);','ret=GetPixel(uv);')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.zeros((32,32,4)),
            warp_reads_blur=True,blur_levels=1,blur_arithmetic_profile='apple-m4pro-gles-vertical-blur-fma-v1')
        from unittest.mock import patch
        import pipeline_fields
        actual_blur=pipeline_fields.blur_bank
        calls=[]
        def observe(*args,**kwargs):
            calls.append(kwargs['arithmetic_profile'])
            return actual_blur(*args,**kwargs)
        with patch.object(pipeline_fields,'blur_bank',side_effect=observe):
            result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)
        assert calls==['apple-m4pro-gles-vertical-blur-fma-v1']
        assert result.history['blur_arithmetic_profile']=='apple-m4pro-gles-vertical-blur-fma-v1'

    def test_motion_half_storage_profile_is_recorded_and_applied(self):
        from pipeline_fields import SourcePipeline
        from motion_vectors import APPLE_RTZ_STORAGE,motion_uv_surface
        warp,comp=trees('ret=GetPixel(uv);','ret=GetPixel(uv);')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.zeros((32,32,4)),
            warp_reads_blur=False,blur_levels=0,motion_uv_storage_profile=APPLE_RTZ_STORAGE)
        uv=pipeline.original_uv+np.float32(.00013)
        result=pipeline.step(warp_uv=uv,uniforms={},frame_wrap=1,motion_state={'mv_a':1})
        np.testing.assert_array_equal(pipeline.motion_uv,motion_uv_surface(uv,storage_profile=APPLE_RTZ_STORAGE))
        assert result.history['motion_uv_storage_profile']==APPLE_RTZ_STORAGE
        with self.assertRaisesRegex(ValueError,'GLES300'):
            SourcePipeline.from_source({},profile='glsl330',compatibility={},
                motion_uv_storage_profile=APPLE_RTZ_STORAGE)

    def test_quad_context_and_large_viewport_are_rejected_before_first_frame(self):
        from pipeline_fields import SourcePipeline
        from quad_lines import PROFILE
        with self.assertRaisesRegex(ValueError,'GLES300'):
            SourcePipeline.from_source({},profile='glsl330',compatibility={},
                                       line_rendering_profile=PROFILE)
        with self.assertRaisesRegex(ValueError,'reference area'):
            SourcePipeline(None,None,initial_feedback=np.zeros((900,900,4)),
                warp_reads_blur=False,blur_levels=0,line_rendering_profile=PROFILE)

    def test_declared_quad_profile_reaches_motion_vectors_on_second_frame(self):
        from pipeline_fields import SourcePipeline
        from motion_vectors import draw_motion_vectors
        from quad_lines import PROFILE
        warp,comp=trees('ret=GetPixel(uv);','ret=GetPixel(uv);')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.zeros((32,32,4)),
            warp_reads_blur=False,blur_levels=0,quantize=True,line_rendering_profile=PROFILE,
            motion_raster_subpixel_bits=8)
        state=dict(mv_a=1,mv_x=2,mv_y=2,mv_dx=.05,mv_dy=-.05,mv_l=1,mv_r=1,mv_g=0,mv_b=0)
        first=pipeline.step(warp_uv=pipeline.original_uv+[.125,0],uniforms={},frame_wrap=1,motion_state=state)
        assert np.count_nonzero(first.feedback[...,:3])==0
        expected=draw_motion_vectors(first.feedback,state,previous_uv=pipeline.motion_uv,
            line_rendering_profile=PROFILE,raster_subpixel_bits=8)
        second=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,motion_state=state)
        np.testing.assert_array_equal(second.feedback,expected)
        assert second.history['motion_vector_line_profile']==PROFILE
        assert second.history['motion_vector_raster_subpixel_bits']==8
        assert second.history['motion_vector_source_frame']==0

    def test_main_texture_size_uses_owned_feedback_dimensions_in_both_stages(self):
        module=importlib.import_module('pipeline_fields')
        warp,comp=trees('ret=float3(texsize_main.zw,texsize_main.x/64);',
                        'ret=GetPixel(uv)*texsize_main.x*texsize_main.z;')
        expected=np.broadcast_to([1/32,1/16,.5],(16,32,3))
        for uniforms in ({},{'texsize_main':[999,999,999,999]}):
            with self.subTest(uniforms=uniforms):
                pipeline=module.SourcePipeline(warp,comp,initial_feedback=np.zeros((16,32,4)),
                    warp_reads_blur=False,blur_levels=0,quantize=False)
                result=pipeline.step(warp_uv=pipeline.original_uv,uniforms=uniforms,frame_wrap=1)
                np.testing.assert_allclose(result.feedback[...,:3],expected,atol=1e-7)
                np.testing.assert_allclose(result.display[...,:3],expected,atol=1e-7)

    def test_main_dimensions_do_not_invent_an_unknown_texture_size(self):
        from pipeline_fields import SourcePipeline
        from field_math import UnresolvedMath
        warp,comp=trees('ret=GetPixel(uv);','ret=float3(texsize_unknown.zw,0);')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.zeros((16,32,4)),
            warp_reads_blur=False,blur_levels=0,quantize=False)
        with self.assertRaises(UnresolvedMath):
            pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)

    def test_tagged_reduction_controls_warp_and_composite_display_fields(self):
        module=importlib.import_module('pipeline_fields')
        source=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\nPSVERSION_COMP=2\n'
            'warp_1=`shader_body {ret=float3(all(uv));}\n'
            'comp_1=`shader_body {ret=GetPixel(uv);}\n')['sections']
        pipeline=module.SourcePipeline(source['warp_']['tree'],source['comp_']['tree'],
            initial_feedback=np.zeros((16,16,4)),warp_reads_blur=False,blur_levels=0,quantize=False,
            language_extensions={'warp':source['warp_']['language_extensions']})
        coordinates=pipeline.original_uv.copy();coordinates[:,:8,0]=0
        result=pipeline.step(warp_uv=coordinates,uniforms={},frame_wrap=1)
        np.testing.assert_array_equal(result.feedback[:,:8,:3],0)
        np.testing.assert_array_equal(result.feedback[:,8:,:3],1)
        # Composite sampling uses its declared mesh coordinates and wrapped
        # bilinear filtering; the two boundary columns mix black and white.
        expected=np.ones((16,16,4),dtype=np.float32)
        expected[:,:7,:3]=0;expected[:,[7,15],:3]=.5
        np.testing.assert_allclose(result.display,expected,atol=1e-6)

    def test_failed_composite_does_not_advance_feedback_or_blur_state(self):
        module=importlib.import_module('pipeline_fields')
        from field_math import UnresolvedMath
        warp,comp=trees('ret=.5;','ret=tex2D(sampler_missing_resource,uv).xyz;')
        pipeline=module.SourcePipeline(warp,comp,initial_feedback=np.zeros((16,16,4)),warp_reads_blur=False,blur_levels=1,quantize=False)
        before=pipeline.feedback.copy();blur_before=pipeline.blur[1].copy()
        with self.assertRaises(UnresolvedMath):
            pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)
        self.assertEqual(pipeline.frame,0)
        np.testing.assert_array_equal(pipeline.feedback,before)
        np.testing.assert_array_equal(pipeline.blur[1],blur_before)
        self.assertEqual(pipeline.blur_source_frame,-2)

    def test_nonlinear_warp_feedback_does_not_consume_displayed_composite(self):
        module=importlib.import_module('pipeline_fields')
        warp,comp=trees('ret=GetPixel(uv)*GetPixel(uv);','ret=1-GetPixel(uv);')
        initial=np.ones((16,16,4),dtype=np.float32);initial[...,:3]=.8
        pipeline=module.SourcePipeline(warp,comp,initial_feedback=initial,warp_reads_blur=False,blur_levels=0,quantize=False)
        first=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)
        second=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)
        np.testing.assert_allclose(first.feedback[...,:3],.64,atol=1e-6)
        np.testing.assert_allclose(first.display[...,:3],.36,atol=1e-6)
        np.testing.assert_allclose(second.feedback[...,:3],.4096,atol=1e-6)

    def test_warp_and_composite_blur_banks_have_different_source_ages(self):
        module=importlib.import_module('pipeline_fields')
        warp,comp=trees('ret=.25*GetBlur1(uv)+.5*GetPixel(uv);','ret=GetBlur1(uv);')
        initial=np.ones((16,16,4),dtype=np.float32);initial[...,:3]=.8
        pipeline=module.SourcePipeline(warp,comp,initial_feedback=initial,warp_reads_blur=True,blur_levels=1,quantize=False)
        results=[pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1) for _ in range(3)]
        for result,value in zip(results,[.4,.4,.3]):np.testing.assert_allclose(result.feedback[...,:3],value,atol=1e-6)
        for result,value in zip(results,[.8,.4,.4]):np.testing.assert_allclose(result.display[...,:3],value,atol=1e-6)
        self.assertEqual(results[2].history['warp_blur_source_frame'],0)
        self.assertEqual(results[2].history['composite_blur_source_frame'],1)

    def test_drawn_feedback_survives_a_black_composite(self):
        module=importlib.import_module('pipeline_fields')
        warp,comp=trees('ret=GetPixel(uv)*.5;','ret=0;')
        pipeline=module.SourcePipeline(warp,comp,initial_feedback=np.zeros((16,16,4)),warp_reads_blur=False,blur_levels=0,quantize=False)
        def draw(field,frame):
            if frame==0:field[...,0]=1
            return field
        first=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,draw=draw)
        second=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,draw=draw)
        np.testing.assert_allclose(first.display[...,:3],0)
        np.testing.assert_allclose(second.feedback[...,0],.5)

    def test_physical_blur_flip_and_sampler_origin_compose_correctly(self):
        module=importlib.import_module('pipeline_fields')
        warp,comp=trees('ret=GetPixel(uv);','ret=GetBlur1(uv);')
        initial=np.ones((64,64,4),dtype=np.float32)
        initial[...,:3]=np.linspace(0,1,64)[:,None,None]
        pipeline=module.SourcePipeline(warp,comp,initial_feedback=initial,warp_reads_blur=False,blur_levels=1,quantize=False)
        result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)
        self.assertLess(result.display[0,32,0],result.display[-1,32,0])


if __name__=='__main__':unittest.main()
