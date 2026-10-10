"""Independent texture-input RGB boxes/norms, not history recurrence proofs."""
import math
from fractions import Fraction

HISTORY={'main','blur1','blur2','blur3'}


def _rounded(value,direction):
    number=float(value)
    if not math.isfinite(number) or value!=0 and number==0:
        raise ValueError('texture colour envelope overflow or underflow')
    if direction<0 and Fraction(number)>value or direction>0 and Fraction(number)<value:
        number=math.nextafter(number,direction)
    if not math.isfinite(number):raise ValueError('texture colour envelope outward rounding overflow')
    return number


def texture_colour_envelopes(transfer):
    stages={}
    for stage,source in transfer['stages'].items():
        r={'source_model':'unknown','all_texture_colour_difference_gain':None,
            'main_or_blur_input_difference_gain':None,'external_texture_input_difference_gain':None,
            'raw_rgb_bounds_if_samples_unit_interval':None,'history_textures':[],
            'external_textures':[],'coordinate_sample_dependency':source['coordinate_sample_dependency'],
            'whole_feedback_contraction':None,'actual_feedback_persistence':None,
            'full_colour_sensitivity':None,'unknown_reasons':[]}
        try:
            if source['source_model']!='affine_sample_colour':raise ValueError('source affine texture mixture unresolved')
            samples=source['sample_contributions'];offset=source['constant_offset_rgb'];uv=source['base_uv_matrix_rgb']
            groups={'all':[Fraction(0)]*3,'history':[Fraction(0)]*3,'external':[Fraction(0)]*3}
            low=[Fraction(0)]*3;high=[Fraction(0)]*3;history=set();external=set()
            for sample in samples:
                texture=sample['canonical_texture']
                if not isinstance(texture,str):raise ValueError('sample texture identity unresolved')
                group='history' if texture in HISTORY else 'external'
                (history if group=='history' else external).add(texture)
                matrix=sample['matrix_rgb_rgba']
                if len(matrix)!=3 or any(len(row)!=4 for row in matrix):raise ValueError('sample colour matrix shape invalid')
                for row,coefficients in enumerate(matrix):
                    for coefficient in coefficients:
                        if not math.isfinite(coefficient):raise ValueError('sample colour coefficient is nonfinite')
                        c=Fraction(coefficient);groups['all'][row]+=abs(c);groups[group][row]+=abs(c)
                        low[row]+=min(c,0);high[row]+=max(c,0)
            r.update(source_model='bounded_affine_texture_inputs',
                all_texture_colour_difference_gain=_rounded(max(groups['all']),math.inf),
                main_or_blur_input_difference_gain=_rounded(max(groups['history']),math.inf),
                external_texture_input_difference_gain=_rounded(max(groups['external']),math.inf),
                history_textures=sorted(history),external_textures=sorted(external))
            if uv is None or any(v!=0 for row in uv for v in row):
                r['unknown_reasons'].append('RGB has coordinate terms without a supplied finite coordinate domain')
            elif offset is None or len(offset)!=3 or any(v is None or not math.isfinite(v) for v in offset):
                r['unknown_reasons'].append('source RGB offset is not a finite supported constant')
            else:
                r['raw_rgb_bounds_if_samples_unit_interval']=[
                    [_rounded(low[i]+Fraction(offset[i]),-math.inf),_rounded(high[i]+Fraction(offset[i]),math.inf)]
                    for i in range(3)]
        except (ValueError,OverflowError,TypeError) as error:
            r['unknown_reasons'].append(str(error))
        stages[stage]=r
    return {'policy':'source-independent-texture-colour-envelope-v1','stages':stages,
        'scope':'raw per-stage colour with sample positions and non-texture inputs fixed',
        'uses_equation_execution':False,'uses_shader_execution':False,'uses_rendered_images':False,
        'conditions':['Each directly sampled RGBA component independently lies in [0,1]; premise is not certified by source',
                      'Nominal real-valued affine coefficients before native rounding/storage; sites remain independent',
                      'Texture identities are source contracts, not observed GPU bindings or missing-texture fallback decisions',
                      'Main/blur input norm treats different histories as independent; it is not the gain of a resolved shared recurrence',
                      'External textures stay fixed for a history-only comparison; random selection epochs/asset changes are separate inputs',
                      'Image-dependent coordinates, blur kernels/history normalization, clipping, drawing/detail and final display remain separate',
                      'No visible sharpness, persistence, brightness, palette or mood certificate follows from these conditional boxes/norms']}
