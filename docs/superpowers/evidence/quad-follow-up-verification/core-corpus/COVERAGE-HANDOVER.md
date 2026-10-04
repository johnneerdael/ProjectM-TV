# Reusing the first actual-core baseline

The first baseline is still running. Use `baseline-completion-index.json` and the
remote acknowledgement as the completion signal; the committed snapshot below is
partial. Do not substitute the stopped direct-engine dataset for this core scan.

`audit.py` joins the exact preset source bytes to the static family index and
verifies saved pair/job checksums, retained-file hashes, 480-frame producer traces,
requested names, complete JNI PCM blocks, selected-frame coverage, repeat equality,
runtime core identity and render-input signatures. Failed attempts remain explicit;
they count toward attempted coverage without supplying successful samples.

Run this offline export while the scanner advances or after it completes:

```sh
build/preset-lab-venv/bin/python docs/superpowers/evidence/quad-follow-up-verification/core-corpus/audit.py \
  --work build/follow-ups/core-corpus/measurements-core-emu-baseline-v1 \
  --families build/follow-ups/corpus-family-review/preset-index.json \
  --output build/follow-ups/core-corpus/baseline-family-audit.json
```

The output stays outside the immutable measurement dataset. An integrity error
produces a nonzero exit and prevents a complete-coverage claim. Missing pair rows
remain pending. A concurrent scan can add later rows after the export has passed
their inventory position; rerun the export to obtain a newer snapshot.

Each exported preset includes its source SHA256, original protocol/signature/run
paths, terminal status, overlapping source features, shader-source hashes and
driver identity. Successful exact pairs also include all 16 native-frame hashes,
native colour/occupancy metrics and original 256×144 APK thumbnail paths. Adjacent
captured pairs support a coarse motion screen; unread frames have no pixel hashes.

This is suitable for verifying corpus membership and finding candidates for
coverage or settings research. It does not establish chill/normal/party labels:
the scan uses one seeded bass signal, and source membership does not prove shader
execution or compilation. Confirm proposed labels with varied music and visual
review. Thumbnail differences are not the historical authored1182 fidelity error.

Keep prior baseline protocol, paths and hashes when comparing a later candidate.
The historical `candidate28-input-equivalence.json` records that the prepared candidate28 protocol
had the same baseline APK, driver-independent inputs and existing baseline input
signatures. The current prepared candidate29-r3 dataset supersedes candidate28;
its emulator pilot and candidate scan still remain to be run. Neither
a completed baseline nor unchanged control presets prove absence of candidate
degradation across the corpus.

At the historical 1,216-pair snapshot, the audit had 13 negative/positive host
tests and the combined host-tool suite passed 64. Available
failed producer results must match the retained JSON and original job/protocol,
source and runtime identities. Genuine early failures may lack runtime fields;
host-only failures need an explicit error and cannot hide a retained producer.
The initial992-pair snapshot remains historical. `reviewed-family-audit.json.gz`
contains a later1216-pair snapshot with these stricter checks and no integrity
issues; it is still partial.

## Capture-schedule provenance

Checkpoint validation compares each corpus job packet's capture indices with the
immutable protocol configuration before accepting any terminal record, including
a host timeout with a successful producer. Rehashing matching packet/result files
does not authorize a different capture schedule. Short pilot jobs retain the
deterministic schedule for their independently keyed measurement window.

The capture-provenance fix has six RED/GREEN mutation cases and a short-pilot
control; the full host-tool suite passes 120 tests. A partial baseline snapshot
checked 9,460 terminal records (9,459 producer results and one explicit
host-only failure) with zero identity/schedule mismatches. This check does not replace the final complete coverage/frame audit.

The current snapshot includes `capture-provenance-validation.inputs.json.gz`: a
frozen job list with exact row, packet and producer-result file hashes, a list
digest and the snapshot generator hash. Check these hashes before reproducing
the producer validation with `capture_provenance_snapshot.py`. Later jobs or
row annotations are separate snapshots. The list does not claim byte equality
with an older remote checkpoint's storage annotations.

Before declaring the snapshot clean, the collector checks the immutable inventory
and runs `checkpoint.verify_job` for every frozen row. This validates row digests,
job directory/key/source identity, retained files and successful frame-observer
evidence. Corrupt row digests, wrong host-only keys/presets and altered inventories
have four RED/GREEN cases; six snapshot tests and 120 total host-tool tests pass.
The current snapshot has 9,460 terminal records and remains partial coverage.

Snapshot source provenance records the collector, checkpoint validator and imported
`run.py` helper SHA-256 values. Generation checks all three source files unchanged
before publishing; reproduction must check those identities before using the
manifest's exact inputs. The baseline helper remains the frozen original runner.
