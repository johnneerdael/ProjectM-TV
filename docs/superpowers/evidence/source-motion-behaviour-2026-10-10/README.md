# Source movement producer qualification

`source_motion_behaviour.motion_evidence(analysis, description, context)` adds
quantified geometry and nominal native feedback movement. The caller supplies
`viewport=[width,height]` and `feedback_fps`. One x unit is one viewport width;
one y unit is one viewport height. The Euclidean norm is in this normalized
coordinate system, not isotropic physical-pixel distance.

The source-only controls pass **34/34**. The producer plus existing vertex-motion,
warp displacement and warp transport suites pass **87/87** with prepared SymPy.
No renderer, images, optical flow or simulated display/feedback sequence is used.

## Mathematics and scope

For a nominal native sampling map `W(q)=Aq+b`, the forward content map is
`A^-1(q-b)`. Express each displacement as `B(q-.5)+d`. Its exact nominal
uniform-unit-square RMS is `sqrt(d.d + ||B||F^2/12)`, and its maximum is the
maximum of the four convex-norm extreme expressions. Multiply these per-step
quantities by the explicit feedback FPS. Do not multiply source-time derivatives
by FPS. Constant authored rotation, zoom, stretch and translation can move
feedback every step despite zero parameter derivatives.

For bounded uniform dynamic affine controls, use
`||forward displacement|| <= ||A^-1|| * ||backward displacement||`. Preserve
control-domain, aspect and native scalar conversion premises. Spatially varying
control bounds alone do not establish an inverse map.

For a selected uniform native procedural warp `W(q)=Aq+b+g(q)`, derive the four
sinusoidal term Jacobian bounds from source coefficients and the explicit factor
ranges. Use the conservative lower bound `1/||A^-1||F` for the affine minimum
singular value and the procedural Frobenius Lipschitz ceiling. A strict positive
margin proves inverse stability for branches retained in the viewport. Either
native rectangular right-triangle diagonal preserves these per-axis edge
bounds. This does not prove a retained inverse for every feature, model wrapping,
or certify native precision/storage. Large warps and custom folds remain unknown.

A separate sampled-content displacement relation bounds `||W(p)-p||` without
requiring inverse uniqueness. It does not assert a feature trajectory or whole
visible-motion rate. Authored constant affine composite lookups expose isolated
fixed-texture inverse time velocity separately from lookup-coordinate velocity.

Native shape centres already use viewport fractions. Radius is NDC and divides
by two; horizontal radius also multiplies by `min(1,height/width)`. Nominal
centre, breathing and rotation derivatives use the incorporated range/response
calculator. The correlated `sin(time)^2` control demonstrates an actual SymPy
bound improvement. Audio amplitude partials retain their own units and unknown
per-second rate. Persistent state, sides/topology and native conversion failures
remain explicit contributors.

Constant/disconnected source candidates cannot establish zero movement while
native shader selection is unresolved. The independent flash review found this
edge case; the RED-to-GREEN control now retains the native fallback possibility.
Known custom-branch controls bind source/profile/archive-matched hypothetical
accepted-stage evidence; they do not establish native-driver acceptance.

`native-projection-source-identity.json` freezes the inspected patched source31
shape/shader/factor files, parser binary and supplied MilkDrop2 comparison source.
Both sources retain the shape centre/radius conventions and the warp ordering:
zoom, stretch, procedural warp, rotation, translation, aspect correction.
ProjectM-TV's selected shader branch and existing pinned readers remain the target.

## Unchanged real sources

`source-selection.json` freezes the first 100 entries of the original unchanged
fixed 2000 SHA-ranked selection before producer measurement. All 100 original
preset hashes match. The final motion-only check has no source-module changes
or used-dependency changes during extraction. At the declared 1920x1080 / 30 FPS
context it produces:

- 46 bounded geometry trajectory records, 14 with a positive rate.
- Four bounded nominal/retained-branch forward transports,three positive.
- Six sampled-content displacement relations, five positive.
- Seven isolated native affine components,two positive.
- Two quantified authored sampling time partials.

The introduced facts are source estimates. 89 native forward contributors remain
unresolved, along with audio/state/custom-map and native selection gaps. These
unknowns are retained rather than promoted to zero. Integrated prominence,
classification usefulness,the full fixed 2000 and paired exports are separate
qualification gates.

Positive examples include `Mig_068.milk` (shape 3: 0.4472135955 viewport units/sec;
retained native wave transport ceiling: 1.3553357413),
`amandio c - living boxes 2.milk` (retained native wave ceiling: 0.01298928052),
and `LuxXx - Flowwerpowwer.milk` (nominal affine transport maximum: 2.1213208493).
These are ceilings or nominal potential; none asserts observed visible contrast.

The producer used 0.26254 s total, 2.625 ms/source mean; complete extraction took
24.151 s. The shared optional SymPy session made 93 queries with 86 cache hits and
zero timeouts. These figures describe this 100-source local run and include no
physical-TV/native rendering performance measurement.

`first100-census.json` keeps the compact per-source facts and canonical full
SHA256. `first100-census.json.gz` losslessly preserves the full JSON, including
contributing source paths and derivative/proof records. The initial checkpoint
is preserved separately; its older producer identity is not final qualification.

Reproduce the producer check from the worktree with:

```sh
MILK_SYMBOLIC_PYTHON=/Users/jneerdael/Scripts/source-analysis-evaluation/python-env/bin/python build/preset-lab-venv/bin/python docs/superpowers/evidence/source-motion-behaviour-2026-10-10/run-census.py
```

Reproduce the focused suite with:

```sh
MILK_SYMBOLIC_PYTHON=/Users/jneerdael/Scripts/source-analysis-evaluation/python-env/bin/python build/preset-lab-venv/bin/python -m pytest tools/milk-analyzer/test_source_motion_behaviour.py tools/milk-analyzer/test_source_vertex_motion.py tools/milk-analyzer/test_source_warp_displacement.py tools/milk-analyzer/test_source_warp_transport.py -q
```
