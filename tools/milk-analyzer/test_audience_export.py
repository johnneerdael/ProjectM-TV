import json
import hashlib
import zipfile
import pytest
from audience_export import export_collection, verify_review_assets


def inputs():
    scores=[0,25,30,70,75,100]
    corpus=[{'preset':f'{i}.milk','sha256':str(i)} for i in range(len(scores))]
    results={str(i):{'preset':f'{i}.milk','sha256':str(i),'identity':'run','status':'scored','score':s} for i,s in enumerate(scores)}
    return corpus,results


def test_exact_overlapping_groups_and_complete_score_table(tmp_path):
    corpus,results=inputs();manifest=export_collection(corpus,results,tmp_path,identity='run',weights={})
    assert manifest['counts']=={'all':6,'chill':3,'normal':4,'party':3}
    assert (tmp_path/'preset-genres/genres/ambient.idx').read_text().splitlines()==['0.milk\t0','1.milk\t0','2.milk\t0']
    assert len((tmp_path/'audience-scores.tsv').read_text().splitlines())==6
    assert json.loads((tmp_path/'audience-review.json').read_text())['scored']==6


@pytest.mark.parametrize('failure',['missing','unscored','wrong_identity','nonfinite','changed_path'])
def test_incomplete_or_changed_results_cannot_be_exported(tmp_path,failure):
    corpus,results=inputs()
    if failure=='missing':del results['0']
    if failure=='unscored':results['0']['status']='unscored'
    if failure=='wrong_identity':results['0']['identity']='old'
    if failure=='nonfinite':results['0']['score']=float('nan')
    if failure=='changed_path':results['0']['preset']='other.milk'
    with pytest.raises(ValueError):export_collection(corpus,results,tmp_path,identity='run',weights={})
    assert not (tmp_path/'audience-review.json').exists()


@pytest.mark.parametrize('tamper',[None,'membership','score','corpus','rank','bands','aliases'])
def test_verify_checks_real_corpus_scores_and_membership_even_with_updated_checksums(tmp_path,tamper):
    corpus,results=inputs();aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as archive:
        for row in corpus:
            payload=row['preset'].encode();row['sha256']=hashlib.sha256(payload).hexdigest()
            archive.writestr('assets/presets/'+row['preset'],payload)
    results={row['sha256']:{'preset':row['preset'],'sha256':row['sha256'],'identity':'run','status':'scored','score':i*20} for i,row in enumerate(corpus)}
    output=tmp_path/'assets';manifest=export_collection(corpus,results,output,identity='run',weights={},run_metadata={'aar_sha256':hashlib.sha256(aar.read_bytes()).hexdigest()})
    if tamper=='membership':
        path=output/'preset-genres/genres/ambient.idx';path.write_text('5.milk\t0\n')
        manifest['checksums']['preset-genres/genres/ambient.idx']=hashlib.sha256(path.read_bytes()).hexdigest()
    if tamper=='score':manifest['presets'][0]['score']=float('nan')
    if tamper=='corpus':manifest['presets'][0]['sha256']='wrong'
    if tamper=='rank':manifest['presets'][0]['rank']=float('nan')
    if tamper=='bands':manifest['bands']['Chill']=[0,100]
    if tamper=='aliases':manifest['core_aliases']['chill']='jazz'
    (output/'audience-review.json').write_text(json.dumps(manifest))
    if tamper:
        with pytest.raises(ValueError):verify_review_assets(output,aar)
    else:assert verify_review_assets(output,aar)['scored']==6
