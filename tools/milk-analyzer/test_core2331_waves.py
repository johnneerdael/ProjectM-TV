"""Release31 waveform contracts; numerical adapters only, no renderer inputs."""
import json
import hashlib
import os
from pathlib import Path
import subprocess

import numpy as np
import pytest

from builtin_wave import _colour, source_builtin_wave
from custom_wave import source_custom_waves
from engine_profiles import CORE_2329_ENGINE, CORE_2331_ENGINE
from test_native_wave import frame


ROOT = Path(__file__).resolve().parents[2]
NEW = Path(os.environ.get('MILK_TEST_2331_BINARIES', ROOT/'build/preset-corpus/source31/adapters'))
OLD = Path(os.environ.get('MILK_TEST_2329_BINARIES', ROOT/'build/preset-corpus/source29/adapters'))


def source(engine=CORE_2331_ENGINE, **settings):
    return {'values': {key: str(value) for key, value in settings.items()},
            'parser_inputs': {'engine': engine}}


def colour(*, engine=CORE_2331_ENGINE, mode=0, alpha=.2, volume=1.05,
           rgb=(.2, .4, .6), brighten=0, modulate=1, start=.75, end=.95):
    return _colour(source(engine, bModWaveAlphaByVolume=modulate,
                          fModWaveAlphaStart=start, fModWaveAlphaEnd=end),
                   {**{'wave_'+c: v for c, v in zip('rgb', rgb)}, 'wave_brighten': brighten},
                   {'vol': volume, 'treb': 1}, mode, alpha, 512, 288,
                   mode1_alpha_boost=True)


@pytest.mark.parametrize('mode,expected', [(0, .3), (1, .375), (2, .054), (5, .054)])
def test_volume_ramp_multiplies_mode_adjusted_alpha_without_upper_bound(mode, expected):
    alpha = .4 if mode in (2, 5) else .2
    assert colour(mode=mode, alpha=alpha)[3] == pytest.approx(expected, abs=1e-7)
    assert colour(engine=CORE_2329_ENGINE, mode=mode, alpha=alpha)[3] == pytest.approx(
        alpha*1.25 if mode == 1 else alpha)


def test_mode3_canvas_base_replaces_authored_alpha_before_treble_and_volume():
    assert colour(mode=3, alpha=.2)[3] == colour(mode=3, alpha=.8)[3]
    assert colour(mode=3, alpha=.2)[3] == pytest.approx(.15*1.3*1.5, abs=1e-7)
    assert colour(engine=CORE_2329_ENGINE, mode=3, alpha=.2, modulate=0)[3] != colour(
        engine=CORE_2329_ENGINE, mode=3, alpha=.8, modulate=0)[3]


def test_mode1_boost_precedes_volume_in_float32_operation_order():
    assert colour(mode=1, alpha=.3, volume=.8)[3] == float(np.float32(.09375002980232239))
    assert colour(engine=CORE_2329_ENGINE, mode=1, alpha=.3, volume=.8)[3] == float(np.float32(.09375004470348358))


@pytest.mark.parametrize('volume,start,end,expected', [(.85,.75,.95,.018),
    (.65,.75,.95,0), (.85,.95,.75,.018), (1.05,.95,.75,0)])
def test_low_volume_and_reversed_ramp_preserve_mode_attenuation(volume, start, end, expected):
    assert colour(mode=2, alpha=.4, volume=volume, start=start, end=end)[3] == pytest.approx(expected, abs=1e-7)


def test_no_modulation_retains_mode_alpha_and_zero_denominator_stays_unresolved():
    assert colour(mode=2, alpha=.4, modulate=0)[3] == pytest.approx(.036, abs=1e-7)
    with np.errstate(invalid='ignore', divide='ignore'):
        with pytest.raises(ValueError, match='colour/opacity'):
            colour(volume=.75, start=.75, end=.75)


@pytest.mark.parametrize('rgb,brighten,expected', [((-.2,.5,2),0,(0,.5,1)),
    ((-.2,.5,2),-1,(0,.5,1)), ((.2,.4,.6),-1,(1/3,2/3,1)),
    ((.002,.004,.01),-1,(.002,.004,.01)), ((.2,.4,.6),-0.,(.2,.4,.6))])
