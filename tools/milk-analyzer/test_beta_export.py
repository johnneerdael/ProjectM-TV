import hashlib
import json
import math
import zipfile
from pathlib import Path

import pytest


def sha(data):
    return hashlib.sha256(data).hexdigest()


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    assets=tmp_path/'assets'
    (assets/'presets').mkdir(parents=True)
    (assets/'textures').mkdir()
    weights={'calm.milk':3,'middle.milk':17,'wild.milk':40,'static.milk':0}
    contents={name:('preset '+name).encode() for name in weights}
    index=''.join(f'{name}\t{weight}\n' for name,weight in weights.items()).encode()
    for name,data in contents.items():(assets/'presets'/name).write_bytes(data)
    (assets/'presets.idx').write_bytes(index)
    (assets/'textures'/'t.png').write_bytes(b'texture')
    aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as z:
        z.writestr('jni/arm64-v8a/libprojectmtv.so',b'native')
        z.writestr('assets/presets.idx',index)
        z.writestr('assets/textures/t.png',b'texture')
        for name,data in contents.items():z.writestr('assets/presets/'+name,data)
    source=Path(__file__).parent
    facts={'aar_sha256':sha(aar.read_bytes()),'native_arm64_sha256':sha(b'native'),
           'model_sha256':sha((source/'profiles/audience-model-v1.json').read_bytes()),
           'scorer_sha256':sha((source/'profiles/scorers/beta-score-v1.py.txt').read_bytes()),
           'descriptor_sha256':sha((source/'descriptors.py').read_bytes()),
           'runtime_sha256':{'core.aar':sha(aar.read_bytes()),'libprojectmtv.so':sha(b'native'),
                             'classes.dex':sha(b'dex'),'libbackendclock.so':sha(b'clock'),
                             'input.f32':sha(b'pcm')},
           'profile':{'frames':420,'warmup':60,'fps':30,'width':128,'height':72,'motion_fps':10},
           'backend':'released-projectmtv-core-jni','release':'v2.3.3',
           'input_policy':'fixed synthetic quiet/melodic/kick reference'}
    facts['identity']=sha(json.dumps(facts,sort_keys=True).encode())
    import beta_export
    monkeypatch.setattr(beta_export,'PUBLISHED_CORE',{
        **beta_export.PUBLISHED_CORE,'aar_sha256':facts['aar_sha256'],
        'native_arm64_sha256':facts['native_arm64_sha256']})
    run=tmp_path/'run'
    (run/'results').mkdir(parents=True)
    (run/'run-identity.json').write_text(json.dumps(facts))
    (run/'corpus.json').write_text(json.dumps({'cases':[{'preset':n,'sha256':sha(d)} for n,d in contents.items()]}))
    model=json.loads((source/'profiles/audience-model-v1.json').read_text())['model']
    for n,features in zip(weights,[[0.,.001,.001,.01],[1.,.1,.2,.3],[2.,1.,2.,.8],[0.,0.,0.,0.]]):
        value=model['intercept']+sum(w*math.log1p(x)/s for w,x,s in zip(model['weights'],features,model['feature_scale']))
        row={'preset':n,'sha256':sha(contents[n]),'identity':facts['identity'],
             'status':'scored','raw_activity':value,'has_activity':n!='static.milk',
             'features':features,'motion_basis':'bidirectional10Hzflow',
             'coherent_up':int(features[0]*6),'coherent_down':int(features[0]*6),'paired_flash_peak':0.,
             'metadata':{'frames':420,'width':128,'height':72,'fps':30,'preset':n,
                         'backend':'published-core-jni','skipped_count':0,'indexed_count':1}}
        (run/'results'/(row['sha256']+'.json')).write_text(json.dumps(row))
    return run,aar,assets,tmp_path/'bundle'


def test_complete_export_retains_weights_and_marks_beta(fixture):
    from beta_export import export_bundle,verify_bundle
    run,aar,assets,bundle=fixture
    manifest=export_bundle(run,aar,assets,bundle)
    assert manifest['status']=='beta'
    assert manifest['default']=='all' and manifest['total_presets']==4
    assert manifest['inactive_presets']==1
    assert set(manifest['groups'])=={'chill','normal','intense'}
    assert (bundle/'genres/chill.idx').read_text()=='calm.milk\t3\n'
    assert (bundle/'genres/normal.idx').read_text()=='middle.milk\t17\n'
    assert (bundle/'genres/intense.idx').read_text()=='wild.milk\t40\n'
    assert not (bundle/'genres/dance.idx').exists()
    assert verify_bundle(bundle,assets)==manifest


@pytest.mark.parametrize('mutation',['missing','unscored','stale_source','stale_identity','bad_schedule','skip'])
def test_export_refuses_partial_or_mismatched_evidence(fixture,mutation):
    from beta_export import export_bundle
    run,aar,assets,bundle=fixture
    path=next((run/'results').glob('*.json'))
    row=json.loads(path.read_text())
    if mutation=='missing':path.unlink()
    else:
        if mutation=='unscored':row['status']='unscored'
        if mutation=='stale_source':row['sha256']='0'*64
        if mutation=='stale_identity':row['identity']='0'*64
        if mutation=='bad_schedule':row['metadata']['frames']=30
        if mutation=='skip':row['metadata']['skipped_count']=1
        path.write_text(json.dumps(row))
    with pytest.raises(ValueError):export_bundle(run,aar,assets,bundle)
    assert not bundle.exists()


