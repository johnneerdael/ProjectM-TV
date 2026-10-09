"""Defined int32 instance style domain with historical/static fallbacks."""
import numpy as np
import pytest
import scene_draw
from engine_profiles import CORE_2329_ENGINE,CORE_2331_ENGINE


@pytest.mark.parametrize('value,expected', [(-1.9,True),(-.99,False),(0,False),
    (.99,False),(1,True),(-2147483648.5,True),(2147483647.9,True)])
def test_instance_outline_truncates_defined_evaluator_domain(value,expected):
    source={'values':{},'parser_inputs':{'engine':CORE_2331_ENGINE}}
    assert scene_draw.source_shape_thickness(source,0,{'thick':value}) is expected


@pytest.mark.parametrize('value', [np.nan,np.inf,-np.inf,2147483648,-2147483649,
                                  {'ieee':'nan'}])
@pytest.mark.parametrize('saved', [0,1])
def test_instance_outline_outside_domain_retains_saved_style(value,saved):
    source={'values':{'shapecode_0_thickOutline':str(saved)},'parser_inputs':{'engine':CORE_2331_ENGINE}}
    assert scene_draw.source_shape_thickness(source,0,{'thick':value}) is bool(saved)


def test_old_engine_and_missing_instance_value_preserve_static_style():
    source={'values':{},'parser_inputs':{'engine':CORE_2329_ENGINE}}
    assert scene_draw.source_shape_thickness(source,0,{'thick':2}) is False
    source['parser_inputs']['engine']=CORE_2331_ENGINE
    assert scene_draw.source_shape_thickness(source,0,{}) is False


def test_draw_uses_each_instance_style_without_reexecuting_equations(monkeypatch):
    from primitives import shape_fan
    positions=[]
    def lines(target,points,*args,**kwargs):
        positions.append(points.copy())
        return target
    monkeypatch.setattr(scene_draw,'draw_lines',lines)
    shape={'x':.5,'y':.5,'rad':.15,'ang':0,'sides':4,'border_a':1,'a':0,'a2':0}
    frame={'main':{},'shapes':[{'index':0,'values':{**shape,'thick':0}},
                             {'index':0,'values':{**shape,'thick':-2}}]}
    source={'values':{},'parser_inputs':{'engine':CORE_2331_ENGINE}}
    scene_draw.draw_source_scene(np.zeros((16,16,4),np.float32),source,frame,None,[])
    assert len(positions)==5
    np.testing.assert_array_equal(positions[0],positions[1])
    assert np.any(positions[1]!=positions[2])
    assert frame['shapes'][1]['values']['thick']==-2
