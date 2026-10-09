# I14 production control preparation

Prepared source only: no build, GL context, GPU/device operation, canonical edit or Git action was performed. Existing source-only README and finite-controls identities remain historical. Root owns execution and any policy decision.

## Build/run integration

Use the CURRENT frozen retained engine checkout, including the preserved angle, traversal, legacy AD and compiled-custom/fallback policies. From the repair worktree:

```sh
cmake -S build/audit/motion-field-proposal -B build/audit/motion-field-proposal/cgl-normal -G Ninja -DREPO_ROOT="$PWD" -DPROJECTM_SOURCE=/absolute/path/to/current/frozen/patched/engine -DSANITIZERS=OFF -DCMAKE_BUILD_TYPE=Debug
cmake --build build/audit/motion-field-proposal/cgl-normal --target motion-field-controls -j 8
build/audit/motion-field-proposal/cgl-normal/motion-field-controls
```

For a separate sanitizer build, use a new cgl-asan build directory and SANITIZERS=ON, then the same target with ASAN_OPTIONS=detect_leaks=0. The ignored wrapper adds the unchanged native-test CMake subtree and compiles only this new target. It is CGL-only; do not infer GLES acceptance from it. The source was checked against existing declarations by reading, not compiled by the preparing agent.

## Actual production stages

1. Real EEL prepares a unit-aspect8x8 PerPixelMesh once. A single D node at normalized(.375,.375) gets(+.25,-.25) endpoint displacement, plus a uniform+.125 U bias. This offset keeps BC, AD and original endpoints above the unchanged minimum-length branch. It is an explicit endpoint-payload injection, not a claim of original arbitrary CPU/GPU producer parity.
2. Actual production warp vertex transform feedback captures every indexed node. Assert expected final UV and unchanged original-UV varying, node evaluation count81 and bit-identical prepared replay with no second equation execution. Compile actual default, custom and failed-custom fallback paths; a blue color marker distinguishes the requested programs at a covered pixel. Warp, angle, traversal, CPU rotation/signed zoom and topology are untouched.
3. Actual production fragment writes into256-square RG16F or RG32F attachments. Read stored floats from the declared UV attachment. Independent rational AD/BC fields are compared at the query point. This proves triangle/raster/storage behavior in the finite fixture; it does not implement original bilerp.
4. Production MotionVectors::Draw consumes that texture with its actual sampler. Assert its MIN/MAG filters are LINEAR. A narrowly scoped control overrides both to NEAREST for one draw and restores them; that is a test-only intervention, not a policy change. Independently reconstruct expected samples from actual stored texels, separating raster formation from subsequent filtering.
5. Production motion shaders export gl_Position through transform feedback. GL-line odd endpoint and Native quad end-center are compared to the sampled field. The latter averages the two end corners so existing width/antialias offsets cancel on CGL. TF strip ordering assumes emitted triangles0/1/2 and2/1/3; root must retain any platform-specific failure rather than silently accepting another endpoint. No GetUV API is invented.
6. Uniform .173/.17309/.25/.5 payloads isolate storage: explicitly injected fragment COLOR1 values test actual render-target conversion, then CPU float uploads test upload conversion separately. Each actual stored value is compared with motion endpoints. RG32F equality and exact-half controls are asserted. Record observed half conversion; no universal RTZ/nearest claim is encoded.

Independent original four-node accumulation uses raw UV corners in A/B/C/D float order and final1−V. With the declared U bias, start(.28125,.296875), original endpoint(.4296875,.2734375); legacy AD(.46875,.234375); compiled-custom BC(.40625,.296875). Off-diagonal queries and binary corner values isolate interpolation from half quantization. The uniform fractional cases separately reveal storage errors.

## Native witness and explicitly test-only oracle

`diagnostic-motion-field-native48x32.milk` preserves default legacy warp. Actual Native profile:physical3840x2160, reference/authored1280x720, mesh48x32, Standard trails, no transition/diffusion and configured texel offsets0. Equation input Y uses inverse-aspect mapping; D is raw node(18,12) atnormalized(.375,.375), whose equation y=.4296875 for16:9. Its static finite displacement avoids arbitrary pow/trig domains; all vectors stay enabled, excluding I16. The single vector starts(.359375,.35546875). Source original bilerp endpoint(.5078125,.33203125), AD(.546875,.29296875). Freeze actual decoded equation inputs and output rather than trusting decimal parser acceptance alone.

`diagnostic-bilerp-oracle-native48x32.patch` is TEST ONLY. It changes the existing motion texture-query expression in both line and Native motion shaders to an explicit analytic four-node tent interpolation for this static fixture. It preserves the feedback warp, legacy AD, angle/traversal, line/minimum styles and all other engine behavior. Apply only to a separate identified source-instrumented oracle role, paired with the SAME preset/PCM/settings. Never ship it or apply to originals: it is not a general compact-node I14 implementation and does not retain dynamic previous fields. It exists to show the causal endpoint difference under finite declared corners. The square8 patch/preset is the matching source-stage witness.

The default warp samples previous feedback and preserves motion drawing; using ret=0 black warp would erase vectors and would not demonstrate the endpoint. Decay.95 bounds accumulated feedback. Frame0 is initialization; motion consumes the previous valid map on subsequent frames. Qualify submitted endpoints and final-output images separately. Original Windows/D3D pixels are not claimed by this analytic oracle.

## Actual ownership and memory

The CGL component control uses a256-square UV owner to isolate causal math, with separate256-square authored and actual3840x2160 Native motion output FBOs. It is not a full MilkdropPreset Standard ownership test. In the Native witness, actual production MilkdropPreset detail Standard at integer scale3 should own1280x720 UV, not automatically physical4K. Root must inspect actual UV texture binding/size and native/canvas vector draws, and record detail active/fallback status. Fallback can own3840x2160 UV.

RG16F nominal logical storage:3,686,400 bytes at1280x720;33,177,600 at3840x2160. An RG32F replacement adds those same amounts (3.515625 or31.640625MiB), while leaving triangle/raster/filter reconstruction intact. These are logical payload arithmetic, not measured driver residency or bandwidth. Compact RG32F node-map/TF alternatives in the prior README need their own new shader/cache/ownership/lifecycle/cost proof; this packet does not adopt them.

## Gaps and owner gates

The control does not establish an original CPU positive-power/oscillator producer, GLES mediump/highp equivalence, arbitrary clip/discard semantics, minimum-length parity, disabled-to-enabled freshness, context-loss/resize handling or whole-corpus fidelity. Those remain separate I10/I12/I13/I15/I16 concerns or bounded qualifiers. Preserve full prior test suites when adopting any implementation.

For source-selected originals Pithlit Colourfall and city slicker, trace actual nodes/endpoints first, retaining their authored faint alpha, tiny warp, audio/time offsets and custom composite. The test-only analytic oracle patch is invalid for those originals. No source inventory becomes an affected census. Final Native captures must explicitly read final framebuffer0 with exact source/APK/native/preset/asset/PCM/profile hashes. Root must review whether compact-node policy costs and ownership are acceptable; deferral remains valid.