def test_changed_texture_or_index_cannot_reuse_scores(fixture):
    from beta_export import export_bundle
    run,aar,assets,bundle=fixture
    (assets/'textures/t.png').write_bytes(b'changed')
    with pytest.raises(ValueError):export_bundle(run,aar,assets,bundle)
    (assets/'textures/t.png').write_bytes(b'texture')
    (assets/'presets.idx').write_text('calm.milk\t0\nmiddle.milk\t0\nwild.milk\t0\nstatic.milk\t0\n')
    with pytest.raises(ValueError):export_bundle(run,aar,assets,bundle)


def test_bundle_validation_checks_membership_even_with_rewritten_checksums(fixture):
    from beta_export import export_bundle,verify_bundle
    run,aar,assets,bundle=fixture
    manifest=export_bundle(run,aar,assets,bundle)
    idx=bundle/'genres/chill.idx'
    idx.write_text('wild.milk\t40\n')
    manifest['checksums']['genres/chill.idx']=sha(idx.read_bytes())
    content={k:v for k,v in manifest.items() if k!='generation_identity'}
    manifest['generation_identity']=sha(json.dumps(content,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    (bundle/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError):verify_bundle(bundle,assets)


def test_existing_bundle_is_preserved_when_new_export_fails(fixture):
    from beta_export import export_bundle
    run,aar,assets,bundle=fixture
    export_bundle(run,aar,assets,bundle)
    before={str(p.relative_to(bundle)):p.read_bytes() for p in bundle.rglob('*') if p.is_file()}
    next((run/'results').glob('*.json')).unlink()
    with pytest.raises(ValueError):export_bundle(run,aar,assets,bundle)
    assert before=={str(p.relative_to(bundle)):p.read_bytes() for p in bundle.rglob('*') if p.is_file()}


def test_other_aar_flavour_cannot_be_claimed_as_standard(fixture,monkeypatch):
    import beta_export
    run,aar,assets,bundle=fixture
    monkeypatch.setitem(beta_export.PUBLISHED_CORE,'aar_sha256','0'*64)
    with pytest.raises(ValueError,match='standard published AAR'):
        beta_export.export_bundle(run,aar,assets,bundle)


def test_activity_must_match_its_recorded_features(fixture):
    from beta_export import export_bundle
    run,aar,assets,bundle=fixture
    path=next((run/'results').glob('*.json'))
    row=json.loads(path.read_text());row['raw_activity']+=10
    path.write_text(json.dumps(row))
    with pytest.raises(ValueError,match='activity'):
        export_bundle(run,aar,assets,bundle)


def test_refit_is_separate_from_original_measurements(fixture):
    from beta_export import export_bundle,verify_bundle
    from activity_model import load_model,activity,scoring_identity
    run,aar,assets,bundle=fixture
    original={p:p.read_bytes() for p in (run/'results').glob('*.json')}
    manifest=export_bundle(run,aar,assets,bundle)
    assert original=={p:p.read_bytes() for p in original}
    assert manifest['derived_scoring']==scoring_identity()
    rows=[json.loads(s) for s in (bundle/'presets.jsonl').read_text().splitlines()]
    for row in rows:
        measurement=json.loads((run/'results'/(row['sha256']+'.json')).read_text())
        assert row['evidence_identity']==measurement['identity']
        assert row['measurement_raw_activity']==measurement['raw_activity']
        assert row['raw_activity']==activity(load_model()['model'],row['features'],row['coherent_up'],row['coherent_down'],row['paired_flash_peak'])
    assert any(r['raw_activity']!=r['measurement_raw_activity'] for r in rows)
    manifest['derived_scoring']['model_sha256']='0'*64
    from preset_lab.identity import digest
    manifest['generation_identity']=digest({k:v for k,v in manifest.items() if k!='generation_identity'})
    (bundle/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises(ValueError,match='Derived scoring'):verify_bundle(bundle,assets)


@pytest.mark.parametrize('pair',['old_scorer_new_model','new_scorer_old_model'])
def test_impossible_producer_model_pair_is_rejected(fixture,pair):
    from beta_export import check_identity
    from activity_model import MODEL_PATH
    root=Path(__file__).parent
    run,aar,assets,bundle=fixture
    facts=json.loads((run/'run-identity.json').read_text())
    if pair=='old_scorer_new_model':
        facts['scorer_sha256']=sha((root/'profiles/scorers/beta-score-v1.py.txt').read_bytes())
        facts['model_sha256']=sha((root/MODEL_PATH).read_bytes())
    else:
        facts['scorer_sha256']=sha((root/'beta_score.py').read_bytes())
        facts['model_sha256']=sha((root/'profiles/audience-model-v1.json').read_bytes())
    facts['identity']=sha(json.dumps({k:v for k,v in facts.items() if k!='identity'},sort_keys=True).encode())
    with pytest.raises(ValueError,match='producer model'):check_identity(facts)
