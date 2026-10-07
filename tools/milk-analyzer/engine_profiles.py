"""Exact published source identities and separately versioned math policies."""

CORE_2315_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': '7ef297fcab5d42d0531ec621ac6a464a5a0e7982da02bb40996bc62a886ae527',
}
CORE_2316_ENGINE = {
    'commit': 'e0b0a967f0ffd7d332106c366668ed271718472b',
    'patches_sha256': 'cd01f0f3cce4f6be05d781b06192dadadbd8254a6fa1c03ea52394d3e48f9ded',
}
# Patch0050 changes texture lookup lifetime; the established scalar/drawing math
# policies are shared, while source and runtime identities remain distinct.
CORE_2315_BLUR = 'projectmtv-core-2.3.15-blur-ranges-v1'
CORE_2315_ZOOM = 'projectmtv-core-2.3.15-signed-unit-zoom-v1'
CORE_2315_DISPLAY = 'projectmtv-core-2.3.15-live-display-controls-v1'
CORE_2315_WAVE = 'projectmtv-core-2.3.15-live-wave-controls-v1'
CORE_2315_SHAPE = 'projectmtv-core-2.3.15-shape-sampler-v1'
LEGACY_BLUR = 'legacy-collapsed-blur-ranges-v1'
LEGACY_ZOOM = 'legacy-glsl-pow-v1'
LEGACY_DISPLAY = 'legacy-static-display-controls-v1'
LEGACY_WAVE = 'legacy-static-wave-controls-v1'


def matches(engine, expected=None):
    targets=(CORE_2315_ENGINE,CORE_2316_ENGINE) if expected is None else (expected,)
    return any(all(engine.get(key)==value for key,value in target.items()) for target in targets)


def select_policy(engine, requested, *, current, legacy):
    selected = requested if requested is not None else current if matches(engine) else legacy
    if selected not in {current, legacy}:
        raise ValueError('unsupported source math policy: '+str(selected))
    if selected == current and not matches(engine):
        raise ValueError('current source math engine identity mismatch')
    return selected
