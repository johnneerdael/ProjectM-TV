from analyzer_test_profiles import validator_path
import importlib
import struct
import zlib
from pathlib import Path
import numpy as np
import pytest
import test_forecast


BINARY=test_forecast.BINARIES/'milk-image-inputs'


def png(path,pixels):
    pixels=np.asarray(pixels,dtype=np.uint8);height,width=pixels.shape[:2]
    def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
    rows=b''.join(b'\0'+row.tobytes() for row in pixels)
    path.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+
                     chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b''))
    return path


def bank(paths,**options):
    return importlib.import_module('materials').MaterialBank(paths,decoder=BINARY,**options)


def test_effective_identity_tracks_delegated_noise_and_freezes_manifest():
    from types import SimpleNamespace
    from materials import material_input_identity
    pixels=np.ones((1,1,4),dtype=np.float32)
    noise=SimpleNamespace(textures={'noise':pixels},manifest={'producer':'unchanged'},upload_format='RGBA')
    inputs=SimpleNamespace(textures={'noise':pixels},manifest={'images':{}},noise_bank=noise)
    baseline=material_input_identity(inputs)
    noise.textures['noise']=np.zeros_like(pixels)
    actual=material_input_identity(inputs)
    assert actual['textures']==baseline['textures']
    assert actual['procedural_inputs']!=baseline['procedural_inputs']
    noise.manifest['producer']='changed'
    assert baseline['procedural_inputs']['manifest']['producer']=='unchanged'


def test_named_texture_callback_mutation_cannot_change_frozen_forecast_inputs(tmp_path):
    image=png(tmp_path/'colour.png',[[[255,0,0,255]]]);inputs=bank([image])
    source=test_forecast.native(test_forecast.BASE+'comp_1=`shader_body {ret=tex2D(sampler_colour,uv).rgb;}\n')
    from shader_compat import check_shader
    evidence={'composite':check_shader(source['sections']['comp_']['source'],stage='composite',profile='glsl330',
        translator=test_forecast.BINARIES/'milk-shader-translate',validator=validator_path(),
        samplers={'sampler_main':'sampler2D','sampler_colour':'sampler2D'},texture_sizes=[])}
    baseline=test_forecast.predict(source,materials=inputs,compatibility=evidence)
    def edit(frame):inputs.textures['colour']=np.zeros_like(inputs.textures['colour'])
    actual=test_forecast.predict(source,materials=inputs,compatibility=evidence,on_frame=edit)
    for observed,expected in zip(actual['frames'],baseline['frames']):
        np.testing.assert_array_equal(observed['display'],expected['display'])
    assert actual['input_hashes']['materials_sha256']==baseline['input_hashes']['materials_sha256']
    changed=test_forecast.predict(source,materials=inputs,compatibility=evidence)
    assert changed['input_hashes']['materials_sha256']!=baseline['input_hashes']['materials_sha256']


def test_native_source_decode_preserves_rows_and_soil_alpha_rounding(tmp_path):
    path=png(tmp_path/'colour.png',[[[255,0,0,255],[0,128,0,128]],[[0,0,255,0],[1,2,3,255]]])
    inputs=bank([path])
    expected=np.array([[[254,0,0,255],[0,64,0,128]],[[0,0,0,0],[1,2,3,255]]],dtype=np.float32)/255
    np.testing.assert_array_equal(inputs.textures['colour'],expected)
    assert inputs.manifest['uses_rendered_reference'] is False


def test_decoder_replacement_during_execution_cannot_receive_producer_credit(tmp_path,monkeypatch):
    import shutil
    import subprocess
    from materials import MaterialBank
    image=png(tmp_path/'colour.png',[[[255,0,0,255]]])
    decoder=tmp_path/'decoder';shutil.copy2(BINARY,decoder)
    original=subprocess.run
    def replace(*args,**kwargs):
        result=original(*args,**kwargs)
        decoder.write_bytes(b'replacement decoder did not produce these pixels')
        return result
    monkeypatch.setattr(subprocess,'run',replace)
    with pytest.raises(ValueError,match='decoder.*changed'):
        MaterialBank([image],decoder=decoder)


def test_case_insensitive_named_binding_and_point_sampler(tmp_path):
    path=png(tmp_path/'CoLoUr.png',[[[255,0,0,255],[0,255,0,255]]])
    inputs=bank([path])
    detail={'canonical_texture':'COLOUR','sampling_policy':{'wrap':False,'linear':False}}
    sampled=inputs.sample(detail,np.array([[.25,.5],[.75,.5]],dtype=np.float32))
    np.testing.assert_array_equal(sampled,np.array([[254,0,0,255],[0,254,0,255]],dtype=np.float32)/255)
    assert inputs.uniforms()['texsize_colour']==[2,1,.5,1]


