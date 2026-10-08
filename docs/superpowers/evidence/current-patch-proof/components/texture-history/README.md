# Fresh/reused attachment initialization and pool allocation proof

![Actual library frames, controlled readbacks and measured allocations](comparison.png)

The lower image panels are actual first-read pixels from the linked libraries'
64×48 RGBA8 `TextureAttachment` objects. A shared GL allocation fixture writes
`(0,160,80,255)` into null-data storage immediately after `glTexImage2D`. A raw
allocation/readback confirms those bytes before either library runs. This makes
unspecified initial contents observable ([Khronos texture-allocation reference](https://registry.khronos.org/OpenGL-Refpages/es3.0/html/glTexImage2D.xhtml)); **green is controlled storage, not a
naturally recorded failure in an artist preset**.

Upstream leaves those bytes in the fresh attachment. Current clears every pixel
to `(0,0,0,0)`, transparent black. The probe writes blue `(32,64,192,255)` into the
first attachment, retires it, then creates another of the same size and format.
Upstream makes a second allocation and again exposes the fixture's green bytes.
Current reuses storage, clears the old blue contents, and again reads transparent
black. All 3,072 RGBA pixels are checked in each readback; the figure shows RGB
at an explicitly labeled nearest-neighbour 4× scale, with alpha stated separately.

**Code-level cause:** current0001's `TextureAttachment::ReplaceTexture` invokes
`ClearPooledTexture` for fresh color storage as well as pool hits. The helper
attaches the texture to a context-local scratch FBO, disables scissor and enables
all color channels for a transparent-black clear, then restores caller draw-FBO,
clear color, color mask and scissor enable state. The probe sets a nondefault
clear color, alternating channel mask and enabled small scissor before both
creations; both libraries preserve the recorded read/draw framebuffer and raster
state. This isolates attachment construction, not `Framebuffer::SetSize`, which
has its own documented binding behavior.

**Pool measurement:** current opts into a 32,768-byte pool for the diagnostic.
One actual driver storage allocation serves both attachment lifetimes, compared
with two upstream allocations. `Texture::PoolBytes()` reports 12,288 bytes after
the first retirement (`64×48×4`). This is library-accounted retained storage,
not measured physical GPU memory or a frame-time improvement. The pool is disabled
by default, costs retained storage when enabled, and is reset to zero before the
normal preset render. Default-off, external ownership, pressure release and
context-recreation controls remain pending; this example does not certify them.

The top panels are unmodified 512×288 frame 59 from unchanged
`Geiss - 3D - Shockwaves.milk`, after restoring diagnostic state. Their RGB MAE is
0.001429; these nearly identical full-library frames show normal rendering after
the probe, not an appearance benefit from pooling. Each library has two fresh
processes with exact 120-frame repeats, no GL errors and no shader warnings/errors.
The controlled pixels, state checks and counts also repeat exactly.

Source reconstruction, independent NDK rebuild/canonical executable comparison,
all 480 decoded RGB frames and PNG payloads pass verification. The common GPU is
the task-owned API36 Android TV emulator 5630, host M4 Pro/GLES3.0; upstream has the
explicit GLES admission adjustment and current disables binary-cache export.
See [complete observations](results.json), [verification](verification.json) and
[figure/readback hashes](figure-audit.json). Complete compressed streams and
workers remain under ignored `build/patch-proof/texture-history-v1` and
`build/patch-proof/component-workers-v4`, with their recorded source identities.
