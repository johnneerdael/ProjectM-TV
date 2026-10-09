# Publication33, identical engine bytes

Downloaded the full published2.3.33 AAR and checksums, verified SHA256 and ZIP CRC,
and compared every AAR byte directly with downloaded2.3.32. Equality holds, and
`git diff v2.3.32 v2.3.33 -- core tools/projectm-patches third_party/projectm` is
empty. This is the docs-only PR68 release, commit
`a3a045bd8a7655e48bce2368008e2ced7d724063`.

The new33 profile retains the previous qualification fields unchanged and binds
its equivalence to the32 profile SHA. It carries forward exact-byte evidence,
not fresh captures or appearance certification. Older31/32 profiles are unchanged.
Numerical corpus defaults now use the full published33 AAR/profile with a separate
core2333 output; source target/core archive remains the qualified source31 pin.
Negative identity guards remain intact.38 focused corpus/default controls and
strictMkDocs pass. Independent review has no findings: full31/32/33 bytes, reference profile hash, historical identities and exact source/AAR guards verified.

No owned corpus runner/worker was live in a successful process query. The Downloads
launcher now points future runs at core2333 output; no run was launched, resumed,
cancelled, modified or relabelled. Source/static work continues in the same worktree.
