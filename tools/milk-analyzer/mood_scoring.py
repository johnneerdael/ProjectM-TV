"""Explicit assumed mood/profile mappings over cached source feature evidence.

No preset execution, display construction or native frame inputs. Missing inputs
retain their weight as score intervals. These scores are preferences/activity,
not calibrated accuracy or medical guarantees.
"""
import copy
import hashlib
import json
import math
from numbers import Real
from pathlib import Path

from source_features import STRICT, SIMULATED
from core_backend import freeze_scorer_sources,verify_scorer_sources


MODEL_ID = 'source-moods-assumed-v1'
ALIASES = {'palette.warm_cool':'colour.warm_cool',
           'palette.coloured_support':'colour.mean_coloured_fraction',
           'palette.effective_hue_bins':'colour.mean_effective_hue_bins',
           'palette.hue_rate_p95_cycles_s':'colour.hue_rate_p95_cycles_s',
           'palette.mean_saturation':'colour.mean_saturation',
           'flash.coherent_transitions_hz':'flashing.coherent_transitions_per_second'}
SOURCE_EVIDENCE={'source-domain-bound','source-point-query','source-equation-statistic',
                 'sampled-source-geometry','source-field-statistic'}
SIGNED_FEATURES={'palette.warm_cool','colour.warm_cool'}
CHILL_CONSTRAINTS = [
    {'feature':'motion.speed_upper_bound_vp_s','maximum':.20,'require_bound':True},
    {'feature':'motion.acceleration_upper_bound_vp_s2','maximum':.60,'require_bound':True},
    {'feature':'motion.jerk_upper_bound_vp_s3','maximum':2.,'require_bound':True},
    {'feature':'flash.coherent_transitions_hz','maximum':0.,'require_bound':True},
    {'feature':'flash.local_or_colour_pulses_hz','maximum':0.,'require_bound':True},
]


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _number(value):
    if isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value):
        raise ValueError('finite scoring number required')
    return float(value)


def _verify(record, allow_simulated):
    if record.get('schema_version') != 1 or record.get('uses_rendered_reference') is not False:
        raise ValueError('source feature record required')
    basis = record.get('feature_basis')
    if basis not in {STRICT, SIMULATED}:raise ValueError('unsupported feature basis')
    if basis == SIMULATED and not allow_simulated:raise ValueError('simulated evidence requires explicit opt-in')
    facts = {key:value for key,value in record.items() if key!='record_sha256'}
    if _digest(facts) != record.get('record_sha256'):raise ValueError('source feature record hash mismatch')
    if _digest(record['context']) != record.get('context_sha256'):raise ValueError('source feature context hash mismatch')
    if _digest(record['context']['domain']) != record['context']['input_hashes']['domain_sha256']:
        raise ValueError('source feature domain payload/hash mismatch')
    for entry in record['features'].values():
        if entry.get('evidence_kind') not in SOURCE_EVIDENCE:raise ValueError('unsupported feature evidence kind')
        if entry['evidence_kind']=='source-field-statistic' and basis!=SIMULATED:
            raise ValueError('display evidence cannot be relabeled strict source')


def _entry(record, name):
    return record['features'].get(name, record['features'].get(ALIASES.get(name)))


def _range(record, name):
    entry = _entry(record, name)
    if not entry or entry.get('status') != 'computed':return None
    if entry.get('evidence_kind') == 'source-field-statistic' and record['feature_basis'] != SIMULATED:
        raise ValueError('display statistic cannot be relabeled strict source evidence')
    value = entry.get('value')
    if value is None:return None
    value = _number(value)
    if name not in SIGNED_FEATURES and value<0:raise ValueError('nonnegative physical scoring feature required: '+name)
    bounds = entry.get('interval')
    if bounds is None:return (value,value)
    if not isinstance(bounds,list) or len(bounds)!=2:raise ValueError('two ordered feature interval endpoints required')
    low,high = map(_number,bounds)
    if low>high or not low<=value<=high:raise ValueError('feature value outside interval')
    if name not in SIGNED_FEATURES and low<0:raise ValueError('nonnegative physical scoring feature required: '+name)
    return low,high


def _normalized(record, name, scale=1, offset=0):
    bounds = _range(record,name)
    if bounds is None:return (0.,1.)
    if bounds[0] < offset and offset==0:raise ValueError('nonnegative physical scoring feature required: '+name)
    return tuple(min(1.,max(0.,(value-offset)/scale)) for value in bounds)


def _score(low, high, *, supported=True):
    low=float(low);high=float(high)
    return {'value': low if math.isclose(low,high,rel_tol=0,abs_tol=1e-12) else None,
            'interval':[low,high], 'interval_kind':'propagated feature ranges and missing-component ranges',
            'supported':bool(supported)}


