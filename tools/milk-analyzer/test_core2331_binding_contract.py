"""Release31 slot typing remains conditional on actual runtime image inputs."""
import copy
import hashlib
from pathlib import Path
import shutil

import pytest

from engine_profiles import CORE_2331_ENGINE
from random_binding_contract import BODY_HASHES, METHODS, POLICY, SOURCE_FILES
from random_binding_contract import native_contract, recognized, verified_contract


ROOT = Path(__file__).resolve().parents[2]
SOURCE31 = ROOT/'build/preset-corpus/source31/production-engine'
SOURCE29 = ROOT/'build/preset-corpus/source29/production-engine'
FILES31 = {**SOURCE_FILES,
    'MilkdropPreset/PerPixelMesh.hpp': '61a06eef48c9ee96fc7451ff17596c816906d5ca6a160769d6c792c85b1fb0d6',
    'MilkdropPreset/MilkdropShader.hpp': 'c777e79ffc90368418c786f04a08613410ff1803b61d18a4f7f8bbdf6dbc10de',
    'MilkdropPreset/PresetState.hpp': '7c0bbf2c7baad0aa8f6d257820745bd376022bc57b602b45f1267a79ea86cf89',
    'Renderer/TextureManager.hpp': '021e053984546581fa80ea085b5beca1d66f1a09e9294cd0de296f0fbae87a15',
    'Renderer/Texture.hpp': 'b8c1b2d2b188470522e39f4f0153637dc2c9460f079e12f7befed09c4e07efde',
    'Renderer/Sampler.hpp': '7c3a547080e5677ee1584fa04ef0b6a5709402e75fb47cd29a5f24f99af78302',
}
BODIES31 = {**BODY_HASHES,
    'TextureManager.GetRandomTexture': '427f40c9a0bf6c45bd74d6a433936a57b45a7999394e541a4859e9eb0f495025',
    'TextureManager.LoadTexture': 'f41c1a0bd50d17d784067bdba0700c2dea7aa4a09aa058ea71ee80ed9e36c20e',
    'MilkdropPreset.Initialize': 'e9b09519fa583dd0263f2657eab74a1cbc9701c043b1235064e2889153f16bad',
    'TextureManager.Preload': '99f526cb3a5aa80fa788687170ff3d053a6201be2fa9b8de1c26b626363b6e58',
    'MilkdropShader.LoadVariables': 'fc5acc978feafffa6d65df74970d40d69209984d024fcc7cea4509393e5b52d3',
}


def contract31():
    return {'policy': POLICY, 'engine': dict(CORE_2331_ENGINE),
            'body_sha256': dict(BODIES31), 'file_sha256': dict(FILES31)}


def inputs31():
    code='shader_body {ret=tex2D(sampler_pc_rand00_red,uv).rgb;}'
    contract=contract31()
    archive='a'*64
    source={'sections': {'comp_': {'source': code, 'status': 'parsed'}},
            'parser_inputs': {'engine': dict(CORE_2331_ENGINE),
                              'random_binding_contract': contract,
                              'engine_archive_sha256': archive}}
    compatibility={'source_sha256': hashlib.sha256(code.encode()).hexdigest(),
        'offline_accepted': True,
        'request': {'code': code, 'stage': 'composite', 'profile': 'gles300',
                    'samplers': {'sampler_pc_rand00_red': 'sampler2D',
                                 'sampler_fw_rand00': 'sampler2D'},
                    'texture_sizes': ['texsize_rand00_red', 'texsize_rand00']},
        'translation': {'engine': dict(CORE_2331_ENGINE),
            'random_binding_contract': copy.deepcopy(contract),
            'engine_archive_sha256': archive,
            'sampler_reference_body_sha256': BODIES31['MilkdropShader.GetReferencedSamplers'],
            'status': 'translated', 'stage': 'composite', 'profile': 'gles300',
            'referenced_samplers': ['pc_rand00_red', 'fw_rand00']}}
    return source,compatibility


def verify(source, compatibility):
    return verified_contract(source, stage='composite', profile='gles300',
                             compatibility=compatibility)


def body_hash(engine, path, signature):
    source=(engine/'src/libprojectM'/path).read_text()
    first=source.index(signature)
    return hashlib.sha256(source[first:source.index('\n}',first)+2].encode()).hexdigest()


