"""Published-core frame transport and immutable selection overlays.

Native measurements are execution evidence, not independent source forecasts.
"""
import math
import hashlib
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


def jni_pcm_inputs(pcm):
    """Return float PCM equivalent to the published runner's U8 JNI input.

    Java computes the shift in float32, rounds ties towards positive infinity,
    and clamps to0..255. The native PCM U8 overload centres those integers at128.
    A float value divided by128 is exactly equivalent under the PCM float overload.
    """
    values=np.asarray(pcm,dtype=np.float32)
    if not np.all(np.isfinite(values)) or np.any(np.abs(values)>1):
        raise ValueError('finite JNI PCM samples in[-1,1] required')
    shifted=np.float32(np.float32(values*np.float32(128))+np.float32(128))
    # Promote only after the Java float32 shift. Adding .5 in float32 can
    # round a value below a half tie upward before floor sees it.
    samples=np.clip(np.floor(shifted.astype(np.float64)+.5),0,255)
    return ((samples.astype(np.float32)-np.float32(128))/np.float32(128)).astype('<f4')


def validate_jni_audio_context(pcm,audio):
    """Reject CPU audio evaluated before the declared JNI ingress conversion."""
    transport=np.asarray(pcm,dtype='<f4')
    effective=jni_pcm_inputs(transport)
    expected=hashlib.sha256(effective.tobytes()).hexdigest()
    if not isinstance(audio,dict) or audio.get('pcm_sha256')!=expected:
        raise ValueError('JNI audio ingress differs from source PCM report')
    return {'policy':'projectmtv-jni-u8-v1',
            'transport_pcm_sha256':hashlib.sha256(transport.tobytes()).hexdigest(),
            'source_pcm_sha256':expected}
