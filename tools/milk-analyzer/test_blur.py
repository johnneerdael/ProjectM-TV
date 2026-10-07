import unittest
import importlib
import numpy as np


class BlurTest(unittest.TestCase):
    def test_declared_vertical_blur_fuses_second_pair_into_rounded_first_product(self):
        import ctypes
        blur=importlib.import_module('blur')
        a=np.array([np.float32(1)/np.float32(255)],np.float32)
        first=np.float32(14.200001);second=np.float32(4.1)
        fma=ctypes.CDLL(None).fmaf;fma.argtypes=[ctypes.c_float]*3;fma.restype=ctypes.c_float
        expected=np.array([fma(second,a[0],np.float32(a[0]*first))],np.float32)
        result=blur.vertical_weighted_sum(a,a,first,second,
            arithmetic_profile='apple-m4pro-gles-vertical-blur-fma-v1')
        np.testing.assert_array_equal(result,expected)
        self.assertNotEqual(result[0],np.float32(a[0]*first+a[0]*second))
        a=np.array([.14411196],np.float32);b=np.array([.4315335],np.float32)
        result=blur.vertical_weighted_sum(a,b,first,second,
            arithmetic_profile='apple-m4pro-gles-vertical-blur-fma-v1')
        self.assertEqual(result[0],np.float32(fma(second,b[0],np.float32(a[0]*first))))
        self.assertNotEqual(result[0],np.float32(fma(first,a[0],np.float32(b[0]*second))))
        with self.assertRaisesRegex(ValueError,'blur arithmetic profile'):
            blur.vertical_weighted_sum(a,a,first,second,arithmetic_profile='unknown')

    def test_native_pass_dimensions_include_rounding_and_minimum_size(self):
        blur=importlib.import_module('blur')
        self.assertEqual(blur.pass_dimensions(512,288),[(256,144),(128,72),(64,36),(64,36),(32,20),(32,20)])
        self.assertEqual(blur.pass_dimensions(64,36),[(32,20),(16,16),(16,16),(16,16),(16,16),(16,16)])

    def test_constant_field_survives_normalized_kernels_and_physical_flip(self):
        blur=importlib.import_module('blur')
        bank=blur.blur_bank(np.full((36,64,3),.25,dtype=np.float32),levels=3,edge_darken=0,quantize=False)
        for level,field in bank.items():
            np.testing.assert_allclose(field,.25,atol=1e-6)
        self.assertEqual(bank[1].shape,(16,16,3))

    def test_native_first_pass_flip_is_not_lost_in_an_asymmetric_field(self):
        blur=importlib.import_module('blur')
        ramp=np.broadcast_to(np.linspace(0,1,64,dtype=np.float32)[:,None,None],(64,64,3))
        field=blur.blur_bank(ramp,levels=1,edge_darken=0,quantize=False)[1]
        self.assertGreater(field[0,8,0],field[-1,8,0])

    def test_progressive_range_encoding_decodes_constant_back_to_original_value(self):
        blur=importlib.import_module('blur')
        minimum=[.1,.2,.3];maximum=[.9,.8,.7]
        bank=blur.blur_bank(np.full((64,64,3),.4,dtype=np.float32),levels=3,minimum=minimum,maximum=maximum,edge_darken=0,quantize=False)
        for level,field in bank.items():
            decoded=field*(maximum[level-1]-minimum[level-1])+minimum[level-1]
            np.testing.assert_allclose(decoded,.4,atol=1e-6)

    def test_edge_darkening_applies_only_on_first_vertical_pass(self):
        blur=importlib.import_module('blur')
        bank=blur.blur_bank(np.ones((64,64,3),dtype=np.float32),levels=3,edge_darken=.5,quantize=False)
        first=bank[1]
        self.assertLess(first[0,0,0],first[8,8,0])
        self.assertGreaterEqual(float(bank[3].min()),float(first.min())-1e-6)

    def test_collapsed_native_safe_range_stays_unresolved_instead_of_being_repaired(self):
        blur=importlib.import_module('blur')
        with self.assertRaisesRegex(ValueError,'collapsed'):
            blur.blur_bank(np.zeros((64,64,3)),levels=1,minimum=[0,0,0],maximum=[.01,1,1])


if __name__=='__main__':unittest.main()
