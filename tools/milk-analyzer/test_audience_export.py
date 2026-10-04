import json
import pytest
from audience_export import export_collection


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
