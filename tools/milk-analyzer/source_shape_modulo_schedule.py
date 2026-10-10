"""Restricted nominal time schedules of shape colour-modulo boundaries."""
import math
from fractions import Fraction


def modulo_schedule(curve,period,*,native_singleton=False):
    result={'policy':'source-shape-nominal-modulo-crossings-v1','nominal_crossing_event_rate_hz':None,
        'period_seconds':None,'strict_boundary_count':None,'crossings':[],
        'native_event_timing_verified':False,'visible_flash_frequency_hz':None,'unknown_reasons':[],
        'conditions':['Supported nominal continuous source-time curve under finite source/intermediate/native-conversion premises',
            'Only strict crossings are counted; tangent contacts and native two-ULP preboundary resets are not quantified',
            'This is one channel schedule; simultaneous channel/shape events cannot simply be added',
            'Clock resets, float32 conversion/remainder rounding and frame sampling can change or miss events',
            'Opacity, geometry, destination and subsequent feedback/composition determine visibility; no flash-safe or mood certificate']}
    if native_singleton:
        result['unknown_reasons']=['native endpoint conversion freezes this supplied channel domain'];return result
    try:
        if curve['curve_kind']=='linear_time':
            rate=curve['signed_linear_rate_per_second'];bias=curve['offset_value']
            if rate in (None,0) or bias is None:raise ValueError('nonzero finite affine source-time curve required')
            duration=period/abs(rate);frequency=abs(rate)/period
            if not all(math.isfinite(v) and v>0 for v in (duration,frequency)):
                raise ValueError('affine modulo schedule numeric domain unresolved')
            offset=(-bias/rate)%duration
            result.update(nominal_crossing_event_rate_hz=frequency,period_seconds=duration,
                crossings=[{'kind':'affine_modulo_cell_crossings','event_offsets_seconds_mod_period':[offset] if math.isfinite(offset) else None,
                    'events_per_period':1,'signed_raw_rate_per_second':rate}])
            return result
        if curve['curve_kind']!='sinusoidal_time':raise ValueError('no supported nonconstant continuous time oscillator')
        bias=curve['offset_value'];amplitude=curve['amplitude_value'];omega=curve['angular_phase_rate_rad_per_second']
        phase=curve['phase_offset_rad'];duration=curve['period_seconds']
        if amplitude==0 or omega==0:raise ValueError('nonconstant oscillator required')
        low=Fraction(bias)-abs(Fraction(amplitude));high=Fraction(bias)+abs(Fraction(amplitude));p=Fraction(period)
        first=low//p+1;last=-((-high)//p)-1;count=max(0,last-first+1)
        if count>16:raise ValueError('more than 16 strict modulo boundaries; schedule remains unquantified')
        if count==0:raise ValueError('no strict nominal boundary crossing; tangent/native events remain separate')
        rows=[]
        for k in range(first,last+1):
            threshold=float(k*p);level=float((k*p-Fraction(bias))/Fraction(amplitude))
            if not math.isfinite(threshold) or not -1<level<1:
                raise ValueError('oscillator crossing threshold numeric domain unresolved')
            if curve['oscillator_function_code']==1:
                root=math.acos(level);angles=(root,math.tau-root)
            else:
                root=math.asin(level);angles=(root%math.tau,(math.pi-root)%math.tau)
            offsets=sorted(((a-phase)/omega)%duration for a in angles)
            rows.append({'kind':'oscillatory_modulo_cell_crossings','cell_boundary_index':k,
                'raw_boundary_value':threshold,'events_per_period':2,
                'event_offsets_seconds_mod_period':offsets if all(math.isfinite(v) for v in offsets) and offsets[0]!=offsets[1] else None})
        frequency=count*2/duration
        if not math.isfinite(frequency) or frequency<=0:raise ValueError('oscillator event rate numeric domain unresolved')
        result.update(nominal_crossing_event_rate_hz=frequency,period_seconds=duration,
            strict_boundary_count=count,crossings=rows)
    except (ValueError,OverflowError,ZeroDivisionError,TypeError) as error:
        result['unknown_reasons']=[str(error)]
    return result
