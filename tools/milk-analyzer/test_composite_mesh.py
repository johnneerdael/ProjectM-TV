import importlib
import unittest
import numpy as np
import test_pipeline_fields
from pipeline_fields import SourcePipeline
from field_math import UnresolvedMath


class CompositeMeshTest(unittest.TestCase):
    def module(self):return importlib.import_module('composite_mesh')

    def test_nonuniform_axes_duplicate_center_seams(self):
        mesh=self.module().make_mesh(512,288)
        self.assertEqual(mesh['u'].shape,(32,))
        self.assertEqual(mesh['v'].shape,(24,))
        self.assertEqual(mesh['u'][15],.5)
        self.assertEqual(mesh['u'][16],.5)
        self.assertEqual(mesh['v'][11],.5)
        self.assertEqual(mesh['v'][12],.5)
        self.assertEqual(mesh['triangles'].shape,(1320,3))
        self.assertEqual(mesh['triangles'].size,3960)
        self.assertGreater(mesh['u'][1]-mesh['u'][0],mesh['u'][15]-mesh['u'][14])

    def test_polar_corner_radius_and_four_center_angles(self):
        mesh=self.module().make_mesh(512,288);polar=mesh['polar']
        np.testing.assert_allclose(polar[[0,0,-1,-1],[0,-1,0,-1],0],1,atol=1e-7)
        for row,col,mult in [(11,15,1.25),(11,16,1.75),(12,15,.75),(12,16,.25)]:
            self.assertEqual(polar[row,col,0],0)
            self.assertAlmostEqual(polar[row,col,1],np.pi*mult,places=6)

    def test_native_hue_corner_order_uses_bilinear_vertex_values(self):
        m=self.module();mesh=m.make_mesh(512,288)
        shade=np.array([[1,0,0],[0,1,0],[0,0,1],[1,1,1]],dtype=np.float32)
        colors=m.vertex_colours(mesh,shade)
        np.testing.assert_array_equal(colors[0,0],[0,1,0,1])
        np.testing.assert_array_equal(colors[0,-1],[1,0,0,1])
        np.testing.assert_array_equal(colors[-1,0],[1,1,1,1])
        np.testing.assert_array_equal(colors[-1,-1],[0,0,1,1])
        np.testing.assert_array_equal(colors[11,15],[.5,.5,.5,1])

    def test_interpolation_uses_selected_cell_diagonal(self):
        m=self.module();mesh=m.make_mesh(512,288)
        values=np.zeros((24,32,1),dtype=np.float32)
        for row,col in [(0,0),(0,16),(12,0),(12,16)]:
            values[row+1,col+1]=1
            query=np.array([[[float(mesh['u'][col]+mesh['u'][col+1])*.5,
                              float(mesh['v'][row]+mesh['v'][row+1])*.5]]],dtype=np.float32)
            expected=.5 if (int(col<16)+int(row<12)+int((col,row)==(16,12)))%2 else 0
            self.assertAlmostEqual(float(m.interpolate(mesh,values,query)[0,0,0]),expected,places=5)
            values[row+1,col+1]=0

    def test_composite_uv_retains_half_texel_offset(self):
        result=self.module().composite_fields(32,18)
        x,y=np.meshgrid((np.arange(32)+.5)/32,(np.arange(18)+.5)/18)
        np.testing.assert_allclose(result['uv'],np.stack((x+.5/32,y+.5/18),axis=-1),atol=2e-7)

    def test_pipeline_supplies_source_composite_polar_and_hue(self):
        warp,comp=test_pipeline_fields.trees('ret=0;','ret=hue_shader*rad;')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.zeros((16,16,4)),
                                warp_reads_blur=False,blur_levels=0,quantize=False)
        result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,
                             render_time=0,hue_offsets=[0]*4)
        self.assertGreater(result.display[0,0,0],result.display[7,7,0])
        self.assertTrue(np.all(np.isfinite(result.display)))

    def test_missing_hue_input_stays_unknown(self):
        warp,comp=test_pipeline_fields.trees('ret=0;','ret=hue_shader;')
        pipeline=SourcePipeline(warp,comp,initial_feedback=np.zeros((4,4,4)),
                                warp_reads_blur=False,blur_levels=0)
        with self.assertRaises(UnresolvedMath):
            pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1)


if __name__=='__main__':unittest.main()
