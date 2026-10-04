"""Recompute provisional scores; arithmetic agreement is not perceptual accuracy."""
import argparse
import hashlib
import json
import math
from numbers import Real
from pathlib import Path

from intensity_calibration import predict_intensity
from intensity_evidence import combine_activity,coherent_flash_proxy


def validate_score(row,model,*,fps,measurement_frames):
    if (isinstance(fps,bool) or not isinstance(fps,Real) or not math.isfinite(fps) or fps<=0
            or type(measurement_frames) is not int or measurement_frames<=0):
        raise ValueError('Positive declared frame schedule required')
    if row.get('status')!='scored':raise ValueError('Record is not scored')
    features=row.get('features')
    if (not isinstance(features,list) or len(features)!=4 or
        any(isinstance(v,bool) or not isinstance(v,Real) or not math.isfinite(v) or v<0 for v in features)):
        raise ValueError('Four finite nonnegative scoring features required')
    descriptors=row.get('descriptors')
    if not isinstance(descriptors,dict) or descriptors.get('frames_measured')!=measurement_frames:
        raise ValueError('Complete declared measurement frame count required')
    flashing=descriptors['flashing'];motion=descriptors['motion']
    expected_rate=(flashing['coherent_brightening_transitions']+
                   flashing['coherent_darkening_transitions'])/(measurement_frames/fps)
    if not math.isclose(features[0],expected_rate,rel_tol=1e-9,abs_tol=1e-9):
        raise ValueError('Flashing feature differs from saved measurements')
    observable_absence=row.get('all_uniform') is True or row.get('all_stationary') is True
    if observable_absence:
        if features[1:3]!=[0,0]:raise ValueError('Uniform/stationary field has nonzero motion features')
        if row.get('all_stationary') is True and features[3]!=0:
            raise ValueError('Stationary field has nonzero brightness change')
        # The native scorer records direct uniform/stationary observations.
        # Its uniform-frame brightness percentile is retained as a feature;
        # absent optical-flow descriptors are not treated as a zero by default.
    else:
        names=['median_speed_viewports_per_second',
               'mean_acceleration_viewports_per_second_squared','matched_brightness_change_p95']
        for value,name in zip(features[1:],names):
            expected=motion.get(name)
            if expected is None or not math.isclose(value,expected,rel_tol=1e-9,abs_tol=1e-9):
                raise ValueError('Scoring feature differs from saved motion: '+name)
    predicted=combine_activity(float(predict_intensity(model,[features])[0]),
                              coherent_flash=coherent_flash_proxy(descriptors,fps=fps))
    actual=row.get('score')
    if (isinstance(actual,bool) or not isinstance(actual,Real) or not math.isfinite(actual) or not 0<=actual<=100
            or not math.isclose(actual,predicted,rel_tol=0,abs_tol=1e-7)):
        raise ValueError('Saved score differs from model and measured contributions')
    return predicted


def audit_run(run,model_path):
    run=Path(run);model_path=Path(model_path)
    metadata=json.loads((run/'run-identity.json').read_text())
    if hashlib.sha256(model_path.read_bytes()).hexdigest()!=metadata['model_sha256']:
        raise ValueError('Model file differs from the scoring run')
    model_data=json.loads(model_path.read_text());model=model_data['model'];profile=metadata['profile']
    corpus=json.loads((run/'corpus.json').read_text())['cases']
    issues=[];verified=0;missing=0;unscored=0
    for case in corpus:
        path=run/'results'/(case['sha256']+'.json')
        if not path.exists():missing+=1;issues.append({**case,'reason':'missing'});continue
        row=json.loads(path.read_text())
        if row.get('status')!='scored':
            unscored+=1;issues.append({**case,'reason':row.get('reason','unscored')});continue
        try:
            if any(row.get(k)!=case[k] for k in ('preset','sha256')) or row.get('identity')!=metadata['identity']:
                raise ValueError('Score record identity differs from corpus/run')
            validate_score(row,model,fps=profile['fps'],measurement_frames=profile['frames']-profile['warmup'])
            verified+=1
        except (ValueError,KeyError,TypeError) as error:
            issues.append({**case,'reason':str(error)})
    return {'corpus':len(corpus),'arithmetically_verified':verified,'missing':missing,'unscored':unscored,
            'invalid':len(issues)-missing-unscored,'ready':not issues,'issues':issues,
            'basis':'Saved feature/descriptor/model arithmetic; not validation of visual prediction accuracy'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--model',type=Path,default=Path(__file__).parent/'profiles/audience-model-v1.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();report=audit_run(args.run,args.model)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='issues'},indent=2))


if __name__=='__main__':main()
