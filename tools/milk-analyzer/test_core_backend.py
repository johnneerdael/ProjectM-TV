import io
import struct
import zipfile
import numpy as np
import pytest

from core_backend import read_frames, write_selection_overlay, reusable_result


def stream(frames=2):
    return io.BytesIO(b'PMCORE01'+struct.pack('<5I',2,1,frames,30,42)+bytes(range(frames*6)))


def test_frame_protocol_preserves_exact_count_and_channel_order():
    values=list(read_frames(stream(),expected_frames=2,width=2,height=1))
    np.testing.assert_array_equal(values[1],[[[6,7,8],[9,10,11]]])


def test_truncated_or_extra_frames_and_wrong_header_are_not_complete_results():
    for payload in (b'bad',stream().getvalue()[:-1],stream().getvalue()+b'log'):
        with pytest.raises(ValueError):list(read_frames(io.BytesIO(payload),expected_frames=2,width=2,height=1))


def test_overlay_selects_exact_name_without_repacking_assets(tmp_path):
    path=tmp_path/'selection.apk';write_selection_overlay(path,"artist's test.milk")
    with zipfile.ZipFile(path) as archive:
        assert archive.namelist()==['assets/presets.idx']
        assert archive.read('assets/presets.idx')==b"artist's test.milk\t0\n"
    with pytest.raises(ValueError):write_selection_overlay(path,'bad\nname.milk')


def test_resume_requires_same_identity_and_finite_score():
    assert reusable_result({'identity':'abc','status':'scored','score':30},'abc')
    assert not reusable_result({'identity':'old','status':'scored','score':30},'abc')
    for value in (None,float('nan'),101,True):
        assert not reusable_result({'identity':'abc','status':'scored','score':value},'abc')
