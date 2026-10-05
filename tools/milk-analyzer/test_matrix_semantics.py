import unittest
import numpy as np
from test_shader_loops import lower
from field_math import evaluate
from grid_math import evaluate_grid


class MatrixSemanticsTest(unittest.TestCase):
    def check(self, body, expected):
        model, field = lower('shader_body {'+body+'}')
        self.assertTrue(model.complete, model.unknown)
        np.testing.assert_array_equal(evaluate(field), expected)
        np.testing.assert_array_equal(evaluate_grid(field, batch_shape=(2,)), [expected]*2)

    def test_bare_matrix_multiplication_is_native_linear_product(self):
        self.check('float2x2 a=float2x2(1,2,3,4);float2x2 b=float2x2(5,6,7,8);'
                   'float2x2 c=a*b;ret=float3(c[0],0);', [19,22,0])

    def test_matrix_compound_multiplication_is_linear_product(self):
        self.check('float2x2 a=float2x2(1,2,3,4);a*=float2x2(5,6,7,8);'
                   'ret=float3(a[1],0);', [43,50,0])

    def test_scalar_matrix_multiplication_casts_to_diagonal(self):
        self.check('float2x2 a=float2x2(1,2,3,4);float2x2 b=a*2.;'
                   'ret=float3(b[0],0);', [2,4,0])

    def test_scalar_matrix_addition_adds_only_diagonal(self):
        self.check('float2x2 a=float2x2(1,2,3,4)+2.;ret=float3(a[0],0);', [3,2,0])

    def test_scalar_declaration_and_explicit_constructor_pad_with_zeros(self):
        for init in ['.5','float2x2(.5)','float2x2(float2(.5,2))']:
            self.check('float2x2 a='+init+';ret=float3(a[0],a[1].x);',
                       [.5,2 if 'float2(' in init else 0,0])

    def test_registered_matrix_copy_helper_affects_all_matching_initializers(self):
        self.check('float2x2 a=float2x2(1,2,3,4);float2x2 b=float2x2(a);'
                   'ret=float3(a[0].x,b[0].x,b[1].y);', [0,0,0])

    def test_matrix_cast_resizes_by_coordinates_and_fills_identity(self):
        self.check('float2x2 a=float2x2(1,2,3,4);float3x3 b=(float3x3)a;'
                   'ret=float3(b[0].x,b[0].z,b[2].z);', [1,0,1])

    def test_batched_scalar_cast_keeps_lane_axis(self):
        model, field=lower('shader_body {float2x2 a=float2x2(1,2,3,4)*bass;ret=float3(a[0],0);}')
        self.assertTrue(model.complete,model.unknown)
        actual=evaluate_grid(field,batch_shape=(2,),inputs={'_c3':[[2,0,0,0],[3,0,0,0]]})
        np.testing.assert_array_equal(actual,[[2,4,0],[3,6,0]])

    def test_rectangular_bare_product_has_no_native_mult_helper(self):
        model, _=lower('shader_body {float2x3 a=float2x3(1,2,3,4,5,6);'
                       'float2x3 b=a*a;ret=b[0];}')
        self.assertFalse(model.complete)


if __name__=='__main__':
    unittest.main()
