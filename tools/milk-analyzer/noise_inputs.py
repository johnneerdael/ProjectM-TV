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

    def sample(self,detail:dict,coordinates:np.ndarray)->np.ndarray:
        name=detail['canonical_texture'];policy=detail['sampling_policy']
        if name not in self.textures:raise ValueError('procedural texture input missing: '+name)
        if policy.get('wrap') is None or policy.get('linear') is None:raise ValueError('procedural sampler policy unresolved')
        texture=self.textures[name]
        if texture.ndim==4:return sample3d(texture,coordinates,wrap=policy['wrap'],linear=policy['linear'])
        # Raw generator row0 is normalized GL-v0; sample2d's top-origin option
        # maps coordinates directly to array rows without a framebuffer flip.
        return sample2d(texture,coordinates,wrap=policy['wrap'],linear=policy['linear'],origin='top')
