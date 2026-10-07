"""Owned-emulator executor for the sealed numerical operator learning retest."""
import copy
import uuid
import hashlib
import json
import shlex
import subprocess
from pathlib import Path

import numpy as np


def verify_runtime_hashes(identity, observed):
    names={'published-core.aar':'aar_sha256','libprojectmtv.so':'native_sha256',
           'classes.dex':'classes_dex_sha256','motion-operator.dex':'operator_dex_sha256'}
    for name,key in names.items():
        if observed.get(name)!=identity.get(key):
            raise ValueError('Sampler runtime does not match qualified identity: '+name)

def verify_consumed_inputs(metadata, *, map_sha256, queries_sha256, output_sha256):
    for name,value in [('physical_map_sha256',map_sha256),
            ('input_queries_sha256',queries_sha256),('output_sha256',output_sha256)]:
        if metadata.get(name)!=value:
            raise ValueError('Sampler consumed input/output identity mismatch: '+name)

class Executor:
    def __init__(self, *, directory, adb, serial, owner_pid, owner_avd, remote, identity, deployment):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=False)
        self.remote=remote
        self.adb=str(adb)
        self.serial=serial;self.avd=owner_avd;self.pid=owner_pid
        self.identity=copy.deepcopy(identity)
        self.deployment=copy.deepcopy(deployment)
        self.namespace=uuid.uuid4().hex
        self.source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        if self.identity.get('executor_source_sha256')!=self.source_sha256:
            raise ValueError('Sampler executor source identity mismatch')
        self.index=0
    def _owned(self):
        command=subprocess.check_output(['ps','-p',str(self.pid),'-o','command='],text=True,timeout=10)
        if self.avd not in command or '-port 5596' not in command:raise ValueError('Owned sampler emulator changed')
        r=subprocess.run([self.adb,'-s',self.serial,'emu','avd','name'],capture_output=True,text=True,check=True,timeout=15)
        if r.stdout.splitlines()[0].strip()!=self.avd:raise ValueError('Sampler AVD identity changed')
    def _run(self,*args):
        self._owned()
        return subprocess.run([self.adb,'-s',self.serial,*args],capture_output=True,text=True,check=True,timeout=30)
    def __call__(self,field,queries,**settings):
        if settings!={'wrap':False,'linear':True,'origin':'bottom'}:raise ValueError('Sampler settings changed')
        if hashlib.sha256(Path(__file__).read_bytes()).hexdigest()!=self.source_sha256:
            raise ValueError('Sampler executor source changed')
        observed={}
        for name in ['classes.dex','libprojectmtv.so','published-core.aar']:
            observed[name]=self._run('shell','sha256sum',self.remote+'/'+name).stdout.split()[0]
            if observed[name]!=self.deployment['sha256'][name]:raise ValueError('Published sampler context changed')
        observed['motion-operator.dex']=self._run('shell','sha256sum',self.remote+'/motion-operator.dex').stdout.split()[0]
        verify_runtime_hashes(self.identity,observed)
        folder=self.directory/f'{self.index:06d}';folder.mkdir();prefix=self.remote+f'/measured-motion-{self.namespace}-{self.index:06d}';self.index+=1
        physical=np.asarray(field[::-1],dtype='<f4').copy();queries=np.asarray(queries,dtype='<f4').copy()
        physical.tofile(folder/'physical-map.f32');queries.tofile(folder/'queries.f32')
        for local,suffix in [('physical-map.f32','.map'),('queries.f32','.query')]:
            self._run('push',str(folder/local),prefix+suffix)
            if self._run('shell','sha256sum',prefix+suffix).stdout.split()[0]!=hashlib.sha256((folder/local).read_bytes()).hexdigest():raise ValueError('Sampler upload changed')
        h,w=field.shape[:2]
        cmd=shlex.join(['env','CLASSPATH='+self.remote+'/motion-operator.dex:'+self.remote+'/classes.dex','LD_LIBRARY_PATH='+self.remote,'app_process','-Djava.library.path='+self.remote,'/system/bin','nl.neerdael.projectm.analysis.MotionSamplerOperator',self.remote+'/libprojectmtv.so',str(w),str(h),prefix+'.map',prefix+'.query',prefix+'.output',prefix+'.meta'])
        result=self._run('shell',cmd);(folder/'stdout.txt').write_text(result.stdout);(folder/'stderr.txt').write_text(result.stderr)
        self._run('pull',prefix+'.output',str(folder/'output.f32'));self._run('pull',prefix+'.meta',str(folder/'metadata.json'))
        metadata=json.loads((folder/'metadata.json').read_text())
        for key in ['renderer','gl_version','core_version']:
            if metadata[key]!=self.identity[key]:raise ValueError('Sampler GL/core context changed: '+key)
        if hashlib.sha256(metadata['vertex_shader'].encode()).hexdigest()!=self.identity['vertex_shader_sha256']:raise ValueError('Sampler shader changed')
        if hashlib.sha256(metadata['fragment_shader'].encode()).hexdigest()!=self.identity['fragment_shader_sha256']:raise ValueError('Sampler shader changed')
        if metadata['queries']!=len(queries) or metadata['width']!=w or metadata['height']!=h:raise ValueError('Sampler request shape changed')
        for local,suffix in [('output.f32','.output'),('metadata.json','.meta')]:
            if self._run('shell','sha256sum',prefix+suffix).stdout.split()[0]!=hashlib.sha256((folder/local).read_bytes()).hexdigest():raise ValueError('Sampler output transport changed')
        values=np.fromfile(folder/'output.f32',dtype='<f4').reshape(-1,2)
        verify_consumed_inputs(metadata,map_sha256=hashlib.sha256(physical.tobytes()).hexdigest(),
            queries_sha256=hashlib.sha256(queries.tobytes()).hexdigest(),output_sha256=hashlib.sha256(values.tobytes()).hexdigest())
        proof=dict(identity=self.identity,executor_source_sha256=self.source_sha256,remote_namespace=self.namespace,core_frame_serial_before=metadata['core_frame_serial_before'],core_frame_serial_after=metadata['core_frame_serial_after'],preset_draws=metadata['preset_draws'],input_map_sha256=hashlib.sha256(np.asarray(field,dtype='<f4').tobytes()).hexdigest(),input_queries_sha256=hashlib.sha256(queries.tobytes()).hexdigest(),output_sha256=hashlib.sha256(values.tobytes()).hexdigest(),physical_map_sha256=metadata['physical_map_sha256'],metadata=metadata,artifact_directory=str(folder))
        return values,proof
