import unittest
import numpy as np
from test_shader_loops import lower
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid


class ShaderComponentsTest(unittest.TestCase):
    def test_same_name_initializer_reads_outer_binding_before_local_scope_begins(self):
        for code,expected in [('float g=2;shader_body {float g=g;ret=g;}',2),
                              ('shader_body {float g=2;{float g=g+1;ret=g;}}',3)]:
            model,result=lower(code)
            self.assertTrue(model.complete,model.unknown)
            np.testing.assert_array_equal(evaluate(result),[expected]*3)

    def test_same_name_initializer_does_not_define_unwritten_outer_storage(self):
        model,result=lower('float g;shader_body {float g=g;ret=g;}')
        self.assertFalse(model.complete)
        self.assertIn('uninitialized shader value reaches a read',model.unknown)

    def test_same_name_initializer_in_later_declarator_sees_new_earlier_binding(self):
        model,result=lower('float g=.1;shader_body {float g=g+.2,h=g;ret=float3(g,h,0);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_allclose(evaluate(result),[.3,.3,0])

    def test_same_name_initializer_without_outer_binding_stays_unresolved(self):
        model,result=lower('shader_body {float missing=missing;ret=missing;}')
        self.assertFalse(model.complete)
        self.assertIn('unbound initializer name in emitted GLSL',model.unknown)

    def test_same_name_initializer_keeps_shared_read_write_order_unresolved(self):
        for expression in ['bump()+g','g+bump()']:
            model,result=lower('float g=1;float bump(){g+=1;return g;}'
                               'shader_body {float g='+expression+';ret=g;}')
            self.assertFalse(model.complete)
            self.assertIn('same-name initializer shared effects not resolved',model.unknown)

    def test_uniform_assignment_uses_native_function_local_replacement(self):
        model,result=lower('shader_body {bass=2;ret=bass;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[2]*3)

    def test_uniform_replacement_does_not_initialize_other_packed_components(self):
        model,result=lower('shader_body {bass=2;ret=mid;}')
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')
        self.assertIn('uninitialized shader value reaches a read',model.unknown)

    def test_first_assignment_rhs_reads_original_uniform_before_replacement(self):
        model,result=lower('shader_body {q18=q18+1;ret=q18;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_qe':[0,2,0,0]}),[3]*3)

    def test_compound_assignment_reads_uninitialized_replacement(self):
        model,result=lower('shader_body {q18+=1;ret=q18;}')
        self.assertFalse(model.complete)
        self.assertIn('uninitialized shader value reaches a read',model.unknown)

    def test_uniform_replacements_are_local_to_each_helper_call(self):
        model,result=lower('float f(){q18=1;return q18;}shader_body {q18=2;ret=f()+q18;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[3]*3)

    def test_scalar_swizzle_repeats_the_scalar_as_native_helpers_do(self):
        model,result=lower('shader_body {float v=bass;ret=v.yxy;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_c3':[2,0,0,0]}),[2]*3)

    def test_narrow_cast_reads_only_consumed_components_and_widening_defines_zero_padding(self):
        for code,expected in [('float4 v;v.xyz=float3(1,2,3);ret=(float3)v;',[1,2,3]),
                              ('float3 v;v.xy=float2(1,2);ret=(float3)((float2)v);',[1,2,0])]:
            model,result=lower('shader_body {'+code+'}')
            self.assertTrue(model.complete,model.unknown)
            np.testing.assert_array_equal(evaluate(result),expected)

    def test_overwritten_index_write_still_checks_bounds_only_in_selected_branch(self):
        model,result=lower('shader_body {float3 v=0;int n=(int)uv.x;if(bass>0){v[n]=1;}v=0;ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_uv':[3,0],'_c3':[0,0,0,0]}),[0]*3)
        with self.assertRaisesRegex(UnresolvedMath,'index'):
            evaluate(result,inputs={'_uv':[3,0],'_c3':[1,0,0,0]})

    def test_component_writes_fully_initialize_a_vector_without_reading_old_values(self):
        model,result=lower('shader_body {float3 v;v.x=bass;v.y=2;v.z=3;ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_c3':[4,0,0,0]}),[4,2,3])

    def test_only_read_components_need_initialization(self):
        model,result=lower('shader_body {float3 v;v.xy=float2(1,2);ret=float3(v.xy,0);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[1,2,0])
        model,result=lower('shader_body {float3 v;v.xy=1;ret=v;}')
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')

    def test_unwritten_lane_can_be_overwritten_after_componentwise_storage_math(self):
        code=('shader_body {float2 v;v.x=uv.x;v*=2;'
              'float2 m=floor(frac(v*.5)*2);v=frac(v)*(1-m)+m*frac(1-v);'
              'v.y=.3;ret=float3(v,0);}')
        model,result=lower(code)
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(result,batch_shape=(2,),inputs={'_uv':[[.1,0],[.7,0]]})
        np.testing.assert_allclose(actual,[[.2,.3,0],[.6,.3,0]],atol=1e-6)

    def test_live_componentwise_unwritten_lane_stays_unresolved(self):
        model,result=lower('shader_body {float2 v;v.x=.2;v*=2;ret=float3(v,0);}')
        self.assertFalse(model.complete)

    def test_coupled_normalize_requires_unwritten_lane_even_if_only_x_is_used(self):
        model,result=lower('shader_body {float2 v;v.x=.2;float2 w=normalize(v);ret=w.xxx;}')
        self.assertFalse(model.complete)

    def test_branch_component_writes_preserve_defined_values_per_lane(self):
        model,result=lower('shader_body {float3 v;if(bass>0){v.x=1;}else{v.x=2;}v.yz=float2(3,4);ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(result,batch_shape=(2,),inputs={'_c3':[[1,0,0,0],[0,0,0,0]]})
        np.testing.assert_array_equal(actual,[[1,3,4],[2,3,4]])

    def test_dynamic_vector_index_write_and_compound_assignment_are_per_lane(self):
        model,result=lower('shader_body {float3 v=float3(1,2,3);int j=(int)floor(uv.x*3);v[j]+=bass;ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(result,batch_shape=(3,),inputs={'_uv':[[.1,0],[.5,0],[.9,0]],'_c3':[4,0,0,0]})
        np.testing.assert_array_equal(actual,[[5,2,3],[1,6,3],[1,2,7]])

    def test_nested_swizzle_index_writes_back_to_the_original_vector(self):
        model,result=lower('shader_body {float3 v=float3(1,2,3);v.yx[0]=7;ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[1,7,3])

    def test_native_vector_index_cast_truncates_and_out_of_range_remains_unknown(self):
        model,result=lower('shader_body {float3 v=0;float j=uv.x;v[j]=4;ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'_uv':[1.9,0]}),[0,4,0])
        with self.assertRaisesRegex(UnresolvedMath,'index'):
            evaluate(result,inputs={'_uv':[3,0]})

    def test_matrix_single_component_write_and_read_keep_hlsl_row_column_order(self):
        model,result=lower('shader_body {float2x2 m=float2x2(1,2,3,4);m._12=7;ret=float3(m._11,m._12,m._21);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[1,7,3])

    def test_matrix_row_assignment_is_not_silently_misread(self):
        model,result=lower('shader_body {float2x2 m=float2x2(1,2,3,4);m[1][0]=7;ret=m[1].xyx;}')
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')

    def test_array_storage_retains_vector_elements(self):
        model,result=lower('shader_body {float3 a[2]={float3(1,0,0),float3(0,1,0)};ret=a[1];}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[0,1,0])

    def test_ordinary_uninitialized_global_is_not_treated_as_an_external_uniform(self):
        model,result=lower('float3 g;shader_body {ret=g;}')
        self.assertFalse(model.complete)
        self.assertEqual(result.op,'unknown')
        model,result=lower('uniform float g;shader_body {ret=g;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result,inputs={'g':2}),[2]*3)

    def test_loop_progressively_initializes_components_and_rejects_unwritten_outputs(self):
        model,result=lower('shader_body {float3 v;for(int n=0;n<3;n++){v[n]=n+1;}ret=v;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[1,2,3])
        model,result=lower('shader_body {float3 v;for(int n=0;n<2;n++){v[n]=n+1;}ret=v;}')
        with self.assertRaisesRegex(UnresolvedMath,'uninitialized'):evaluate(result)

    def test_loop_can_read_defined_components_while_others_remain_unwritten(self):
        model,result=lower('shader_body {float3 v;for(int n=0;n<1;n++){v[n]=5;}ret=v.xxx;}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(result),[5]*3)


if __name__=='__main__':unittest.main()
