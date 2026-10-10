# Native shape material temporal candidates

The new `material_temporal` descriptor applies understood source-time curves
to centre, perimeter and border RGBA controls. It retains raw oscillator
period/rate and nominal envelopes, then declares a float32 endpoint domain.
Singleton domains can expose the established native constant colour value;
missing/nonfinite domains keep unknown results.

Native references: prepared source34 `Renderer/Color.hpp` lines135–149 uses
float32 period256/255 and `fmod(fmod(x,m)+m,m)`; `CustomShape.cpp` line401
uses source-alpha blending and its borderIterations expression at215–216
compares raw double alpha against the float32.0001threshold.
Original MilkDrop2.25c `vis_milk2/milkdropfs.cpp` lines2388–2397 packs channels
with integer255scaling/masking; that different policy is not restored here.
Reference root: `/Users/jneerdael/Scripts/milkdrop2_v2.25c_OPEN_SOURCED_20130514_orig_code/`.

The possible-wrap test uses rational modulo-cell comparison and a declared
two-period-ULP zone below boundaries, including negative near-zero rounding
in the remainder-plus-period addition. This is conditional candidate risk,
not an observed event, its rate, or a certificate of all numeric-step absence.
Raw alpha draw gating is separate from modulo-converted blend alpha.

Disabled-border channels do not raise consumed risk. Fill channels are excluded
only when both native fan endpoint alphas are proved zero under finite ordinary
source-alpha blending. One transparent endpoint still affects intermediate
pixels through RGB/alpha interpolation. Texture/geometry/composition/feedback
visibility stays unresolved. No displayed flash frequency or mood is claimed.

Fourteen controls cover native constants, safe oscillation, RGB/alpha period
crossing, near-zero rounding, zero lower endpoint, unsupported audio/state,
raw border gating, disabled borders, float32 singleton/overflow and fan-alpha
consumption. Twelve tests initially failed before the feature existed; the
transparent-fan consumption regression also failed before its guard. Producer
focused193tests pass; independent review passed155plus the final14controls.
The full prepared suite passes**2,517tests and92subtests in144.95seconds**.
Strict MkDocs and whitespace checks pass. These are source-math checkpoints.

The unchanged100source sample includes125shapes in53presets and1500channels:
1122have supported raw rates/conditional wrap results;378stay unknown.
Thirty-two channels across six presets have nonzero nominal time variation.
Eight channels across two presets have possible wrap candidates; four shapes
across those same two presets have possible consumed wrap candidates. Two
shapes in one preset have possible border-gate changes. These are local
source risks, not confirmed visible flashing or Intense labels.

The100preset operations total33.96seconds, maximum1.47seconds for one preset
on this host. These sample timings are not a corpus/hardware guarantee. No
native equation/shader execution, audio/time samples or captured images were
used. `census.json` records the per-preset candidates and source/parser/model/
engine identities. ZIP CRC and all source-byte/hash joins match the preceding
compound-motion batch.

Raw paired batch:
`build/preset-corpus/source-material-temporal-2026-10-10/batch-000001.zip`
SHA256 `a49183816fc1fb8bdbfa36d276ef5790c15ad08e7774471ffbdf32e28b4c5b96`.
Source34matches the observed latest2.3.36full AAR bytes. Unchanged-AAR
runtime qualification remains pending independently. No native code, presets,
shared device or duplicate full corpus was changed or operated.