def test_rgb_clamps_before_any_nonzero_brightening(rgb, brighten, expected):
    np.testing.assert_allclose(colour(rgb=rgb, brighten=brighten, modulate=0)[:3], expected, atol=1e-7)
    np.testing.assert_allclose(colour(engine=CORE_2329_ENGINE, rgb=rgb, brighten=brighten,
                                    modulate=0)[:3], rgb, atol=1e-7)


def test_nonfinite_rgb_is_unresolved_after_ordered_comparisons():
    with pytest.raises(ValueError, match='colour/opacity'):
        colour(rgb=(np.nan, .4, .6), modulate=0)


def custom_scene(points):
    return {'viewport': [128,72], 'frames': [{'waves': [{'index': 0, 'points': points}]}]}


def point(x, y):
    return {'x': x, 'y': y, 'r': .5, 'g': .25, 'b': 0, 'a': 1}


def test_custom_dots_preserve_authored_count_and_colours_while_lines_still_smooth():
    scene = custom_scene([point(.1,.2), point(.6,.8), point(.9,.3)])
    dots = source_custom_waves(source(wavecode_0_bUseDots=1), scene)['frames'][0][0]
    assert len(dots['positions']) == len(dots['colours']) == 3
    old = source_custom_waves(source(CORE_2329_ENGINE, wavecode_0_bUseDots=1), scene)['frames'][0][0]
    line = source_custom_waves(source(), scene)['frames'][0][0]
    assert len(old['positions']) == len(line['positions']) == 5
    assert source_custom_waves(source(wavecode_0_bUseDots=1), scene)['dot_submission_policy'] == 'projectmtv-core-2.3.31-authored-custom-dots-v1'


def test_custom_single_finite_dot_ignores_nan_input_but_nonfinite_output_stays_unresolved():
    scene = custom_scene([{**point(.3,.7), 'sample': {'ieee': 'nan'}}])
    assert len(source_custom_waves(source(wavecode_0_bUseDots=1), scene)['frames'][0][0]['positions']) == 1
    assert source_custom_waves(source(), scene)['frames'][0] == []
    assert source_custom_waves(source(wavecode_0_bUseDots=1), custom_scene([]))['frames'][0] == []
    scene['frames'][0]['waves'][0]['points'][0]['x'] = {'ieee': 'nan'}
    with pytest.raises(ValueError, match='unresolved|nonfinite'):
        source_custom_waves(source(wavecode_0_bUseDots=1), scene)


def adapter(folder, name):
    binary = folder/name
    if not binary.is_file():
        pytest.skip(f'prepared adapter required: {binary}')
    return binary


def execute_wave(folder, tmp_path, mode=0, *, live=False, frames=None, **options):
    output=tmp_path/'wave.json'; request=tmp_path/'wave-request.json'
    request.write_text(json.dumps({'mode': mode, 'mode_policy': 'evaluated-live-v1' if live else 'static-v1',
        'width':512,'height':288,'output':str(output),'frames':frames or [frame(time=1,wave_mode=mode)], **options}))
    process=subprocess.run([str(adapter(folder,'milk-wave-inputs')),str(request)], capture_output=True, text=True)
    assert process.returncode == 0, process.stderr
    result=json.loads(output.read_text())
    assert result['engine_identity'] == (CORE_2331_ENGINE if folder==NEW else CORE_2329_ENGINE)
    return result


def test_exact_release31_wave_adapter_accepts_live_controls(tmp_path):
    result = execute_wave(NEW, tmp_path, 6, live=True)
    assert result['engine_identity'] == CORE_2331_ENGINE
    assert result['frames'][0]['mode'] == 6


@pytest.mark.parametrize('mode,width,new_count,old_count', [(4,512,339,319),
    (6,512,339,159),(7,512,339,159),(4,1024,681,319),(6,1024,479,479),
    (6,5,3,159),(8,512,511,511)])
def test_native_line_caps_are_inherited_from_exact_copied_bodies(tmp_path, mode, width, new_count, old_count):
    current = execute_wave(NEW,tmp_path,mode,width=width)['frames'][0]
    old = execute_wave(OLD,tmp_path,mode,width=width)['frames'][0]
    assert len(current['vertex_waves'][0]) == new_count
    assert len(old['vertex_waves'][0]) == old_count


