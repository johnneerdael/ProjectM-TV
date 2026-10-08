"""Read complete RGB sequences without materializing a whole 4K stream."""
from __future__ import annotations

import gzip
import hashlib
from pathlib import Path
import shutil


def inspect_rgb(path: Path, width: int, height: int, frames: int = 120,
                snapshots: tuple[int, ...] = ()) -> dict:
    if width <= 0 or height <= 0 or frames <= 0:
        raise ValueError('RGB dimensions and frame count must be positive')
    frame_size = width * height * 3
    opener = gzip.open if path.suffix == '.gz' else Path.open
    digest = hashlib.sha256()
    hashes, retained = [], {}
    with opener(path, 'rb') as stream:
        for index in range(frames):
            data = stream.read(frame_size)
            if len(data) != frame_size:
                raise ValueError('RGB stream length differs')
            digest.update(data)
            hashes.append(hashlib.sha256(data).hexdigest())
            if index in snapshots:
                retained[index] = data
        if stream.read(1):
            raise ValueError('RGB stream length differs')
    return {'frame_hashes': hashes, 'stream_sha256': digest.hexdigest(),
            'bytes': frame_size * frames, 'snapshots': retained}


def payload_path(directory: Path) -> Path:
    raw = directory / 'frames.rgb'
    return raw if raw.is_file() else directory / 'frames.rgb.gz'


def compress_rgb(directory: Path, width: int, height: int, expected: dict) -> None:
    """Remove the new raw copy only after independently checking its lossless copy."""
    raw, compressed = directory / 'frames.rgb', directory / 'frames.rgb.gz'
    with raw.open('rb') as source, gzip.GzipFile(
            filename=str(compressed), mode='wb', compresslevel=1, mtime=0) as output:
        shutil.copyfileobj(source, output, length=1024 * 1024)
    observed = inspect_rgb(compressed, width, height, len(expected['frame_hashes']))
    if (observed['frame_hashes'] != expected['frame_hashes'] or
            observed['stream_sha256'] != expected['stream_sha256']):
        raise ValueError('Compressed RGB payload does not preserve the original frames')
    raw.unlink()
