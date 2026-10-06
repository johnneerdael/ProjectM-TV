"""Historical trees/translations are source evidence; EEL execution stays live."""
import pytest
from analyzer_test_profiles import historical_read, historical_shader


def pytest_configure(config):
    config.addinivalue_line('markers', 'historical_profile(name): exact archived native source regression')


@pytest.fixture(autouse=True)
def historical_native_profile(request, monkeypatch):
    marker = request.node.get_closest_marker('historical_profile')
    if marker is None:
        return
    name, = marker.args
    if name == 'legacy_pre30':
        import test_native_reader
        import test_shader_compat
        import test_sampler_state_binding
        monkeypatch.setattr(test_native_reader.NativeReaderTest, 'read',
                            lambda self, body, version=201: historical_read(name, body, version))
        monkeypatch.setattr(test_shader_compat.ShaderCompatibilityTest, 'check',
                            lambda self, code, stage='composite', profile='glsl330':
                            historical_shader(name, code, stage=stage, profile=profile,
                                samplers={'sampler_main':'sampler2D'}, texture_sizes=['texsize_main']))
        monkeypatch.setattr(test_sampler_state_binding, 'check_shader',
                            lambda code, **kwargs: historical_shader(name, code,
                                **{k:v for k,v in kwargs.items() if k not in {'translator','validator'}}))
