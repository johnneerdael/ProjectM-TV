"""Pinned slot association, conditional on runtime textures rather than observations.

This is a source-language contract. It supplies no image, dimensions, GL unit,
selection epoch, successful load or driver/appearance evidence.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

from sampling_policy import texture_settings
from engine_profiles import CORE_2331_ENGINE,CORE_2334_ENGINE


POLICY = 'projectmtv-random-slot-inputs-v1'
METHODS = {
    'MilkdropShader.LoadTexturesAndCompile': ('MilkdropPreset/MilkdropShader.cpp', 'void MilkdropShader::LoadTexturesAndCompile(', '2f3ba7eada45e65821b6f2b942f0f37f4bd89c8765300c97a37520a3a333938f'),
    'MilkdropShader.GetReferencedSamplers': ('MilkdropPreset/MilkdropShader.cpp', 'void MilkdropShader::GetReferencedSamplers(', 'e2cedb2940bf69834244f2b9a081c21a0c4f5666de887ad23b80b6bac24f9447'),
    'TextureManager.GetRandomTexture': ('Renderer/TextureManager.cpp', 'auto TextureManager::GetRandomTexture(', '7b69be9e037aed0b430ac6f49fb1082273d5156c33958a081fa0f7d16c857a47'),
    'TextureManager.GetTexture': ('Renderer/TextureManager.cpp', 'TextureSamplerDescriptor TextureManager::GetTexture(', '043fb7d85e676adb25ab606e0c656e23bcd26cf712d6c309f9952793304be0fe'),
    'TextureManager.ExtractTextureSettings': ('Renderer/TextureManager.cpp', 'void TextureManager::ExtractTextureSettings(', '9d67b7e31e6016b9ff54077168c2030491b64f0785529777a1419c2e24bf9872'),
    'TextureManager.LoadTexture': ('Renderer/TextureManager.cpp', 'auto TextureManager::LoadTexture(', 'da954731847411188f40bb947bf51d5b7181d3f000d15c61e0177a9ca72622a3'),
    'TextureSamplerDescriptor.SamplerDeclaration': ('Renderer/TextureSamplerDescriptor.cpp', 'auto TextureSamplerDescriptor::SamplerDeclaration(', 'd868913835dc9f6458b1a1bbe44fde4dffac38ed0ea72a637a3c727b43d22373'),
    'TextureSamplerDescriptor.TexSizeDeclaration': ('Renderer/TextureSamplerDescriptor.cpp', 'auto TextureSamplerDescriptor::TexSizeDeclaration(', '34c90baf231753f012f69e21330bf0e2ca7361fd5398fd6c063ca6b26cea0bc0'),
    'TextureSamplerDescriptor.Bind': ('Renderer/TextureSamplerDescriptor.cpp', 'void TextureSamplerDescriptor::Bind(', 'a878f6ed163204e1fba022e94ddbc58ceaf3ebe12291d075cfa738adda5798b2'),
    'TextureSamplerDescriptor.ShortRandomAlias': ('Renderer/TextureSamplerDescriptor.cpp', 'auto ShortRandomAlias(', 'f9c04d1da77c09159ff1b7320e5b015a1c4f5f3c67c2526541f3d31f39330550'),
    'MilkdropPreset.Initialize': ('MilkdropPreset/MilkdropPreset.cpp', 'void MilkdropPreset::Initialize(', '302d5d0beeb9aab46f30d90f488e6b15f6812918c0f971f60dcb879fda522305'),
    'TextureManager.GetSampler': ('Renderer/TextureManager.cpp', 'auto TextureManager::GetSampler(', '86808d805455bd5f269478ad8f64e0737b76a532e29d784f353e0af229c3cccf'),
    'TextureManager.Preload': ('Renderer/TextureManager.cpp', 'void TextureManager::Preload(', 'd3d1a39a1176e07d52faca62a88d55a6fc83ad207b5afd868e389db91579c74a'),
    'Sampler.Constructor': ('Renderer/Sampler.cpp', 'Sampler::Sampler(', 'b467206c63fd6cb069c929a0054579efe46e0fc6c1b64e629e10cfd6877e8d8b'),
    'Sampler.Bind': ('Renderer/Sampler.cpp', 'void Sampler::Bind(', '4126ec94f1a79ef506040870904f98c8fc3a5b05becd0856992aecba3675ae7d'),
    'Texture.Bind': ('Renderer/Texture.cpp', 'void Texture::Bind(', '04f9f9edf638507ba6333237bccdfdbe0789a55a69971908f8d9ca393388eb2a'),
    'MilkdropShader.LoadVariables': ('MilkdropPreset/MilkdropShader.cpp', 'void MilkdropShader::LoadVariables(', 'c65eacca0e080c46bac5f3d959ce7b3bad64a4737e7c386899b48fd7ec8d2290'),
    'PerPixelMesh.Draw': ('MilkdropPreset/PerPixelMesh.cpp', 'void PerPixelMesh::Draw(', '8a92931649bade9d4dc02caafb36f91c38a5eb27f9c9caf01f883232cd259838'),
    'Sampler.WrapMode': ('Renderer/Sampler.cpp', 'void Sampler::WrapMode(', 'd54b5750d5777dbd3ce54d3e4bb4e9085579a2a01ff017053eedb068782f86a2'),
}
BODY_HASHES = {name: data[2] for name, data in METHODS.items()}
SOURCE_FILES = {
    'MilkdropPreset/PerPixelMesh.hpp': 'bc12286c4d12e4208d65c09bbdad16cb7fe41b5c57d03f19239fd21e42323dff',
    'MilkdropPreset/MilkdropShader.hpp': 'd5ff7a12145c9e6771072744757b569cee1e7e13477f54f726df26b147efd83a',
    'MilkdropPreset/PresetState.hpp': '834412310ad591ed7d25fd0d1d565cb69737bb6c6db0780596bda15d0cd51595',
    'Renderer/TextureManager.hpp': 'a865479a47cdd4ba64a8b74f90fd0f1823a9914c90f245d4a4ae20566918fc00',
    'Renderer/TextureSamplerDescriptor.hpp': 'adc68ba5b14f28e1d9829b719bb05fb959a41aed8105cfc615865c6baf9fc7cf',
    'Renderer/Texture.hpp': '762917b61eeb4b692d477e7c906d51d5798439e1bdb3aab9c4e030ee0f4dae86',
    'Renderer/Sampler.hpp': '2e99730e688f6b74568871ab364e34b35c57bb55094164bcd881369896084678',
}

# All nineteen guarded methods match prepared source29. The five differences
# from the archived pre43 contract concern entropy, texture upload, shader
# initialization and frame-random replay; selected images remain runtime inputs.
# Keep the archived pins unchanged and qualify only this exact release31 tuple.
CORE_2331_BODY_HASHES = {**BODY_HASHES,
    'TextureManager.GetRandomTexture': '427f40c9a0bf6c45bd74d6a433936a57b45a7999394e541a4859e9eb0f495025',
    'TextureManager.LoadTexture': 'f41c1a0bd50d17d784067bdba0700c2dea7aa4a09aa058ea71ee80ed9e36c20e',
    'MilkdropPreset.Initialize': 'e9b09519fa583dd0263f2657eab74a1cbc9701c043b1235064e2889153f16bad',
    'TextureManager.Preload': '99f526cb3a5aa80fa788687170ff3d053a6201be2fa9b8de1c26b626363b6e58',
    'MilkdropShader.LoadVariables': 'fc5acc978feafffa6d65df74970d40d69209984d024fcc7cea4509393e5b52d3',
}
CORE_2331_SOURCE_FILES = {**SOURCE_FILES,
    'MilkdropPreset/PerPixelMesh.hpp': '61a06eef48c9ee96fc7451ff17596c816906d5ca6a160769d6c792c85b1fb0d6',
    'MilkdropPreset/MilkdropShader.hpp': 'c777e79ffc90368418c786f04a08613410ff1803b61d18a4f7f8bbdf6dbc10de',
    'MilkdropPreset/PresetState.hpp': '7c0bbf2c7baad0aa8f6d257820745bd376022bc57b602b45f1267a79ea86cf89',
    'Renderer/TextureManager.hpp': '021e053984546581fa80ea085b5beca1d66f1a09e9294cd0de296f0fbae87a15',
    'Renderer/Texture.hpp': 'b8c1b2d2b188470522e39f4f0153637dc2c9460f079e12f7befed09c4e07efde',
    'Renderer/Sampler.hpp': '7c3a547080e5677ee1584fa04ef0b6a5709402e75fb47cd29a5f24f99af78302',
}


def native_contract(engine: Path,*,identity=None):
    """Stamp recognized source bodies; older/changed implementations fail closed."""
    hashes = {}
    try:
        files = {path: hashlib.sha256((engine/'src/libprojectM'/path).read_bytes()).hexdigest()
                 for path in SOURCE_FILES}
        for name, (path, signature, _) in METHODS.items():
            source = (engine/'src/libprojectM'/path).read_text()
            start = source.index(signature)
            body = source[start:source.index('\n}', start)+2]
            hashes[name] = hashlib.sha256(body.encode()).hexdigest()
    except (OSError, ValueError, UnicodeError):
        return None
    if hashes == BODY_HASHES and files == SOURCE_FILES:
        if identity in (CORE_2331_ENGINE,CORE_2334_ENGINE):return None
        return {'policy': POLICY, 'body_sha256': hashes, 'file_sha256': files}
    if hashes == CORE_2331_BODY_HASHES and files == CORE_2331_SOURCE_FILES:
        selected=CORE_2331_ENGINE if identity is None else identity
        if selected not in (CORE_2331_ENGINE,CORE_2334_ENGINE):return None
        return {'policy': POLICY, 'engine': dict(selected),
                'body_sha256': hashes, 'file_sha256': files}
    return None


def recognized(value):
    if not isinstance(value, dict) or value.get('policy') != POLICY:
        return False
    if value.get('engine') in (CORE_2331_ENGINE,CORE_2334_ENGINE):
        return (value.get('body_sha256') == CORE_2331_BODY_HASHES and
                value.get('file_sha256') == CORE_2331_SOURCE_FILES)
    return ('engine' not in value and value.get('body_sha256') == BODY_HASHES and
            value.get('file_sha256') == SOURCE_FILES)


def verified_contract(source, *, stage, profile, compatibility):
    """Establish typed slot inputs only for the matching accepted source/profile."""
    if not isinstance(source, dict) or not isinstance(compatibility, dict):
        return None
    if stage not in {'warp', 'composite'} or profile not in {'glsl330', 'gles300'}:
        return None
    sections = source.get('sections')
    if not isinstance(sections, dict):
        return None
    section = sections.get('warp_' if stage == 'warp' else 'comp_', {})
    if not isinstance(section, dict):
        return None
    code = section.get('source')
    if not isinstance(code, str) or section.get('status') != 'parsed':
        return None
    parser = source.get('parser_inputs', {})
    translation = compatibility.get('translation', {})
    if not isinstance(parser, dict) or not isinstance(translation, dict):
        return None
    contract = parser.get('random_binding_contract')
    archive = parser.get('engine_archive_sha256')
    if (not recognized(contract) or translation.get('random_binding_contract') != contract or
            not isinstance(archive, str) or re.fullmatch('[0-9a-f]{64}', archive) is None or
            translation.get('engine_archive_sha256') != archive or
            translation.get('sampler_reference_body_sha256') != BODY_HASHES['MilkdropShader.GetReferencedSamplers']):
        return None
    if contract.get('engine') in (CORE_2331_ENGINE,CORE_2334_ENGINE):
        if parser.get('engine') != contract['engine'] or translation.get('engine') != contract['engine']:
            return None
    elif parser.get('engine') in (CORE_2331_ENGINE,CORE_2334_ENGINE) or translation.get('engine') in (CORE_2331_ENGINE,CORE_2334_ENGINE):
        return None
    request = compatibility.get('request', {})
    if not isinstance(request, dict):
        return None
    digest = hashlib.sha256(code.encode()).hexdigest()
    if (compatibility.get('source_sha256') != digest or compatibility.get('offline_accepted') is not True or
            request.get('code') != code or request.get('stage') != stage or request.get('profile') != profile or
            translation.get('status') != 'translated' or translation.get('stage') != stage or
            translation.get('profile') != profile):
        return None
    references = translation.get('referenced_samplers')
    if not isinstance(references, list) or not references or not all(isinstance(n, str) for n in references):
        return None
    allowed = {'sampler_'+name for name in references}
    size_inputs = {}
    for name in references:
        base = texture_settings('sampler_'+name)['texture']
        random = re.fullmatch(r'rand([0-9]{2})(?:_[A-Za-z0-9_]+)?', base, re.I)
        if random is not None and int(random[1]) <= 15:
            canonical = f'texsize_rand{int(random[1]):02d}'
            size_inputs['texsize_'+base] = canonical
            if len(base)>7: size_inputs['texsize_'+base[:6]] = canonical
        if re.fullmatch(r'rand[0-9]{2}_[A-Za-z0-9_]+', base, re.I):
            offset = 3 if len(name)>3 and name[2]=='_' else 0
            allowed.add('sampler_'+name[:offset+6])
    requested = request.get('samplers')
    if not isinstance(requested, dict):
        return None
    inputs = {}
    for alias, dtype in requested.items():
        if not isinstance(alias, str):
            return None
        match = re.fullmatch(r'sampler_(?:[A-Za-z]{2}_)?rand([0-9]{2})(?:_([A-Za-z0-9_]+))?', alias, re.I)
        if match is None:
            if re.match(r'sampler_(?:[A-Za-z]{2}_)?rand[0-9]', alias, re.I):
                return None
            continue
        slot = int(match[1])
        if slot > 15 or dtype != 'sampler2D' or alias not in allowed:
            return None
        inputs[alias] = {'slot': slot, 'texture_input': f'rand{slot:02d}',
            'uploaded_texsize_input': f'texsize_rand{slot:02d}',
            'selection_epoch': None, 'selected_asset': None, 'uploaded_dimensions': None,
            'lifetime': 'one PresetState instance; shared across stages and shader reloads',
            'filename_filter_hint': (match[2] or '').lower(), 'unit': None,
            'required_target': 'GL_TEXTURE_2D', 'conditional_on_valid_descriptor': True}
    if not inputs:
        return None
    sizes = request.get('texture_sizes')
    if (not isinstance(sizes, list) or not all(isinstance(name, str) for name in sizes) or
            any(re.match(r'texsize_(?:[A-Za-z]{2}_)?rand[0-9]', name, re.I) and name not in size_inputs
                for name in sizes)):
        return None
    result = {'policy': POLICY, 'basis': 'native source contract; conditional runtime inputs',
        'profile': profile, 'samplers': dict(requested), 'random_inputs': inputs,
        'main_binding_policy': 'projectmtv-core-2.2.6-v1',
        'texsize_inputs': size_inputs,
        'selected_assets': None, 'native_driver_verified': False, 'appearance_verified': False,
        'runtime_requirements': [
            'Supply a valid loaded GL_TEXTURE_2D image and uploaded texsize for each referenced slot.',
            'Keep each slot image/texsize fixed for one PresetState selection epoch across both stages.',
            'Honor alias modes and filtered-first lexical selection; an existing slot wins over later filters.',
            'Missing/prefix-miss/failed loads, target mismatches and native fallback remain unresolved.',
            'Source typing supplies no actual GL unit, asset hash or appearance certification.'],
        'engine_archive_sha256': archive, 'body_sha256': dict(contract['body_sha256']),
        'file_sha256': dict(contract['file_sha256'])}
    if 'engine' in contract:
        result['engine'] = dict(contract['engine'])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--identity-file',type=Path)
    args = parser.parse_args()
    identity=None if args.identity_file is None else json.loads(args.identity_file.read_text())
    print(json.dumps(native_contract(args.engine,identity=identity), sort_keys=True))
