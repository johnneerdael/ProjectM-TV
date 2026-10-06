from pathlib import Path
import json
import os
import subprocess
import pytest
from forecast import read_source
from builtin_wave import source_builtin_wave
from scene_equations import execute_scene

ROOT=Path(__file__).resolve().parents[2]
prepared=ROOT/'build/visual-loop/source44/adapters'
BINARY=Path(os.environ.get('MILK_TEST_CURRENT_BINARIES',str(prepared if prepared.is_dir() else ROOT/'build/milk-analyzer/native')))

@pytest.fixture
def current_inputs(tmp_path):
    if not (BINARY/'milk-native-reader').is_file():
        pytest.skip('prepared source44 adapters required for live dot geometry control')
    path=tmp_path/'dots2310.milk'
    path.write_text('MILKDROP_PRESET_VERSION=201\n[preset00]\nnWaveMode=6\nbWaveDots=1\nfWaveAlpha=.5\n')
    source=read_source(path,reader=BINARY/'milk-native-reader')
    pcm=tmp_path/'silence.f32';pcm.write_bytes(bytes(1470*4))
    request=tmp_path/'audio-request.json';output=tmp_path/'audio.json'
    request.write_text(json.dumps({'pcm_path':str(pcm),'output':str(output),'fps':30,'frames':1,'channels':1}))
    subprocess.run([str(BINARY/'milk-audio-inputs'),str(request)],check=True,capture_output=True,text=True)
    data=json.loads(output.read_text())
    assert data['engine_archive_sha256']==source['parser_inputs']['engine_archive_sha256']
    scene=execute_scene(source,data['frames'],reader=BINARY/'milk-native-reader',width=256,height=144,mesh_x=8,mesh_y=8)
    return source,scene,data


def test_live44_gles_dot_geometry_keeps_single_two_pixel_point(current_inputs):
    source,scene,data=current_inputs
    result=source_builtin_wave(source,scene,data,binary=BINARY/'milk-wave-inputs',line_rendering_profile='projectmtv-gles-quad-lines-v1')
    wave=result['frames'][0]
    assert result['engine_archive_sha256']==source['parser_inputs']['engine_archive_sha256']
    assert wave['point_size']==2 and wave['copy_offsets']==[[0,0]]
    assert wave['draw_mode']=='points' and wave['rgba'][3]==.5


def test_live44_dot_guard_rejects_changed_identity(current_inputs):
    source,scene,data=current_inputs
    source['parser_inputs']['engine']['patches_sha256']='0'*64
    with pytest.raises(ValueError,match='engine identity mismatch'):
        source_builtin_wave(source,scene,data,binary=BINARY/'milk-wave-inputs',line_rendering_profile='projectmtv-gles-quad-lines-v1')
