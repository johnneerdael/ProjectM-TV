# Paired source shape trajectories

The additive `center_trajectory` descriptor joins supported x/y control curves.
Constant and affine-time paths supply centres, velocities and nominal joint
speed. Equal-frequency harmonics supply a reconstructable 2-by-2 matrix,
source circle/ellipse/line classification, principal semiaxes and peak speed.
Different-frequency or mixed drift/harmonic paths retain independent axis
curves and a speed upper bound; unknown/state/audio/nonlinear axes abstain.

Signed rates and phases preserve cosine evenness and sine oddness. Exact
source identities determine degenerate paths; no tolerance flattens a thin
ellipse into a line. Joint-speed overflow stays unknown without losing the
whole preset export. These are continuous authored-coordinate calculations,
not physical screen paths, perceived motion or feedback-motion measurements.
Projection, clipping, discrete frames and numerical trig remain conditions.

Eighteen test-first controls cover known paths, reconstructed positions,
signed phases, near-degeneracy, unmatched frequencies and unknown/nonfinite
inputs. Independent review passed 192 focused tests. The prepared full suite
passed **2,430 tests and 92 subtests in 143.58 seconds**. Strict MkDocs passed.
These results validate source rules, not whole-preset appearance or mood.

The unchanged fixed 100 originals exported with the explicit source34 reader.
There are 40 supported shape paths across 23 presets: 30 stationary, seven
independent-axis paths, one line oscillation and two ellipses. Six presets have
nonstationary supported paths. The remaining 85 shape paths are unresolved;
no unknown path is silently counted as still. Counts overlap across presets.
The raw batch has verified ZIP CRC and exact original-source byte/hash joins
with the preceding feedback-bound sample. `census.json` records per-preset
paths, model/parser identity and archive hashes.

Raw paired batch:
`build/preset-corpus/source-trajectory-2026-10-10/batch-000001.zip`
SHA256: `173ecb69e7c6823746abc243635b62479cb141691649e70bb1bda06e3e0ac015`.

No preset, native engine or shared device was changed. Source34 remains an
explicit conditional source adapter; published-AAR runtime qualification and
default activation are pending separately. No rendered frames were used.
