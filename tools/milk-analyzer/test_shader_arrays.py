import unittest
import numpy as np
from test_shader_loops import lower
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid


class ShaderArraysTest(unittest.TestCase):
    def check(self,body,expected):
        model,field=lower('shader_body {'+body+'}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(field),expected)
        np.testing.assert_array_equal(evaluate_grid(field,batch_shape=(2,)),[expected]*2)

    def test_scalar_array_initializer(self):
        self.check('float a[3]={1,2,3};ret=float3(a[0],a[1],a[2]);',[1,2,3])

    def test_vector_array_member_write(self):
        self.check('float2 a[2]={float2(1,2),float2(3,4)};a[1].x=8;'
                   'ret=float3(a[0],a[1].x);',[1,2,8])

    def test_unwritten_elements_and_components_are_not_zero(self):
        self.check('float2 a[2];a[0].x=7;ret=float3(a[0].x);',[7]*3)
        for read in ['a[0].y','a[1].x']:
            model,field=lower('shader_body {float2 a[2];a[0].x=7;ret='+read+';}')
            self.assertTrue(model.complete,model.unknown)
            with self.assertRaisesRegex(UnresolvedMath,'uninitialized'):evaluate(field)

    def test_loop_fills_array_with_state_carry(self):
        self.check('float a[3];for(int i=0;i<3;i++){a[i]=i+1;}'
                   'ret=float3(a[0],a[1],a[2]);',[1,2,3])

    def test_loop_reads_prior_writes(self):
        self.check('float a[3]={1,2,3};for(int i=0;i<3;i++){a[i]+=a[(i+2)%3];}'
                   'ret=float3(a[0],a[1],a[2]);',[4,6,9])

    def test_float_index_uses_native_truncation_and_lane_selection(self):
        model,field=lower('shader_body {float a[3]={2,4,8};ret=a[bass];}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate_grid(field,batch_shape=(2,),
            inputs={'_c3':[[1.9,0,0,0],[-.5,0,0,0]]}),[[4]*3,[2]*3])
        with self.assertRaisesRegex(UnresolvedMath,'bounds'):
            evaluate(field,inputs={'_c3':[3,0,0,0]})

    def test_overwritten_array_write_still_checks_bounds_in_selected_branch(self):
        model,field=lower('shader_body {float a[2]={1,2};if(bass>0){a[9]=3;}ret=a[0];}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(field,inputs={'_c3':[0,0,0,0]}),[1]*3)
        with self.assertRaisesRegex(UnresolvedMath,'bounds'):
            evaluate(field,inputs={'_c3':[1,0,0,0]})

    def test_const_expression_size_and_whole_array_copy(self):
        self.check('const int n=1+2;float a[n]={1,2,3};float b[n];b=a;'
                   'ret=float3(b[0],b[1],b[2]);',[1,2,3])

    def test_helper_array_argument_retains_element_type_and_size(self):
        model,field=lower('float f(float a[3]){return a[1];}'
                          'shader_body {float a[3]={1,2,3};ret=f(a);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate(field),[2]*3)

    def test_invalid_initializer_layout_is_not_invented(self):
        for source in ['float2 a[2]={1,2,3,4};ret=a[0].x;',
                       'float a[3]={1};ret=a[0];']:
            model,_=lower('shader_body {'+source+'}')
            self.assertFalse(model.complete)
            self.assertIn('native GLSL array initializer layout mismatch',model.unknown)

    def test_const_array_write_cannot_be_reported_as_valid_shader_state(self):
        model,_=lower('shader_body {const float a[2]={1,2};a[0]=7;ret=a[0];}')
        self.assertFalse(model.complete)
        self.assertIn('assignment to const GLSL value',model.unknown)

    def test_index_storage_side_effect_order_remains_explicitly_unresolved(self):
        model,_=lower('shader_body {float a[2]={4,5};ret=a[(a[0]=0)];}')
        self.assertFalse(model.complete)
        self.assertIn('array index side-effect order unresolved',model.unknown)


if __name__=='__main__':
    unittest.main()
