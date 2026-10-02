import json
import sys
from pathlib import Path

import pytest

from preset_lab.identity import file_digest
from preset_lab.models import Corpus,EngineIdentity,PresetRecord,RunConfig
from preset_lab.pipeline import analyze_library


@pytest.fixture
def setup(tmp_path):
    repo=tmp_path/"repo"
    presets=repo/"core/src/main/assets/presets"
    textures=repo/"core/src/main/assets/textures"
    presets.mkdir(parents=True)
    textures.mkdir()
    (textures/"noise.png").write_bytes(b"texture")
    for name in ("a.milk","b.milk"):
        (presets/name).write_text("[preset00]\nper_frame_1=zoom=bass;\n")
    worker=tmp_path/"fake-worker"
    log=tmp_path/"launches.jsonl"
    worker.write_text(f"#!{sys.executable}\n"+f"LOG={str(log)!r}\n"+'''
import json,sys
from pathlib import Path
job=json.loads(Path(sys.argv[2]).read_text())
with open(LOG,'a') as f: f.write(json.dumps(job)+'\\n')
cfg=job['config']; n=round((cfg['warmup_seconds']+cfg['measurement_seconds'])*cfg['fps'])
w=cfg['width']; h=cfg['height']
for i in range(n):
 pixels=bytes((x*7+y*11+i*13+c*19)%256 for y in range(h) for x in range(w) for c in range(3))
 sys.stdout.buffer.write(pixels)
Path(job['manifest_path']).write_text(json.dumps({'status':'success','frames':n,'width':w,'height':h,'fps':cfg['fps']}))
''')
    worker.chmod(0o755)
    config=RunConfig(width=8,height=8,warmup_seconds=0,measurement_seconds=.2)
    identity=EngineIdentity("a"*40,"b"*64,"c"*64)
    return repo,worker,log,config,identity,tmp_path/"work"


def records(repo):
    return [PresetRecord(p.name,file_digest(p),0) for p in sorted((repo/"core/src/main/assets/presets").glob("*.milk"))]


def analyze(setup,corpus_identity="d"*64,**options):
    repo,worker,log,config,identity,work=setup
    return analyze_library(records(repo),Corpus((),{},corpus_identity),config,work,worker,
                           repo=repo,identity=identity,**options)


def launches(setup):
    return len(setup[2].read_text().splitlines()) if setup[2].exists() else 0


def test_unchanged_replay_and_music_changes_do_not_render_again(setup):
    first=analyze(setup)
    count=launches(setup)
    assert count>0 and len(first)==2
    second=analyze(setup)
    assert launches(setup)==count
    assert [fp.raw for fp in second]==[fp.raw for fp in first]
    analyze(setup,corpus_identity="e"*64)
    assert launches(setup)==count


def test_changed_preset_only_renders_its_own_jobs(setup):
    analyze(setup)
    count=launches(setup)
    (setup[0]/"core/src/main/assets/presets/a.milk").write_text("[preset00]\nper_frame_1=zoom=mid;\n")
    analyze(setup)
    new=[json.loads(line) for line in setup[2].read_text().splitlines()[count:]]
    assert new and all(Path(job["preset_path"]).name=="a.milk" for job in new)


def test_texture_change_invalidates_measurements(setup):
    analyze(setup)
    count=launches(setup)
    (setup[0]/"core/src/main/assets/textures/noise.png").write_bytes(b"new texture")
    analyze(setup)
    assert launches(setup)>count


def test_deleted_fingerprints_rebuild_from_stored_features_without_rendering(setup):
    analyze(setup)
    count=launches(setup)
    for path in (setup[5]/"fingerprints").glob("*.json"):
        path.unlink()
    result=analyze(setup)
    assert launches(setup)==count
    assert len(result)==2
    assert len(list((setup[5]/"fingerprints").glob("*.json")))==2


def test_incomplete_cache_record_is_not_reused(setup):
    analyze(setup)
    count=launches(setup)
    cached=next((setup[5]/"render-features").glob("*.json"))
    cached.write_text('{"incomplete":')
    analyze(setup)
    assert launches(setup)>count
