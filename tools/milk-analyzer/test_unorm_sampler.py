import json
from pathlib import Path
import numpy as np
import pytest


def test_apple_profile_matches_fresh_four_corner_packed_readbacks():
    from unorm_sampler import sample_apple_unorm8
    proof=json.loads((Path(__file__).parent/'fixtures/apple-gles-sampler-learning-2026-10-07.json').read_text())
    width,height=proof['dimensions'];x,y=np.meshgrid(np.arange(width)%2,np.arange(height)%2)
    texture=np.asarray(proof['corners'],np.float32)[y*2+x]/255
    for row in proof['observations']:
        case=proof['cases'][row['case']-1]
        uv=(np.array([16.5,16.5],np.float32)+np.asarray(case['phase'],np.float32))*np.array([1/width,1/height],np.float32)
        value=sample_apple_unorm8(texture,uv,wrap=True,linear=True,origin='top')[row['axis']]
        assert int(np.floor(value*16777216))==row['packed_bits']


def test_apple_volume_matches_fresh_noncubic_packed_readbacks():
    from unorm_sampler import sample_apple_volume_unorm8
    proof=json.loads((Path(__file__).parent/'fixtures/apple-gles-volume-sampler-learning-2026-10-07.json').read_text())
    width,height,depth=proof['frozen']['dimensions']
    corners=np.asarray(proof['frozen']['corners'],np.float32)
    z,y,x=np.indices((depth,height,width))
    volume=corners[z%2,y%2,x%2]/255
    for row in proof['observed']['results']:
        uv=proof['frozen']['records'][row['case']-1]['uv']
        value=sample_apple_volume_unorm8(volume,uv,wrap=True,linear=True)[row['axis']]
        assert abs(int(np.floor(value*16777216))-row['packed_bits'])<=1


def test_volume_profile_preserves_old_2d_guard_and_routes_material_volumes(tmp_path):
    from unorm_sampler import APPLE_VOLUME_PROFILE, sample_apple_volume_unorm8
    from noise_inputs import NoiseBank
    from materials import MaterialBank
    from test_materials import BINARY as decoder
    import hashlib
    pixels=np.array([0,8,16,24,32,40,48,56],np.uint8)
    raw=np.stack((pixels,pixels,pixels,np.full(8,255,np.uint8)),-1).tobytes()
    (tmp_path/'volume.bin').write_bytes(raw)
    (tmp_path/'manifest.json').write_text(json.dumps({'schema_version':1,'uses_rendered_reference':False,
        'packed_word_encoding':'uint32 little endian','native_upload_format':'RGBA',
        'textures':{'noisevol_hq':{'file':'volume.bin','dimensions':[2,2,2],
                                 'sha256':hashlib.sha256(raw).hexdigest()}}}))
    noise=NoiseBank(tmp_path);materials=MaterialBank([],decoder=decoder,noise_bank=noise)
    detail={'canonical_texture':'noisevol_hq','sampling_policy':{'wrap':True,'linear':True}}
    uv=np.array([[.25,.25,.25+.5/256/2]],np.float32)
    expected=sample_apple_volume_unorm8(noise.textures['noisevol_hq'],uv,wrap=True,linear=True)
    for bank in [noise,materials]:
        np.testing.assert_array_equal(bank.sample(detail,uv,sampling_profile=APPLE_VOLUME_PROFILE),expected)


def test_apple_volume_addressing_and_storage_guards():
    from unorm_sampler import sample_apple_volume_unorm8
    volume=np.zeros((2,2,2,4),np.float32);volume[...,3]=1;volume[1,0,1,:3]=[1,0,1]
    np.testing.assert_array_equal(sample_apple_volume_unorm8(volume,[1.75,-.75,1.75],
        wrap=True,linear=False),[1,0,1,1])
    np.testing.assert_array_equal(sample_apple_volume_unorm8(volume,[9,-9,9],
        wrap=False,linear=False),[1,0,1,1])
    for data,uv in [(np.full((2,2,2,4),.123),[.5,.5,.5]),
                    (volume,[.5,.5]),(volume,[float('inf'),.5,.5])]:
        with pytest.raises(ValueError):sample_apple_volume_unorm8(data,uv,wrap=True,linear=True)


