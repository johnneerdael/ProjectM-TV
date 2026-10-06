"""Prevent historical main-sampler defaults under verified patched engines."""
import pytest
import forecast
from sampling_policy import main_sampler_bindings


@pytest.mark.parametrize('engine',list(forecast.PRODUCTION_EQUATION_ENGINES.values()))
def test_verified_patched_engine_defaults_to_reserved_main_unit_zero(engine):
    policy=forecast.source_main_binding_policy(engine,None)
    bindings=main_sampler_bindings(['sampler_fc_main'],stage='warp',frame_wrap=0,policy=policy)
    assert bindings['sampler_main']['unit']==0
    assert bindings['sampler_main']['wrap'] is False
    assert bindings['sampler_fc_main']['unit']==1
    assert bindings['sampler_fc_main']['wrap'] is False


@pytest.mark.parametrize('engine',[{},dict(forecast.CORE_237_EQUATION_ENGINE,patches_sha256='unverified')])
def test_unknown_or_modified_engine_does_not_inherit_current_contract(engine):
    assert forecast.source_main_binding_policy(engine,None)=='legacy-sorted-v1'


def test_explicit_historical_diagnostic_policy_is_retained():
    assert forecast.source_main_binding_policy(forecast.CORE_237_EQUATION_ENGINE,'legacy-sorted-v1')=='legacy-sorted-v1'


def test_unsupported_policy_is_rejected():
    with pytest.raises(ValueError,match='main binding policy'):
        forecast.source_main_binding_policy(forecast.CORE_237_EQUATION_ENGINE,'latest')