def _constraints(record, rules):
    rows=[]
    for rule in rules:
        name=rule['feature'];entry=_entry(record,name);bounds=_range(record,name)
        maximum=rule.get('maximum');minimum=rule.get('minimum')
        if maximum is None and minimum is None:raise ValueError('constraint threshold required')
        maximum=_number(maximum) if maximum is not None else math.inf
        minimum=_number(minimum) if minimum is not None else -math.inf
        if minimum>maximum:raise ValueError('ordered constraint thresholds required')
        if bounds is None:state='unknown'
        elif bounds[0]>maximum or bounds[1]<minimum:state='violated'
        elif rule.get('require_bound',False) and (
                entry.get('evidence_kind')!='source-domain-bound' or
                entry.get('interval_kind')!='conservative-domain-bound' or
                entry.get('support',{}).get('scope')!='preset-output' or
                entry.get('support',{}).get('domain_sha256')!=record['context']['input_hashes']['domain_sha256']):
            state='unknown'
        elif bounds[0]>=minimum and bounds[1]<=maximum:state='passed'
        else:state='unknown'
        rows.append({'feature':name,'state':state,'rule':copy.deepcopy(rule)})
    return {'required_total':len(rows),'supported_passed':sum(row['state']=='passed' for row in rows),
            'violated':sum(row['state']=='violated' for row in rows),
            'unknown':sum(row['state']=='unknown' for row in rows),'results':rows}


def _fit(bounds,target,scale):
    low,high=target
    def fit(value):
        distance=max(low-value,0.,value-high)/scale
        return math.exp(-.5*distance**2) if distance<40 else 0.
    smallest=min(fit(bounds[0]),fit(bounds[1]))
    largest=1. if bounds[0]<=high and bounds[1]>=low else max(fit(bounds[0]),fit(bounds[1]))
    return smallest,largest


def _profile(record, scores, profile):
    preferences=profile.get('preferences',[])
    weights=[_number(item['weight']) for item in preferences]
    if any(weight<=0 for weight in weights):raise ValueError('positive preference weights required')
    largest=max(weights,default=1.)
    weights=[weight/largest for weight in weights]
    if any(weight==0 for weight in weights):raise ValueError('preference weight underflow; numeric domain unresolved')
    total=supported=low=high=0.
    unknowns=[]
    for preference,weight in zip(preferences,weights):
        name=preference['feature'];scale=_number(preference['scale'])
        target=preference['target']
        if weight<=0 or scale<=0 or not isinstance(target,list) or len(target)!=2:
            raise ValueError('positive preference weight/scale and target interval required')
        target=list(map(_number,target))
        if target[0]>target[1]:raise ValueError('ordered preference target required')
        if name.startswith('score.'):
            key=name.removeprefix('score.')
            if key not in scores:raise ValueError('unknown score preference: '+key)
            bounds=tuple(scores[key]['interval'])
            known=scores[key]['value'] is not None or scores[key]['supported']
        else:
            bounds=_range(record,name);known=bounds is not None
        if bounds is None:
            pair=(0.,1.);unknowns.append(name)
        else:
            pair=_fit(bounds,target,scale)
            if not known:unknowns.append(name)
        total+=weight;low+=weight*pair[0];high+=weight*pair[1]
        if known:supported+=weight
    suitability=_score(100*low/total,100*high/total) if total else {'value':None,'interval':[0.,100.],
        'interval_kind':'no requested preference measurements'}
    constraints=_constraints(record,profile.get('constraints',[]))
    coverage=supported/total if total else 0.
    minimum_coverage=_number(profile.get('minimum_preference_coverage',.9))
    maximum_width=_number(profile.get('maximum_suitability_interval_width',10.))
    if not 0<=minimum_coverage<=1 or not 0<=maximum_width<=100:raise ValueError('valid profile evidence thresholds required')
    eligible=(constraints['unknown']==0 and constraints['violated']==0 and
              coverage>=minimum_coverage and suitability['interval'][1]-suitability['interval'][0]<=maximum_width)
    return {'id':profile['id'],'eligible':eligible,'suitability':suitability,
            'supported_preference_weight_fraction':coverage,'constraints':constraints,'unknowns':unknowns}


