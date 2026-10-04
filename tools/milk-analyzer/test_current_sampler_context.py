import json,hashlib,subprocess,tempfile
from pathlib import Path
from coverage_audit import audit_source
from shader_compat import check_shader


def test_current_sampler_state_requires_source_bound_compiler_context():
    binaries=Path(__file__).resolve().parents[2]/'build/milk-analyzer/merged32-native'
    raw=('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\ncomp_1='+chr(96)+
         'sampler sampler_main = sampler_state {AddressU=CLAMP;};shader_body {ret=GetPixel(uv);}\n').encode()
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'test.milk';path.write_bytes(raw)
        source=json.loads(subprocess.check_output([str(binaries/'milk-native-reader'),str(path)]))
    source.update(preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256='reader')
    code=source['sections']['comp_']['source']
    report=check_shader(code,stage='composite',profile='gles300',translator=binaries/'milk-shader-translate',
                        validator=Path('/opt/homebrew/bin/glslangValidator'),samplers={'sampler_main':'sampler2D'},texture_sizes=[])
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
    binaries=Path(__file__).resolve().parents[2]/'build/milk-analyzer/merged32-native'
    raw=('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\ncomp_1='+chr(96)+
         'sampler sampler_rand04 = sampler_state {AddressU=CLAMP;};'
         'shader_body {ret=tex2D(sampler_rand04,uv);}\n').encode()
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'test.milk';path.write_bytes(raw)
        source=json.loads(subprocess.check_output([str(binaries/'milk-native-reader'),str(path)]))
    source.update(preset_sha256=hashlib.sha256(raw).hexdigest(),reader_sha256='reader')
    report=check_shader(source['sections']['comp_']['source'],stage='composite',profile='gles300',
        translator=binaries/'milk-shader-translate',validator=Path('/opt/homebrew/bin/glslangValidator'),
        samplers={'sampler_main':'sampler2D','sampler_rand04':'sampler2D'},texture_sizes=[])
    assert report['offline_accepted'],report
    audit=audit_source(raw,cache=source,reader_sha='reader',shader_profile='gles300',
                       shader_compatibility={'composite':report})
    assert not next(u for u in audit['units'] if u['stage']=='composite')['lowering_complete']
