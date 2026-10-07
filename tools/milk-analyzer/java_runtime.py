"""Bind executed DEX bytes to an AAR through a reproducible local D8 build.

The build manifest describes compiler/platform/helper bytecode inputs. Checks
reconstruct DEX from the supplied AAR, rather than trusting a claimed relationship
between independently hashed classes and runtime output. No device is accessed.
"""
import argparse
from contextlib import contextmanager
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _bytes_sha(data):
    return hashlib.sha256(data).hexdigest()


@contextmanager
def snapshot_runtime(args,relative_files):
    """Keep the verified and subsequently deployed runtime on private paths."""
    with tempfile.TemporaryDirectory(prefix='projectmtv-runtime-') as temporary:
        root=Path(temporary);runtime=root/'runtime';runtime.mkdir()
        names=set(relative_files)
        proof=args.runtime/'runtime-java.json'
        proof_bytes=proof.read_bytes() if proof.is_file() else None
        if proof_bytes is not None:
            names.update(json.loads(proof_bytes).get('helper_classes',{}))
        for name in sorted(names):
            source=_bound_path(args.runtime,name)
            target=_bound_path(runtime,name);target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(source.read_bytes())
        if proof_bytes is not None:(runtime/'runtime-java.json').write_bytes(proof_bytes)
        frozen=copy.copy(args)
        frozen.runtime=runtime;frozen.aar=root/'core.aar';frozen.pcm=root/'input.f32'
        frozen.aar.write_bytes(args.aar.read_bytes());frozen.pcm.write_bytes(args.pcm.read_bytes())
        yield frozen


def write_runtime_proof(aar,runtime,dex_path,d8,platform,min_api,helpers):
    """Record build inputs; verification independently reconstructs the DEX."""
    runtime=Path(runtime)
    if type(min_api) is not int or not 21<=min_api<=34:
        raise ValueError('Supported explicit Java runtime API required')
    bound={}
    for helper in helpers:
        helper=Path(helper).resolve()
        name=str(helper.relative_to(runtime.resolve()))
        if helper.suffix!='.class':raise ValueError('Java helper class required')
        bound[name]=_sha(helper)
    if not bound:raise ValueError('Bound Java helper bytecode required')
    with zipfile.ZipFile(aar) as archive:classes=archive.read('classes.jar')
    proof={'schema_version':1,'classes_jar_sha256':_bytes_sha(classes),'dex_sha256':_sha(dex_path),
           'd8_jar_path':str(Path(d8).resolve()),'d8_jar_sha256':_sha(d8),
           'android_jar_path':str(Path(platform).resolve()),'android_jar_sha256':_sha(platform),
           'min_api':min_api,'helper_classes':bound}
    (runtime/'runtime-java.json').write_text(json.dumps(proof,indent=2,sort_keys=True)+'\n')
    return proof


