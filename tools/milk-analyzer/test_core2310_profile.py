import pytest
import forecast

ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': '545ca48adad787f963f9b29c1fc4fd7e8a71fb910f586c8747f96a075d130ddf',
}
POLICY = 'projectmtv-core-2.3.10-cold-thread-v1'


def test_published44_source_preserves_current_main_and_shape_sampling():
    assert forecast.source_main_binding_policy(ENGINE,None)=='projectmtv-core-2.2.6-v1'
    assert forecast.source_shape_sampler_policy(ENGINE,None)=='projectmtv-core-2.3.8-shape-state-v1'


def test_published44_equation_rng_has_its_own_exact_source_identity():
    assert POLICY in forecast.PRODUCTION_EQUATION_ENGINES
    assert forecast.PRODUCTION_EQUATION_ENGINES[POLICY]==ENGINE


def settings(**updates):
    return dict(width=32,height=32,mesh_x=8,mesh_y=8,profile='gles300',
                initial_rgba=[0,0,0,0],hue_offsets=[0]*4,
                equation_seed=forecast.PRODUCTION_EQUATION_SEED,
                blur_levels=0,quantize=True,**updates)


def test_44_higher_resolution_is_rejected_before_appearance_prediction(tmp_path):
    domain=settings();domain.update(width=1280,height=720)
    with pytest.raises(ValueError,match='2.3.10 higher-resolution'):
        forecast.forecast_source({'parser_inputs':{'engine':ENGINE}},audio={},binaries=tmp_path,
                                 domain=domain,compatibility={})


def test_44_rng_policy_cannot_borrow_historical43_identity(tmp_path):
    domain=settings(equation_rng_policy=POLICY)
    with pytest.raises(ValueError,match='engine identity mismatch'):
        forecast.forecast_source({'parser_inputs':{'engine':forecast.CORE_237_EQUATION_ENGINE}},
                                 audio={},binaries=tmp_path,domain=domain,compatibility={})


def test_mutated44_source_is_not_granted_current_shape_policy():
    changed=dict(ENGINE,patches_sha256='0'*64)
    assert forecast.source_main_binding_policy(changed,None)=='legacy-sorted-v1'
    with pytest.raises(ValueError,match='identity mismatch'):
        forecast.source_shape_sampler_policy(changed,'projectmtv-core-2.3.8-shape-state-v1')