def test_apple_volume_z_axis_halfway_rules_match_frozen_controls():
    from unorm_sampler import sample_apple_volume_unorm8
    proof=json.loads((Path(__file__).parent/'fixtures/apple-gles-volume-sampler-learning-2026-10-07.json').read_text())
    volume=np.zeros((4,4,4,4),np.float32);volume[...,3]=1;volume[1::2,...,:3]=8/255
    for row in proof['z_ties']['observed']['results']:
        phase=proof['z_ties']['frozen']['records'][row['case']-1]['phase_z']
        uv=(np.array([.5,.5,.5],np.float32)+[0,0,phase])/4
        value=sample_apple_volume_unorm8(volume,uv,wrap=True,linear=True)[row['axis']]
        assert abs(int(np.floor(value*16777216))-row['packed_bits'])<=1


def test_volume_coefficients_preserve_y_complements_at_discriminating_boundaries():
    from unorm_sampler import sample_apple_volume_unorm8
    proof=json.loads((Path(__file__).parent/'fixtures/apple-gles-volume-sampler-learning-2026-10-07.json').read_text())
    z,y,x=np.indices((4,4,4))
    for controls in proof['coefficient_controls']:
        corners=np.asarray(controls['corners'],np.float32)
        volume=corners[z%2,y%2,x%2]/255
        for observed in controls['observations']:
            fractions=controls['cases'][observed['case']-1]['fraction8']
            uv=(np.float32(.5)+np.asarray(fractions,np.float32)/256)/4
            value=sample_apple_volume_unorm8(volume,uv,wrap=True,linear=True)[observed['axis']]
            assert int(np.floor(value*16777216))==observed['packed_bits']


def test_apple_profile_rounds_coordinate_and_filtered_byte_ties_upward():
    from unorm_sampler import sample_apple_unorm8
    width,height=256,144;x,y=np.meshgrid(np.arange(width)%2,np.arange(height)%2)
    corners=np.array([[0,0,0,255],[8,0,8,255],[0,8,8,255],[8,8,0,255]],np.float32)
    texture=corners[y*2+x]/255
    proof=json.loads((Path(__file__).parent/'fixtures/apple-gles-sampler-learning-2026-10-07.json').read_text())
    for key,phases in [('raw_tie_controls',[1/256,3/256,5/256,7/256]),
                       ('coordinate_tie_controls',[.5/256,1.5/256,2.5/256,3.5/256])]:
        for row in proof[key]['observed']:
            uv=(np.array([16.5,16.5],np.float32)+[phases[row['case']-1],0])*np.array([1/width,1/height],np.float32)
            value=sample_apple_unorm8(texture,uv,wrap=True,linear=True,origin='top')[row['axis']]
            assert abs(int(np.floor(value*16777216))-row['packed_bits'])<=1


def test_apple_pipeline_profile_is_explicit_and_rejects_float_feedback():
    from pipeline_fields import SourcePipeline
    from unorm_sampler import APPLE_PROFILE, sample_apple_unorm8
    texture=np.array([[[0,0,0,1],[8/255,0,8/255,1]],
                      [[0,8/255,8/255,1],[8/255,8/255,0,1]]],np.float32)
    pipeline=SourcePipeline(None,None,initial_feedback=texture,warp_reads_blur=False,
        blur_levels=0,texture_sampling_profile=APPLE_PROFILE)
    uv=np.array([[.25+.5/256/2,.25]],np.float32)
    np.testing.assert_array_equal(pipeline._sample_main(texture,uv,wrap=True,linear=True),
        sample_apple_unorm8(texture,uv,wrap=True,linear=True,origin='top'))
    with pytest.raises(ValueError):
        SourcePipeline(None,None,initial_feedback=texture,warp_reads_blur=False,
            blur_levels=0,quantize=False,texture_sampling_profile=APPLE_PROFILE)
    with pytest.raises(ValueError):
        SourcePipeline(None,None,initial_feedback=texture,warp_reads_blur=False,
            blur_levels=0,main_sampling_profile='swiftshader-unorm8-fixed16-v1',
            texture_sampling_profile=APPLE_PROFILE)


def test_apple_sampler_keeps_addressing_and_storage_guards():
    from unorm_sampler import sample_apple_unorm8
    texture=np.array([[[1,0,0,1],[0,1,0,1]],[[0,0,1,1],[1,1,1,1]]],np.float32)
    np.testing.assert_array_equal(sample_apple_unorm8(texture,[1.25,-.75],
        wrap=True,linear=False,origin='top'),[1,0,0,1])
    np.testing.assert_array_equal(sample_apple_unorm8(texture,[.25,.25],
        wrap=False,linear=False,origin='bottom'),[0,0,1,1])
    for field,coords,origin in [(np.full((2,2,4),.123),[.25,.25],'top'),
                               (texture,[float('nan'),.25],'top'),(texture,[.25,.25],'guess')]:
        with pytest.raises(ValueError):
            sample_apple_unorm8(field,coords,wrap=False,linear=True,origin=origin)


