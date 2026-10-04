# Shader initialization source analysis

This focused subset of the experimental analyzer from [PR #25](https://github.com/johnneerdael/ProjectM-TV/pull/25)
imports its inductive main-Q domain and shader selector proof. It omits audience
scoring, review APK configuration and device-running commands. The source analysis
is a diagnostic tool; parsing or lowering success does not certify appearance.

## Four initialization cases

`martin - ludicrous speed.milk` initializes `index4` with native `rand(12)` and
updates it through a bounded Boolean increment and signed remainder. The main-Q
proof includes initialization, frame resets and persistent custom locals, proving
post-frame q29 in 0..7. Float32 narrowing and signed-int conversion establish
`int(q29)%4` in 0..3. Equality branches use immutable expression identity;
missing cases, negative/nonfinite/overflow inputs, changed recurrences, shared
register effects and local shadows cannot borrow the proof. Runtime scalar/grid
guards retain its premise even when the result folds to a constant.

The other three presets are `Serge + martin - crystal palace tunnel003.milk`
(`mus`), `martin - mandelbox explorer - wreck diver nz+ liquititty.milk`
(`dist_c`) and `martin - organic light.milk` (`uv3`). The Microsoft legacy compiler
reflects these globals as external constants with NULL defaults. Previously they
became uninitialized ordinary GLSL globals. Patch 0038 preserves uninitialized
scalar/vector float globals as uniform inputs and uses the existing initialized
per-invocation copies when shaders write them. Mixed comma declarations preserve
individual storage classes. Locals, static/const declarations, initialized globals,
arrays and matrices retain their previous handling.

The versioned `projectmtv-implicit-extern-zero-v1` target policy models GLES link-time
zero initialization for unbound implicit inputs. An explicit binding supplied when
lowering or evaluating a scalar/grid field overrides that default, including different
values for different grid lanes. The policy is enabled only for declarations carrying the native
implicit-uniform marker, in a reader stamped for the new engine. `strict-v1` keeps
external inputs symbolic. It never initializes a local just because its name matches.

This focused tool retains source parsing, equation-domain proof, shader lowering,
and offline compatibility checks. It does not include the experimental pipeline
simulation from PR #25. No image or device result is inferred from source checks.

This policy defines current core behavior. It does not claim equivalence to old
D3D9 device-register history, nor does NULL legacy reflection prove a zero value.
Authored presets and assignment order are unchanged. Before/after visual differences
for previously undefined values cannot be interpreted as appearance regressions
without a specified input policy.

## Build and validate

Initialize recursive submodules. Apply the committed projectM patch series through
an Android build or the native test runner before building source adapters. Build
host regressions using the normal repository prerequisites:

```sh
bash core/src/test/native/run_native_tests.sh
```

The Preset Lab CI job reuses its prepared engine and archive, builds the two CPU-only
adapters (`milk-native-reader`, `milk-shader-translate`), and runs:

```sh
python -m pytest tools/milk-analyzer -q
```

For a retained host engine build, configure adapters explicitly:

```sh
cmake -S tools/milk-analyzer -B build/milk-analyzer/native \
  -DENGINE_SOURCE=/absolute/path/to/patched/projectm \
  -DENGINE_BUILD=/absolute/path/to/host/build \
  -DENGINE_IDENTITY_FILE=/absolute/path/to/build-identity.json \
  -DSANITIZERS=OFF
cmake --build build/milk-analyzer/native -j 4
```

Match `SANITIZERS` to the linked archive. The identity JSON records pinned commit,
patch digest and instrumentation scope. Native reader fixtures retain raw and
assembled equation trees separately and stamp the selected loading policy. Prepared
historical adapters cannot certify the new target policy. The broader original
PR #25 suite remains a supplemental compatibility check; it is not imported here.

The native tests exercise actual parser generation, default and nonzero input values,
copy reset across invocations, local/static/initialized controls and preset hashes
checked each time the tests run. Offline translator tests require `glslangValidator`.
Numerical source tests require NumPy and pytest from the existing
`tools/preset-lab/requirements.lock`. No app runtime dependency is added.

## References

- [D3D9 global shader inputs](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-writing-shaders-9)
- [D3D9 application-driven constant initialization](https://learn.microsoft.com/en-us/windows/win32/direct3dhlsl/dx-graphics-hlsl-using-shaders-9)
- [GLSL ES 3.00 storage and initialization rules](https://registry.khronos.org/OpenGL/specs/es/3.0/GLSL_ES_Specification_3.00.pdf)
