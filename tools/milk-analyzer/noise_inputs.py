"""Procedural texture inputs from native source generation, never rendered frames.

Packed words retain the target implementation's random generator and smoothing.
Upload format is explicit: desktop BGRA and GLES RGBA interpret the same bytes
differently. This module does not imply identical RNG output across platforms.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from spatial import sample2d,sample3d


def decode_words(payload:bytes,dimensions,upload_format:str)->np.ndarray:
    if upload_format not in {'RGBA','BGRA'}:raise ValueError('explicit RGBA/BGRA upload format required')
    if len(dimensions)!=3 or any(type(n) is not int or n<=0 for n in dimensions):
        raise ValueError('three positive physical texture dimensions required')
    width,height,depth=dimensions
    if len(payload)!=width*height*depth*4:raise ValueError('procedural input byte size mismatch')
    words=np.frombuffer(payload,dtype='<u4')
    shifts=[0,8,16,24] if upload_format=='RGBA' else [16,8,0,24]
    channels=((words[:,None]>>np.array(shifts,dtype=np.uint32))&255).astype(np.float32)/255
    shape=(height,width,4) if depth==1 else (depth,height,width,4)
    return channels.reshape(shape)


def validate_noise_clock(bank,contract:dict|None,*,profile:str)->int|None:
    """Bind declared Android procedural inputs to their initialization clock.

    Android libc++ system_clock counts microseconds, independently of the
    declared render-frame clock. Other platform periods require separate policy.
    """
    if not contract:return None
    if contract.get('policy')!='core-thread-inputs-v1' and 'noise_initialization_clock_ns' not in contract:return None
    if 'noise_initialization_clock_ns' not in contract:
        raise ValueError('declared Android noise initialization clock required')
    if (contract.get('policy')!='core-thread-inputs-v1' or profile!='gles300' or
            contract.get('noise_clock_period')!='android-libcxx-microseconds-v1'):
        raise ValueError('explicit supported Android noise clock policy required')
    clock=contract['noise_initialization_clock_ns']
    if type(clock) is not int or not 0<=clock<2**63:
        raise ValueError('noise initialization clock must be nonnegative int64 nanoseconds')
    seed=(clock//1000)&0xffffffff
    if bank.manifest.get('seed_policy')!='production-clock-seed-v1':
        raise ValueError('production procedural noise seed policy required for paired clock inputs')
    actual=bank.manifest.get('seed')
    if type(actual) is not int or not 0<=actual<2**32 or actual!=seed:
        raise ValueError('procedural noise seed differs from declared initialization clock')
    if any(row.get('generator_seed')!=seed for row in bank.manifest.get('textures',{}).values()):
        raise ValueError('procedural noise texture generator seed differs from declared clock')
    return seed


class NoiseBank:
    def __init__(self,directory:Path,*,upload_format:str|None=None):
        root=Path(directory).resolve();self.manifest=json.loads((root/'manifest.json').read_text())
        if self.manifest.get('schema_version')!=1 or self.manifest.get('uses_rendered_reference') is not False:
            raise ValueError('source-generated procedural manifest required')
        if self.manifest.get('packed_word_encoding')!='uint32 little endian':raise ValueError('unsupported packed noise encoding')
        self.upload_format=upload_format or self.manifest['native_upload_format'];self.textures={}
        for name,row in self.manifest['textures'].items():
            path=(root/row['file']).resolve()
            if path.parent!=root:raise ValueError('procedural input must reside in its declared directory')
            payload=path.read_bytes()
            if hashlib.sha256(payload).hexdigest()!=row['sha256']:raise ValueError('procedural input hash mismatch')
            self.textures[name]=decode_words(payload,row['dimensions'],self.upload_format)

    def uniforms(self)->dict:
        return {'texsize_'+name:[row['dimensions'][0],row['dimensions'][1],1/row['dimensions'][0],1/row['dimensions'][1]]
                for name,row in self.manifest['textures'].items()}

    def sample(self,detail:dict,coordinates:np.ndarray,*,sampling_profile='portable')->np.ndarray:
        from unorm_sampler import sampler_2d
        sample=sampler_2d(sampling_profile)
        name=detail['canonical_texture'];policy=detail['sampling_policy']
        if name not in self.textures:raise ValueError('procedural texture input missing: '+name)
        if policy.get('wrap') is None or policy.get('linear') is None:raise ValueError('procedural sampler policy unresolved')
        texture=self.textures[name]
        if texture.ndim==4:
            if sampling_profile!='portable':raise ValueError('declared texture profile supports only2D inputs')
            return sample3d(texture,coordinates,wrap=policy['wrap'],linear=policy['linear'])
        # Raw generator row0 is normalized GL-v0; sample2d's top-origin option
        # maps coordinates directly to array rows without a framebuffer flip.
        return sample(texture,coordinates,wrap=policy['wrap'],linear=policy['linear'],origin='top')
