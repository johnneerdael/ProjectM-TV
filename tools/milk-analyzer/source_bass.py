"""Predict causal band-input response using matched source-only forecasts.

Waveform/spectrum/time/state/RNG are held fixed. Native-derived vol/vol_att are
recomputed from the overridden bands. This measures a declared intervention,
not actual rendered response or a guarantee for arbitrary songs.
"""
import copy
import hashlib
from pathlib import Path
import tempfile
import numpy as np
from forecast import forecast_source,digest


AREA_THRESHOLD=8/255


def band_variant(audio, schedule, *, warmup_frames):
    frames=audio.get('frames',[])
    if audio.get('uses_rendered_reference') is not False or not frames:
        raise ValueError('source-generated nonempty audio required')
    if type(warmup_frames) is not int or not 0<=warmup_frames<len(frames):
        raise ValueError('warmup must leave measured frames')
    if not isinstance(schedule,list) or len(schedule)!=len(frames):
        raise ValueError('band schedule must match every audio frame')
    result=copy.deepcopy(audio);changed=False
    for i,(before,override) in enumerate(zip(frames,schedule)):
        if not isinstance(override,dict) or set(override)-{'bass','bass_att'}:
            raise ValueError('only bass/bass_att overrides are permitted')
        for name,value in override.items():
            if isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value) or value<0:
                raise ValueError('finite nonnegative band override required')
            with np.errstate(over='ignore'):
                native=float(np.float32(value))
            if not np.isfinite(native):raise ValueError('band override exceeds native float32')
            differs=native!=float(np.float32(before[name]))
            if i<warmup_frames and differs:raise ValueError('band override changes warmup')
            changed|=differs
            result['frames'][i][name]=native
        if override:
            frame=result['frames'][i]
            for output,names in [('vol',('bass','mid','treb')),('vol_att',('bass_att','mid_att','treb_att'))]:
                values=[np.float32(frame[name]) for name in names]
                frame[output]=float((values[0]+values[1]+values[2])*np.float32(.333))
    if not changed:raise ValueError('band schedule changes no input; reactivity cannot be measured')
    result['band_intervention']={'schedule_sha256':digest(schedule),'allowed_bands':['bass','bass_att'],
        'derived_outputs':['vol','vol_att'],'warmup_frames':warmup_frames}
    return result


def pixel_response(frame, control, *, threshold=AREA_THRESHOLD):
    a,b=np.asarray(frame,dtype=np.float32),np.asarray(control,dtype=np.float32)
    if a.shape!=b.shape or a.ndim!=3 or a.shape[-1] not in {3,4}:
        raise ValueError('matched predicted RGB/RGBA fields required')
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)) or np.any((a<0)|(a>1)) or np.any((b<0)|(b>1)):
        raise ValueError('finite normalized predicted fields required')
    if not np.isfinite(threshold) or not 0<threshold<1:raise ValueError('response area threshold must be in (0,1)')
    difference=np.mean(np.abs(a[...,:3]-b[...,:3]),axis=-1)
    affected=difference>threshold
    return dict(magnitude=float(difference.mean()),affected_area=float(affected.mean()),
                local_intensity=float(difference[affected].mean()) if np.any(affected) else 0.)


def summarize(trajectory, onset_time):
    values=np.array([row['magnitude'] for row in trajectory])
    peak=float(np.quantile(values,.95));peak_index=int(np.argmin(np.abs(values-peak)))
    threshold=max(.002,float(values.max())*.1)
    arrivals=[row['time'] for row in trajectory if row['time']>=onset_time and row['magnitude']>threshold]
    return dict(peak_magnitude=peak,mean_magnitude=float(values.mean()),
                maximum_magnitude=float(values.max()),
                maximum_affected_area=max(row['affected_area'] for row in trajectory),
                area_at_peak=trajectory[peak_index]['affected_area'],
                intensity_at_peak=trajectory[peak_index]['local_intensity'],
                mean_affected_area=float(np.mean([row['affected_area'] for row in trajectory])),
                first_response_seconds=float(arrivals[0]-onset_time) if arrivals else None,
                onset_time=onset_time,response_threshold=threshold)


