import unittest
import numpy as np
from test_shader_loops import lower
from grid_math import evaluate_grid


class SamplingTraceTest(unittest.TestCase):
    def test_pipeline_trace_distinguishes_stage_site_and_frame_history(self):
        from test_pipeline_fields import trees
        from pipeline_fields import SourcePipeline
        warp,comp=trees('ret=GetPixel(uv);','ret=GetPixel(uv);')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.ones((16,16,4)),warp_reads_blur=False,blur_levels=0)
        records=[]
        result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,
                             on_sample=lambda stage,detail,uv,lanes:records.append((stage,detail,uv,lanes)))
        self.assertEqual([r[0] for r in records],['warp','composite'])
        self.assertEqual([r[1]['frame'] for r in records],[-1,0])
        self.assertEqual([r[1]['site_index'] for r in records],[0,0])
        np.testing.assert_array_equal(records[0][3],np.arange(256))
        np.testing.assert_allclose(records[0][2],pipeline.original_uv.reshape(-1,2))
        np.testing.assert_allclose(result.display,1)

    def test_trace_retains_selected_output_lanes_across_loop_iterations(self):
        model,field=lower('shader_body {float sum=0;int n=0;while(n<bass){sum+=GetPixel(uv+float2(n*.1,0)).x;n++;}ret=sum;}')
        self.assertTrue(model.complete,model.unknown)
        records=[]
        def trace(detail,uv,lanes):records.append((detail,uv.copy(),lanes.copy()))
        result=evaluate_grid(field,batch_shape=(3,),inputs={'_uv':[[.2,0],[.4,0],[.6,0]],'_c3':[[1,0,0,0],[2,0,0,0],[0,0,0,0]]},
                             sample=lambda detail,uv:np.tile([.25,0,0,1],(len(uv),1)),on_sample=trace)
        self.assertEqual([r[2].tolist() for r in records],[[0,1],[1]])
        np.testing.assert_allclose(records[1][1],[[.5,0]],atol=1e-6)
        self.assertEqual(records[0][0]['canonical_texture'],'main')
        np.testing.assert_allclose(result,[[.25]*3,[.5]*3,[0]*3])


if __name__=='__main__':unittest.main()
