# Isolated output attempts

Use `run_v2.py` for new protocols. `run.py` remains byte-frozen for the active
baseline and historical measurements; do not overwrite it during that scan.
The renderer, Java/JNI observer, audio, frame selection and pixel inputs are
unchanged. Runner v2 changes transport/evidence handling and therefore requires
a new protocol and capture checks before a corpus scan.

For a rerun, preserve the previous output and metadata in a previous-attempt
folder, allocate a fresh local incoming directory and a unique app-owned remote
output path, then verify the atomic producer result and captures before moving
that incoming directory to the current output. A crash before result publication
cannot inherit a previous success. Invalid/partial data stays in the attempt
folder; failed rows name available producer results explicitly for validation.

Five regression cases fail before and pass after: preserved prior output, unique
remote attempts, crash-before-result rejection, wrong-identity rejection and
verified promotion. The complete host-tool suite passes75 tests. The active
baseline's4395 successful job records were independently compared with the JSON
returned by their instrumentation invocation; all match, with zero stale-return
mismatches at this snapshot. These observations are partial, not corpus completion.

New runner source identity is part of a new protocol. Reuse old baseline records
by their exact render-input signatures without rewriting original provenance.
The upcoming candidate corpus must use v2 after its actual-core controls pass.
