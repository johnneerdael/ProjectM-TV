# Source effect prominence controls

The `source-effect-prominence-v1` producer joins source custom-shape support,
native alpha/material envelopes and the final composite transfer. It uses no
raster frames, image processing, shader execution or audio simulation. These
controls qualify a conditional mathematical producer, not visual accuracy or
native device performance. The fixed2000 integration study remains a separate
qualification run.

`prominence_evidence(analysis, description, context)` returns `components` and
`by_component`, with component identity/stage, continuous source support,
opacity, final RGB difference gain, source and displayed contribution intervals,
visible-contrast intervals, feedback uncertainty, source paths and source/model/
context identities. A contribution interval bounds potential normalized
integrated encoded RGB influence. Its visible-contrast lower bound is always 0:
an opaque incoming material may match its destination or be erased by later
draws. Source RGB times alpha fan integrals are exported separately.

The target shape projection was checked against pinned source34 production
`CustomShape.cpp` and original MilkDrop2 `milkdropfs.cpp`: centre=(2*x-1,1-2*y),
NDC radius, aspectY=min(1,height/width), angle=ang+pi/4. The patched TV projection
also translates by (+1/targetWidth,+1/targetHeight) before Y inversion. Polygon
clipping uses continuous ideal trigonometry after finite float32 parameter
conversion. Nominal area remains separate from clipped source support; these
numbers exclude native trig/raster rounding. Pointwise main lookup support adds
a one-target-texel bilinear dilation under the declared Native target-size
premise. Different texture dimensions or a different sampling contract require
separate qualification.

Coincident constant instances share one union footprint. Other configured
instances use max-individual-area and capped summed-area union bounds; opacity
does not multiply an already summed area twice. Constant fan alpha integrals
also bound clipped subsets. Unknown sampled RGBA retains possible influence.
Borders retain an explicit unresolved stroke/replay contribution instead of
disappearing when the fill is transparent.
Arbitrary resampling uses the capped sum of configured instance alpha ceilings
per texel, rather than a single-instance alpha or the source-area integral.
This bounds repeated additive and over blending; unresolved possible borders
retain a unit per-texel ceiling.

Selected custom affine/nonlinear colour paths can attenuate or amplify the
incoming term. Saturation/range proofs can establish output independence under
the declared sampled-RGBA domain. Main/blur-driven coordinates reject the
fixed-sample colour gain: an inner lookup can move an outer lookup across
arbitrary image contrast. A separate whole-output RGB range ceiling may still
bound that remapper. Arbitrary remapping/blur can expand a nonzero footprint to
the entire display. Native legacy gamma is a brightness redraw gain; brighten,
darken and solarize use their bounded pointwise polynomial difference ceilings.

Unknown custom compilation/fallback selection, discard, unsupported gamma/masks,
invalid native material/geometry inputs and zero texture zoom retain uncertainty.
In particular, zero alpha does not certify transparency for known nonfinite
native RGB or radius conversion. A local composite-domain traversal budget keeps
the gain interval unbounded and disables support preservation while retaining
independent component support and opacity. Literal-folding exhaustion keeps
component-local unknowns and uses the existing generic scalar envelope where
available. Neither fallback establishes a finite-domain certificate; the global
semantic traversal budget still propagates with its exhaustion flag.

Scenario scalar input domains and explicit context scalar input domains share
the support/material envelope. Conflicting ranges for the same input name are
rejected explicitly. These are declared mathematical domains, not measured audio.
Accumulated feedback is exported separately;
a tiny current injection is not a proof of permanently tiny feedback influence.

The frozen fixture is
`tools/milk-analyzer/fixtures/static-prominence-controls-2026-10-10.json`.
It records fifteen source controls, exact source/reader/model identities, and hashes
of both original and patched projection/filter source references. Custom-stage
acceptance in these controls is an explicit mathematical selection premise,
not an actual compiler acceptance result. The broader test file contains 49
controls, including guarded Z3 range refinement that rejects an impossible
on-screen centre without sampling time. The proof retains its nominal numeric
model and `native_numeric_certified=false`.

Validation on 2026-10-10:

```sh
MILK_PROOF_PYTHON=/Users/jneerdael/Scripts/source-analysis-evaluation/python-env/bin/python build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer/test_source_prominence.py tools/milk-analyzer/test_source_shape_contribution.py tools/milk-analyzer/test_source_fill_envelopes.py tools/milk-analyzer/test_source_texture_envelopes.py -q
```

Initial result: 65 passed. The initial missing-producer controls failed before
implementation; additional coordinate-domain, finite-conversion and proof-range
controls also failed before their corresponding fixes. Prepared full-suite and
source-only paired-export qualification belong to the integration task.

The budget-repair prepared prominence, colour-character, static-behaviour and scoring
controls passed together: 92 tests in 9.77 seconds. This includes the 964-node,
48-sample composite budget regression, the three hash-bound original literal
budget failures, invalid UV/material transparency controls, global traversal
exhaustion, declared context ranges and conflicting-domain rejection. The initial ten
fixture controls were regenerated under that producer hash with all preset,
reader and source-reference hashes unchanged.

The exact 124 failed members of the fixed2000 study were re-extracted through
one copied pinned native reader and the frozen compatibility joins. All 124 now
retain prominence components, with zero prominence or support exceptions.
`budget-recovery-124.json` records their preset identities, component identities,
guarded transfer evidence and producer/reader/result hashes. The 121 composite
domain-budget cases retain unbounded transfer and no pointwise support claim;
the three literal-budget cases retain component-local geometry unknowns. This
recovery does not establish complete-model mood eligibility.

The subsequent aggregate-alpha repair passed 98 prepared prominence,
colour-character, static-behaviour and scoring tests in 9.72 seconds. Four new
controls first reproduced the unsafe single-instance ceiling with two/twenty
coincident instances under additive/over blending. A fifth first reproduced
the resampled possible-border zero; a pointwise control verifies the original
source integral remains the bound. The fixture now includes these five controls
under producer hash `0eae7e2fb03d6abd67292af9e39f1599f7d3f3be0fa441e32bf1774e5684ce0c`.
The 124-case census above retains its original checkpoint hash; no cohort was
rerun for this focused repair.