def test_native_4k_line_decisions_keep_reference_width_and_circle_closes_explicitly(tmp_path):
    result = execute_wave(NEW,tmp_path,6,width=3840,height=2160,line_reference_width=512,line_reference_height=288)
    assert len(result['frames'][0]['vertex_waves'][0]) == 339
    current = execute_wave(NEW,tmp_path,0)['frames'][0]
    old = execute_wave(OLD,tmp_path,0)['frames'][0]
    assert not current['closed_loop'] and len(current['vertex_waves'][0]) == 481
    assert old['closed_loop'] and len(old['vertex_waves'][0]) == 479
    assert current['vertex_waves'][0][0] == current['vertex_waves'][0][-1]
    assert current['vertex_waves'][0][2] != old['vertex_waves'][0][2]


def test_native_wave_body_hashes_bind_line_caps_and_circle_closure(tmp_path):
    report=execute_wave(NEW,tmp_path)
    for name in ['Waveforms/Circle.cpp','Waveforms/DerivativeLine.cpp','Waveforms/Line.cpp','Waveforms/DoubleLine.cpp']:
        original=NEW.parent/'production-engine/src/libprojectM/MilkdropPreset'/name
        adapted=NEW/'cpu-wave-source'/name
        assert report['source_hashes'][name] == {'original':hashlib.sha256(original.read_bytes()).hexdigest(),
                                               'adapted':hashlib.sha256(adapted.read_bytes()).hexdigest()}


@pytest.mark.parametrize('width,height,mystery', [(512,288,.3),(288,512,-.2)])
def test_circle_closure_retains_asymmetric_audio_and_mystery_geometry(tmp_path,width,height,mystery):
    data=frame(time=10001.123456789,wave_mode=0,wave_x=.3,wave_y=.7,wave_mystery=mystery,
               waveform_right=(np.sin(np.arange(480)*.031)*10).tolist())
    result=execute_wave(NEW,tmp_path,frames=[data],width=width,height=height)
    positions=result['frames'][0]['vertex_waves'][0]
    assert len(positions)==481 and positions[-1]==positions[0]
    assert positions[2]!=positions[-3]


def wave_points(folder, tmp_path, *, count=100, separation=20, dots=False, spectrum=False,
                smoothing=0, left=None, right=None, code='x=value1;y=value2;'):
    request=tmp_path/'point-request.json'; maximum=512 if spectrum else 480
    request.write_text(json.dumps({'programs': {'frame': 'r=r;', 'point': code}, 'steps': [
        {'program':'frame','variables':{'samples':count,'r':1,'g':1,'b':1,'a':1}},
        {'program':'point','capture':['sample','value1','value2','x','y','r','g','b','a'],
         'wave_points': {'frame_program':'frame','spectrum':spectrum,'dots':dots,'separation':separation,
            'smoothing':smoothing,'scaling':1,'preset_wave_scale':1,'left':left if left is not None else list(range(maximum)),
            'right':right if right is not None else list(range(maximum))}}]}))
    process=subprocess.run([str(adapter(folder,'milk-native-reader')),'--equations',str(request)], capture_output=True,text=True)
    assert process.returncode == 0, process.stderr
    return json.loads(process.stdout)['steps'][1]['points']


@pytest.mark.parametrize('count,sep,left,right', [(100,20,180,200),(100,-3,191,189),
    (480,0,0,0),(100,1000,0,0),(500,20,0,0),(1,0,239,239)])
def test_custom_centered_channel_windows_and_invalid_fallback(tmp_path, count, sep, left, right):
    points = wave_points(NEW,tmp_path,count=count,separation=sep,dots=count==1)
    assert points[0]['value1'] == pytest.approx(np.float32(left)*np.float32(.004))
    assert points[0]['value2'] == pytest.approx(np.float32(right)*np.float32(.004))
    if count > 1:
        old=wave_points(OLD,tmp_path,count=count,separation=sep)
        assert old[0]['value1'] == old[0]['value2'] == 0
    if count > 480:
        assert points[-1]['value1'] == pytest.approx(np.float32(479)*np.float32(.004))


