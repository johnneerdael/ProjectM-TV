"""Named historical native test profiles; configuration is never semantic evidence.

Set MILK_TEST_<NAME>_BINARIES to a preserved adapter directory. Both reader
and translator must report the pinned archive, patches and instrumentation.
Normal tests read checked-in source-bound snapshots. Missing/wrong snapshots
fail rather than silently borrowing current adapters. Regeneration requires
MILK_TEST_RECORD_HISTORICAL=1 and the exact preserved adapters.
"""
from functools import lru_cache
import copy
import hashlib
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PROFILES = {
    "merged32": {
        "engine": {
            "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
            "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e",
            "patches_sha256": "54fe3cd59ebf8ab44d3ec408672750f3eaacfa3c919db95fbb11b336b8c801a9"
        },
        "engine_archive_sha256": "ec863db1dd170bab4235f0e457c4b6fb18bc993b56cab337556828e759a4a98c",
        "shader_header_sha256": "6717e212969ea9c5e7d38bd2133d8624cea820409016a17ae9b281467fe1832b"
    },
    "merged35": {
        "engine": {
            "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
            "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e",
            "patches_sha256": "a0c7ddefb6e18c13641b3aaa48a0b90abc78b2f27f3f688ea5d02a551697895c"
        },
        "engine_archive_sha256": "01c128d5bca6e27b834878a437088ab63294ff8a99dac2abe3211486f68c9963",
        "shader_header_sha256": "6717e212969ea9c5e7d38bd2133d8624cea820409016a17ae9b281467fe1832b"
    },
    "merged37": {
        "engine": {
            "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
            "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e",
            "patches_sha256": "561165f1c11ca4df1fad0e637a38455ea5a6129ead9394855c800ee53e80bf83"
        },
        "engine_archive_sha256": "ce18814ab57c203535e18ba92be9474798ce5ba064357946efa702ce644f1648",
        "shader_header_sha256": "6717e212969ea9c5e7d38bd2133d8624cea820409016a17ae9b281467fe1832b"
    },
    "legacy_pre30": {
        "engine": {
            "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
            "instrumentation_sha256": "f936d8aa1a6480e598af9e6bce89a51d8a04ab79f5660280e1fb3fc901f5daa7",
            "patches_sha256": "3d9012b010691cef43d31d8bb7f9465348b621334bb7ae25b483e760766c0db6"
        },
        "engine_archive_sha256": "1209ee81dacbc772931e2d66337d1e574d8ebf1b806c5f575eccfc812eceedb4",
        "shader_header_sha256": "6717e212969ea9c5e7d38bd2133d8624cea820409016a17ae9b281467fe1832b"
    },
    "random_contract": {
        "engine": {
            "commit": "e0b0a967f0ffd7d332106c366668ed271718472b",
            "instrumentation_sha256": "5bc595dcca2b85a705ad491f8b2636c03968960ade5adea4a253abf79857b93e",
            "patches_sha256": "d21d4e3d9725178c000fd6f7ea5cd331389fb1100b70fce51341ece65d3fd818"
        },
        "engine_archive_sha256": "3a9aecf10f3e209504eff08ffc02b16d6ff8fbda8bc224fbf5e6bac2d4838a5d",
        "shader_header_sha256": "6717e212969ea9c5e7d38bd2133d8624cea820409016a17ae9b281467fe1832b"
    }
}


def validate_identity(name, metadata):
    if name not in PROFILES:
        raise ValueError(f'unknown historical profile: {name}')
    expected = PROFILES[name]
    for key, value in expected.items():
        assert metadata.get(key) == value, f'{name}: mismatched {key}: {metadata.get(key)!r}'


def profile_path(name):
    if name not in PROFILES:
        raise ValueError(f'unknown historical profile: {name}')
    default = 'legacy-pre30-native' if name == 'legacy_pre30' else name + '-native'
    variable = 'MILK_TEST_' + name.upper() + '_BINARIES'
    return Path(os.environ.get(variable, ROOT/'build/milk-analyzer'/default))


@lru_cache(maxsize=None)
def verified_binaries(name):
    directory = profile_path(name)
    reader, translator = directory/'milk-native-reader', directory/'milk-shader-translate'
    variable = 'MILK_TEST_' + name.upper() + '_BINARIES'
    for binary in (reader, translator):
        assert binary.is_file(), f'{name}: missing {binary}; supply exact preserved adapters via {variable}'
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary)/'identity.milk'
        path.write_text('MILKDROP_PRESET_VERSION=201\nPSVERSION_COMP=2\ncomp_1=`shader_body {ret=.4;}\n')
        report = json.loads(subprocess.check_output([str(reader), str(path)]))
        validate_identity(name, report['parser_inputs'])
        if name == 'legacy_pre30':
            assert report['equation_assembly_policy'] == 'milkdrop-records-v1'
        path = Path(temporary)/'request.json'
        path.write_text(json.dumps(dict(code='shader_body {ret=.4;}', stage='composite',
                                        profile='gles300', samplers={}, texture_sizes=[])))
        translated = json.loads(subprocess.check_output([str(translator), str(path)]))
        validate_identity(name, translated)
        assert translated['status'] == 'translated'
        assert translated['native_driver_verified'] is False
    return directory