def score_source_features(record, *, profile=None, allow_simulated=False):
    source_hashes=freeze_scorer_sources()
    record=copy.deepcopy(record);profile=copy.deepcopy(profile)
    _verify(record,allow_simulated)
    motion=_normalized(record,'motion.speed_p95_vp_s',.75)
    acceleration=_normalized(record,'motion.acceleration_p95_vp_s2',3.)
    jerk=_normalized(record,'motion.jerk_p95_vp_s3',15.)
    discontinuity=_normalized(record,'motion.discontinuities_hz',2.)
    _normalized(record,'flash.coherent_transitions_hz',4.)
    _normalized(record,'flash.coherent_delta_peak',.30)
    # Clip after multiplying raw normalized factors, as specified in the report.
    raw_rate=_range(record,'flash.coherent_transitions_hz');raw_delta=_range(record,'flash.coherent_delta_peak')
    flash=(0.,1.) if raw_rate is None or raw_delta is None else tuple(
        min(1.,max(0.,raw_rate[i]/4*raw_delta[i]/.30)) for i in (0,1))
    brightness=_normalized(record,'brightness.jump_p95',.30)
    response=_normalized(record,'audio.bass_peak_rgb_effect',.20)
    terms=[(.28,motion),(.12,acceleration),(.08,jerk),(.32,flash),(.12,brightness),(.08,response)]
    intensity=[max(1+99*sum(weight*pair[i] for weight,pair in terms),1+99*flash[i]) for i in (0,1)]
    smooth=[100*(1-.35*acceleration[i]-.45*jerk[i]-.20*discontinuity[i]) for i in (1,0)]
    warmth=_range(record,'palette.warm_cool');chroma=_range(record,'palette.coloured_support')
    if warmth is not None and not -1<=warmth[0]<=warmth[1]<=1:raise ValueError('warm/cool coordinate must be −1..1')
    if chroma is None or chroma[0]<.2:warmth=None
    warm=[50*(1+value) for value in warmth] if warmth is not None else [0.,100.]
    cold=[50*(1-value) for value in reversed(warmth)] if warmth is not None else [0.,100.]
    psychedelic_terms=[(.20,_normalized(record,'palette.effective_hue_bins',7.,1)),
        (.25,_normalized(record,'structure.nonlinear_warp')),
        (.25,_normalized(record,'feedback.complexity')),
        (.20,_normalized(record,'structure.symmetry')),
        (.10,_normalized(record,'palette.hue_rate_p95_cycles_s',.50))]
    psychedelic=[100*sum(weight*pair[i] for weight,pair in psychedelic_terms) for i in (0,1)]
    scores={name:_score(*bounds) for name,bounds in [('intensity',intensity),('smoothness',smooth),
            ('warm',warm),('cold',cold),('psychedelic',psychedelic)]}
    requirements={'intensity':['motion.speed_p95_vp_s','motion.acceleration_p95_vp_s2','motion.jerk_p95_vp_s3',
        'flash.coherent_transitions_hz','flash.coherent_delta_peak','brightness.jump_p95','audio.bass_peak_rgb_effect'],
        'smoothness':['motion.acceleration_p95_vp_s2','motion.jerk_p95_vp_s3','motion.discontinuities_hz'],
        'psychedelic':['palette.effective_hue_bins','structure.nonlinear_warp','feedback.complexity',
                      'structure.symmetry','palette.hue_rate_p95_cycles_s']}
    for name,features in requirements.items():
        missing=[feature for feature in features if _range(record,feature) is None]
        scores[name].update(supported=not missing,unknown_inputs=missing)
    for name in ('warm','cold'):
        scores[name].update(supported=warmth is not None,
            unknown_inputs=[] if warmth is not None else ['palette.warm_cool or sufficient coloured support'])
    constraints=_constraints(record,CHILL_CONSTRAINTS)
    bands=[];ambiguous=[]
    for name,low,high in [('Chill',1,30),('Normal',25,75),('Intense',70,100)]:
        if intensity[0]>=low and intensity[1]<=high and intensity[1]-intensity[0]<=10:
            if name!='Chill' or constraints['unknown']==constraints['violated']==0:bands.append(name)
        elif intensity[0]<=high and intensity[1]>=low:ambiguous.append(name)
    tags=[]
    for name,key,threshold in [('Smooth','smoothness',80),('Warm','warm',70),('Cold','cold',70)]:
        if scores[key]['interval'][0]>=threshold:tags.append(name)
    structural=sum(_normalized(record,name)[0]>=.6 for name in
                   ('structure.nonlinear_warp','feedback.complexity','structure.symmetry'))
    if scores['psychedelic']['interval'][0]>=70 and structural>=2:tags.append('Psychedelic')
    result={'schema_version':1,'model_id':MODEL_ID,'model_status':'initial assumed weights; not calibrated',
            'scoring_source_sha256':source_hashes[Path(__file__).name],
            'scoring_sources_sha256':source_hashes,
            'feature_record_sha256':record['record_sha256'],'context_sha256':record['context_sha256'],
            'feature_basis':record['feature_basis'],'scores':scores,'bands':bands,
            'ambiguous_bands':ambiguous,'tags':tags,'chill_constraints':constraints,
            'profile_sha256':None,'profile':None,
            'limitations':['Supplied bound evidence is a producer declaration, not newly proved by this scorer',
                           'Partial shape geometry is not substituted for whole-preset motion',
                           'Genre suitability describes preferences, not the genre inherent in a preset']}
    if profile is not None:
        result['profile_sha256']=_digest(profile)
        result['profile']=_profile(record,scores,profile)
    verify_scorer_sources(source_hashes)
    return result
