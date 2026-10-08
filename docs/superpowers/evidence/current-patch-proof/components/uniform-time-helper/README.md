# Compound uniform write shared with shader helpers

![The original star/ray pattern changes when helpers see the authored time modification](comparison.png)

Unchanged bundled preset:
`Martin - QBikal - Surface Turbulence IIeeeee hakanh mash-up k10.milk`, SHA256
`5d7e6434c83ab2285b71d346114e3fb57547d7f5c811f8a49f35b4f4d2bfbd56`.

The composite performs `time *= 0.6`, then calls `hardcore_stars` twice. The helper
reads time in its coordinates, and its output reaches the displayed star/ray
pattern. GLSL's uniforms are read-only: the translator must initialize a writable
copy from incoming time and share that copy across the entry point and helpers.
Current0002 supplies that initialization and sharing; a function-local uninitialized
replacement cannot implement the authored operation.

**What to look for:** upstream/current-minus0002 show prominent rays around the
right-hand centre at frame119; current has a different star/ray arrangement at the
same source time. This is restoration of authored shader state, not a brightness
improvement claim. All roles compile without warnings; this case is distinct from
the array/fallback comparisons. The separate nonzero uniform-bank control shows
preserved incoming values numerically.

Every role has two exact120-frame RGB repeats at512×288 and zero GL errors.
Source reconstruction, canonical executable rebuilding and complete decoded-stream
verification pass. Panels use unchanged GPU pixels. [Results](results.json),
[verification](verification.json), [frame audit](figure-audit.json).
