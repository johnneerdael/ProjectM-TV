"""A runtime's DEX must reproduce from the supplied AAR and bound build inputs."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import pytest


SDK=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT',Path.home()/'Library/Android/sdk')))


def verify(aar,root,dex):
    return importlib.import_module('java_runtime').verify_runtime_classes(aar,root,dex)


def test_missing_proof_is_not_accepted_as_an_independent_dex_hash(tmp_path):
    aar=tmp_path/'core.aar';runtime=tmp_path/'runtime';runtime.mkdir()
    with zipfile.ZipFile(aar,'w') as z:z.writestr('classes.jar',b'published classes')
    dex=runtime/'classes.dex';dex.write_bytes(b'stale dex')
    with pytest.raises(ValueError,match='proof'):
        verify(aar,runtime,dex)


def test_edited_dex_cannot_borrow_a_matching_classes_jar(tmp_path):
    r=tmp_path/'runtime';r.mkdir();dex=r/'classes.dex';dex.write_bytes(b'stale')
    aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as z:z.writestr('classes.jar',b'new classes')
    (r/'runtime-java.json').write_text(json.dumps({'schema_version':1,
        'classes_jar_sha256':hashlib.sha256(b'new classes').hexdigest(),
        'dex_sha256':hashlib.sha256(b'other dex').hexdigest()}))
    with pytest.raises(ValueError,match='DEX'):
        verify(aar,r,dex)


@pytest.mark.parametrize('replace_inputs',[False,True])
def test_real_bound_dex_is_rebuilt_and_stale_dex_fails_even_with_updated_manifest(tmp_path,monkeypatch,replace_inputs):
    candidates=sorted((SDK/'build-tools').glob('*/d8'))
    d8=candidates[-1] if candidates else SDK/'build-tools/missing/d8'
    platform=SDK/'platforms/android-34/android.jar'
    java=Path(shutil.which('javac') or '')
    if not d8.is_file() or not platform.is_file() or not java.is_file():
        pytest.skip('installed Android D8/JDK inputs required')
    r=tmp_path/'runtime';r.mkdir();classes=r/'helper-classes';classes.mkdir()
    source=r/'Host.java';source.write_text('public class Host { public static int value() { return 3; } }')
    subprocess.run([str(java),'--release','8','-d',str(classes),str(source)],check=True,capture_output=True)
    aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as z:z.writestr('classes.jar',zipfile_empty())
    jar=r/'classes.jar';jar.write_bytes(zipfile_empty());dex=r/'classes.dex'
    subprocess.run([str(d8),'--min-api','21','--lib',str(platform),'--output',str(r),str(jar),str(classes/'Host.class')],check=True,capture_output=True)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    proof={'schema_version':1,'classes_jar_sha256':sha(jar),'dex_sha256':sha(dex),
        'd8_jar_path':str(d8.parent/'lib/d8.jar'),'d8_jar_sha256':sha(d8.parent/'lib/d8.jar'),
        'android_jar_path':str(platform),'android_jar_sha256':sha(platform),
        'min_api':21,'helper_classes':{'helper-classes/Host.class':sha(classes/'Host.class')}}
    (r/'runtime-java.json').write_text(json.dumps(proof))
    if replace_inputs:
        original_run=subprocess.run
        helper=classes/'Host.class'
        def changed_inputs(command,**kwargs):
            helper.write_bytes(b'replaced bytecode')
            (r/'runtime-java.json').write_text('{}')
            return original_run(command,**kwargs)
        monkeypatch.setattr(subprocess,'run',changed_inputs)
        original_proof_sha=sha(r/'runtime-java.json')
        identity=verify(aar,r,dex)
        assert identity['proof_sha256']==original_proof_sha
        assert identity['helper_classes_sha256']==proof['helper_classes']
        return
    assert verify(aar,r,dex)['reconstructed_dex_sha256']==sha(dex)
    dex.write_bytes(b'stale classes with edited manifest');proof['dex_sha256']=sha(dex)
    (r/'runtime-java.json').write_text(json.dumps(proof))
    with pytest.raises(ValueError,match='reproduc'):
        verify(aar,r,dex)


def zipfile_empty():
    import io
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w'):pass
    return out.getvalue()


def test_runtime_snapshot_keeps_original_deployment_bytes(tmp_path):
    from types import SimpleNamespace
    from java_runtime import snapshot_runtime
    root=tmp_path/'runtime';root.mkdir()
    originals={'classes.dex':b'dex','libprojectmtv.so':b'native','libbackendclock.so':b'clock'}
    for name,data in originals.items():(root/name).write_bytes(data)
    aar=tmp_path/'core.aar';aar.write_bytes(b'aar')
    pcm=tmp_path/'pcm';pcm.write_bytes(b'pcm')
    args=SimpleNamespace(runtime=root,aar=aar,pcm=pcm)
    with snapshot_runtime(args,tuple(originals)) as frozen:
        for name in originals:(root/name).write_bytes(b'replaced')
        aar.write_bytes(b'replaced');pcm.write_bytes(b'replaced')
        assert frozen.aar.read_bytes()==b'aar'
        assert frozen.pcm.read_bytes()==b'pcm'
        for name,data in originals.items():assert (frozen.runtime/name).read_bytes()==data
        snapshot_path=frozen.runtime
    assert not snapshot_path.exists()


def test_manifest_writer_records_exact_inputs(tmp_path):
    from java_runtime import write_runtime_proof
    root=tmp_path/'runtime';(root/'helpers').mkdir(parents=True)
    helper=root/'helpers/Host.class';helper.write_bytes(b'helper')
    dex=root/'classes.dex';dex.write_bytes(b'dex')
    d8=tmp_path/'d8.jar';d8.write_bytes(b'compiler')
    platform=tmp_path/'android.jar';platform.write_bytes(b'platform')
    aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as z:z.writestr('classes.jar',b'published')
    write_runtime_proof(aar,root,dex,d8,platform,21,[helper])
    proof=json.loads((root/'runtime-java.json').read_text())
    assert proof['classes_jar_sha256']==hashlib.sha256(b'published').hexdigest()
    assert proof['helper_classes']=={'helpers/Host.class':hashlib.sha256(b'helper').hexdigest()}
    assert proof['dex_sha256']==hashlib.sha256(b'dex').hexdigest()


def test_runtime_snapshot_rejects_parent_components_even_when_source_resolves_inside(tmp_path):
    from types import SimpleNamespace
    from java_runtime import snapshot_runtime
    root=tmp_path/'original';root.mkdir();(root/'Host.class').write_bytes(b'helper')
    (root/'runtime-java.json').write_text(json.dumps({'helper_classes':{'../original/Host.class':'unused'}}))
    aar=tmp_path/'core.aar';aar.write_bytes(b'aar');pcm=tmp_path/'pcm';pcm.write_bytes(b'pcm')
    args=SimpleNamespace(runtime=root,aar=aar,pcm=pcm)
    with pytest.raises(ValueError,match='relative Java helper'):
        with snapshot_runtime(args,()):pytest.fail('parent path accepted by snapshot')
