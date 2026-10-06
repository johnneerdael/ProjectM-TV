import hashlib
import pytest
from analyzer_test_profiles import historical_source, historical_shader
from coverage_audit import audit_source


def test_current_sampler_state_requires_source_bound_compiler_context():
    raw=('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\ncomp_1='+chr(96)+
         'sampler sampler_main = sampler_state {AddressU=CLAMP;};shader_body {ret=GetPixel(uv);}\n').encode()
    source=historical_source('merged32',raw)
    source.update(preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256='reader')
    code=source['sections']['comp_']['source']
    report=historical_shader('merged32',code,stage='composite',profile='gles300',samplers={'sampler_main':'sampler2D'},texture_sizes=[])
    assert report['offline_accepted'],report
    audit=audit_source(raw,cache=source,reader_sha='reader',shader_profile='gles300',
                       shader_compatibility={'composite':report})
    unit=next(u for u in audit['units'] if u['stage']=='composite')
    assert unit['lowering_complete'],unit
    report['source_sha256']='stale'
    audit=audit_source(raw,cache=source,reader_sha='reader',shader_profile='gles300',
                       shader_compatibility={'composite':report})
    assert not next(u for u in audit['units'] if u['stage']=='composite')['lowering_complete']


def test_random_alias_type_declaration_does_not_prove_native_association():
    raw=('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\ncomp_1='+chr(96)+
         'sampler sampler_rand04 = sampler_state {AddressU=CLAMP;};'
         'shader_body {ret=tex2D(sampler_rand04,uv);}\n').encode()
    source=historical_source('merged32',raw)
    source.update(preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256='reader')
    report=historical_shader('merged32',source['sections']['comp_']['source'],stage='composite',profile='gles300',
        samplers={'sampler_main':'sampler2D','sampler_rand04':'sampler2D'},texture_sizes=[])
    assert report['offline_accepted'],report
    audit=audit_source(raw,cache=source,reader_sha='reader',shader_profile='gles300',
                       shader_compatibility={'composite':report})
    assert not next(u for u in audit['units'] if u['stage']=='composite')['lowering_complete']

pytestmark = pytest.mark.historical_profile("merged32")
