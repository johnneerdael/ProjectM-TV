"""The CLI consumes cached records, not native/predicted frame arrays."""
import json
from pathlib import Path
import subprocess
import sys

from test_mood_scoring import complete,record


def test_cached_record_can_be_rescored_without_loading_a_preset_or_runtime(tmp_path):
    source=tmp_path/'features.json';output=tmp_path/'scores.json'
    source.write_text(json.dumps(record(complete())))
    command=[sys.executable,str(Path(__file__).with_name('source_classify.py')),
             '--features',str(source),'--profile','neutral-v1','--output',str(output)]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    scores=json.loads(output.read_text())
    assert scores['scores']['intensity']['value']==1
    assert scores['model_status']=='initial assumed weights; not calibrated'
    assert scores['profile']['id']=='neutral-v1'


def test_cli_rejects_simulated_records_without_opt_in(tmp_path):
    source=tmp_path/'features.json';output=tmp_path/'scores.json'
    source.write_text(json.dumps(record(complete(),basis='source-field-simulation')))
    command=[sys.executable,str(Path(__file__).with_name('source_classify.py')),
             '--features',str(source),'--output',str(output)]
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode!=0
    assert not output.exists()
    command.append('--allow-simulated')
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
