"""Code-derived transfer-function properties; these helpers do not inspect images.

These are exact answers for their declared reduced models, not a replacement for
interpreting an arbitrary shader's spatial/colour state. Callers must establish
the reduction and carry its assumptions into the prediction.
"""
import math
import cmath


def clipped_affine_feedback(*,gain:float,injection:float)->dict:
    """Analyze x_next=clamp(gain*x+injection,0,1) for nonnegative gain."""
    if not math.isfinite(gain) or not math.isfinite(injection) or gain<0:
        raise ValueError("finite nonnegative gain and finite injection required")
    if gain>=1:
        return {"status":"noncontractive","fixed_point":None,"half_life_frames":None}
    return {"status":"contractive","fixed_point":max(0,min(1,injection/(1-gain))),
            "half_life_frames":math.log(.5)/math.log(gain) if gain else 0,
            "settling_90_percent_frames":math.log(.1)/math.log(gain) if gain else 0}


def inverse_sqrt_ridge(*,numerator:float,root_bias:float,
                      constant_injection:float,output_scale:float)->dict:
    """Support of a positive seed c+scale*k/(sqrt(s)+bias), s>=0.

Negative s is a distinct undefined sqrt domain, not an extrapolated smooth field.
"""
    values=(numerator,root_bias,constant_injection,output_scale)
    if any(not math.isfinite(v) for v in values) or numerator<0 or root_bias<=0 or output_scale<0:
        raise ValueError("finite positive denominator and nonnegative numerator/scale required")
    if constant_injection==0 and output_scale*numerator==0:
        support_end=0
    elif constant_injection>=0:
        support_end=math.inf
    else:
        threshold=output_scale*numerator/(-constant_injection)-root_bias
        support_end=threshold**2 if threshold>0 else 0
    return {"positive_support_end":support_end,"undefined_domain":"coordinate < 0",
            "orientation":"normal of the scalar coordinate being square-rooted"}


def delayed_affine_feedback(*,recent_gain:float,older_gain:float,injection:float)->dict:
    """Local analysis of x[t]=a*x[t-1]+b*x[t-2]+j, before clipping.

    This does not establish global stability of clipped, spatial, multichannel
    shaders. Negative coefficients in particular prevent a contraction claim
    based only on the unsaturated characteristic roots.
    """
    if any(not math.isfinite(v) for v in (recent_gain,older_gain,injection)):
        raise ValueError("finite coefficients required")
    discriminant=cmath.sqrt(recent_gain**2+4*older_gain)
    roots=((recent_gain+discriminant)/2,(recent_gain-discriminant)/2)
    radius=max(abs(root) for root in roots)
    denominator=1-recent_gain-older_gain
    return {"status":"locally_stable" if radius<1 else "locally_unstable_or_neutral",
            "validity":"unsaturated linear recurrence only",
            "coefficients":{"frame_minus_1":recent_gain,"frame_minus_2":older_gain},
            "fixed_point":injection/denominator if denominator else None,
            "characteristic_roots":[{"real":r.real,"imaginary":r.imag} for r in roots],
            "spectral_radius":radius,
            "asymptotic_half_life_frames":math.log(.5)/math.log(radius) if 0<radius<1 else (0 if radius==0 else None)}
