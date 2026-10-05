import copy
import hashlib
import json
import pytest

from intensity_calibration import predict_intensity
from intensity_evidence import combine_activity,coherent_flash_proxy
from score_audit import validate_score,audit_run


def case():
    model={'intercept':4,'weights':[10,20,30,40],'feature_scale':[1,1,1,1]}
    descriptors={'frames_measured':360,'flashing':{
        'coherent_brightening_transitions':0,'coherent_darkening_transitions':0,
        'peak_mean_luma_jump':0,'peak_brightness_change_area':0,
        'peak_paired_luma_area_product':0},'motion':{
        'median_speed_viewports_per_second':.1,
        'mean_acceleration_viewports_per_second_squared':.2,
        'matched_brightness_change_p95':.3}}
    features=[0,.1,.2,.3]
    score=combine_activity(float(predict_intensity(model,[features])[0]),
                           coherent_flash=coherent_flash_proxy(descriptors,fps=30))
    return model,{'status':'scored','score':score,'features':features,'descriptors':descriptors}


def test_recompute_valid_score_from_saved_measurements():
    model,row=case()
    assert validate_score(row,model,fps=30,measurement_frames=360)==row['score']


@pytest.mark.parametrize('mutation',['score','feature','frames','nonfinite','missing','boolean','motion_shape','missing_flash'])
def test_reject_stale_or_inconsistent_scoring_records(mutation):
    model,row=case();row=copy.deepcopy(row)
    if mutation=='score':row['score']+=1
    if mutation=='feature':row['features'][1]+=.2
    if mutation=='frames':row['descriptors']['frames_measured']=16
    if mutation=='nonfinite':row['features'][0]=float('nan')
    if mutation=='missing':del row['descriptors']
    if mutation=='boolean':row['features'][0]=False
    if mutation=='motion_shape':row['descriptors']['motion']=[]
    if mutation=='missing_flash':
        del row['descriptors']['flashing']['peak_paired_luma_area_product']
    with pytest.raises(ValueError):validate_score(row,model,fps=30,measurement_frames=360)


def test_real_run_model_envelope_and_incomplete_coverage(tmp_path):
    model,row=case();model_path=tmp_path/'model.json'
    model_path.write_text(json.dumps({'model':model}))
    (tmp_path/'run-identity.json').write_text(json.dumps({
        'identity':'run','model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),
        'profile':{'fps':30,'frames':420,'warmup':60}}))
    cases=[{'preset':'one.milk','sha256':'one'},{'preset':'two.milk','sha256':'two'}]
    (tmp_path/'corpus.json').write_text(json.dumps({'cases':cases}))
    (tmp_path/'results').mkdir()
    (tmp_path/'results/one.json').write_text(json.dumps({**row,**cases[0],'identity':'run'}))
    report=audit_run(tmp_path,model_path)
    assert report['arithmetically_verified']==1
    assert report['invalid']==0
    assert report['missing']==1
    assert not report['ready']


@pytest.mark.parametrize('payload',['{','[]'])
def test_bad_result_file_is_reported_without_aborting_remaining_records(tmp_path,payload):
    model,row=case();model_path=tmp_path/'model.json'
    model_path.write_text(json.dumps({'model':model}))
    (tmp_path/'run-identity.json').write_text(json.dumps({
        'identity':'run','model_sha256':hashlib.sha256(model_path.read_bytes()).hexdigest(),
        'profile':{'fps':30,'frames':420,'warmup':60}}))
    cases=[{'preset':'bad.milk','sha256':'bad'},{'preset':'good.milk','sha256':'good'}]
    (tmp_path/'corpus.json').write_text(json.dumps({'cases':cases}))
    (tmp_path/'results').mkdir()
    (tmp_path/'results/bad.json').write_text(payload)
    (tmp_path/'results/good.json').write_text(json.dumps({**row,**cases[1],'identity':'run'}))
    report=audit_run(tmp_path,model_path)
    assert report['invalid']==1
    assert report['arithmetically_verified']==1
    assert not report['ready']


def test_positive_flash_contribution_must_not_be_omitted():
    model,row=case();f=row['descriptors']['flashing']
    f.update(coherent_brightening_transitions=12,coherent_darkening_transitions=12,
             peak_paired_luma_area_product=.64)
    row['features'][0]=2
    row['score']=80
    assert validate_score(row,model,fps=30,measurement_frames=360)==pytest.approx(80)
    del f['peak_paired_luma_area_product']
    row['score']=float(predict_intensity(model,[row['features']])[0])
    with pytest.raises(ValueError):validate_score(row,model,fps=30,measurement_frames=360)
