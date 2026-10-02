from dataclasses import asdict
import pytest

from preset_lab.dance_selection import select_dance
from preset_lab.models import PresetRecord, MatchDecision, RunConfig, EngineIdentity
from preset_lab.export import export_bundle, verify_bundle
from preset_lab.identity import load_json
from pathlib import Path


EXPERIMENT = dict(version='bass-screen-v1', code='c'*64, worker='d'*64,
                  engine=asdict(EngineIdentity('a'*40,'b'*64,'c'*64)), textures_sha256='e'*64,
                  audio={name:'f'*64 for name in ('control','bass-0.05','bass-0.15','bass-0.30')},
                  config=asdict(RunConfig()), texture_bundle_sha256='e'*64)

def measured(name, score, status='success', sha='a'*64):
    record = PresetRecord(name, sha, 7)
    return dict(preset=asdict(record), status=status, score=score, reasons=[],
                levels={f'bass-{v:.2f}': {'peak_magnitude':score} for v in (.05,.15,.30)},
                protocol=dict(EXPERIMENT), control_repeat_identical=True)


def test_selects_requested_count_by_screen_strength_not_fixed_cutoff():
    rows = [measured(f'{i}.milk', i/1000) for i in range(600)]
    library = [PresetRecord(**r['preset']) for r in rows]
    selected = select_dance(rows, library, 500, experiment=EXPERIMENT)
    assert len(selected) == 500
    assert selected[0]['preset']['path'] == '599.milk'
    assert selected[-1]['preset']['path'] == '100.milk'
    assert selected[-1]['score'] == .1


def test_unknown_stale_and_nonfinite_measurements_are_excluded():
    rows = [measured('ok.milk', .2), measured('unknown.milk', 1, 'unknown'),
            measured('stale.milk', .9, sha='b'*64), measured('nan.milk', float('nan'))]
    library = [PresetRecord(r['preset']['path'], 'a'*64, 7) for r in rows]
    assert [r['preset']['path'] for r in select_dance(rows, library, 1, experiment=EXPERIMENT)] == ['ok.milk']
    with pytest.raises(ValueError, match='only 1'):
        select_dance(rows, library, 2, experiment=EXPERIMENT)


def test_duplicate_records_do_not_fill_collection_twice():
    row = measured('same.milk', .2)
    with pytest.raises(ValueError, match='duplicate'):
        select_dance([row,row], [PresetRecord(**row['preset'])], 2, experiment=EXPERIMENT)


def test_ties_sort_by_filename_and_invalid_count_is_rejected():
    rows = [measured('b.milk', .2), measured('a.milk', .2)]
    library = [PresetRecord(**r['preset']) for r in rows]
    assert select_dance(rows, library, 1, experiment=EXPERIMENT)[0]['preset']['path'] == 'a.milk'
    with pytest.raises(ValueError):
        select_dance(rows, library, 0, experiment=EXPERIMENT)


def test_export_updates_dance_count_weights_and_evidence_and_preserves_other_genres(tmp_path):
    from preset_lab.dance_selection import export_dance_selection
    measurements = [measured(f'{i}.milk',i/10) for i in range(4)]
    library = [PresetRecord(**r['preset']) for r in measurements]
    ids = [g['id'] for g in load_json(Path(__file__).parents[1]/'src/preset_lab/profiles/genres.json')['genres']]
    decisions = [MatchDecision(library[0],g,.7,.8,.75,True,'music-tested',{}) for g in ids]
    base = export_bundle(decisions,library,{'library_coverage':'partial'},tmp_path/'base')
    result = export_dance_selection(measurements,library,base,tmp_path/'selection',{'scan_status':'running'},3, experiment=EXPERIMENT)
    manifest = verify_bundle(result,library)
    assert (result/'genres/dance.idx').read_text() == '1.milk\t7\n2.milk\t7\n3.milk\t7\n'
    assert (result/'genres/ambient.idx').read_text() == (base/'genres/ambient.idx').read_text()
    assert next(g for g in manifest['genres'] if g['id']=='dance')['count'] == 3
    assert manifest['evidence']['categories']['dance']['selection_count'] == 3
    assert manifest['evidence']['categories']['dance']['cutoff_score'] == .1
    import json
    rows=[json.loads(line) for line in (result/'presets.jsonl').read_text().splitlines()]
    dance=[r for r in rows if r['genre_id']=='dance']
    assert len(dance)==3
    assert all(r['evidence_state']=='bass-screen-tested' for r in dance)
    assert {r['rank'] for r in dance}=={1,2,3}
    # Repeated refresh must not nest prior manifest metadata indefinitely.
    result = export_dance_selection(measurements,library,result,result,{'scan_status':'complete'},3, experiment=EXPERIMENT)
    assert verify_bundle(result,library)['evidence']['categories']['dance']['scan_status']=='complete'


@pytest.mark.parametrize('dependency',['code','worker','engine','textures_sha256','audio','config'])
def test_stale_experiments_cannot_displace_current_scores(dependency):
    fresh=measured('fresh.milk',.2)
    stale=measured('stale.milk',.9)
    stale['protocol'][dependency]='obsolete'
    library=[PresetRecord(**r['preset']) for r in (fresh,stale)]
    selected=select_dance([stale,fresh],library,1,experiment=EXPERIMENT)
    assert selected[0]['preset']['path']=='fresh.milk'


def test_refresh_accepts_library_addition_and_replaced_dance_member(tmp_path):
    from preset_lab.dance_selection import export_dance_selection
    old=measured('old.milk',.2)
    retained=measured('retained.milk',.1)
    old_library=[PresetRecord(**r['preset']) for r in (old,retained)]
    ids=[g['id'] for g in load_json(Path(__file__).parents[1]/'src/preset_lab/profiles/genres.json')['genres']]
    decisions=[MatchDecision(old_library[0] if g=='dance' else old_library[1],g,.7,.8,.75,True,'music-tested',{}) for g in ids]
    base=export_bundle(decisions,old_library,{},tmp_path/'base')
    replaced=measured('old.milk',.5,sha='b'*64)
    added=measured('new.milk',.9)
    library=[PresetRecord(**r['preset']) for r in (replaced,added,retained)]
    result=export_dance_selection([replaced,added],library,base,tmp_path/'new',{},2,experiment=EXPERIMENT)
    manifest=verify_bundle(result,library)
    assert (result/'genres/dance.idx').read_text()=='new.milk\t7\nold.milk\t7\n'
    assert manifest['evidence']['engine_identity']==EXPERIMENT['engine']
    assert manifest['evidence']['app_patches_sha256']==EXPERIMENT['engine']['patches_sha256']
