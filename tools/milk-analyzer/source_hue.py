"""Native composite four-corner hue recipe; no fragment colours are guessed."""
import numpy as np


def composite_hue_recipe(field):
    from source_appearance import _packed_reads
    from source_uniforms import NATIVE_TIME_INPUT
    components=sorted(_packed_reads(field).get('_vDiffuse',set())&{0,1,2})
    if not components:return None
    f=lambda x:float(np.float32(x))
    bias=f(.6);amplitude=f(.3)
    low=.5+.5*(bias-amplitude)/(bias+amplitude)
    return {'policy':'source31-native-composite-hue-v1','generator_code':10,
        'consumed_rgb_components':components,'nominal_unwrapped_clock_input':NATIVE_TIME_INPUT,
        'raw_corner':{'bias_rgb':[bias]*3,'amplitude_rgb':[amplitude]*3,
            'angular_rate_rad_per_second_rgb':[30*f(x) for x in (.0143,.0107,.0129)],
            'rate_expression':'renderContext.time*float32(30)*float32(rate_constant)',
            'rate_constants_rgb':[f(x) for x in (.0143,.0107,.0129)],
            'base_phase_offsets_rgb':[3,1,6],'corner_phase_steps_rgb':[21,13,9],
            'random_offset_indices_rgb':[3,1,2],
            'phase_expression':'time*30*rate_constant + base_phase + corner_index*corner_step + preset_random_phase'},
        'normalization':{'operation':'0.5+0.5*(raw_channel/max(raw_rgb))',
                         'scope':'each of four corners independently; channels become coupled'},
        'corner_count':4,'corner_weights':['x*y','(1-x)*y','x*(1-y)','(1-x)*(1-y)'],
        'vertex_weight_coordinates':'x=vertex_position.x*.5+.5,y=vertex_position.y*.5+.5',
        'spatial_interpolation':'corner blend at composite mesh vertices, then triangle interpolation',
        'fragment_bilinear_evaluation_is_exact':False,
        'nominal_input_range_rgb':[[low,1.] for _ in range(3)],'nominal_alpha':1.,
        'random_phase_values':None,'random_phase_lifetime':'preset instance, selected at initialization',
        'actual_palette':None,'final_multicolour_guaranteed':False,'observed_runtime_binding':False,
        'conditions':['Finite phase inputs and valid source domains required; nominal bounds omit float32/transcendental/interpolation error',
                      'Random phases and actual render clock/context are external inputs, not invented source constants',
                      'Grid topology/projection and GPU triangle interpolation determine fragment hue, not direct per-pixel bilinear evaluation',
                      'Only consumed RGB lanes contribute; authored powers, masks, permutations, textures and later processing determine final palette',
                      'No visible flashing, warm/cold mood, dominance or complete scene reconstruction is certified']}
