"""Cheap source export caching, corruption and paired-batch controls."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys

import pytest

from test_core2331_warp import BINARIES


def module():
    assert importlib.util.find_spec('effect_family_export'), 'static export entry point missing'
    import effect_family_export
    return effect_family_export


def preset(tmp_path,name='calm.milk'):
    path=tmp_path/name
    path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nfWaveAlpha=0\n'
        'comp_1=`shader_body {ret=GetPixel(float2(ang/6.28,1/(rad+.1)));}\n')
    return path


def test_cached_export_skips_native_parsing_and_is_identical(tmp_path,monkeypatch):
    export=module();path=preset(tmp_path);cache=tmp_path/'cache'
    first,hit=export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)
    assert hit is False and first['status']=='computed'
    assert first['analysis']['uses_shader_execution'] is False
    assert first['analysis']['uses_equation_execution'] is False
    def forbidden(*args,**kwargs):raise AssertionError('cached export reparsed source')
    monkeypatch.setattr(export,'read_source',forbidden)
    second,hit=export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)
    assert hit is True and first==second


def test_cache_tampering_is_reported_instead_of_reused(tmp_path):
    export=module();path=preset(tmp_path);cache=tmp_path/'cache'
    export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)
    file=next(cache.glob('*.json'));value=json.loads(file.read_text())
    value['record']['analysis']['families']=[];file.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='cache.*hash'):
        export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)


def test_changed_preset_gets_new_cache_entry(tmp_path):
    export=module();path=preset(tmp_path);cache=tmp_path/'cache'
    first,_=export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)
    path.write_text('[preset00]\nfWaveAlpha=0\nzoom=1\nwarp=0\n')
    second,hit=export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)
    assert hit is False and first['preset']['sha256']!=second['preset']['sha256']
    assert len(list(cache.glob('*.json')))==2


def test_no_numerical_backend_is_called_for_export(tmp_path,monkeypatch):
    export=module();path=preset(tmp_path)
    original=subprocess.run;commands=[]
    def observe(command,*args,**kwargs):
        commands.append(command)
        assert '--equations' not in command
        assert not any('audio-inputs' in str(p) or 'wave-inputs' in str(p) for p in command)
        return original(command,*args,**kwargs)
    monkeypatch.setattr(subprocess,'run',observe)
    record,_=export.export_preset(path,reader=BINARIES/'milk-native-reader')
    assert record['analysis']['uses_rendered_images'] is False
    assert len(commands)==1


def test_script_writes_paired_batches_and_resumes(tmp_path):
    module();source=tmp_path/'presets';source.mkdir()
    preset(source,'one.milk');preset(source,'two.milk')
    output=tmp_path/'results';script=Path(__file__).with_name('effect_family_export.py')
    command=[sys.executable,str(script),str(source),'--reader',str(BINARIES/'milk-native-reader'),
             '--output',str(output),'--batch-size','1']
    process=subprocess.run(command,capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    assert len(list(output.glob('batch-*.zip')))==2
    first=list(output.rglob('results/*.json'))
    assert len(first)==2
    process=subprocess.run(command,capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    events=[json.loads(line) for line in process.stdout.splitlines()]
    assert events[0]['pending']==0


def test_model_change_since_import_is_rejected_before_cache_lookup(tmp_path,monkeypatch):
    export=module();path=preset(tmp_path);cache=tmp_path/'cache'
    export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)
    old=export.model_file_hashes()
    monkeypatch.setattr(export,'model_file_hashes',lambda:{**old,'effect_families.py':'0'*64})
    with pytest.raises(ValueError,match='model.*import'):
        export.export_preset(path,reader=BINARIES/'milk-native-reader',cache=cache)


def test_earlier_loaded_family_implementation_cannot_be_stamped_as_current(tmp_path,monkeypatch):
    export=module();path=preset(tmp_path)
    older={**export.model_file_hashes(),'effect_families.py':'0'*64}
    monkeypatch.setattr(export,'_FAMILY_IMPORT_HASHES',older,raising=False)
    with pytest.raises(ValueError,match='model.*import'):
        export.export_preset(path,reader=BINARIES/'milk-native-reader')


def test_parser_timeout_is_a_paired_null_record_and_next_case_continues(tmp_path,monkeypatch):
    export=module();source=tmp_path/'presets';source.mkdir()
    preset(source,'one.milk');preset(source,'two.milk');output=tmp_path/'results'
    real=export.read_source
    def timeout(path,*args,**kwargs):
        if Path(path).name=='one.milk':raise subprocess.TimeoutExpired(['reader'],30)
        return real(path,*args,**kwargs)
    monkeypatch.setattr(export,'read_source',timeout)
    code=export.main([str(source),'--reader',str(BINARIES/'milk-native-reader'),'--output',str(output)])
    assert code==1
    one=json.loads((output/'results/one.json').read_text())
    two=json.loads((output/'results/two.json').read_text())
    assert one['status']=='timeout' and one['analysis'] is None
    assert one['error_type']=='TimeoutExpired'
    assert two['status']=='computed'
    assert len(list(output.glob('batch-*.zip')))==1
