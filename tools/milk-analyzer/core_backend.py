"""Published-core frame transport and immutable selection overlays.

Native measurements are execution evidence, not independent source forecasts.
"""
import math
import struct
import zipfile
from numbers import Real

import numpy as np


def _read_exact(stream, count):
    chunks=[]
    while count:
        chunk=stream.read(count)
        if not chunk:raise ValueError('Truncated core frame transport')
        chunks.append(chunk);count-=len(chunk)
    return b''.join(chunks)


def read_header(stream, *, expected_frames, width=128, height=72):
    if _read_exact(stream,8)!=b'PMCORE01':raise ValueError('Invalid core frame header')
    w,h,frames,fps,pid=struct.unpack('<5I',_read_exact(stream,20))
    if (w,h,frames,fps)!=(width,height,expected_frames,30) or pid<2:
        raise ValueError('Core frame schedule or process identity differs')
    return {'width':w,'height':h,'frames':frames,'fps':fps,'pid':pid}


def read_frames(stream, *, expected_frames, width=128, height=72, header=None):
    header=header or read_header(stream,expected_frames=expected_frames,width=width,height=height)
    if (header['width'],header['height'],header['frames'])!=(width,height,expected_frames):
        raise ValueError('Frame reader and header differ')
    for _ in range(expected_frames):
        yield np.frombuffer(_read_exact(stream,width*height*3),dtype=np.uint8).reshape(height,width,3)
    if stream.read(1):raise ValueError('Unexpected trailing data in frame transport')


def write_selection_overlay(path, preset):
    if not isinstance(preset,str) or not preset or any(c in preset for c in '\r\n\t'):
        raise ValueError('A single index-safe preset name required')
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
        entry=zipfile.ZipInfo('assets/presets.idx',date_time=(1980,1,1,0,0,0))
        entry.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(entry,(preset+'\t0\n').encode('utf-8'))


def reusable_result(result, identity):
    score=result.get('score')
    return (result.get('identity')==identity and result.get('status')=='scored' and
            isinstance(score,Real) and not isinstance(score,bool) and math.isfinite(score) and 0<=score<=100)
