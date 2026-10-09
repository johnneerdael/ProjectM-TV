"""Durable incremental exports must survive interruption without false completion."""
import json
from pathlib import Path
import zipfile
import pytest


def inventory(root,count):
    from corpus_store import discover
    root.mkdir()
    for i in range(count):
        (root/f'{i:03d} — colour.milk').write_text('[preset00]\nfDecay=1\n')
    return discover(root)


def test_exact_100_boundary_and_final_partial_zip_pair_names(tmp_path):
    from corpus_store import RunStore
    cases=inventory(tmp_path/'presets',205)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        for case in cases:
            store.complete(case,{'status':'computed','feature_record':{'features':{}}})
        assert len(list((tmp_path/'out').glob('batch-*.zip')))==2
        store.flush(partial=True)
    archives=sorted((tmp_path/'out').glob('batch-*.zip'))
    assert len(archives)==3
    sizes=[]
    for path in archives:
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            manifest=json.loads(z.read('batch-manifest.json'))
            sizes.append(manifest['completed_count'])
            for row in manifest['results']:
                assert 'presets/'+row['preset']['relative_path'] in z.namelist()
                assert 'results/'+str(Path(row['preset']['relative_path']).with_suffix('.json')) in z.namelist()
    assert sizes==[100,100,5]


def test_resume_preserves_terminal_failure_and_rejects_identity_drift(tmp_path):
    from corpus_store import RunStore
    cases=inventory(tmp_path/'presets',3)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        store.complete(cases[0],{'status':'unsupported','feature_record':None,'error':'unknown shader'})
        store.flush(partial=True)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        assert [c['relative_path'] for c in store.pending()]==[c['relative_path'] for c in cases[1:]]
        assert store.counts()['unsupported']==1
    with pytest.raises(ValueError,match='identity'):
        RunStore(tmp_path/'out',{'identity':'changed'},cases,batch_size=100)


def test_output_lock_and_corrupted_result_are_not_silently_accepted(tmp_path):
    from corpus_store import RunStore
    cases=inventory(tmp_path/'presets',1)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        with pytest.raises(RuntimeError,match='already running'):
            RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100)
        store.complete(cases[0],{'status':'computed','feature_record':{}})
    (tmp_path/'out'/'results'/Path(cases[0]['relative_path']).with_suffix('.json')).write_text('{}')
    with pytest.raises(ValueError,match='hash'):
        RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100)


def test_zip_written_before_index_commit_is_reconciled(tmp_path,monkeypatch):
    from corpus_store import RunStore
    cases=inventory(tmp_path/'presets',1)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        store.complete(cases[0],{'status':'computed','feature_record':{}})
        def fail(*args):raise RuntimeError('crash after ZIP')
        monkeypatch.setattr(store,'_record_archive',fail)
        with pytest.raises(RuntimeError,match='crash after ZIP'):store.flush(partial=True)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        assert store.flush(partial=True) is None
        assert len(list((tmp_path/'out').glob('batch-*.zip')))==1


def test_changed_source_is_rejected_before_archive(tmp_path):
    from corpus_store import RunStore
    cases=inventory(tmp_path/'presets',1)
    with RunStore(tmp_path/'out',{'identity':'test'},cases,batch_size=100) as store:
        store.complete(cases[0],{'status':'computed','feature_record':{}})
        Path(cases[0]['path']).write_text('changed')
        with pytest.raises(ValueError,match='preset.*changed'):store.flush(partial=True)
def test_atomic_json_concurrent_same_destination_has_private_temporaries(tmp_path,monkeypatch):
    import threading
    from concurrent.futures import ThreadPoolExecutor
    from corpus_store import atomic_json
    import json
    from pathlib import Path
    barrier=threading.Barrier(2)
    original=Path.replace
    def synchronized(path,destination):
        barrier.wait(timeout=5)
        return original(path,destination)
    monkeypatch.setattr(Path,'replace',synchronized)
    destination=tmp_path/'same-cache.json'
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(atomic_json,destination,{'writer':i}) for i in range(2)]
        for future in futures:future.result(timeout=10)
    assert json.loads(destination.read_text()) in [{'writer':0},{'writer':1}]
    assert len(list(tmp_path.iterdir()))==1
