# Locked15 evaluator control

This is a non-image evaluator test, not a preset render. Each role runs twice
with seed12345 and two fresh threads executing `value=rand(1000000);`128 times,
then a separate context compiling/executing `value=.;`.

| Role | Fresh-thread streams equal | Lone dot compiles as zero |
|---|---|---|
| Upstream | No | No |
| Without0003 | No | No |
| Patched | Yes | Yes |

All three roles repeat exactly. The verifier requires this complete role set,
retained worker bytes and source/canonical-binary reconstruction, real retained
output and zero execution receipts. [Results](results.json) and
[verification](verification.json) preserve the locked15 source120547f3 identities.
Inputs staged by the generic capture wrapper are recorded, but this control does
not consume a preset, audio or textures and produces no framebuffer.

Full workers/inputs remain in ignored build/patch-proof/locked15-evaluator-v1,
current15-job-bound-workers-v2 and current15-evaluator-worker-v1.
