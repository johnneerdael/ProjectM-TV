"""Match original fans against exact released31 native index coverage."""
import re
import numpy as np
import pytest
from test_core2331_warp import ROOT
from primitives import draw_borders,draw_triangles


def native_indices(version):
    text=(ROOT/f'build/preset-corpus/source{version}/production-engine/src/libprojectM/MilkdropPreset/Border.cpp').read_text()
    block=text.split('m_borderMesh.Indices().Set(',1)[1].split(');',1)[0]
    values=[int(x) for x in re.findall(r'\d+',block)]
    assert len(values)==24
    return np.array(values).reshape(8,3).tolist()


def indexed_borders(values,indices):
    out=np.zeros((32,32,4),np.float32)
    outer=np.float32(values['ob_size']);inner=np.float32(values['ib_size'])
    for i,prefix in enumerate(['ob_','ib_']):
        r=np.float32(1)-outer-(inner if i else np.float32(0))
        R=np.float32(1)-outer if i else np.float32(1)
        p=np.array([[R,R],[R,-R],[-R,R],[-R,-R],[r,r],[r,-r],[-r,r],[-r,-r]],np.float32)
        colours=np.tile([values[prefix+c] for c in 'rgba'],(8,1)).astype(np.float32)
        out=draw_triangles(out,p*.5+.5,colours,indices,additive=False,quantize=True)
    return out


@pytest.mark.parametrize('outer,inner',[(.1,.2),(0,0),(-.3,.2),(1.5,.3),(.4,1.5)])
def test_release31_triangle_order_matches_original_alpha_fans(outer,inner):
    values={'ob_size':outer,'ib_size':inner}
    values.update(dict(zip(['ob_'+c for c in 'rgba'],[.8,.2,.4,.5])))
    values.update(dict(zip(['ib_'+c for c in 'rgba'],[.1,.6,.3,.3])))
    expected=draw_borders(np.zeros((32,32,4),np.float32),values,quantize=True)
    actual=indexed_borders(values,native_indices(31))
    np.testing.assert_array_equal(actual,expected)
    if outer>1 or inner>1:
        assert not np.array_equal(indexed_borders(values,native_indices(29)),expected)