def test_apple_source_factory_requires_gles_and_history_reports_effective_profile(monkeypatch):
    from pipeline_fields import SourcePipeline
    from unorm_sampler import APPLE_PROFILE
    with pytest.raises(ValueError,match='GLES300'):
        SourcePipeline.from_source({'values':{},'sections':{}},profile='glsl330',compatibility={},
            initial_feedback=np.zeros((16,16,4)),warp_reads_blur=False,blur_levels=0,
            texture_sampling_profile=APPLE_PROFILE)
    import legacy_composite
    original=legacy_composite.legacy_display;seen=[]
    def observe(*args,**kwargs):
        seen.append(kwargs.get('sampling_profile'))
        return original(*args,**kwargs)
    monkeypatch.setattr(legacy_composite,'legacy_display',observe)
    pipeline=SourcePipeline(None,None,initial_feedback=np.zeros((16,16,4)),
        warp_reads_blur=False,blur_levels=0,composite_kind='legacy_composite',
        texture_sampling_profile=APPLE_PROFILE)
    result=pipeline.step(warp_uv=pipeline.original_uv,uniforms={},frame_wrap=1,decay=1,
        render_time=0,hue_offsets=[0,0,0,0])
    assert seen==[APPLE_PROFILE]
    assert result.history['texture_sampling_profile']==APPLE_PROFILE
    assert result.history['main_sampling_profile']==APPLE_PROFILE


def test_recorded_float_readbacks_match_fixed_sampler_arithmetic():
    from unorm_sampler import sample_unorm8
    proof=json.loads((Path(__file__).parent/'fixtures/swiftshader-sampler-learning-2026-10-04.json').read_text())
    for case in proof['cases']:
        width,height=case['dimensions'];texture=np.zeros((height,width,4),dtype=np.float32)
        texture[...,3]=1;texture[-1,0,0]=1
        for row in case['readback']['rows']:
            expected=np.array(row['rgba'],dtype=np.float32)
            np.testing.assert_array_equal(sample_unorm8(texture,row['uv'],wrap=False,linear=True,origin='bottom'),expected)


def test_sampler_requires_actual_unorm_storage_and_declared_origin():
    from unorm_sampler import sample_unorm8
    for texture,origin in [(np.full((2,2,4),.123),'top'),(np.zeros((2,2,4)),'guess')]:
        with pytest.raises(ValueError):sample_unorm8(texture,[.25,.25],wrap=False,linear=True,origin=origin)


def test_repeat_and_nearest_addressing_preserve_physical_texels():
    from unorm_sampler import sample_unorm8
    texture=np.array([[[1,0,0,1],[0,1,0,1]],[[0,0,1,1],[1,1,1,1]]],dtype=np.float32)
    np.testing.assert_array_equal(sample_unorm8(texture,[1.25,-.75],wrap=True,linear=False,origin='top'),[1,0,0,1])
    np.testing.assert_array_equal(sample_unorm8(texture,[.25,.25],wrap=False,linear=False,origin='bottom'),[0,0,1,1])


def test_pipeline_profile_is_explicit_and_requires_quantized_feedback():
    from pipeline_fields import SourcePipeline
    with pytest.raises(ValueError):SourcePipeline(None,None,initial_feedback=np.zeros((2,2,4)),
        warp_reads_blur=False,blur_levels=0,quantize=False,main_sampling_profile='swiftshader-unorm8-fixed16-v1')
    with pytest.raises(ValueError):SourcePipeline(None,None,initial_feedback=np.zeros((2,2,4)),
        warp_reads_blur=False,blur_levels=0,main_sampling_profile='guess')


@pytest.mark.parametrize('origin',['top','bottom'])
@pytest.mark.parametrize('linear',[False,True])
def test_near_zero_negative_repeat_coordinates_stay_inside_the_16bit_domain(origin,linear):
    from unorm_sampler import sample_unorm8
    texture=np.array([[[1,0,0,1],[0,1,0,1]],[[0,0,1,1],[1,1,1,1]]],dtype=np.float32)
    actual=sample_unorm8(texture,[[-1e-9,.25],[.25,-1e-9]],wrap=True,linear=linear,origin=origin)
    expected=sample_unorm8(texture,[[0,.25],[.25,0]],wrap=True,linear=linear,origin=origin)
    np.testing.assert_array_equal(actual,expected)
