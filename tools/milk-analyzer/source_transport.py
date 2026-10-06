"""Restricted inverse-map feedback transport, independent of image contents."""
import numpy as np
import math


def linear_feedback_bounds(gain,*,fps,initial_bound,injection_bound,steps):
    """For an explicitly supplied scalar linear recurrence, not arbitrary milk.

    Assumption: a norm-nonexpansive transport and |J|≤injection_bound. This helper
    does not prove that a preset implements that recurrence or has visible trails.
    """
    values=(gain,fps,initial_bound,injection_bound)
    if any(isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) for value in values):
        raise ValueError('finite scalar feedback parameters required')
    if not 0<gain<1 or fps<=0 or initial_bound<0 or injection_bound<0 or type(steps) is not int or steps<0:
        raise ValueError('contracting scalar recurrence and nonnegative bounds required')
    decay=math.exp(steps*math.log(gain))
    accumulated=-math.expm1(steps*math.log(gain))/(1-gain)
    old_term=decay*initial_bound;new_term=injection_bound*accumulated
    if initial_bound>0 and old_term==0:
        raise ValueError('positive feedback state underflow; numeric domain unresolved')
    if injection_bound>0 and steps>0 and new_term==0:
        raise ValueError('positive feedback injection underflow; numeric domain unresolved')
    bound=old_term+new_term
    asymptotic=injection_bound/(1-gain)
    half_life=(math.log(.5)/math.log(gain))/fps
    if half_life==0:raise ValueError('positive half-life underflow; numeric domain unresolved')
    if not all(math.isfinite(value) for value in (bound,asymptotic,half_life)):
        raise ValueError('feedback-bound numeric domain unresolved')
    return {'half_life_s':half_life,'state_bound_after_steps':bound,
            'asymptotic_state_bound':asymptotic,'steps':steps,
            'source_recurrence_proved':False,'visible_trails_established':False,
            'assumption':'scalar constant gain; norm-nonexpansive transport; bounded injection',
            'limitations':['Not inferred from fDecay or an arbitrary feedback shader',
                           'Nonlinear gain, clipping, composite visibility and source recurrence proof remain separate']}


def affine_transport(matrix,offset,positions,*,dt,boundary='unwrapped'):
    """For query W(p)=A*p+b, an old feature x appears at A⁻¹(x−b).

    This is potential transport per update, not visible motion. Texture wrapping,
    clamping, appearance/injection and nonlinear maps require separate models.
    """
    if boundary!='unwrapped':raise ValueError('feedback boundary policy not modeled')
    if isinstance(dt,bool) or not np.isfinite(dt) or dt<=0:raise ValueError('positive finite transport interval required')
    a=np.asarray(matrix,dtype=np.float64);b=np.asarray(offset,dtype=np.float64)
    p=np.asarray(positions,dtype=np.float64)
    if a.shape!=(2,2) or b.shape!=(2,) or p.ndim!=2 or p.shape[1]!=2 or not len(p):
        raise ValueError('2D affine map and nonempty positions required')
    if not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)) or not np.all(np.isfinite(p)):
        raise ValueError('finite affine transport inputs required')
    try:
        if not np.isfinite(np.linalg.cond(a)) or np.linalg.cond(a)>1e12:
            raise ValueError('invertible affine map within numeric domain required')
        next_positions=np.linalg.solve(a,(p-b).T).T
    except np.linalg.LinAlgError as error:
        raise ValueError('invertible affine map required') from error
    with np.errstate(all='ignore'):
        velocity=(next_positions-p)/dt
        speeds=np.hypot(velocity[:,0],velocity[:,1])
    if not np.all(np.isfinite(next_positions)) or not np.all(np.isfinite(speeds)):
        raise ValueError('affine transport numeric domain unresolved')
    return {'basis':'strict-source-no-display-frames','uses_display_fields':False,
            'next_positions':next_positions.tolist(),'velocity':velocity.tolist(),
            'speed_p95_vp_s':float(np.percentile(speeds,95)),
            'maximum_speed_vp_s':float(speeds.max()),'query_count':len(p),
            'points_exiting_viewport':int(np.any((next_positions<0)|(next_positions>1),axis=1).sum()),
            'visible_motion_established':False,'boundary':boundary,
            'limitations':['Potential transport of supplied positions, not screen-area or visibility evidence',
                           'A static nonidentity feedback map can move content each update',
                           'No wrapping/clamping, injection, colour/composite or nonlinear-map inference']}
