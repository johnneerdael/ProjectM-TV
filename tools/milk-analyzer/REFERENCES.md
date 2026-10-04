# Semantic references

Use the [creator's preset authoring guide](https://www.geisswerks.com/milkdrop/milkdrop_preset_authoring.html)
for authoring intent. Cross-check runtime details against the pinned projectM
source and executable fixtures.

Implementation map:

| Guide topic | Analyzer work |
| --- | --- |
| Variable pools and Q/T transfers | Native equation scopes and state loader |
| Per-vertex equations and interpolated UVs | Spatial mesh operators |
| Warp versus composite | Feedback/display separation |
| Texture filtering and addressing | Sampling policy and field samplers |
| Blur ranges and texture precision | Blur pipeline and framebuffer storage |
| Noise textures | Native CPU buffers, channel decoding and field sampling |
| Shapes and waves | Source wave geometry and shape/border fills; hardware coverage/outlines pending |
| Motion-vector trails | Native fractional grid, prior warp map, minimum length and pre-warp canonical lines; GPU precision/coverage pending |
| Shader control flow | Typed native loop trees and per-lane loop state |

Noise-table sizes are conceptual for filtered textures; verify physical sizes
from implementation. Documentation and runtime differences must remain explicit.

## Motion-vector draw and feedback order

The pinned `MilkdropPreset/MotionVectors.cpp` truncates double grid counts before
capping at 64x48, preserves fractional diversions for uncapped grids, clips grid
origins to the interior and derives minimum length from 1.25/viewport.
`Shaders/PresetMotionVectorsVertexShaderGlsl330.vert` samples the previous map
with a Y-reversed texture coordinate, scales displacement, lengthens short
nonzero vectors and uses a two-component minimum-length fallback for zero motion.
Its Y reversal followed by native orthogonal projection is preserved.

The pinned `MilkdropPreset.cpp` draws vectors on previous feedback before warp,
skips them on the first frame and writes an RG16F map only while vectors are
enabled. Disabled frames retain a stale map. `MilkdropShader.cpp` initializes
`_mv_tex_coords.xy` at the beginning of the warp body; later ordinary UV changes
do not alter it, but explicit output writes do. Output parameters begin
uninitialized, so unwritten components are not incoming shader uniforms.
The source pipeline commits map updates only after the full frame succeeds.

Canonical unsmoothed lines are used. GPU precision, desktop line smoothing and
cold maps never written by warp remain limitations; this addition does not
certify pixel-level renderer agreement.

## Shader random vectors and matrices

`MilkdropShader.cpp` initializes one four-component preset vector and 20 banks
of translation/rotation centre/speed values per shader construction. Its
`floatRand` computes float32 `(rand() % 7381) / 7380.0f`. Every LoadVariables call
consumes a four-component frame vector and six draws for each of four fresh
rotation matrices, even if the shader does not use those uniforms. Warp and
composite share the process stream but retain different preset banks.

The native matrix sequence is `T * Rx`, then `Rz * previous`, then `Ry * previous`.
`Renderer/Shader.cpp::SetUniformMat3x4` takes `glm::mat3x4`, so conversion from
mat4 removes translation and uploads three columns/four rows. The HLSL input
`float4x3` is represented as four rows/three columns in the field evaluator.
The first persistent rotation has zero speed, but later banks have increasing
speed multipliers; matrix groups must not be assumed to be strictly static from
their names.

The data-only adapter copies constructor/random-load bodies, uses the pinned
GLM headers and intercepts uniform upload with the native conversion signature.
Source/body/GLM/upload-source hashes and host/compiler identities are recorded.
Tests independently check C-rand draw positions, matrix axes/composition, shape
and translation loss, shader-field multiplication and composite-grid use.
These are source/CPU checks, not rendered appearance validation. C-rand algorithm,
compiler argument evaluation order, startup/idle/fallback events and target
profile must be bound before claiming a particular engine's random input stream.

## Forecast integration and renderer time

The source forecast supplies previous feedback after pre-warp motion drawing to
textured custom shapes. Native `CustomShape.cpp` binds the previous-main texture
for an empty image descriptor; known named images instead use texture aspect
1.0. `TextureManager::TryLoadingTexture` returns a placeholder for a missing
named file, so missing names must not automatically be treated as previous main.
Known named inputs now resolve through the source material registry; missing
placeholder initialization remains unresolved. The final display is not fed back.

`Renderer/RenderContext.hpp` declares double time. Hue calculations and waveform
expressions can multiply that double before narrowing for `sinf`/float storage.
This differs from EEL/shader time, which is loaded as float. The waveform CPU
facade and JSON bridge now preserve double time, and `source_builtin_wave` uses
the original audio-schedule time rather than the narrowed equation copy.
Long-clock numerical fixtures detected the previous early narrowing. The
forecaster passes original render time to composite hue math as well.

## Named image decoding and sampling

`TextureManager::LoadTexture` calls SOIL with forced RGBA and
`SOIL_FLAG_MULTIPLY_ALPHA`. The pinned SOIL2 stb header performs decoding;
SOIL's premultiplication computes each RGB byte as `(colour * alpha + 128) >> 8`.
This includes its rounding for opaque pixels; substituting division by 255 would
predict different bytes. Source image rows are uploaded without an INVERT_Y flag.
The CPU bridge keeps those operations and omits GL creation, querying and upload.
Source file/pixel/decoder identities are captured in the material manifest.

Texture lookup strips sampler qualifiers and compares case-insensitive file
stems. Generated uniform identifiers retain their original spelling. The source
registry requires unambiguous supplied files; it does not guess native scanner
order for collisions or random selections. Device resizing/NPOT behavior and
missing placeholders remain separate profile requirements.

## Checked source snapshots

- MilkDrop 2: `https://git.code.sf.net/p/milkdrop2/code`, commit
  `f05b0d811a87a17c4624170c26c93bac39b05bde`.
- BeatDrop: `https://github.com/mvsoft74/BeatDrop`, commit
  `53d83ee29841e0ae11bc4bd85f67cb09594762a2`.
- MilkDrop3: `https://github.com/milkdrop2077/MilkDrop3`, commit
  `6b39088f789441e18cc1665519ee7ffe439cece5`.

The supplied BeatDrop and MilkDrop3 `vis_milk2/state.h` files define 32 Q variables
and eight T variables. MilkDrop3's README describes later capabilities; its
`state.h` last changed in the checked history on 2023-04-17. Track documented
release capabilities separately from available source capabilities.

Whitespace-normalized comparisons found matching `fCubicInterpolate` and
`dwCubicInterpolate` implementations across all three snapshots. BeatDrop and
MilkDrop3 also share identical normalized `AddNoiseTex` and `AddNoiseVol` bodies.
The concrete noise allocations include 256² HQ 2D and 32³ HQ volume storage.
These sources support the noise-initialization work; projectM's pinned generator,
random seed handling and upload channel order remain the execution target.

The volume-smoothing layouts differ: BeatDrop/MilkDrop3 index Z using the locked
texture's slice stride, whereas the pinned projectM generator uses `z * size`
in its smoothing accesses even though its buffer allocation/fill is `size³`.
Verify this numerically when porting noise generation; do not silently substitute
the upstream layout and predict a different texture from the production engine.

Both supplied repositories were inspected read-only. BeatDrop has an existing
change to `vis_milk2/text1.bin`; that file was excluded from source comparisons.

## Equation evaluator

User-supplied `projectm-eval`: commit
`e8c311e86f4d8c082e96e02b6a33525034eee6d4`, repository
`https://github.com/projectM-visualizer/projectm-eval`.
Its checked compiler/context/API files match the pinned engine copies. The
observed `TreeFunctions.c` difference is the lab's controlled-seed, per-thread
random state patch. The native reader already executes these compiled EEL
programs and exports their trees; this library does not interpret pixel shaders.

Keep synthetic-audio probes and source/live-output dependencies as measurements
with declared domains and units. Example normalized scores or millisecond
throughput estimates supplied in discussion are not measured results. Native
rendering remains validation of frozen predictions, not their classification
input.

## Shader loops and stateful unary operations

The pinned engine's `vendor/hlslparser/src/HLSLTree.h` defines pre-increment,
pre-decrement, post-increment and post-decrement as unary operators3through6.
`GLSLGenerator.cpp` emits the corresponding GLSL prefix/postfix operators and
ordinary `for`/`while` statements, including boolean condition conversion.
`native_reader.cpp` retains initialization, condition, increment and body nodes.
The field interpreter preserves scoped counters and per-lane state rather than
substituting a fixed iteration count. Its computation budgets are explicit
unresolved boundaries, not promises about native GPU termination.

Numeric fixtures cover native scopes, returned/stored increment values, variable
iteration counts, nested/helper loops, branch-state inheritance, selected-lane
texture samples and nontermination handling. A source-only corpus probe on
`306 nz+ no knead to think, as i'm dead.milk` checks its sixteen-iteration
composite loop against an independently simplified algebraic result under
declared constant texture/Q/audio inputs. No rendered reference is used.

## Component initialization and target translation

The [GLSL specification](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.pdf)
defines reads before initialization as undefined (section5.8), uniform values as
externally initialized/read-only (section4.3.5), and local initializer scope
(section4.2). Preserve these rules rather than providing missing values as zero.
The numeric state engine carries a validity mask for each component and rejects
actual reads of unwritten components, including after partial loop updates.

The pinned `GLSLGenerator.cpp` emits scalar-swizzle helpers, casts vector indices
to integer, turns matrix row indexing into a getter, and maps single matrix
members to transposed GLSL storage indices. A matrix row getter is not a writable
l-value; multiple matrix-member selectors are also not faithfully emitted.
Its identifier output does not rename a global to preserve an HLSL same-name
local initializer binding. Keep those target-language boundaries unresolved.

The same generator calls `HLSLTree::ReplaceUniformsAssignments()` before emitting
GLSL. This changes uniform assignment destinations and subsequent references to
function-local declarations. The replacements are **not initialized from the
uniform**, and only assigned components become valid. Binary RHS traversal occurs
before the assignment's LHS replacement. Unary increments alone do not trigger
this transformation. Native HLSL identifier global markers survive the rewrite;
the reader exports the actual generated local binding explicitly. The previous
assumption that every uniform assignment necessarily causes compiler rejection
was incorrect and has been replaced with native execution-stage semantics.

`generate_shader_adapter.py` extracts unchanged CPU method bodies from the pinned
`MilkdropShader.cpp`. The adapter replaces GL-owning objects with data-only views
and explicit descriptor declarations, omitting texture loading, translation caches
and actual driver compilation. Both native HLSL parsing and GLSL generation use
the pinned archive, including its alternate-NaN-propagation generator flag.
Offline fragment validation records `glslangValidator` binary identity. Its result
is syntax evidence under an explicit descriptor/profile, not a driver/link or
appearance guarantee. Reader language-extension prototypes are not injected into
this target translation path.

`PerPixelMesh::CompileWarpShader` disables a shader after compilation failure.
`FinalComposite::CompileCompositeShader` replaces a failed composite with
`ret = tex2D(sampler_main, uv).xyz`, then compiles that default. Fall back to the
corresponding stage only when rejection is established; parser/lowering unknowns
alone do not establish failure. In the 436-section historical uniform-write group,
413 now lower completely, and offline accepted counts are 436 for GLSL330 and 435 for
GLES300 under reader-derived explicit declarations. No render was used.

`TextureSamplerDescriptor.cpp` emits `uniform` sampler/texture-size declarations.
The reader's previous automatic texture-size declarations omitted that qualifier;
the new reader repairs it and the corpus trees were regenerated under a new
binary identity. Existing parser snapshots remain historical evidence, not
current binding metadata. The private engine and published renderer were not
changed.

## Native audio and built-in waveform math

`Audio/PCM.cpp`, `MilkdropFFT.cpp`, `WaveformAligner.cpp` and `Loudness.cpp` in the
pinned archive supply waveform/spectrum/band execution. The CPU bridge uses the
same complete-frame tail ingestion and frame/time schedule as the lab worker.
The720frame trace comparison found zero difference for every recorded band.

`MilkdropPreset/Waveforms/` supplies all16mode math bodies and smoothing. CMake
copies these into the build directory, changes the namespace and replaces the
GL-owning state includes with minimal views. Math body text is preserved; source
and adapted file hashes plus adapter identity are exported. The original engine
source/archive is unchanged. Geometry runs without creating `PresetState` or
`BlurTexture`, whose original constructors initialize GL resources.

`Waveform.cpp` supplies static draw flags, mode-specific opacity, volume
modulation ordering, colour maximization, copy offsets and the built-in waveform
projection. The adapter exposes the geometry's possible `wave_a` modification;
the draw spec uses that result. Line mode6 ignores `wave_y` and uses `wave_x` for
its vertical position. The raw mode is file-level; changing EEL `wave_mode`,
`wave_thick` or `wave_additive` does not change the native static renderer flags.
GPU line/point coverage and complete draw ordering remain separate requirements.

## Matrix translation

The pinned `GLSLGenerator::OutputExpression` routes bare matrix multiplication
through `mult0`, whose square-matrix overloads return GLSL `x * y`. Compound
matrix multiplication uses GLSL `*=`. These are linear products. Scalar operands
are cast to the expression's matrix type, producing diagonal matrices; matrix
casts copy overlapping coordinates and fill remaining entries from an identity.
HLSL row/column types map to transposed GLSL type names, preserving numeric row
storage (`float2x3` maps to GLSL `mat3x2`).

`HLSLTree::EnumerateMatrixCtorsNeeded` and `GLSLGenerator::OutputMatrixCtors`
establish a shader-wide helper registry. Scalar/vector arguments fill rows in
order and omitted cells remain zero. Matrix arguments are ignored by the native
helper body. Once a matrix-copy signature is registered, declaration initializer
emission can select it elsewhere in the same shader, including wrapping another
constructor. Preserve that behavior rather than substituting ordinary matrix
copy semantics. The field interpreter mirrors registry collection and distinguishes
constructor helpers from ordinary GLSL casts. Overfilled helpers remain unknown
because the native helper builder can index outside its component storage.

`test_matrix_semantics.py` verifies independent numerical examples through both
scalar and batched field evaluation. `test_shader_compat.py` checks the native
generated helper/operator source and offline acceptance in both target profiles.
All 82 historically blocked matrix sections now lower and their generated source
passes both profiles under declared reader-derived samplers. These checks establish
translation and mathematical fixture behavior, without claiming driver precision,
all runtime numeric domains or complete appearance prediction.

## Arrays and target constructor rules

`GLSLGenerator::OutputDeclarationAssignment` emits an array initializer as
`element_type[](raw expressions)`, without grouping flat scalar values into
vector elements or padding missing elements. Retain those exact boundaries.
Offline compiler fixtures demonstrate rejection of a flat scalar list for vector
arrays and partial initializers. GLES300 additionally rejects implicit integer
elements in float-array constructors that desktop GLSL330 accepts.

The native reader already exports array size expressions and aggregate element
lists. The field interpreter resolves declared integer constant lengths, preserves
an independent array axis and stores per-element/component validity. Dynamic
index conversion uses the generator's integer cast; bounds violations stay
unresolved. The grid evaluator carries arrays through loops and selected branches,
including bounds checks for writes later overwritten. Array-index side effects
and unestablished sizes remain explicit gaps. Const writes are rejected rather
than predicted as mutable shader state.

The isolated native translator crashes for the unsized-array helper regression
fixture in `test_shader_compat.py`, matching a separate native-reader failure.
Do not convert such a process failure into a normal compilation rejection or
assume that the renderer reaches its fallback handler. The wrapper returns an
unknown compatibility result; no engine source change was made. This behavior
is distinct from the 56 initializer-layout rejections verified in both profiles.

## Stage selection and legacy display

`PresetState.hpp` initializes warp/composite shader levels to 2; `Initialize`
sets both to 0 below preset version 200, reads shared `PSVERSION` at version 200,
and separate keys afterwards. `PerPixelMesh` uses its fixed fragment shader for
disabled/empty/rejected warp code. That shader multiplies sampled RGBA by
`(decay,decay,decay,1)`, using live decay capped at 1. Sampling alpha survives;
custom HLSL warp output sets alpha to 1 through its generated return statement.

`FinalComposite` selects default pass-through for missing/rejected code at a
positive level. Legacy `VideoEcho`/`Filters` are selected only at a disabled
composite level. Their gamma/echo/filter controls come from file-level
`PresetState`, unlike the similarly named main-frame EEL variables. Random hue
offsets and render time are explicit numeric-profile inputs.

`VideoEcho.cpp` defines oversized mesh coordinates, independent corner shades,
clamp/linear sampling, orientation, replacement/additive draw order and gamma
redraw fractions. Preserve its branch difference below gamma1: the non-echo
branch draws a fractional base; the echo branch retains its full base draw.
`Filters.cpp` establishes per-draw blend equations and brighten/darken/solarize/
invert order. The CPU implementation clips source fragments, blends, then stores
the framebuffer, preserving quantization at draw boundaries. It does not claim
bit-identical rasterization/rounding, and no native render was used for validation.

`FinalComposite::InitializeMesh` creates 32×24 vertices with cubic squishing,
duplicated center rows/columns, axis-angle fixups and quadrant-dependent
triangulation. `ApplyHueShaderColors` calculates four normalized RGB shades and
bilinearly assigns vertex colours using source position; actual fragments then
receive triangle interpolation. Preserve both steps and the reversed corner
mapping, rather than directly applying a four-corner gradient at each pixel.
This method does not read `PresetState.shader`/`fShader`.

`generate_composite_adapter.py` copies the native initialization/math/hue bodies,
omitting only the GL upload tail. `native_composite.cpp` supplies data-only state
and records source/body hashes. The independent Python implementation matches
2,304 vertices and 11,880 indices across three profiles, with small float32
polar/colour differences. An additional 64-point barycentric oracle uses native
physical positions and indices. It confirms interpolation within 3.7×10⁻⁷,
without resolving GPU angular-seam edge ownership or raster precision.

`CustomWaveform.cpp`, `WaveformPerFrameContext.cpp` and
`WaveformPerPointContext.cpp` establish custom-wave context, audio preparation and
geometry lifetimes. The wave frame uses external render/audio state; point
read-only inputs copy mutable main-frame variables. Init T defaults reset each
wave frame; frame Q/T copies occur once before points, whose modifications then
carry between points. Position/RGBA reset for each point, while point custom
locals persist. Global memory/register changes retain shape-then-wave order.

Preserve native details: `enabled` uses nonzero integer truth; the final count
does not subtract `sep`; dots still require at least two points; spectrum source
indices truncate float stride; waveform data smooths forward and backward before
scaling. Geometry smoothing inherits the previous vertex's colour at inserted
points. Custom thick-line offsets use half normalized-pixel increments with
width as both denominators, unlike built-in waves. Track these differences rather
than substituting a generic line/wave interpretation.

## Line and point coverage

[OpenGL3.3core](https://registry.khronos.org/OpenGL/specs/gl/glspec33.core.pdf)
sections3.4.1/3.5.1 define point-square coverage, diamond-exit line coverage,
half-open endpoints and fragment interpolation. The GL permits bounded raster
alternatives; canonical math is not a driver pixel-equivalence guarantee.
`line_points.py` uses that canonical model with top-origin coordinate conversion
and explicit tie perturbation. Source draw ordering follows `MilkdropPreset.cpp`;
shape outline/static-thick behavior and centre-darkening fans come from
`CustomShape.cpp` and `DarkenCenter.cpp`.

The GLSL exponential-function rules define zero base with nonpositive exponent
as undefined. Scalar/grid evaluators preserve that boundary rather than using
NumPy's finite0^0value. The third diagnostic's native black-start behavior is
therefore still a target-specific uncertainty; a positive-seed numerical probe
is recorded as a different declared condition, never a native-match claim.
