from pathlib import Path
import json

import pytest

from preset_lab.export import export_bundle,verify_bundle
from preset_lab.models import MatchDecision,PresetRecord
from preset_lab.identity import load_json, digest, file_digest, canonical_json


def fixture():
    root=Path(__file__).parents[1]/"src/preset_lab/profiles"
    ids=[g["id"] for g in load_json(root/"genres.json")["genres"]]
    record=PresetRecord("John's café & colours.milk","a"*64,37)
    decisions=[MatchDecision(record,g,.7,.8,.75,True,"music-tested",{}) for g in ids]
    return record,decisions


def test_exports_exact_membership_weights_and_reproducible_bytes(tmp_path):
    record,decisions=fixture()
    first=export_bundle(decisions,[record],{"library_coverage":"partial"},tmp_path/"first")
    second=export_bundle(decisions,[record],{"library_coverage":"partial"},tmp_path/"second")
    assert (first/"genres/ambient.idx").read_text()=="John's café & colours.milk\t37\n"
    assert {p.relative_to(first):p.read_bytes() for p in first.rglob("*") if p.is_file()} == {
        p.relative_to(second):p.read_bytes() for p in second.rglob("*") if p.is_file()}
    manifest=verify_bundle(first,[record])
    assert len(manifest["genres"])==12
    assert manifest["evidence"]["library_coverage"]=="partial"


def test_predicted_only_data_does_not_become_music_tested_export(tmp_path):
    record,decisions=fixture()
    from dataclasses import replace
    predictions=[replace(d,evidence_state="predicted") for d in decisions]
    with pytest.raises(ValueError,match="eligible"):
        export_bundle(predictions,[record],{},tmp_path/"export")


def test_tampered_index_and_stale_preset_are_rejected(tmp_path):
    record,decisions=fixture()
    bundle=export_bundle(decisions,[record],{},tmp_path/"export")
    (bundle/"genres/dance.idx").write_text("John's café & colours.milk\t0\n")
    with pytest.raises(ValueError,match="checksum"):
        verify_bundle(bundle,[record])
    bundle=export_bundle(decisions,[record],{},tmp_path/"fresh")
    from dataclasses import replace
    with pytest.raises(ValueError,match="stale"):
        verify_bundle(bundle,[replace(record,sha256="b"*64)])


def test_bad_paths_unknown_members_and_weights_fail_before_publication(tmp_path):
    record,decisions=fixture()
    from dataclasses import replace
    invalid=replace(record,path="../escape.milk")
    with pytest.raises(ValueError):
        export_bundle([replace(d,preset=invalid) for d in decisions],[invalid],{},tmp_path/"bad")
    assert not (tmp_path/"bad").exists()
    with pytest.raises(ValueError,match="weight"):
        export_bundle(decisions,[replace(record,weight_mb=0)],{},tmp_path/"weights")


@pytest.mark.parametrize('mutation', ['missing_checksum','duplicate_catalog','missing_evidence','duplicate_preset'])
def test_rehashed_inconsistent_bundle_is_rejected(tmp_path, mutation):
    record, decisions = fixture()
    bundle = export_bundle(decisions,[record],{},tmp_path/'bundle')
    manifest = load_json(bundle/'manifest.json')
    if mutation == 'missing_checksum':
        manifest['checksums'].pop('genres/dance.idx')
    elif mutation == 'duplicate_catalog':
        manifest['genres'].append(manifest['genres'][0])
    elif mutation == 'duplicate_preset':
        manifest['presets'].append(manifest['presets'][0])
    else:
        rows=[json.loads(line) for line in (bundle/'presets.jsonl').read_text().splitlines()]
        (bundle/'presets.jsonl').write_text(''.join(canonical_json(r)+'\n' for r in rows if r['genre_id']!='dance'))
        manifest['checksums']['presets.jsonl']=file_digest(bundle/'presets.jsonl')
    manifest.pop('generation_identity')
    manifest['generation_identity']=digest(manifest)
    (bundle/'manifest.json').write_text(canonical_json(manifest))
    with pytest.raises(ValueError):
        verify_bundle(bundle,[record])
