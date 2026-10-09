"""Integrated source34 forecasts keep math lineage and source identity distinct."""
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from engine_profiles import CORE_2331_ENGINE,CORE_2334_ENGINE
from forecast import read_source,forecast_source
from test_corpus15_audio import run_audio

ROOT=Path(__file__).resolve().parents[2]
NEW=ROOT/'build/preset-corpus/source34/adapters'
OLD=ROOT/'build/preset-corpus/source31/adapters'


@pytest.mark.parametrize('body',[
    'warp=.8\nfWaveAlpha=0\nfGammaAdj=1.0005\nper_pixel_1=q1=q1+1;dx=q1*.0001;\n',
    'warp=0\nfWaveAlpha=.1\nshapecode_0_enabled=1\nshape_0_per_frame1=rad=.2+bass*.1;\n',
    'warp=0\nfWaveAlpha=.2\nbWaveDots=1\nnWaveMode=0\n',
])
def test_source34_forecast_preserves_source31_display_and_attribution(tmp_path,body):
    preset=tmp_path/'case.milk';preset.write_text('[preset00]\n'+body)
    reports=[]
    for folder,engine,version in [(OLD,CORE_2331_ENGINE,'31'),(NEW,CORE_2334_ENGINE,'34')]:
        source=read_source(preset,reader=folder/'milk-native-reader')
        assert source['parser_inputs']['engine']==engine
        result,audio=run_audio(folder,tmp_path,np.zeros(2*2940),fps=15,frames=2)
        assert result.returncode==0,result.stderr
        domain={'width':16,'height':8,'mesh_x':8,'mesh_y':8,'profile':'gles300',
            'initial_rgba':[.1,.2,.3,1],'hue_offsets':[0]*4,'equation_seed':0x4141f00d,
            'equation_rng_policy':'projectmtv-core-2.3.'+version+'-cold-thread-v1',
            'blur_levels':0,'quantize':True,'line_rendering_profile':'projectmtv-gles-quad-lines-v1',
            'triangle_subpixel_bits':8}
        report=forecast_source(source,audio=audio,binaries=folder,domain=domain,compatibility={})
        assert report['status']=='computed'
        assert report['provenance']['engine']==engine
        assert len(report['source_features']['features'])==47
        reports.append(report)
    for before,after in zip(reports[0]['frames'],reports[1]['frames']):
        np.testing.assert_array_equal(before['display'],after['display'])