def _bound_path(root,relative):
    if not isinstance(relative,str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('relative Java helper path required')
    path=(root/relative).resolve()
    if not path.is_relative_to(root.resolve()):raise ValueError('Java helper escapes runtime directory')
    return path


def verify_runtime_classes(aar,runtime,dex_path):
    runtime=Path(runtime);dex_path=Path(dex_path)
    proof_path=runtime/'runtime-java.json'
    if not proof_path.is_file():raise ValueError('Runtime Java build proof missing; prepare a source-bound DEX')
    proof_bytes=proof_path.read_bytes();proof=json.loads(proof_bytes)
    if proof.get('schema_version')!=1:raise ValueError('Unsupported runtime Java proof schema')
    aar_bytes=Path(aar).read_bytes()
    with zipfile.ZipFile(io.BytesIO(aar_bytes)) as archive:
        try:classes=archive.read('classes.jar')
        except KeyError as error:raise ValueError('Supplied AAR has no classes.jar') from error
    classes_sha=hashlib.sha256(classes).hexdigest()
    if proof.get('classes_jar_sha256')!=classes_sha:raise ValueError('Runtime Java classes do not belong to supplied AAR')
    dex_sha=_sha(dex_path)
    if proof.get('dex_sha256')!=dex_sha:raise ValueError('Runtime DEX differs from build proof')
    d8=Path(proof.get('d8_jar_path',''));platform=Path(proof.get('android_jar_path',''))
    if not d8.is_file() or not platform.is_file():raise ValueError('Declared Java compiler/platform input missing')
    d8_bytes=d8.read_bytes();platform_bytes=platform.read_bytes()
    if _bytes_sha(d8_bytes)!=proof.get('d8_jar_sha256'):raise ValueError('Declared D8 compiler input differs')
    if _bytes_sha(platform_bytes)!=proof.get('android_jar_sha256'):raise ValueError('Declared Android platform input differs')
    api=proof.get('min_api')
    if type(api) is not int or not 21<=api<=34:raise ValueError('Supported explicit Java runtime API required')
    helpers=proof.get('helper_classes')
    if not isinstance(helpers,dict) or not helpers:raise ValueError('Bound Java helper bytecode required')
    bound=[]
    for name,expected in sorted(helpers.items()):
        path=_bound_path(runtime,name)
        if path.suffix!='.class' or not path.is_file():raise ValueError('Java helper bytecode missing: '+name)
        data=path.read_bytes()
        if _bytes_sha(data)!=expected:
            raise ValueError('Java helper bytecode differs: '+name)
        bound.append((name,data))
    java=shutil.which('java')
    if java is None:raise ValueError('JDK required to verify source-bound runtime classes')
    with tempfile.TemporaryDirectory(prefix='projectmtv-dex-proof-') as temporary:
        root=Path(temporary);jar=root/'published-classes.jar';jar.write_bytes(classes)
        compiler=root/'d8.jar';compiler.write_bytes(d8_bytes)
        android=root/'android.jar';android.write_bytes(platform_bytes)
        paths=[]
        for name,data in bound:
            helper=root/'helpers'/name;helper.parent.mkdir(parents=True,exist_ok=True)
            helper.write_bytes(data);paths.append(helper)
        output=root/'dex';output.mkdir()
        command=[java,'-cp',str(compiler),'com.android.tools.r8.D8','--min-api',str(api),
                 '--lib',str(android),'--output',str(output),str(jar),*[str(p) for p in paths]]
        process=subprocess.run(command,capture_output=True,text=True,timeout=60)
        if process.returncode:raise ValueError('Runtime DEX reconstruction failed: '+process.stderr[:2000])
        files=sorted(output.glob('*.dex'))
        if len(files)!=1 or files[0].name!='classes.dex':raise ValueError('Single reconstructed DEX required')
        reconstructed=_sha(files[0])
    if reconstructed!=dex_sha:raise ValueError('Runtime DEX is not reproducible from supplied AAR/classes inputs')
    return {'policy':'published-aar-reproduced-dex-v1','classes_jar_sha256':classes_sha,
            'aar_sha256':_bytes_sha(aar_bytes),
            'dex_sha256':dex_sha,'reconstructed_dex_sha256':reconstructed,
            'd8_jar_sha256':proof['d8_jar_sha256'],'android_jar_sha256':proof['android_jar_sha256'],
            'helper_classes_sha256':dict(helpers),'min_api':api,'proof_sha256':_bytes_sha(proof_bytes)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('aar','runtime','dex','d8-jar','android-jar'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--min-api',type=int,required=True)
    parser.add_argument('--helper',type=Path,action='append',required=True)
    args=parser.parse_args()
    write_runtime_proof(args.aar,args.runtime,args.dex,args.d8_jar,args.android_jar,args.min_api,args.helper)
    print(json.dumps(verify_runtime_classes(args.aar,args.runtime,args.dex),indent=2,sort_keys=True))


if __name__=='__main__':main()
