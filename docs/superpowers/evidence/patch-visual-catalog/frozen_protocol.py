"""Independent byte anchors for this catalog's admitted source and PCM workloads."""
import hashlib


# Independently reconstructed from e98fca85 plus its pinned evaluator and
# frozen 8a15996e deterministic instrumentation, then compared with the actual
# original build source. See upstream-source-anchor.json for the observation.
UPSTREAM_SOURCE_TREE_SHA256 = 'cbd3e22aae01abde85c6ae6af80e63b01196c4c2a15f269b75aa88b89cd0fa62'

FROZEN_PCM = {
    240: '3075e03ba2c11bb0f3c73e26729c25cded47a8377e33115753b27a2d4f90b4ad',
    480: '46e958627945f0f44683fc6223876636c46a3de7ec128328e8f705982254b1fd',
}


def frozen_pcm(evidence, frames):
    if frames not in FROZEN_PCM:
        raise ValueError('catalog frames must be 240 or 480')
    path = evidence / 'audio' / f'frozen-{frames}-frames.f32'
    payload = path.read_bytes()
    if (len(payload) != frames * 1470 * 4 or
            hashlib.sha256(payload).hexdigest() != FROZEN_PCM[frames]):
        raise ValueError('frozen PCM bytes changed: ' + str(path))
    return payload
