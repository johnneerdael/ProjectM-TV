import json
import hashlib
import zipfile
import subprocess
import sys
from pathlib import Path
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


@pytest.mark.parametrize('tamper',[None,'membership','memory_weight','extra_weight_column','score','corpus','rank','bands','aliases'])
def test_verify_checks_real_corpus_scores_and_membership_even_with_updated_checksums(tmp_path,tamper):
    corpus,results=inputs();aar=tmp_path/'core.aar'
    with zipfile.ZipFile(aar,'w') as archive:
        for row in corpus:
            payload=row['preset'].encode();row['sha256']=hashlib.sha256(payload).hexdigest()
            archive.writestr('assets/presets/'+row['preset'],payload)
        archive.writestr('assets/presets.idx',''.join(f"{row['preset']}\t{i+1}\n" for i,row in enumerate(corpus)))
    results={row['sha256']:{'preset':row['preset'],'sha256':row['sha256'],'identity':'run','status':'scored','score':i*20} for i,row in enumerate(corpus)}
    output=tmp_path/'assets';manifest=export_collection(corpus,results,output,identity='run',weights={row['preset']:i+1 for i,row in enumerate(corpus)},run_metadata={'aar_sha256':hashlib.sha256(aar.read_bytes()).hexdigest()})
    if tamper=='membership':
        path=output/'preset-genres/genres/ambient.idx';path.write_text('5.milk\t0\n')
        manifest['checksums']['preset-genres/genres/ambient.idx']=hashlib.sha256(path.read_bytes()).hexdigest()
    if tamper in {'memory_weight','extra_weight_column'}:
        path=output/'preset-genres/genres/ambient.idx'
        original=path.read_text()
        changed='0.milk\t0' if tamper=='memory_weight' else '0.milk\t1\t999'
        path.write_text(original.replace('0.milk\t1',changed))
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


def cli_run(tmp_path):
    model=tmp_path/'model.json'
    model.write_text(json.dumps({'model':{'intercept':20,'weights':[0,0,0,0],'feature_scale':[1,1,1,1]}}))
    aar=tmp_path/'core.aar';run=tmp_path/'run';run.mkdir();(run/'results').mkdir()
    cases=[]
    with zipfile.ZipFile(aar,'w') as archive:
        for name in ('a.milk','b.milk'):
            raw=name.encode();sha=hashlib.sha256(raw).hexdigest()
            archive.writestr('assets/presets/'+name,raw);cases.append({'preset':name,'sha256':sha})
        archive.writestr('assets/presets.idx','a.milk\t0\nb.milk\t0\n')
    (run/'corpus.json').write_text(json.dumps({'cases':cases}))
    (run/'run-identity.json').write_text(json.dumps({
        'identity':'run','aar_sha256':hashlib.sha256(aar.read_bytes()).hexdigest(),
        'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),
        'profile':{'fps':30,'frames':420,'warmup':60}}))
    for row in cases:
        (run/'results'/(row['sha256']+'.json')).write_text(json.dumps({**row,
            'identity':'run','status':'scored','score':20,'features':[0,0,0,0],
            'descriptors':{'frames_measured':360,'flashing':{
                'coherent_brightening_transitions':0,'coherent_darkening_transitions':0,
                'peak_paired_luma_area_product':0},'motion':{
                'median_speed_viewports_per_second':0,
                'mean_acceleration_viewports_per_second_squared':0,'matched_brightness_change_p95':0}}}))
    output=tmp_path/'review-assets'
    script=Path(__file__).with_name('audience_export.py')
    command=[sys.executable,str(script),'--run',str(run),'--model',str(model),
             '--aar',str(aar),'--output',str(output)]
    return command,run,aar,output,script


@pytest.mark.parametrize('failure',[None,'stale','missing'])
def test_cli_enforces_complete_recomputed_scores_before_writing_assets(tmp_path,failure):
    command,run,aar,output,script=cli_run(tmp_path)
    path=next((run/'results').glob('*.json'))
    if failure=='stale':
        row=json.loads(path.read_text());row['score']=21;path.write_text(json.dumps(row))
    if failure=='missing':path.unlink()
    result=subprocess.run(command,capture_output=True,text=True,timeout=20)
    if failure:
        assert result.returncode!=0
        assert not output.exists()
        error=json.loads(result.stdout)
        assert error['status']=='incomplete'
        assert not error['audit']['ready']
        assert '--run' in error['audit_command']
    else:
        assert result.returncode==0,result.stderr
        assert json.loads(result.stdout)['status']=='complete'
        assert verify_review_assets(output,aar)['scored']==2


def test_asset_verification_does_not_require_scipy(tmp_path):
    command,run,aar,output,script=cli_run(tmp_path)
    created=subprocess.run(command,capture_output=True,text=True,timeout=20)
    assert created.returncode==0,created.stderr
    code='''import builtins,runpy,sys
original=builtins.__import__
def guarded(name,*args,**kwargs):
    if name=="scipy" or name.startswith("scipy."):raise ImportError("SciPy intentionally unavailable")
    return original(name,*args,**kwargs)
builtins.__import__=guarded
path,aar,output=sys.argv[1:]
sys.path.insert(0,str(__import__("pathlib").Path(path).parent))
sys.argv=[path,"--verify","--aar",aar,"--output",output]
runpy.run_path(path,run_name="__main__")
'''
    verified=subprocess.run([sys.executable,'-c',code,str(script),str(aar),str(output)],
                            capture_output=True,text=True,timeout=20)
    assert verified.returncode==0,verified.stderr
    assert json.loads(verified.stdout)['status']=='verified'
