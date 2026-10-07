"""Check temporal colour statements against numerical source-predicted RGB.

This validates explicit predicates over every claimed frame. It does not parse
free-form prose, inspect native references or certify structure/motion claims.
"""
import hashlib
import numpy as np


def validate_colour_claim(rgb,*,frame_numbers,claimed_frames,lower_rgb,upper_rgb,minimum_area):
    values=np.asarray(rgb)
    if values.dtype!=np.uint8 or values.ndim!=4 or values.shape[-1]!=3 or any(n<=0 for n in values.shape):
        raise ValueError('nonempty uint8 frame RGB arrays required')
    def ordered(ids):
        return isinstance(ids,list) and all(type(n) is int and n>0 for n in ids) and ids==sorted(set(ids))
    if not ordered(frame_numbers) or len(frame_numbers)!=len(values):raise ValueError('ordered unique frame IDs required')
    if not claimed_frames:raise ValueError('nonempty claimed frames required')
    if not ordered(claimed_frames) or not set(claimed_frames)<=set(frame_numbers):
        raise ValueError('ordered claimed frame IDs must belong to supplied frames')
    lo=np.asarray(lower_rgb,dtype=float);hi=np.asarray(upper_rgb,dtype=float)
    if lo.shape!=(3,) or hi.shape!=(3,) or not np.all(np.isfinite([lo,hi])) or np.any(lo<0) or np.any(hi>1) or np.any(lo>hi):
        raise ValueError('finite ordered normalized RGB bounds required')
    if type(minimum_area) not in (int,float) or not np.isfinite(minimum_area) or not 0<minimum_area<=1:
        raise ValueError('minimum colour area in (0,1] required')
    normalized=values.astype(np.float64)/255
    coverage=np.all((normalized>=lo)&(normalized<=hi),axis=-1).mean(axis=(1,2))
    table={str(n):float(v) for n,v in zip(frame_numbers,coverage)}
    failed=[n for n in claimed_frames if table[str(n)]<minimum_area]
    if failed:raise ValueError('colour claim unsupported on frames '+', '.join(map(str,failed)))
    return {'basis':'numerical RGB predicate; source-only arrays supplied by caller',
            'rgb_sha256':hashlib.sha256(values.tobytes()).hexdigest(),
            'frame_numbers':frame_numbers.copy(),'claimed_frames':claimed_frames.copy(),
            'coverage_by_frame':table,'matched_frames':[n for n,v in zip(frame_numbers,coverage) if v>=minimum_area],
            'lower_rgb':lo.tolist(),'upper_rgb':hi.tolist(),'minimum_area':minimum_area,
            'claimed_frames_verified':True}


def describe_colour_presence(result,*,label):
    ids=result.get('claimed_frames');table=result.get('coverage_by_frame');minimum=result.get('minimum_area')
    if (result.get('claimed_frames_verified') is not True or not isinstance(ids,list) or not ids or
            any(type(n) is not int or n<=0 for n in ids) or ids!=sorted(set(ids)) or
            not isinstance(table,dict) or type(minimum) not in (int,float) or
            not np.isfinite(minimum) or not 0<minimum<=1 or
            any(type(table.get(str(n))) not in (int,float) or not np.isfinite(table[str(n)]) or
                not minimum<=table[str(n)]<=1 for n in ids)):
        raise ValueError('verified colour coverage required before formatting')
    frames=', '.join(map(str,result['claimed_frames']))
    return f"A {label} field occupies at least {result['minimum_area']*100:g}% of the screen on frames {frames}."
