import unittest
import numpy as np
from test_shader_loops import lower
from field_math import evaluate,UnresolvedMath
from grid_math import evaluate_grid


class PowDomainTest(unittest.TestCase):
    def test_zero_base_nonpositive_exponent_is_unresolved_not_numpy_one(self):
        for exponent in [0,-1]:
            model,field=lower(f'shader_body {{ret=pow(bass,{exponent});}}')
            self.assertTrue(model.complete,model.unknown)
            with self.assertRaisesRegex(UnresolvedMath,'pow'):
                evaluate(field,inputs={'_c3':[0,0,0,0]})
            with self.assertRaisesRegex(UnresolvedMath,'pow'):
                evaluate_grid(field,batch_shape=(2,),inputs={'_c3':[[1,0,0,0],[0,0,0,0]]})

    def test_guarded_or_positive_exponent_zero_remains_valid(self):
        model,field=lower('shader_body {ret=bass==0 ? 0 : pow(bass,0);}')
        self.assertTrue(model.complete,model.unknown)
        np.testing.assert_array_equal(evaluate_grid(field,batch_shape=(2,),inputs={'_c3':[[0,0,0,0],[2,0,0,0]]}),[[0]*3,[1]*3])
        model,field=lower('shader_body {ret=pow(bass,.5);}')
        np.testing.assert_array_equal(evaluate(field,inputs={'_c3':[0,0,0,0]}),[0]*3)


if __name__=='__main__':unittest.main()
