from pathlib import Path
from dataclasses import replace

import pytest

from preset_lab.export import export_bundle,import_bundle
from preset_lab.models import MatchDecision,PresetRecord
from preset_lab.inventory import inventory
from preset_lab.identity import load_json


def test_import_checks_current_assets_and_preserves_previous_on_failure(tmp_path):
    repo=tmp_path/"repo"
    assets=repo/"core/src/main/assets"
    (assets/"presets").mkdir(parents=True)
    (assets/"textures").mkdir()
    (assets/"presets/a.milk").write_text("preset")
    (assets/"presets.idx").write_text("a.milk\t7\n")
    records,metadata=inventory(assets/"presets",assets/"presets.idx",assets/"textures")
    genres=load_json(Path(__file__).parents[1]/"src/preset_lab/profiles/genres.json")["genres"]
    rows=[MatchDecision(records[0],g["id"],.8,.8,.8,True,"music-tested",{}) for g in genres]
    bundle=export_bundle(rows,records,{"texture_sha256":metadata["texture_sha256"]},tmp_path/"bundle")
    target=import_bundle(bundle,repo)
    before=(target/"genres/ambient.idx").read_bytes()
    assert before==b"a.milk\t7\n"
    assert import_bundle(target,repo,check=True)==target
    (bundle/"genres/ambient.idx").write_text("wrong.milk\t7\n")
    with pytest.raises(ValueError):
        import_bundle(bundle,repo)
    assert (target/"genres/ambient.idx").read_bytes()==before
