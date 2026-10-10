"""Source EEL close-factor equality stays separate from strict shader equality."""
import math
import pytest
from shader_fields import Field
from effect_families import _EEL,_number
from test_effect_families import read
from test_source_appearance import appearance


def scalar(value):return Field('constant',detail={'value':value})


@pytest.mark.parametrize('delta,expected',[(0,1),(.000009,1),(-.000009,1),(.00001,0),(-.00001,0),(.000011,0)])
def test_eel_equality_preserves_native_strict_close_factor_boundary(delta,expected):
    expr=_EEL.operation('equal',(scalar(delta),scalar(0)))
    assert _number(expr)==expected


def test_shader_scalar_equality_remains_exact():
    assert _number(Field('equal',(scalar(.000009),scalar(0))))==0


def test_authored_assignment_then_eel_equal_selects_native_branch():
    d=appearance(read('fWaveAlpha=0\nshapecode_0_enabled=1\n'
        'shape_0_per_frame1=k=.000009;x=if(equal(k,0),.2,.8);y=.5;rad=.2;\n'))
    e=next(e for e in d['elements'] if e['id']=='shape_0')
    assert e['center_trajectory']['center_source_xy']==pytest.approx([.2,.5])


def test_unbound_eel_equal_keeps_explicit_target_semantics_in_export():
    from source_appearance import _expression
    expr=_EEL.operation('equal',(Field('input',detail={'name':'bass'}),scalar(1)))
    assert _number(expr) is None
    assert _expression(expr)['nodes'][0]['op']=='eel_equal'


def test_nonfinite_constant_eel_equal_stays_unresolved():
    expr=_EEL.operation('equal',(scalar(math.inf),scalar(math.inf)))
    assert _number(expr) is None
