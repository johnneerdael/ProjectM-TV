# Published2.3.32 byte-equivalent reference

PR67 merged into the experimental predictor parent branch as6680a910 on
2026-10-09. Continuation uses `feat/predictor-static-output-bounds` in the same
`predictor-memory-repair` worktree. Main integration remains a separate gate.

Latest release2.3.32, commit `b3fe686c7190a046f8c91e6cab5333f1ccc57f5f`, is
a documentation-only release. The full published AAR was downloaded from its
versioned release asset, rather than substituting an extracted native library.

Its SHA256 is
`13290b486d08569f229f1f684e57aba849a31a2506270a4d305777322d8d7377`.
Direct comparison with the downloaded2.3.31 full AAR exits0. The tag diff for
`core`, `tools/projectm-patches` and `third_party/projectm` is empty. Native
libraries, Java classes, presets and textures therefore retain exact bytes.

`profiles/published-core-v2.3.32.json` records the32 publication filename/commit,
the reference31 profile hash, and this byte-equivalence method. Historical
qualification scopes remain unchanged: exact-byte source/runtime controls carry
forward; no new runtime capture, whole-corpus appearance or performance credit.
The source engine and independently pinned host CPU archive stay at their
qualified source31 identities.

Corpus defaults select the32 AAR/profile and `-core2332` output directory.
The `core2331` target continues to denote the unchanged engine source policy.
Explicit31 publication inputs and source29 diagnostics remain supported under
their original identities. Changed model/profile/run identities require a new
run folder. No numerical corpus run was started.

38 focused publication/runner controls pass, including latest defaults, direct
full-byte equality, explicit historical31 admission, arbitrary-archive rejection
and worker preflight. Independent read-only review confirms the reference hash,
unchanged qualification fields and exact AAR/CPU guards. Strict MkDocs passes.

Prepared local download:
`build/preset-corpus/published32/projectM-TV-core-2.3.32.aar`.
No new source adapters or native builds were necessary.
