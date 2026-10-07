"""Named source texture inputs from pinned decoding and explicit file bindings."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import numpy as np
from spatial import sample2d


def material_input_identity(bank):
    """Identify decoded arrays used by sampling, separately from file provenance."""
    if bank is None:return None
    textures={}
    for name,array in sorted(bank.textures.items()):
        values=np.ascontiguousarray(array,dtype=np.float32)
        if values.ndim not in (3,4) or values.shape[-1]!=4 or not all(values.shape):
            raise ValueError('RGBA material array dimensions required: '+name)
        if not np.all(np.isfinite(values)):raise ValueError('Finite material array required: '+name)
        textures[name]={'shape':list(values.shape),'dtype':'float32',
                        'sha256':hashlib.sha256(memoryview(values)).hexdigest()}
    result={'policy':'effective-texture-arrays-v1','manifest':copy.deepcopy(bank.manifest),'textures':textures}
    if hasattr(bank,'upload_format'):result['upload_format']=bank.upload_format
    if getattr(bank,'noise_bank',None) is not None:
        # MaterialBank delegates procedural sampling to this bank, which can
        # differ from its constructor-time shallow texture dictionary.
        result['procedural_inputs']=material_input_identity(bank.noise_bank)
    return result


class MaterialBank:
    def __init__(self, paths, *, decoder: Path, maximum_texture_size=16384, noise_bank=None):
        self.noise_bank=noise_bank
        self.textures={} if noise_bank is None else dict(noise_bank.textures)
        self.manifest=dict(schema_version=1,uses_rendered_reference=False,images={},
            maximum_texture_size=maximum_texture_size,
            procedural=None if noise_bank is None else noise_bank.manifest)
        payloads=[];names=set()
        for original in paths:
            path=Path(original).resolve();name=path.stem.lower()
            if name in names or name in self.textures:raise ValueError('ambiguous source texture name: '+name)
            names.add(name);payloads.append((name,path,path.read_bytes()))
        decoder=Path(decoder).resolve()
        decoder_sha=hashlib.sha256(decoder.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix='milk-materials-') as directory:
            root=Path(directory);files=[]
            for i,(_,path,raw) in enumerate(payloads):
                frozen=root/(str(i)+path.suffix);frozen.write_bytes(raw)
                files.append(dict(input=str(frozen),output=str(root/(str(i)+'.rgba'))))
            request=root/'request.json';request.write_text(json.dumps(dict(files=files,maximum_texture_size=maximum_texture_size)))
            process=subprocess.run([str(decoder),str(request)],capture_output=True,text=True,timeout=60)
            if hashlib.sha256(decoder.read_bytes()).hexdigest()!=decoder_sha:
                raise ValueError('decoder changed during execution')
            if process.returncode:raise ValueError('source image decoding unresolved: '+process.stderr.strip())
            report=json.loads(process.stdout)
            if report.get('uses_rendered_reference') is not False or len(report['rows'])!=len(payloads):
                raise ValueError('source texture decode response mismatch')
            for (name,path,raw),row in zip(payloads,report['rows']):
                pixels=Path(row['output']).read_bytes();width,height=row['width'],row['height']
                if len(pixels)!=width*height*4:raise ValueError('source image input length mismatch')
                values=np.frombuffer(pixels,dtype=np.uint8).reshape(height,width,4).astype(np.float32)/255
                values.setflags(write=False);self.textures[name]=values
                self.manifest['images'][name]=dict(path=str(path),file_sha256=hashlib.sha256(raw).hexdigest(),
                    pixels_sha256=hashlib.sha256(pixels).hexdigest(),width=width,height=height)
            self.manifest['decoder']={key:value for key,value in report.items() if key!='rows'}
        self.manifest['decoder_binary_sha256']=decoder_sha

    def uniforms(self):
        result={} if self.noise_bank is None else self.noise_bank.uniforms()
        for name,row in self.manifest['images'].items():
            result['texsize_'+name]=[row['width'],row['height'],1/row['width'],1/row['height']]
        return result

    def sample(self, detail, coordinates):
        name=detail['canonical_texture'].lower();policy=detail['sampling_policy']
        if name not in self.textures:raise ValueError('source texture input missing: '+name)
        if name not in self.manifest['images']:
            return self.noise_bank.sample({**detail,'canonical_texture':name},coordinates)
        if policy.get('wrap') is None or policy.get('linear') is None:raise ValueError('source texture sampler unresolved')
        return sample2d(self.textures[name],coordinates,wrap=policy['wrap'],linear=policy['linear'],origin='top')
