# Source shape colour-difference size, area weighting and modulo cadence

This checkpoint improves the information behind shape flashing mechanisms rather
than using a binary detector as an intensity score. It executes no equations,
shaders, audio simulations or image classification.

## Difference-size math

At fixed geometry and barycentric position, compare two possible untextured shape
material states with the same destination RGB in `[0,1]`. For fan centre/perimeter
weights `(w,1-w)`, source alpha within its linear domain and RGB endpoints,
the incoming term is the interpolated alpha times interpolated RGB. Product-rule
triangle ceilings form a quadratic in `w`; exact rational coefficients and its
interior extremum produce the maximum. Transparent-centre colour is therefore
weighted by actual fan alpha, rather than assigning it full-shape opacity.

For source-alpha-over, use maximum endpoint contrast against the fixed destination.
Alpha clipping outside the linear endpoint domain uses a scalar Lipschitz ceiling.
RGB clipping is nonexpansive. The [OpenGL ES 3.0 blend specification §4.1.7](https://registry.khronos.org/OpenGL/specs/es/3.0/es_spec_3.0.pdf)
provides the declared normalized-target blend model. Unknown texture RGB/alpha
keeps the bound null. Border gating includes the zero-effective-alpha off state;
that control exposed an initial underestimate and passed after repair.

Nominal fill-area ceilings and configured instance count weight the local
difference. The exported coefficient still requires target aspectY. Overlap is
counted repeatedly, and clipping/rasterization, moving geometry, thick/repeated
borders and subsequent feedback/composition remain separate. Borders have no
claimed area coefficient. A large difference between arbitrarily separated states
is not proof of an abrupt event: `abrupt_change_verified` remains false and visible
flash strength remains null.

## Nominal channel timing

Affine time drift crosses a modulo cell every `period/abs(rate)` seconds.
For a supported single sine/cosine, exact rational enumeration counts strict
interior multiples of the native float32 `256/255` period; each is crossed twice
per cycle. Signed amplitudes/rates and phase offsets are retained. Enumeration
is capped at 16 boundaries; excess, unsupported/discrete, numeric-domain and
native-singleton cases remain unquantified. Tangencies and native preboundary
rounding resets are not credited as exact schedule events.

Native source34 `CustomShape.cpp` lines 215–246 separates raw-alpha border gating
from native colour modulo conversion. Original MilkDrop2 `milkdropfs.cpp` retains
packed-byte shape colours and SRCALPHA/INVSRCALPHA blending; current native
float-modulo conversion remains its own qualified target. Source-only schedules
exclude clock resets, numeric quantization and frame aliasing. Per-channel events
can coincide and must not be summed into a whole-preset visible frequency.

## Verified coverage

The same seeded 2,000-preset selection and full inventory hashes are preserved.
All 2,000 terminal exports and exact archive source/result pairs verify; 20 batches
complete in 476.84 seconds. All 2,000 descriptions validate the schema, including
two explicit unknown budget fallbacks. Structured coverage is 1,998, up from the
immutable baseline's 1,995 after the previous typed-projection/mask repair.
No new source interpretation gaps or lost structured descriptions are introduced.

New quantities are available for:

- 635 presets with complete local two-state material difference ceilings.
- 268 presets with nominal fill-area weighting.
- 48 presets with consumed-channel nominal modulo schedules.

Restricting to presets already reporting a shape modulo or border-gate mechanism,
144 have a matching local size ceiling, 40 have a matching fill-area ceiling,
and 48 have a channel schedule. The exact matching element/part matters; a
bounded unrelated border is not counted as a bounded fill hazard. Groups overlap.
These are conditional source facts, not 144 verified flashes or mood assignments.

Nine difference-size controls and ten timing controls pass, including independently
computed fan differences, transparent-centre weighting, clipped-alpha destination
contrast, border off state, multiple/signed oscillator crossings and unknown cases.
Independent review passes 43 focused controls including exact-profile Grind,
finding no remaining actionable issue. The prepared full suite passes 3,109 tests
plus 92 subtests in 202.85 seconds. Original 100 controls retain structured/schema
output; strict MkDocs and diff whitespace checks pass.

The two retained source fallbacks are deep diver's cognitive dissonance and Grind
230, with exact names/hashes in `checkpoint.json`. They are not native renderer
failure claims. Full feedback, visible screen prominence and reliable mood scores
remain unverified; no engine patch or new AAR runtime qualification is added.

## Artifacts

Compressed `report.json.gz`, `flash-census.json.gz` and `controls-census.json.gz`
contain complete source IDs, numerical records and scope/unknown reasons.
`hazard-availability.json` provides the matching preset lists;
`source-comparison.json` records source-gap and structured-status differences.
`checkpoint.json` seals the run/report identity and qualification counts.

Local full results: `build/preset-corpus/source-shape-flash-size-2000-2026-10-10/`,
including 20 paired ZIP batches and source-bound compiler proofs. Logs:

- `build/preset-corpus/source-shape-flash-size-2000.log`
- `build/preset-corpus/source-shape-flash-size-suite.log`
- `build/preset-corpus/source-shape-flash-size-controls-100-2026-10-10/`
- `build/preset-corpus/source-shape-flash-size-evidence-2026-10-10/`

The original frozen 2,000-case audit remains unchanged. No renderer, presets or
traversal limits were modified in this feature.