def test_duplicate_name_and_missing_texture_do_not_guess_a_binding(tmp_path):
    a=png(tmp_path/'A.png',[[[255,0,0,255]]]);b=png(tmp_path/'a.png',[[[0,255,0,255]]])
    with pytest.raises(ValueError,match='ambiguous'):bank([a,b])
    inputs=bank([a])
    with pytest.raises(ValueError,match='missing'):
        inputs.sample({'canonical_texture':'missing','sampling_policy':{'wrap':True,'linear':True}},np.array([[.5,.5]]))


def test_corrupt_image_and_dimension_limit_do_not_return_plausible_pixels(tmp_path):
    bad=tmp_path/'bad.png';bad.write_bytes(b'invalid image')
    with pytest.raises(ValueError):bank([bad])
    image=png(tmp_path/'wide.png',[[[0,0,0,255]]*3])
    with pytest.raises(ValueError,match='size'):bank([image],maximum_texture_size=2)


def test_named_material_enters_shader_forecast(tmp_path):
    image=png(tmp_path/'colour.png',[[[255,0,0,255]]])
    inputs=bank([image])
    source=test_forecast.native(test_forecast.BASE+'per_frame_1=q1=2;\n'
                               'comp_1=`shader_body {ret=tex2D(sampler_colour,uv).rgb*q1*.5;}\n')
    from shader_compat import check_shader
    evidence={'composite':check_shader(source['sections']['comp_']['source'],stage='composite',profile='glsl330',
        translator=test_forecast.BINARIES/'milk-shader-translate',validator=validator_path(),
        samplers={'sampler_main':'sampler2D','sampler_colour':'sampler2D'},texture_sizes=[])}
    result=test_forecast.predict(source,compatibility=evidence,materials=inputs)
    np.testing.assert_allclose(result['frames'][0]['display'][...,:3],np.broadcast_to([254/255,0,0],(32,32,3)),atol=1e-7)


def test_named_image_shape_uses_image_instead_of_previous_main(tmp_path):
    image=png(tmp_path/'colour.png',[[[0,255,0,255]]]);inputs=bank([image])
    source=test_forecast.native(test_forecast.BASE+'warp_1=`shader_body {ret=0;}\n'
        'shapecode_0_enabled=1\nshapecode_0_textured=1\nshapecode_0_image=colour\nshapecode_0_rad=1\n'
        'shapecode_0_r=1\nshapecode_0_g=1\nshapecode_0_b=1\nshapecode_0_r2=1\nshapecode_0_g2=1\nshapecode_0_b2=1\n'
        'shapecode_0_a=1\nshapecode_0_a2=1\n')
    result=test_forecast.predict(source,materials=inputs)
    np.testing.assert_allclose(result['frames'][0]['feedback'][16,16,:3],[0,254/255,0],atol=2e-6)


def test_original_case_texture_size_uniform_is_bound_to_the_named_material(tmp_path):
    image=png(tmp_path/'colour.png',[[[255,0,0,255],[0,255,0,255]]]);inputs=bank([image])
    source=test_forecast.native(test_forecast.BASE+'comp_1=`shader_body {ret=texsize_COLOUR.xy/2;}\n')
    from shader_compat import check_shader
    evidence={'composite':check_shader(source['sections']['comp_']['source'],stage='composite',profile='glsl330',
        translator=test_forecast.BINARIES/'milk-shader-translate',validator=validator_path(),
        samplers={'sampler_main':'sampler2D'},texture_sizes=['texsize_COLOUR'])}
    result=test_forecast.predict(source,compatibility=evidence,materials=inputs)
    np.testing.assert_allclose(result['frames'][0]['display'][...,:3],np.broadcast_to([1,.5,0],(32,32,3)),atol=1e-7)


def test_migrated_decoder_provenance_does_not_claim_a_soil_source(tmp_path):
    import os,json,subprocess
    binary=Path(os.environ.get('MILK_TEST_2321_BINARIES','build/visual-loop/source2321/adapters'))/'milk-image-inputs'
    if not binary.is_file():pytest.skip('prepared4.2 decoderrequired')
    image=png(tmp_path/'image.png',[[[255,0,0,255]]]);request=tmp_path/'request.json'
    request.write_text(json.dumps({'maximum_texture_size':32,'files':[{'input':str(image),'output':str(tmp_path/'image.rgba')}]}))
    result=json.loads(subprocess.check_output([str(binary),str(request)],text=True))
    assert result['decoder_backend']=='stbi-with-tv-premultiply-v1'
    assert result['soil_source_sha256'] is None
    assert result['decoder_implementation_source_path']=='vendor/stb_image/stb_image.c'
    assert len(result['decoder_implementation_source_sha256'])==64
