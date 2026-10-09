"""Published34 has a distinct identity and an explicit unchanged-math lineage."""
import engine_profiles as profiles


def test_source34_identity_is_registered_without_renaming_source31():
    assert hasattr(profiles,'CORE_2334_ENGINE'),'exact source34 identity missing'
    engine=profiles.CORE_2334_ENGINE
    assert engine=={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
                   'patches_sha256':'a6e0298331988d9777607f2cb75ade4bb362f69787e865aaaf6578479267d0df'}
    assert profiles.matches(engine)
    assert not profiles.matches(engine,profiles.CORE_2331_ENGINE)


def test_source34_math_lineage_is_separate_from_exact_identity():
    assert hasattr(profiles,'math_matches'),'explicit math lineage missing'
    engine={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
            'patches_sha256':'a6e0298331988d9777607f2cb75ade4bb362f69787e865aaaf6578479267d0df'}
    assert profiles.math_matches(engine,profiles.CORE_2331_ENGINE)
    assert not profiles.math_matches(engine,profiles.CORE_2329_ENGINE)
    assert not profiles.math_matches({**engine,'patches_sha256':'0'*64},profiles.CORE_2331_ENGINE)
    assert not profiles.math_matches({**engine,'commit':'0'*40},profiles.CORE_2331_ENGINE)
    assert not profiles.math_matches(profiles.CORE_2331_ENGINE,engine)


def test_source34_rng_policy_retains_exact_engine_attribution():
    from forecast import PRODUCTION_EQUATION_ENGINES
    key='projectmtv-core-2.3.34-cold-thread-v1'
    assert key in PRODUCTION_EQUATION_ENGINES,'source34 RNG policy missing'
    assert PRODUCTION_EQUATION_ENGINES[key]['patches_sha256']=='a6e0298331988d9777607f2cb75ade4bb362f69787e865aaaf6578479267d0df'


def test_source34_display_centre_and_sampling_policies_use_declared_math():
    from forecast import source_centre_policies,source_builtin_viewport_policy
    from composite_mesh import CORE_2322_CENTRES
    from primitives import CORE_2322_SHAPE_CENTRES
    from quad_lines import PROFILE,RETAINED_CLIP_VIEWPORT
    engine={'commit':'6f64807467e312034883a4389e6aa80a675458bc',
            'patches_sha256':'a6e0298331988d9777607f2cb75ade4bb362f69787e865aaaf6578479267d0df'}
    assert source_centre_policies(engine,{})==(CORE_2322_CENTRES,CORE_2322_SHAPE_CENTRES)
    assert source_builtin_viewport_policy(engine,{'profile':'gles300',
        'line_rendering_profile':PROFILE,'triangle_subpixel_bits':8})==RETAINED_CLIP_VIEWPORT
