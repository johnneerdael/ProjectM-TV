import importlib
import unittest
import numpy as np
import test_native_reader
import test_shader_compat
from field_math import UnresolvedMath


class StageResolutionTest(unittest.TestCase):
    def resolve(self,source,evidence=None):
        return importlib.import_module('stage_resolution').resolve_stages(source,profile='glsl330',compatibility=evidence or {})

    def test_milkdrop2_missing_shader_levels_use_native_level_two_defaults(self):
        plan=self.resolve({'values':{'MILKDROP_PRESET_VERSION':'201'},'sections':{}})
        self.assertEqual(plan['warp']['kind'],'fixed_warp')
        self.assertEqual(plan['composite']['kind'],'default_composite')

    def test_milkdrop1_ignores_shader_levels_and_source(self):
        plan=self.resolve({'values':{'PSVERSION_COMP':'2'},'sections':{'comp_':{'source':'bad'}}})
        self.assertEqual(plan['composite']['kind'],'legacy_composite')
        self.assertEqual(plan['warp']['kind'],'fixed_warp')

    def test_version200_uses_shared_shader_level(self):
        plan=self.resolve({'values':{'MILKDROP_PRESET_VERSION':'200','PSVERSION':'0','PSVERSION_COMP':'2'},'sections':{}})
        self.assertEqual(plan['composite']['kind'],'legacy_composite')

    def test_rejected_composite_uses_default_with_verified_source_identity(self):
        source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {q18++;ret=q18;}\n')
        code=source['sections']['comp_']['source']
        report=test_shader_compat.ShaderCompatibilityTest().check(code)
        plan=self.resolve(source,{'composite':report})
        self.assertEqual(plan['composite']['kind'],'default_composite')
        self.assertTrue(plan['composite']['conditional_on_native_profile'])
        report['source_sha256']='stale'
        self.assertEqual(self.resolve(source,{'composite':report})['composite']['kind'],'unknown')

    def test_unresolved_process_failure_cannot_select_fallback(self):
        source={'values':{'MILKDROP_PRESET_VERSION':'201'},'sections':{'comp_':{'source':'shader_body {ret=1;}'}}}
        plan=self.resolve(source,{'composite':{'offline_accepted':None}})
        self.assertEqual(plan['composite']['kind'],'unknown')

    def test_native_reader_activity_matches_missing_level_defaults(self):
        source=test_native_reader.NativeReaderTest().read('comp_1=`shader_body {ret=1;}\n')
        self.assertTrue(source['sections']['comp_']['active'])

    def test_default_pipeline_preserves_feedback_alpha_and_applies_live_decay(self):
        from pipeline_fields import SourcePipeline
        source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\n')
        initial=np.full((4,4,4),.8,dtype=np.float32);initial[...,3]=.4
        pipeline=SourcePipeline.from_source(source,profile='glsl330',compatibility={},
            initial_feedback=initial,warp_reads_blur=False,blur_levels=0,quantize=False)
        result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=0,decay=.5)
        np.testing.assert_allclose(result.feedback[...,:3],.4)
        np.testing.assert_allclose(result.feedback[...,3],.4)
        np.testing.assert_allclose(result.display[...,3],1)
        self.assertEqual(result.history['composite_kind'],'default_composite')

    def test_unknown_custom_stage_refuses_numeric_pipeline(self):
        from pipeline_fields import SourcePipeline
        source=test_native_reader.NativeReaderTest().read('PSVERSION_COMP=2\ncomp_1=`shader_body {ret=1;}\n')
        with self.assertRaises(UnresolvedMath):
            SourcePipeline.from_source(source,profile='glsl330',compatibility={},
                initial_feedback=np.zeros((4,4,4)),warp_reads_blur=False,blur_levels=0)

    def test_custom_warp_receives_native_vertex_diffuse_decay(self):
        from pipeline_fields import SourcePipeline
        from test_pipeline_fields import trees
        warp,comp=trees('ret=GetPixel(uv)*_vDiffuse.rgb;','ret=GetPixel(uv);')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.full((4,4,4),.8),
                                warp_reads_blur=False,blur_levels=0,quantize=False)
        result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,decay=.5)
        np.testing.assert_allclose(result.feedback[...,:3],.4)

    def test_legacy_pipeline_uses_file_settings_and_preserves_feedback(self):
        from pipeline_fields import SourcePipeline
        source=test_native_reader.NativeReaderTest().read('fGammaAdj=2\nfDecay=1\n',version=100)
        initial=np.full((4,4,4),.1,dtype=np.float32);initial[...,3]=1
        pipeline=SourcePipeline.from_source(source,profile='glsl330',compatibility={},
            initial_feedback=initial,warp_reads_blur=False,blur_levels=0,quantize=False)
        result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={'gamma':0},frame_wrap=0,
                             decay=1,legacy_time=0,hue_offsets=[0]*4)
        self.assertEqual(result.history['composite_kind'],'legacy_composite')
        self.assertTrue(np.all(result.display[...,:3]>.1))
        np.testing.assert_allclose(result.feedback[...,:3],.1)


if __name__=='__main__':unittest.main()
