# Offline actual-core corpus comparison

`compare.py` compares the baseline role from one immutable dataset with the
candidate role from another. Run it without a device connection. It reads and
verifies existing evidence and writes only the requested report, which must be
outside both datasets. It never reruns rendering, installs an APK, rewrites a
protocol, or adopts the current host runner as historical provenance.

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/compare.py --baseline build/follow-ups/core-corpus/measurements-core-emu-baseline-v1 --candidate build/follow-ups/core-corpus/measurements-core-emu-candidate29-final --output build/follow-ups/core-corpus/comparison.json
```

The default examines every inventory preset, including explicit missing/pending
cases. `--limit N --offset N` selects an explicitly partial preview in original
inventory order. The tool processes one preset at a time; it retains report
metadata, not the corpus images, in memory. The final JSON includes the full
original protocols, protocol/inventory file hashes, original pair/run paths and
row hashes, original render-input signatures, exact sampled native hashes,
thumbnail identities and native colour metrics. Neither the original datasets
nor their records are retagged.

## Comparable inputs and integrity

Require schema-2 production `projectm-tv:core` / ProjectMJNI / EGL GLES3 evidence.
Verify each selected role's APK, embedded ELF and source/ordered-patch identity,
all packaged preset/texture bytes against the inventory, and both PCM files and
the exact short-input prefix. Require identical inventory and observer hashes,
clock/engine instrumentation, core library entry, prewarm setting, device identity,
2364×1330 dimensions, 30 fps, seed, warm-up/measurement windows and selected-frame
coverage. Reject a bootstrap identity mismatch before writing a report.

APK/core hashes, source commits and ordered patches intentionally differ between
baseline and candidate. Original protocol and runner hashes may differ: v1
baseline evidence remains usable with v2 candidate evidence. Emulator launch PID,
launch timestamp/hash, output-attempt paths and native-proof retention flags are transport provenance retained
in the original protocols; they do not replace matching device/driver checks.

For each available pair, verify its checksum and render-input signature, require
two distinct original jobs in correct repeat order, verify all retained hashes
and sizes, revalidate input packets and producer identities, and run the existing
checkpoint/observer/audit validators. Validate complete frame/name/switch/PCM
traces, selected/native hash agreement and retained PNGs. Android opaque RGBA
PNGs are decoded to RGB for screening; nonopaque or malformed thumbnails fail.
Available identity fields in failed evidence must match their original inputs.
Host failures need explicit diagnostics; a retained producer cannot silently be
ignored or attributed to the wrong attempt. An integrity issue is uncomparable
and makes the CLI exit 1 after saving the report. Missing rows/repeat jobs are
pending, never an invented render failure.

Require the six recorded runtime GL/EGL/fingerprint/ABI fields to be present and
identical in both repeats and across the compared pair. A failure before runtime
identity is available remains uncomparable, even if the candidate succeeds.
Mixed repeat outcomes and unequal selected native repeat hashes also remain
uncomparable. These checks preserve failed evidence without claiming recovery
from an unknown environment.

## Categories and review ranking

| Category | Meaning |
| --- | --- |
| `unchanged_native_samples` | Both sides repeat exactly and all 16 selected native hashes match across sides. |
| `changed_needs_visual_review` | Both sides repeat exactly but selected native hashes change. |
| `recovered_load_compatibility` | Comparable repeated baseline failure/substitution becomes repeated candidate success; no visual-fidelity claim. |
| `new_failure` | Comparable repeated baseline success becomes repeated candidate failure/substitution. |
| `both_failed` | Both sides have comparable repeated terminal failures/substitutions. |
| `nondeterministic_uncomparable` | Repeat, driver or integrity evidence prevents comparison. |
| `missing_pending` | A pair or repeat job is not yet available. |

Rank changed cases by descending mean thumbnail RGB MAE, then descending mean
absolute change in adjacent-pair thumbnail motion, then preset filename. RGB MAE
is the mean absolute channel difference normalized to [0,1]. Motion measures RGB
MAE within each of the eight adjacent selected pairs on each side and preserves
both values and their absolute delta. All sample differences are reported.
Ranking prioritizes review; it provides no pass/fail quality threshold.

`verified_pairs` counts validated terminal pairs, including failed and
nondeterministic pairs. `rendered_successful_runs` counts successful jobs within
those pairs. `recovered_presets` counts only comparable compatibility recoveries.
Category totals cover the selected inventory; `unselected_presets` and
`missing_pending` expose separate preview and pending coverage. `complete_coverage`
means every inventory pair has validated terminal evidence on both sides; it
includes explicit failures and never means every preset rendered successfully.
A live baseline scan can append pairs while this read-only pass runs, so a report
is an incremental observation, not an atomic completion snapshot.

Native colour metrics remain named and unmodified. Neither brightness changes
nor a hard 10% gate imply better/worse output. Thumbnails are screening evidence,
not authored1182 `img_err`; 16 selected hashes say nothing about unread frames.
Even complete attempted coverage produces no full-corpus fidelity verdict or
chill/normal/party classification from one controlled bass stimulus.

## Validation

```sh
build/preset-lab-venv/bin/python -m unittest discover -s docs/superpowers/evidence/quad-follow-up-verification/core-corpus -p test_compare.py -v
```

The fixture suite exercises real APK ZIPs, PCM, row checksums, lossless frame
traces and Android-style opaque RGBA thumbnails. It covers all categories,
corruption, missing evidence, mismatched observer/settings/assets/inputs/drivers,
and repeat/status integrity. A read-only eight-preset local preview verified
8 baseline pairs / 16 successful baseline runs; all 8 candidate pairs remained
pending and there were no integrity issues. That preview is explicitly partial
and supplies no candidate visual outcome.
