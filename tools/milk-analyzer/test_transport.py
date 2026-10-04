import unittest
import numpy as np


def coordinates(width=32,height=18):
    x,y=np.meshgrid((np.arange(width)+.5)/width,(np.arange(height)+.5)/height)
    return np.stack((x,y),axis=-1)


class TransportTest(unittest.TestCase):
    def test_query_expansion_means_forward_feature_contraction(self):
        from transport import sampling_jacobian,local_transport
        uv=coordinates();query=.5+(uv-.5)*[1.03,1]
        jacobian=sampling_jacobian(query)
        np.testing.assert_allclose(jacobian,np.broadcast_to([[1.03,0],[0,1]],jacobian.shape),atol=1e-6)
        result=local_transport(jacobian)
        np.testing.assert_allclose(result['forward_singular_values'],np.broadcast_to([1,1/1.03],result['forward_singular_values'].shape),atol=1e-6)
        self.assertTrue(np.all(result['area_scale']<1))

    def test_periodic_difference_does_not_mistake_frac_seam_for_a_huge_shear(self):
        from transport import sampling_jacobian
        uv=coordinates();query=np.mod(uv+[.2,.3],1)
        jacobian=sampling_jacobian(query,periodic_axes=(True,True))
        np.testing.assert_allclose(jacobian,np.broadcast_to(np.eye(2),jacobian.shape),atol=1e-6)

    def test_rotation_alone_does_not_claim_area_concentration(self):
        from transport import sampling_jacobian,local_transport
        uv=coordinates();rotation=np.array([[0,-1],[1,0]])
        query=(uv-.5)@rotation.T+.5
        result=local_transport(sampling_jacobian(query))
        np.testing.assert_allclose(result['area_scale'],1,atol=1e-6)

    def test_exact_affine_repetition_uses_matrix_power_not_singular_value_powers(self):
        from transport import affine_transport
        query=np.array([[1,1],[0,1]])
        result=affine_transport(query,[0,0],steps=3)
        np.testing.assert_allclose(result['forward_after_steps'],[[1,-3],[0,1]])
        np.testing.assert_allclose(result['singular_values_after_steps'],np.linalg.svd([[1,-3],[0,1]],compute_uv=False))

    def test_wrapped_case_three_family_has_horizontal_attractor_but_no_vertical_fixed_point(self):
        from transport import separable_fixed_points
        rc=1;s=1+.03*rc;delta=.0005
        offset=[.5+s*(delta-.5)+1,.5+s*(delta-1.5)+rc**.005]
        result=separable_fixed_points([s,s],offset,periodic_axes=(True,True))
        np.testing.assert_allclose(result[0],[.5-delta*s/(s-1)],atol=1e-10)
        self.assertEqual(result[1],[])

    def test_singular_map_and_neutral_fixed_line_do_not_get_fabricated_answers(self):
        from transport import local_transport,separable_fixed_points
        with self.assertRaisesRegex(ValueError,'singular'):local_transport(np.zeros((2,2)))
        result=separable_fixed_points([1,1],[0,.1],periodic_axes=(True,True))
        self.assertEqual(result,['all',[]])


if __name__=='__main__':unittest.main()
