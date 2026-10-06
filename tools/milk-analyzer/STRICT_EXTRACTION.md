# Strict source extraction

`source_extract.py` is the primary extraction path for the no-image classification
contract. It reads exact preset bytes, executes the source-bound equation adapter,
tracks custom shape geometry and evaluates isolated typed composite-shader queries.
It constructs no display/feedback image, calls no optical flow, loads no native
reference frames and starts no device.

```sh
python tools/milk-analyzer/source_extract.py \
  --preset example.milk --audio source-audio.json \
  --binaries /absolute/path/to/source49/adapters \
  --profile gles300 --width 256 --height 144 --output source-features.json
python tools/milk-analyzer/source_classify.py \
  --features source-features.json --profile melodic-techno-v1 --output scores.json
```

The audio JSON is a source-generated native CPU audio report, not a recording of
rendered output. Its engine archive must match the reader and its PCM/audio identity
is preserved. The equation seed defaults to the published2.3.15cold-thread policy;
use `--equation-seed` and `--equation-rng-policy` for an explicitly declared
alternative. The default loading policy models patched2.2.8+assembly/omission;
`--equation-loader-policy strict-raw-v1` retains strict diagnostics.

Shader compatibility is checked offline with the source-bound translator and
`glslangValidator`. Acceptance remains conditional on the declared native profile,
not a device compilation/appearance certificate. A missing/unmodeled composite
path leaves palette features unknown rather than invoking a renderer.

## Isolated colour queries

`strict_source_features.colour_queries` evaluates a lowered shader return expression
under explicit scalar query inputs. The initial maximum is128queries; no prefix is
silently substituted when the budget is exceeded. `--queries` can provide a JSON
list of `_uv`, `_uv_orig`, `_rad_ang` or `_vDiffuse` inputs. These are shader input
coordinates/values, not assumed raster pixel centres. Query overrides cannot replace
the audio, equation or time uniforms produced by the actual source execution.

Missing feedback, material, random, diffuse or polar inputs stay unknown. RGB is
checked finite and clamped to the declared normalized output range before colour
statistics. This does not emulate GPU quantization, transcendentals or full geometry
visibility. The scalar evaluator keeps operation/branch ordering and guarded loops.

Ordinary DAG dependencies identify spatial/texture inputs. Hidden loop-plan
dependencies conservatively prevent a spatial-independence claim. A supported
return expression independent of all spatial/texture inputs supplies a uniform
palette for the declared frame inputs. Spatial query colours alone do not establish
screen-area coverage, so whole-preset palette scores are withheld for them.

The initial record exposes warm/cool balance, coloured support and spatial effective
hue bins for that supported uniform case, alongside custom-shape geometry and sparse
warp-map query displacement. It does not manufacture complete motion, pulse, bass,
symmetry/fractal or arbitrary feedback features from this subset. Unknowns are
actionable requirements for further source math, not image-inspection requests.

## Sparse warp and feedback mathematics

`scene_warp.warp_fields(..., query_uv=points)` reuses evaluated native mesh values,
warp vertex math and triangle interpolation at1…128declared points. It avoids the
viewport grid allocation. The record's displacement measures the query map; it is
not automatically feedback feature velocity or visible movement. Custom warp shader
coordinate changes and native high-resolution/detail policies need separate coverage.

For a restricted affine query map `W(p)=A*p+b`,
`source_transport.affine_transport` calculates old-content positions using
`p_next=A⁻¹(p_old−b)`. A static translation or rotation therefore moves content each
update even though `dW/dt=0`. It reports potential speed and exits from the viewport.
Singular/ill-conditioned matrices remain unresolved. Wrapping/clamping and actual
visibility are not inferred.

`source_transport.linear_feedback_bounds` provides half-life and state estimates
for explicitly supplied constant scalar gain, norm-nonexpansive transport and bounded
injection. It does not infer this recurrence from `fDecay` or certify a preset's
visible trail persistence. Positive numerical underflow is rejected rather than
being returned as zero, and half-life divisions avoid an overflowing denominator.

## Identity and controls

The path freezes model hashes at import, checks them before/after extraction and
requires a fresh process after edits. Context preserves exact source/parse, audio,
domain, compatibility, engine/archive and reader identities. Query policy is part
of the declared domain. Output is a cached strict source feature record; profile
changes can rescore it without executing source again.

```sh
python -m pytest tools/milk-analyzer/test_strict_source_features.py tools/milk-analyzer/test_source_transport.py -q
```

These controls test mathematical/source behaviour, not rendered appearance. Keep
the optional source-field simulator and published-AAR numerical reference separately
labeled. See [source mathematics and original references](SOURCE_MATH.md),
[feature evidence](SOURCE_FEATURES.md) and [scoring assumptions](SOURCE_SCORING.md).
