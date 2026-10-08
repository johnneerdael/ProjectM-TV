import importlib
import math
import unittest
import numpy as np
from field_math import UnresolvedMath


class LegacyCompositeTest(unittest.TestCase):
    def module(self):return importlib.import_module('legacy_composite')

    def test_hue_uses_float_context_time_and_float_intermediates(self):
        time=np.float32(10001.123456789)
        offsets=np.array([0,11,23,37],np.float32)
        channels=[]
        for rate,phase,slot in [(.0143,3,3),(.0107,1,1),(.0129,6,2)]:
            angle=time*np.float32(30)*np.float32(rate)
            angle=angle+np.float32(phase)
            angle=angle+offsets[slot]
            channels.append(np.float32(.6)+np.float32(.3)*np.sin(angle))
        raw=np.array(channels,np.float32)
        expected=np.float32(.5)+np.float32(.5)*(raw/raw.max())
        np.testing.assert_allclose(self.module().corner_shades(10001.123456789,offsets)[0],
                                    expected,atol=2e-7,rtol=0)

    def test_gamma_redraw_weights_match_native_branch_rules(self):
        m=self.module()
        self.assertEqual(m.gamma_weights(2.5,echo=False),[1,1,.5])
        self.assertEqual(m.gamma_weights(.5,echo=False),[.5])
        self.assertEqual(m.gamma_weights(.5,echo=True),[1])
        self.assertEqual(m.gamma_weights(2.5,echo=True),[1,1,.5])

    def test_hue_corner_mapping_and_unused_offset_zero(self):
        m=self.module();shade=m.corner_shades(0,[0,0,0,0])
        raw=np.array([.6+.3*math.sin(3),.6+.3*math.sin(1),.6+.3*math.sin(6)])
        np.testing.assert_allclose(shade[0],.5+.5*raw/raw.max(),atol=1e-7)
        np.testing.assert_array_equal(shade,m.corner_shades(0,[99,0,0,0]))

    def test_filter_blend_equations_preserve_native_order(self):
        m=self.module();field=np.full((2,2,4),.25,dtype=np.float32)
        cases=[({'bBrighten':'1'},.4375),({'bDarken':'1'},.0625),
               ({'bSolarize':'1'},.375),({'bInvert':'1'},.75),
               ({'bDarken':'1','bInvert':'1'},.9375)]
        for settings,expected in cases:
            np.testing.assert_allclose(m.apply_filters(field,settings,quantize=False),expected)

    def test_file_gamma_controls_brightness_without_echo(self):
        m=self.module();field=np.full((8,8,4),.1,dtype=np.float32);field[...,3]=1
        first=m.legacy_display(field,values={'fGammaAdj':'1'},time=0,hue_offsets=[0]*4,quantize=False)
        second=m.legacy_display(field,values={'fGammaAdj':'2'},time=0,hue_offsets=[0]*4,quantize=False)
        np.testing.assert_allclose(second[...,:3],first[...,:3]*2,atol=1e-7)

    def test_echo_uses_static_zoom_and_cxx_negative_orientation_remainder(self):
        m=self.module();field=np.zeros((8,8,4),dtype=np.float32);field[...,3]=1
        field[...,0]=np.linspace(0,.5,8)[None,:]
        settings={'fGammaAdj':'1','fVideoEchoAlpha':'1','fVideoEchoZoom':'1'}
        normal=m.legacy_display(field,values={**settings,'nVideoEchoOrientation':'0'},time=0,hue_offsets=[0]*4,quantize=False)
        negative=m.legacy_display(field,values={**settings,'nVideoEchoOrientation':'-1'},time=0,hue_offsets=[0]*4,quantize=False)
        flipped=m.legacy_display(field,values={**settings,'nVideoEchoOrientation':'1'},time=0,hue_offsets=[0]*4,quantize=False)
        np.testing.assert_array_equal(normal,negative)
        self.assertLess(normal[0,0,0],normal[0,-1,0])
        self.assertGreater(flipped[0,0,0],flipped[0,-1,0])

    def test_missing_random_inputs_and_invalid_zoom_remain_unknown(self):
        m=self.module();field=np.zeros((4,4,4))
        with self.assertRaises(UnresolvedMath):m.legacy_display(field,values={},time=0,hue_offsets=None)
        with self.assertRaises(UnresolvedMath):
            m.legacy_display(field,values={'fVideoEchoAlpha':'1','fVideoEchoZoom':'0'},time=0,hue_offsets=[0]*4)

    def test_additive_redraw_quantizes_after_blending(self):
        m=self.module();field=np.ones((8,8,4),dtype=np.float32)
        shade=m.legacy_display(field,values={'fGammaAdj':'1'},time=0,hue_offsets=[0]*4,quantize=False)
        unit=np.float32(1)/np.float32(255)
        field[...,0]=unit/shade[0,0,0]
        raw=m.legacy_display(field,values={'fGammaAdj':'1'},time=0,hue_offsets=[0]*4,quantize=False)
        self.assertEqual(raw[0,0,0],unit)
        actual=m.legacy_display(field,values={'fGammaAdj':'1.5'},time=0,hue_offsets=[0]*4,quantize=True)
        self.assertEqual(actual[0,0,0],np.float32(2)/np.float32(255))


if __name__=='__main__':unittest.main()


def test_pr57_tint_amount_zero_fractional_and_threshold():
    from legacy_composite import corner_shades
    offsets=[0,11,23,37]
    historical=corner_shades(1,offsets)
    np.testing.assert_array_equal(corner_shades(1,offsets,shader_amount=0),np.ones((4,3),np.float32))
    np.testing.assert_array_equal(corner_shades(1,offsets,shader_amount=.001),np.ones((4,3),np.float32))
    expected=historical*np.float32(.25)+np.float32(.75)
    np.testing.assert_array_equal(corner_shades(1,offsets,shader_amount=.25),expected)
    np.testing.assert_array_equal(corner_shades(1,offsets,shader_amount=1),historical)
