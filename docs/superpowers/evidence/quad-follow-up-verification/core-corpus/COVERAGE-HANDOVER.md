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
`candidate28-input-equivalence.json` records that the prepared candidate28 protocol
has the same baseline APK, driver-independent inputs and existing baseline input
signatures; its emulator pilot and candidate scan still remain to be run. Neither
a completed baseline nor unchanged control presets prove absence of candidate
degradation across the corpus.

The initial audit has seven negative/positive host tests. Together with existing
runner, recovery, disk-guard and checkpoint tests, the host-tool suite passes58.