def predict_bass_response(source, *, audio, binaries, domain, compatibility, interventions,
                          warmup_frames, random_inputs=None, noise_bank=None, materials=None, area_threshold=AREA_THRESHOLD):
    if not isinstance(interventions,dict) or not interventions:
        raise ValueError('named nonempty bass interventions required')
    variants={name:band_variant(audio,schedule,warmup_frames=warmup_frames)
              for name,schedule in interventions.items()}
    # Validate the threshold even if a run would later fail or have no response.
    if not np.isfinite(area_threshold) or not 0<area_threshold<1:
        raise ValueError('response area threshold must be in (0,1)')
    count=len(audio['frames']);height,width=domain['height'],domain['width']
    kwargs=dict(source=source,binaries=binaries,domain=domain,compatibility=compatibility,
                random_inputs=random_inputs,noise_bank=noise_bank,materials=materials,retain_surfaces=False)
    levels={};control_hash=hashlib.sha256()
    with tempfile.TemporaryDirectory(prefix='source-bass-') as directory:
        path=Path(directory)/'control.f32'
        storage=np.memmap(path,dtype='<f4',mode='w+',shape=(count,height,width,3))
        index=0
        def baseline(frame):
            nonlocal index
            storage[index]=frame['display'][...,:3]
            control_hash.update(storage[index].tobytes());index+=1
        control=forecast_source(audio=audio,on_frame=baseline,**kwargs)
        if index!=count:raise ValueError('source control frame count mismatch')
        storage.flush()
        repeat_hash=hashlib.sha256();index=0
        def repeat(frame):
            nonlocal index
            if not np.array_equal(frame['display'][...,:3],storage[index]):
                raise ValueError('source control is not repeatable')
            repeat_hash.update(np.asarray(frame['display'][...,:3],dtype='<f4').tobytes());index+=1
        repeated=forecast_source(audio=audio,on_frame=repeat,**kwargs)
        if index!=count or repeat_hash.digest()!=control_hash.digest():
            raise ValueError('source control repeat identity mismatch')
        if repeated['input_hashes']!=control['input_hashes'] or repeated['provenance']!=control['provenance']:
            raise ValueError('source control repeat model/input identity mismatch')
        for name,variant in variants.items():
            trajectory=[];index=0
            changed=[i for i,(a,b) in enumerate(zip(audio['frames'],variant['frames']))
                     if any(np.float32(a[key])!=np.float32(b[key]) for key in ('bass','bass_att'))]
            onset=audio['frames'][changed[0]]['time']
            def observe(frame):
                nonlocal index
                rgb=frame['display'][...,:3]
                if index<warmup_frames:
                    if not np.array_equal(rgb,storage[index]):raise ValueError('source intervention warmup drift')
                else:
                    trajectory.append(dict(time=frame['time'],input_changed=index in changed,
                        **pixel_response(rgb,storage[index],threshold=area_threshold)))
                index+=1
            result=forecast_source(audio=variant,on_frame=observe,**kwargs)
            if index!=count:raise ValueError('source intervention frame count mismatch')
            for key in ['preset_sha256','parsed_source_sha256','pcm_sha256','domain_sha256',
                        'compatibility_sha256','random_sha256','materials_sha256']:
                if result['input_hashes'][key]!=control['input_hashes'][key]:
                    raise ValueError('unmatched source experiment input: '+key)
            if result['provenance']!=control['provenance']:
                raise ValueError('source model/binary changed between matched experiments')
            levels[name]=dict(trajectory=trajectory,summary=summarize(trajectory,onset),
                schedule=copy.deepcopy(interventions[name]),schedule_sha256=digest(interventions[name]),
                variant_audio_sha256=result['input_hashes']['audio_sha256'])
        del storage
    return dict(schema_version=1,status='computed',uses_rendered_reference=False,appearance_accuracy_verified=False,
        control_repeat_identical=True,control_sha256=control_hash.hexdigest(),levels=levels,
        area_threshold=area_threshold,warmup_frames=warmup_frames,input_hashes=control['input_hashes'],
        provenance=control['provenance'],
        intervention_scope='Bass/bass_att plus their native-derived vol/vol_att; waveform/spectrum and other bands unchanged',
        units='Mean absolute normalized RGB difference across the whole predicted screen; area is included in magnitude',
        limitations=['Source-model counterfactual, not validated native screen response',
                     'Only these inputs, dose schedules, state and sampled duration',
                     'No nonlinear response should be extrapolated from a single dose'])
