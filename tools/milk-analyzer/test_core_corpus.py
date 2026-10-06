import json
import pytest
import sys
import zipfile
import core_corpus

from core_corpus import atomic_json


def test_atomic_result_rejects_nonfinite_scores_without_overwriting_valid_result(tmp_path):
    path=tmp_path/'result.json'
    atomic_json(path,{'score':30,'status':'scored'})
    with pytest.raises(ValueError):atomic_json(path,{'score':float('nan')})
    assert json.loads(path.read_text())=={'score':30,'status':'scored'}


def test_result_update_writes_complete_replacement(tmp_path):
    path=tmp_path/'result.json'
    atomic_json(path,{'status':'unscored','reason':'missing'})
    atomic_json(path,{'status':'scored','score':42})
    assert json.loads(path.read_text())=={'status':'scored','score':42}
    assert not path.with_suffix('.json.tmp').exists()


@pytest.mark.parametrize('library', [b'stale-v7-library', b'arm64-library'])
def test_cli_rejects_runtime_from_another_aar_before_device_access(tmp_path,monkeypatch,library):
    aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as archive:
        archive.writestr('jni/armeabi-v7a/libprojectmtv.so',b'published-v7-library')
        archive.writestr('jni/arm64-v8a/libprojectmtv.so',b'arm64-library')
    runtime=tmp_path/'runtime'
    (runtime/'jni/armeabi-v7a').mkdir(parents=True)
    (runtime/'dex').mkdir()
    (runtime/'jni/armeabi-v7a/libprojectmtv.so').write_bytes(library)
    (runtime/'dex/classes.dex').write_bytes(b'dex')
    (runtime/'libbackendclock.so').write_bytes(b'clock')
    pcm=tmp_path/'input.f32';pcm.write_bytes(b'pcm')
    model=tmp_path/'model.json';model.write_text(json.dumps({'model':{}}))
    output=tmp_path/'scores'
    monkeypatch.setattr(sys,'argv',['core_corpus.py','--aar',str(aar),
        '--runtime',str(runtime),'--pcm',str(pcm),'--model',str(model),
        '--output',str(output),'--device','test-owned-device'])
    def device_access(*args,**kwargs):
        pytest.fail('A mismatched AAR/runtime pair reached adb')
    monkeypatch.setattr(core_corpus.subprocess,'check_output',device_access)
    with pytest.raises(ValueError,match='Runtime library.*AAR'):
        core_corpus.main()
    assert not (output/'run-identity.json').exists()


def test_matching_runtime_library_is_bound_to_exact_aar_abi(tmp_path):
    import hashlib
    aar=tmp_path/'core.aar';library=tmp_path/'libprojectmtv.so'
    library.write_bytes(b'published-v7-library')
    with zipfile.ZipFile(aar,'w') as archive:
        archive.writestr('jni/armeabi-v7a/libprojectmtv.so',library.read_bytes())
    assert core_corpus.verify_runtime_library(aar,library)==hashlib.sha256(library.read_bytes()).hexdigest()


def test_missing_required_aar_abi_cannot_use_another_architecture(tmp_path):
    aar=tmp_path/'core.aar';library=tmp_path/'libprojectmtv.so'
    library.write_bytes(b'arm64-library')
    with zipfile.ZipFile(aar,'w') as archive:
        archive.writestr('jni/arm64-v8a/libprojectmtv.so',library.read_bytes())
    with pytest.raises(ValueError,match='no armeabi-v7a'):
        core_corpus.verify_runtime_library(aar,library)