FIXTURES = Path(__file__).resolve().parent/'fixtures/historical-profiles'


def _capture_or_load(name, kind, request, capture):
    """Replay parser/translation source evidence, never numeric native execution."""
    encoded = json.dumps(request, sort_keys=True, separators=(',', ':')).encode()
    digest = hashlib.sha256(encoded).hexdigest()
    path = FIXTURES/name/(kind+'-'+digest+'.json')
    if os.environ.get('MILK_TEST_RECORD_HISTORICAL') == '1':
        directory = verified_binaries(name)
        output, binary = capture(directory)
        record = dict(schema_version=1, profile=name, kind=kind, request=request,
                      request_sha256=digest, output=output,
                      adapter_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                      output_sha256=hashlib.sha256(json.dumps(output, sort_keys=True,
                          separators=(',', ':')).encode()).hexdigest())
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, sort_keys=True, separators=(',', ':'))+'\n')
    assert path.is_file(), f'{name}: missing source-bound historical fixture {path.name}; regenerate from verified adapters'
    record = json.loads(path.read_text())
    assert record['schema_version'] == 1
    assert (record['profile'], record['kind'], record['request_sha256']) == (name, kind, digest)
    assert record['request'] == request, f'{name}: historical source request mismatch'
    output = record['output']
    assert record['output_sha256'] == hashlib.sha256(json.dumps(output, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest(), f'{name}: stale historical payload digest'
    validate_identity(name, output['parser_inputs'] if kind == 'reader' else output['identity'])
    assert len(record['adapter_sha256']) == 64
    return copy.deepcopy(output), record['adapter_sha256']


def historical_source(name, raw):
    """Load a tree exported by the exact archived native reader for these bytes."""
    def capture(directory):
        reader = directory/'milk-native-reader'
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'fixture.milk'
            path.write_bytes(raw)
            output = json.loads(subprocess.check_output([str(reader), str(path)]))
        return output, reader
    result, reader_sha = _capture_or_load(name, 'reader', {'source_hex': raw.hex()}, capture)
    result.update(preset_sha256=hashlib.sha256(raw).hexdigest(), reader_sha256=reader_sha)
    return result


def historical_read(name, body, version=201):
    return historical_source(name, (f'MILKDROP_PRESET_VERSION={version}\n[preset00]\n'+body).encode())


def historical_shader(name, code, *, stage, profile, samplers, texture_sizes, validator=None):
    """Compile archived native translation with the actual installed GLSL validator."""
    if stage not in {'warp', 'composite'}:
        raise ValueError('explicit warp/composite stage required')
    if profile not in {'glsl330', 'gles300'}:
        raise ValueError('explicit glsl330/gles300 profile required')
    request = dict(code=code, stage=stage, profile=profile,
                   samplers=samplers, texture_sizes=texture_sizes)
    def capture(directory):
        translator = directory/'milk-shader-translate'
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'request.json'
            path.write_text(json.dumps(request))
            process = subprocess.run([str(translator), str(path)], capture_output=True,
                                     text=True, errors='replace', timeout=15)
        translation = (json.loads(process.stdout) if process.returncode == 0 else
                       dict(status='unknown', reason=f'native translator process exit {process.returncode}'))
        return dict(identity=PROFILES[name], translation=translation,
                    diagnostics=process.stderr), translator
    output, translator_sha = _capture_or_load(name, 'translator', request, capture)
    translation = output['translation']
    if translation['status'] != 'unknown':
        validate_identity(name, translation)
    accepted = None if translation['status'] == 'unknown' else False
    diagnostics = ''
    validator = Path(validator) if validator is not None else validator_path()
    if translation['status'] == 'translated':
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'shader.frag'
            path.write_text(translation['glsl'])
            process = subprocess.run([str(validator), '-S', 'frag', str(path)],
                                     capture_output=True, text=True, errors='replace', timeout=15)
        assert process.returncode in {0, 2}, 'offline GLSL compiler failed: '+process.stderr+process.stdout
        accepted = process.returncode == 0
        diagnostics = process.stdout + process.stderr
    return dict(source_sha256=hashlib.sha256(code.encode()).hexdigest(), request=request,
                translation=translation, translation_diagnostics=output['diagnostics'],
                translator_sha256=translator_sha, validator_sha256=hashlib.sha256(validator.read_bytes()).hexdigest(),
                offline_accepted=accepted, compiler_diagnostics=diagnostics,
                predicted_stage=(None if accepted is None else 'custom_'+stage if accepted else
                                 'fixed_warp' if stage == 'warp' else 'default_composite'),
                native_driver_verified=False)



def validator_path():
    return Path(os.environ.get('MILK_GLSLANG_VALIDATOR') or shutil.which('glslangValidator')
                or '/opt/homebrew/bin/glslangValidator')
