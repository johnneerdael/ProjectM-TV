"""Explicit deterministic inputs for offline corpus simulation, not native observations."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import numpy as np
from corpus_store import atomic_json,file_hash
from sampling_policy import texture_settings

NOISE_NAMES=('noise_lq','noise_lq_lite','noise_mq','noise_hq','noisevol_lq','noisevol_hq')
IMAGE_SUFFIXES={'.png','.jpg','.jpeg','.tga','.bmp','.dib','.dds'}


def synthetic_pcm(*,frames,fps,seed):
    if type(fps) is not int or fps not in (15,30,60) or type(frames) is not int or frames<1:
        raise ValueError('declared15/30/60 cadence and positive frame count required')
    rng=np.random.default_rng(seed);t=np.arange(frames*(44100//fps),dtype=np.float64)/44100
    beat=np.mod(t,.5);hat=np.mod(t,.25)
    kick=.5*np.exp(-beat*32)*np.sin(2*np.pi*(55*t+2*np.sin(2*np.pi*beat)*np.exp(-beat*40)))
    chord=.10*np.sin(2*np.pi*220*t)+.07*np.sin(2*np.pi*330*t)+.05*np.sin(2*np.pi*440*t)
    high=.10*np.exp(-hat*130)*rng.uniform(-1,1,len(t))
    return np.clip(kick+chord+high,-1,1).astype('<f4')


def texture_index(directory):
    images={}
    for path in sorted(Path(directory).resolve(strict=True).rglob('*')):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:continue
        if path.is_symlink():raise ValueError('symlinked texture input')
        name=path.stem.lower()
        if name in images:raise ValueError('ambiguous source texture name: '+name)
        images[name]={'name':name,'path':str(path),'sha256':file_hash(path)}
    return images


def sampler_request(references):
    result={'sampler_main':'sampler2D'}
    for raw in references:
        name=raw.removeprefix('sampler_');texture=texture_settings(name)['texture'].lower()
        result['sampler_'+name]='sampler3D' if texture.startswith('noisevol_') else 'sampler2D'
        random=re.fullmatch(r'rand(\d{2})(?:_(\w+))?',texture)
        if random and random.group(2):
            prefix=name[:3] if len(name)>3 and name[2]=='_' else ''
            result['sampler_'+prefix+'rand'+random.group(1)]='sampler2D'
    return result


def declared_random_assets(stage_references,images,*,preset_sha,seed):
    slots={};aliases={}
    for stage in ('warp','composite'):
        for raw in sorted(stage_references.get(stage,[])):
            texture=texture_settings(raw)['texture'].lower()
            match=re.fullmatch(r'rand(\d{2})(?:_(\w+))?',texture)
            if not match:continue
            slot='rand'+match.group(1)
            if int(match.group(1))>15:raise ValueError('unsupported random texture slot: '+slot)
            if slot not in slots:
                candidates=[row for name,row in sorted(images.items()) if name.startswith(match.group(2) or '')]
                if not candidates:raise ValueError('random texture prefix has no image: '+str(match.group(2)))
                key=hashlib.sha256(f'{seed}:{preset_sha}:{slot}'.encode()).digest()
                slots[slot]=candidates[int.from_bytes(key[:8],'little')%len(candidates)]
            aliases[texture]=slots[slot]['name'];aliases[slot]=slots[slot]['name']
    return slots,aliases


def prepare_inputs(directory,*,binaries,textures,frames,fps,seed,pcm=None):
    """Called under the controller's single-owner lock; freeze every actual file."""
    from core_backend import jni_pcm_inputs
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    transport=synthetic_pcm(frames=frames,fps=fps,seed=seed) if pcm is None else np.fromfile(pcm,dtype='<f4')
    if len(transport)!=frames*(44100//fps):raise ValueError('PCM must contain exactly the requested mono44100 cadence')
    if not np.all(np.isfinite(transport)) or np.any(np.abs(transport)>1):raise ValueError('finite normalized PCM required')
    transport.tofile(directory/'transport.f32');effective=jni_pcm_inputs(transport);effective.tofile(directory/'effective.f32')
    audio_request={'pcm_path':str((directory/'effective.f32').resolve()),'output':str((directory/'audio.json').resolve()),
        'fps':fps,'frames':frames,'channels':1,'clock_policy':'ideal-frame-fractions-v1',
        'preset_progress_policy':'explicit-zero-placeholder-v1'}
    atomic_json(directory/'audio-request.json',audio_request)
    process=subprocess.run([str(Path(binaries)/'milk-audio-inputs'),str(directory/'audio-request.json')],capture_output=True,text=True,timeout=60)
    if process.returncode:raise ValueError('audio input preparation failed: '+process.stderr.strip())
    noise=directory/'noise';request={'seed':seed,'seed_policy':'production-clock-seed-v1','names':list(NOISE_NAMES),'output':str(noise.resolve())}
    atomic_json(directory/'noise-request.json',request)
    process=subprocess.run([str(Path(binaries)/'milk-noise-inputs'),str(directory/'noise-request.json')],capture_output=True,text=True,timeout=60)
    if process.returncode:raise ValueError('noise input preparation failed: '+process.stderr.strip())
    images=texture_index(textures)
    manifest={'schema_version':1,'signal':'fixed-kick-chord-hat-v1' if pcm is None else 'supplied-mono-f32',
        'fps':fps,'frames':frames,'seed':seed,'textures':images,
        'random_texture_policy':'declared-sha256-slot-selection-v1; stable per preset across stages; not an observed native selection',
        'shader_random_policy':'declared-mt19937-u31-v1; not Android/bionic C-rand parity',
        'cadence_scope':'Actual15fps simulation; not downsampling native30fps state. Progress explicitly0; no coldJNI extrapolation.',
        'files':{p.relative_to(directory).as_posix():file_hash(p) for p in sorted(directory.rglob('*')) if p.is_file() and p.name!='manifest.json'}}
    atomic_json(directory/'manifest.json',manifest);return manifest


def verify_inputs(directory,manifest):
    root=Path(directory)
    for name,sha in manifest['files'].items():
        if file_hash(root/name)!=sha:raise ValueError('prepared input hash changed: '+name)
    for row in manifest['textures'].values():
        if file_hash(row['path'])!=row['sha256']:raise ValueError('texture input changed: '+row['path'])
