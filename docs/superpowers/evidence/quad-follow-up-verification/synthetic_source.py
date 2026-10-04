# Synthetic geometry copied from the priority evidence hits.py; measurement code is separate.
HEAD = 'MILKDROP_PRESET_VERSION=201\nPSVERSION=0\nPSVERSION_WARP=0\nPSVERSION_COMP=0\n[preset00]\nfGammaAdj=1.0\nfDecay=0.0\nfVideoEchoAlpha=0.0\nnWaveMode={mode}\nbAdditiveWaves=1\nbWaveDots=0\nbWaveThick={mthick}\nbModWaveAlphaByVolume=0\nbMaximizeWaveColor=0\nbTexWrap=0\nbBrighten=0\nbDarken=0\nbSolarize=0\nbInvert=0\nfWaveAlpha={malpha}\nfWaveScale=1.0\nfWaveSmoothing=0.0\nwave_r=1.0\nwave_g=1.0\nwave_b=1.0\nwave_x=0.5\nwave_y=0.5\nzoom=1.0\nrot=0.0\nwarp=0.0\nsx=1.0\nsy=1.0\nmv_a=0.0\nob_a=0.0\nib_a=0.0\n'
CW = 'wavecode_0_enabled=1\nwavecode_0_samples=512\nwavecode_0_bDrawThick={thick}\nwavecode_0_bAdditive=1\nwavecode_0_bUseDots=0\nwavecode_0_smoothing=0\nwavecode_0_r=1\nwavecode_0_g=1\nwavecode_0_b=1\nwavecode_0_a=0.125\nwave_0_per_point1={pp}\n'
PP = {'circle': 'x = 0.5 + 0.3*cos(sample*6.283); y = 0.5 + 0.4*sin(sample*6.283);', 'wiggle': 'x = 0.05 + 0.9*sample; y = 0.5 + 0.35*sin(sample*6.283*3);'}

def presets():
    d = {}
    for shp, pp in PP.items():
        for th in (0, 1):
            d[f"hit-cw-{shp}-{('thick' if th else 'thin')}"] = HEAD.format(mode=0, mthick=0, malpha=0.0) + CW.format(thick=th, pp=pp)
    for mode, nm in ((0, 'circle'), (6, 'line')):
        for th in (0, 1):
            d[f"hit-mw-{nm}-{('thick' if th else 'thin')}"] = HEAD.format(mode=mode, mthick=th, malpha=0.125)
    return d