def test_spectrum_input_retains_stride_and_separation_clamps(tmp_path):
    for sep in [-3,20,1000]:
        assert wave_points(NEW,tmp_path,separation=sep,spectrum=True) == wave_points(
            OLD,tmp_path,separation=sep,spectrum=True)


def test_channel_windows_precede_both_smoothing_passes(tmp_path):
    left=(np.sin(np.arange(480)*.17)*10).tolist()
    right=(np.cos(np.arange(480)*.11)*7).tolist()
    current=wave_points(NEW,tmp_path,smoothing=.75,left=left,right=right)
    # Feed the historical prefix loop the same centered slices. Matching every
    # point discriminates offsets applied only to the first or forward sample.
    prefix=wave_points(OLD,tmp_path,smoothing=.75,left=np.roll(left,-180).tolist(),
                       right=np.roll(right,-200).tolist())
    assert current==prefix


def test_single_dot_reader_supplies_nan_sample_and_executes_overwriting_program(tmp_path):
    points=wave_points(NEW,tmp_path,count=1,dots=True,code='x=.25;y=.75;r=1;g=.5;b=0;a=1;')
    assert len(points) == 1 and points[0]['sample'] == {'ieee':'nan'}
    assert [points[0][c] for c in ('x','y','r','g','b','a')] == [.25,.75,1,.5,0,1]
    assert wave_points(NEW,tmp_path,count=1,dots=False) == []
    assert wave_points(OLD,tmp_path,count=1,dots=True) == []
    assert wave_points(NEW,tmp_path,count=0,dots=True) == []
    consuming=wave_points(NEW,tmp_path,count=1,dots=True,code='x=sample;')
    assert consuming[0]['x'] == {'ieee':'nan'}


@pytest.mark.parametrize('alpha,omitted', [(.003999,True),(.004,False),(.004001,False)])
def test_builtin_submission_threshold_and_raw_frame_retention(tmp_path, alpha, omitted):
    from scene_equations import execute_scene
    from test_scene_equations import frames
    from test_builtin_wave import audio
    preset=tmp_path/'threshold.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=6\n'
                     f'fWaveAlpha={alpha}\nper_frame_1=wave_mode=6;wave_a={alpha};wave_r=-.2;wave_g=.5;wave_b=2;wave_brighten=-1;\n')
    process=subprocess.run([str(adapter(NEW,'milk-native-reader')),str(preset)],capture_output=True,text=True)
    assert process.returncode == 0, process.stderr
    current=json.loads(process.stdout)
    inputs=frames()[:1]
    scene=execute_scene(current,inputs,reader=NEW/'milk-native-reader',width=128,height=72,mesh_x=8,mesh_y=8)
    main=scene['frames'][0]['main'].copy()
    result_report=source_builtin_wave(current,scene,audio(inputs),binary=NEW/'milk-wave-inputs')
    assert result_report['appearance_policy'] == 'projectmtv-core-2.3.31-original-wave-appearance-v1'
    result=result_report['frames'][0]
    assert result['omitted'] is omitted
    assert bool(result['positions']) is not omitted
    assert result['rgba'][3] == pytest.approx(alpha)
    np.testing.assert_allclose(result['rgba'][:3],[0,.5,1])
    assert scene['frames'][0]['main'] == main


def test_builtin_dots_keep_the_shared_circle_smoothing(tmp_path):
    from scene_equations import execute_scene
    from test_scene_equations import frames
    from test_builtin_wave import audio
    preset=tmp_path/'circle-dots.milk'
    preset.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\n'
                     'per_frame_1=wave_mode=0;wave_usedots=1;wave_a=.5;\n')
    inputs=frames()[:1]
    counts=[]
    for folder in [NEW,OLD]:
        process=subprocess.run([str(adapter(folder,'milk-native-reader')),str(preset)],capture_output=True,text=True)
        assert process.returncode==0,process.stderr
        current=json.loads(process.stdout)
        scene=execute_scene(current,inputs,reader=folder/'milk-native-reader',width=128,height=72,mesh_x=8,mesh_y=8)
        result=source_builtin_wave(current,scene,audio(inputs),binary=folder/'milk-wave-inputs')['frames'][0]
        assert result['draw_mode']=='points'
        counts.append(len(result['positions'][0]))
    assert counts==[481,479]
