import hashlib,json,shutil,subprocess
from pathlib import Path
import pytest
from test_native_reader import READER
from scan import read_preset


def test_scan_reads_exact_preset_snapshot_when_authored_file_changes(tmp_path,monkeypatch):
    preset=tmp_path/'sample.milk';preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nzoom=1.25\n')
    source_sha=hashlib.sha256(preset.read_bytes()).hexdigest();reader_sha=hashlib.sha256(READER.read_bytes()).hexdigest()
    original=subprocess.run
    def change_source(args,**kwargs):
        preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nzoom=2.5\n')
        return original(args,**kwargs)
    monkeypatch.setattr(subprocess,'run',change_source)
    result=read_preset(READER,preset,tmp_path/'output',reader_sha)
    cached=json.loads(Path(result['tree']).read_text())
    assert cached['preset_sha256']==source_sha
    assert float(cached['values']['zoom'])==1.25


def test_scan_rejects_stale_reader_before_creating_cache(tmp_path):
    adapter=tmp_path/'reader';shutil.copy2(READER,adapter)
    preset=tmp_path/'sample.milk';preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nzoom=1.25\n')
    with pytest.raises(ValueError,match='reader.*identity'):
        read_preset(adapter,preset,tmp_path/'output','0'*64)
    assert not (tmp_path/'output').exists()


def test_scan_rebuild_cannot_attribute_new_reader_to_old_cache_identity(tmp_path,monkeypatch):
    adapter=tmp_path/'reader';shutil.copy2(READER,adapter);reader_sha=hashlib.sha256(adapter.read_bytes()).hexdigest()
    preset=tmp_path/'sample.milk';preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nzoom=1.25\n')
    original=subprocess.run
    def rebuild(args,**kwargs):
        adapter.write_text('#!/bin/sh\nexit 7\n');adapter.chmod(0o755)
        return original(args,**kwargs)
    monkeypatch.setattr(subprocess,'run',rebuild)
    result=read_preset(adapter,preset,tmp_path/'output',reader_sha)
    cached=json.loads(Path(result['tree']).read_text())
    assert result['syntax_complete'] is True
    assert cached['reader_sha256']==reader_sha
    assert float(cached['values']['zoom'])==1.25
    with pytest.raises(ValueError,match='reader.*identity'):
        read_preset(adapter,preset,tmp_path/'output',reader_sha)
