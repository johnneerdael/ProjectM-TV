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
It records twenty-four source controls, exact source/reader/model identities, and hashes
of both original and patched projection/filter source references. Custom-stage
acceptance in these controls is an explicit mathematical selection premise,
not an actual compiler acceptance result. The broader test file contains 82
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

The legacy echo extension follows pinned source34 and the original MilkDrop2
draw sequence: gamma/echo/hue draws precede brighten, darken, solarize and
invert. Patched native main code clamps gamma to [0,8] and echo zoom to
[.001,1000] before their float conversion; echo alpha remains unclamped.
Active echo draws the same current main texture twice with signed weights
1-alpha and alpha. The difference bound sums their absolute weights and the
native gamma redraw weights, bounds static hue tint magnitude, then applies
the ordered polynomial filter ceilings. Active echo retains its base draw at
gamma below one; the gamma-only branch has its separate native count epsilon.
Negative/threshold echo alpha selects gamma-only. Invalid integer orientation
conversion uses the native omission fallback after truncation.

These gains hold scalar controls fixed. They describe instantaneous sampled
main colour influence, exclude scalar-control response and retain accumulated
feedback as a separate unknown. Possible echo uses full-display support;
finite contributing source/hue/material domains remain explicit premises.
Opaque/nonfinite controls, unbounded alpha conversion, colour-product overflow,
unresolved selected custom outputs and contradicted finite incoming-main
premises cannot supply a finite legacy certificate. The nominal producer does
not certify native rounding or storage quantization jumps.

`legacy-transfer-196.json` records the exact focused source probe of the 196
previously unresolved fixed2000v5 transfer operators: 187 now have conditional
finite gains (172 possible echo, 15 gamma-only). Seven unresolved custom outputs
and two legacy alpha envelopes remain unknown. The operator probe checkpoint
and final joined producer hashes are recorded separately; the final join also
rejects gamma 0/.1/.5 attenuation for known-invalid incoming native domains.
No full source cohort or rendered frames were run for this extension.

Final prepared prominence, colour-character, static-behaviour, scoring and
native legacy controls passed: 152 tests in 11.87 seconds. Source-only branch,
signed blend, ordered filter, clamp, declared-domain, orientation, nonfinite and
incoming-domain controls were observed failing before their corresponding
fixes. The fixture producer hash at that checkpoint was
`6e63d9da66f437561b67b83614a3c04b03b3101bed3f245182dbd5e062d0ba67`.

The native legacy quad expands horizontally on portrait targets, even without
echo. Source support preservation therefore requires a declared finite positive
landscape or square viewport. Portrait and unknown viewports retain the finite
colour-response gain but use full-display support and the per-texel contribution
ceiling. The portrait/unknown controls first failed with the old area bound;
landscape/square source integrals, finite transparent source and known-invalid
source controls preserve their respective behavior. The prepared combined
suite passed 160 tests in 12.10 seconds. Twenty-four fixture controls were
regenerated under producer hash
`e45955491e50596020b7a122abda00c771dece628bae864f8b417d131c245df0`.
No cohort or source export was run for this focused support correction.

The latest fixture refresh follows the frozen sampled-colour modulus and blur
propagation integration. The existing 24 controls retain their preset and native
reference identities. Their derived prominence model identity is
`fd2bf29bab3acb7e6c6d5e30a3dbc9a773f5fc22e9202efdc0e2ad4b101f1a27`;
the fixture also records source-file SHA256 dependencies for prominence
(`451fac77037ebb1875f1779d149c5f46d3644ff674538201e548b29da78758bb`) and
the modulus (`108c1a42f3a628d80b841055ceb92b3911b61375b7360f87c23478de6c5ccc3f`).
Earlier 124/196-case results retain their original checkpoint identities and
were not regenerated or reinterpreted. This refresh ran no cohort, full tests
or devices.

Reproduce the fixture-only refresh after both modules are frozen:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/static-behaviour-prominence/refresh_prominence_fixture.py
```

The script loads the prepared source-component environment, regenerates only
the existing fixture controls, verifies their preset/reader/reference identities,
checks producer files stayed frozen, and records raw dependency hashes separately
from the producer's derived model identity. Fixed-site two-state modulus evidence
requires independent unit-interval sampled RGBA, held coordinates/masks/uniforms
and valid native source domains. Its per-texel difference ceiling does not imply a
time rate, blur propagation bound or known feedback trajectory.