@pytest.fixture
def copied_source31(tmp_path):
    if not SOURCE31.is_dir():pytest.skip('prepared exact34-patch source31 required')
    for name in set(FILES31) | {row[0] for row in METHODS.values()}:
        relative=Path('src/libprojectM')/name
        (tmp_path/relative).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SOURCE31/relative,tmp_path/relative)
    return tmp_path


def test_source31_exact_native_contract_and_source29_method_equivalence(copied_source31):
    assert native_contract(copied_source31)==contract31()
    if not SOURCE29.is_dir():pytest.skip('prepared source29 needed for comparison')
    for name,(path,signature,_) in METHODS.items():
        assert body_hash(SOURCE29,path,signature)==body_hash(SOURCE31,path,signature)==BODIES31[name]


def test_source31_typed_slots_keep_alias_modes_lifetime_and_unknown_images():
    source,compatibility=inputs31()
    context=verify(source,compatibility)
    assert context is not None
    assert context['engine']==CORE_2331_ENGINE
    assert context['body_sha256']==BODIES31
    assert context['file_sha256']==FILES31
    aliases=context['random_inputs']
    assert {v['slot'] for v in aliases.values()}=={0}
    assert context['texsize_inputs']['texsize_rand00_red']==context['texsize_inputs']['texsize_rand00']
    assert context['samplers']==compatibility['request']['samplers']
    for value in aliases.values():
        assert value['lifetime']=='one PresetState instance; shared across stages and shader reloads'
        assert value['required_target']=='GL_TEXTURE_2D'
        assert value['selection_epoch'] is None
        assert value['selected_asset'] is None
        assert value['unit'] is None
        assert value['uploaded_dimensions'] is None
    assert context['selected_assets'] is None
    assert context['native_driver_verified'] is context['appearance_verified'] is False


@pytest.mark.parametrize('name', list(METHODS))
def test_source31_changed_method_revokes_contract(copied_source31,name):
    assert native_contract(copied_source31)==contract31()
    path,signature,_=METHODS[name]
    target=copied_source31/'src/libprojectM'/path
    source=target.read_text();start=source.index(signature)
    brace=source.index('{',start)
    target.write_text(source[:brace+1]+'\n    /* unqualified method */'+source[brace+1:])
    assert native_contract(copied_source31) is None


@pytest.mark.parametrize('name', list(FILES31))
def test_source31_changed_header_revokes_contract(copied_source31,name):
    assert native_contract(copied_source31)==contract31()
    target=copied_source31/'src/libprojectM'/name
    target.write_bytes(target.read_bytes()+b'\n// unqualified header\n')
    assert native_contract(copied_source31) is None


@pytest.mark.parametrize('mutation', ['body','header','contract_engine','source_engine',
    'translation_engine','missing_engine','archive','scan','type','size'])
def test_source31_changed_provenance_revokes_typed_slots(mutation):
    source,compatibility=inputs31()
    assert verify(source,compatibility) is not None
    contract=source['parser_inputs']['random_binding_contract']
    if mutation=='body':contract['body_sha256']['TextureManager.GetRandomTexture']='0'*64
    elif mutation=='header':contract['file_sha256']['MilkdropPreset/PresetState.hpp']='0'*64
    elif mutation=='contract_engine':contract['engine']['patches_sha256']='0'*64
    elif mutation=='source_engine':source['parser_inputs']['engine']['patches_sha256']='0'*64
    elif mutation=='translation_engine':compatibility['translation']['engine']['patches_sha256']='0'*64
    elif mutation=='missing_engine':contract.pop('engine')
    elif mutation=='archive':source['parser_inputs']['engine_archive_sha256']='0'*64
    elif mutation=='scan':compatibility['translation']['referenced_samplers']=['main']
    elif mutation=='type':compatibility['request']['samplers']['sampler_pc_rand00_red']='sampler3D'
    else:compatibility['request']['texture_sizes'].append('texsize_rand16')
    assert verify(source,compatibility) is None


def test_historical_contract_still_recognized_and_cannot_be_relabeled_source31():
    historical={'policy': POLICY,'body_sha256':dict(BODY_HASHES),'file_sha256':dict(SOURCE_FILES)}
    assert recognized(historical)
    source,compatibility=inputs31()
    source['parser_inputs']['random_binding_contract']=historical
    compatibility['translation']['random_binding_contract']=copy.deepcopy(historical)
    assert verify(source,compatibility) is None


@pytest.mark.parametrize('value', [None,[],{},'invalid'])
def test_contract_recognition_rejects_malformed_values(value):
    assert not recognized(value)
