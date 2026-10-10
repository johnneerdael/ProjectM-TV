# Optional precision-query component

Date: 2026-10-10. The bridge exports existing pure scalar Fields into FPCore and
FPTaylor requests, retaining exact existing binary literals and operation order.
Callers declare finite input domains and a common binary32/binary64 format.
Unsupported casts, phase-qualified bindings, division policies, effects and
texture operations are rejected rather than replaced. This common-format model
is distinct from the engine's mixed EEL/upload/shader/storage pipeline.

## Actual integration and controls

`source_precision_export.export_precision_query` is a dependency-free exporter.
`run_fptaylor_js` executes a separately supplied portable FPTaylor bundle under
a process deadline. Query, bundle and config bytes are frozen, their hashes are
retained, and runtime identity is checked before/after. The worker keeps all
diagnostics, rejects oversized returned records and never supplies a native proof
certificate. The portable interval backend excludes trig.

A mutation regression verifies that an edited live bundle cannot change the
executed snapshot while retaining the old hash. Prepared FPTaylor controls and
export negatives pass. An independent review's provenance finding was fixed
with this regression before qualification.

Daisy built from its unchanged pinned source with Java25/SBT1.9.9. Java26 exposed
a Comparator/Ordering conflict; the failed build was preserved and the supported
JDK was used. A local development truststore reuses the OS-trusted proxy root
without disabling TLS validation or modifying system Java truststores. No tool
implementation was copied into the app or analyzer.

The same emitted FPCore requests run through Daisy's official Tree-sitter/dataflow
CLI with Float32 and affine ranges. Four positive controls (cancellation, linear
gain, correlated quadratic and trig) compute tool-model error estimates. Both
tools reject the overflow case; portable FPTaylor rejects trig before execution.

For `(1+x)-x`, x in [0,16777216], the exact nominal result is1, while binary32
rounding at the upper endpoint produces0. FPTaylor bounds absolute error by
1.0078125; Daisy by1.0000001192092896. This checks that real simplification is not
a native floating-point equivalence theorem. It is not a whole-preset error bound.

## Authored source cases and cost

The unchanged fixed32 source selection contains115 consumed audio-dependent mesh/
shape control fields. Only two nontrivial calculations fit this narrow bridge and
the declared band [0,2] domains. Both execute in FPTaylor and Daisy:
`warp` in Fumbling_Foo & Flexi, Martin, Orb, Unchained - Acid Mandala v4d.milk;
`rad` in placebo heal drift backfire depersonified outfro mockternael qolourth
qordially yoresth.milk. Exact preset/query/tool records are retained.

The preliminary all-variable selection included identity audio inputs; it was
excluded from this consumed-control comparison. Supported identity variables
do not count as newly understood calculations. Missing state/input domains and
unsupported functions remain explicit. No previously blocked preset, numerical
prediction or mood score was resolved or promoted. These tools provide an
independent, reusable precision-query facility for later concrete discrepancies.

Tool time and process-inclusive time are recorded separately per case. There is
no measured end-to-end predictor speedup. Neither compiler acceptance nor a
roundoff estimate establishes native behavior, image fidelity or visual quality.

## Other precision candidates

Herbie was subsequently prepared in an isolated Minimal Racket 9.3 runtime and
executed on both exact consumed-source FPCore inputs plus the cancellation
control. All three inputs produced proposals in 4.425 seconds total with fixed
seed 12345 and bounded deadlines. An unsound-egraph warning on the audio-sum case
is retained: that proposal remains quarantined and unverified. The cancellation
proposal 1.0 changes binary32 behavior at the upper input endpoint, demonstrating
why suggestions belong to separately labelled new/adapted effects. None modifies
authored prediction arithmetic. See the sibling compiler evidence's HERBIE.md
for exact inputs, proposals, package identities and retained setup failures.
Native FPTaylor was not built; the portable bundle is the qualified backend here.
No CPU/GPU transcendental equivalence or denormal policy is certified.

Official references: [FPTaylor](https://github.com/soarlab/FPTaylor),
[FPTaylor JS](https://github.com/monadius/FPTaylorJS),
[Daisy](https://github.com/malyzajko/daisy),
[Herbie CLI and FPCore](https://herbie.uwplse.org/doc/latest/using-cli.html).
