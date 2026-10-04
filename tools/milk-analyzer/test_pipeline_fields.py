import unittest
import importlib
import numpy as np
import test_native_reader


def trees(warp,composite):
    native=test_native_reader.NativeReaderTest().read('PSVERSION_WARP=2\nPSVERSION_COMP=2\n'
        f'warp_1=`shader_body {{ {warp} }}\ncomp_1=`shader_body {{ {composite} }}\n')
    return native['sections']['warp_']['tree'],native['sections']['comp_']['tree']


class PipelineFieldsTest(unittest.TestCase):
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
