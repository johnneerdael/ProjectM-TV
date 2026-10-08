"""Source contracts for the published 15-patch renderer, separate from GPU proof."""
import numpy as np
import pytest

ENGINE={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
        'patches_sha256':'65313919430bd6d1531292b405463d8ec400a44bcfddfb1eb808fbaba16b5ad0'}


def test_2327_identity_retains_verified_tint_centres_and_separate_rng():
    import engine_profiles as profiles
    import forecast
    from legacy_composite import source_tint_amount
    from composite_mesh import CORE_2322_CENTRES
    from primitives import CORE_2322_SHAPE_CENTRES
    assert profiles.CORE_2327_ENGINE==ENGINE
    assert profiles.matches(ENGINE)
    assert forecast.PRODUCTION_EQUATION_ENGINES['projectmtv-core-2.3.27-cold-thread-v1']==ENGINE
    assert forecast.source_centre_policies(ENGINE,{})==(CORE_2322_CENTRES,CORE_2322_SHAPE_CENTRES)
    assert source_tint_amount({'values':{'fShader':'.25'},'parser_inputs':{'engine':ENGINE}})==.25
    assert not profiles.matches({**ENGINE,'patches_sha256':'0'*64})


def test_negative_nested_integer_power_has_signed_cpu_semantics():
    from spatial import warp_vertex_uv
    from engine_profiles import CORE_2327_ZOOM
    for exponent,expected in ((2,.625),(3,.4375),(0,.0)):
        # At radius1 the inner power is exponent. CPU (-2)^2=4,
        # (-2)^3=-8, and (-2)^0=1; positive GL power retains its own rules.
        actual=warp_vertex_uv([[1,0]],zoom=-2,zoomexp=exponent,zoom_policy=CORE_2327_ZOOM)
        np.testing.assert_array_equal(actual,[[expected if exponent else 1,.5]])
    with pytest.raises(ValueError,match='power domain'):
        warp_vertex_uv([[1,0]],zoom=-2,zoomexp=2)


def test_cpu_negative_power_does_not_fabricate_fractional_or_positive_gl_domains():
    from spatial import warp_vertex_uv
    from engine_profiles import CORE_2327_ZOOM
    with pytest.raises(ValueError,match='numeric domain'):
        warp_vertex_uv([[1,0]],zoom=-2,zoomexp=.5,zoom_policy=CORE_2327_ZOOM)
    with pytest.raises(ValueError,match='power domain'):
        warp_vertex_uv([[1,0]],zoom=2,zoomexp=-2,zoom_policy=CORE_2327_ZOOM)
