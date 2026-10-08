# I13 isolated angle seam proposal

All artifacts are under ignored `build/audit/angle-seam-proposal/`. No canonical source, patches, tests/helpers/docs, git state or devices were changed. No GL context or GPU was used. Snapshot identities are in `source-identity.json` (current0001–0027).

## Source contract

Both original sources, `milkdrop2/src/vis_milk2` and original2.25c, are byte-identical for plugin.cpp and milkdropfs.cpp. SHA256 respectively:

- plugin.cpp: c768b9a3a2f434a1a29155eceea32ade812c7cd65f73bf05f63823b9f7dc7d65
- milkdropfs.cpp: 68749d31bb6b3020ca89b1e7630fd704e58a5de8dd6275c9f5ea005c6586a7d9

Original plugin.cpp:2272–2285 builds the mesh angle using atan2f(y*aspectY,x*aspectX), with its center override. milkdropfs.cpp:1839–1842 copies that float angle into double equation ang. The generated exact left-middle axis has +0 Y, negative X and a positive pi seam.

Current PerPixelMesh preserves a raw cached atan2 angle for shader attribute3, but negates it for equation ang. The physical legacy mapping and traversal differ off axis; their existing mapping remains untouched. At the exact left axis only, negation turns the original positive seam into a negative one.

`angle-seam-proposal.patch` changes only that equation assignment: select the cached signed angle for exact legacy/default/fallback left-axis nodes; otherwise retain negation. There is no epsilon, additional atan2, extra evaluation/pass/target/buffer, or change to static cache/upload, topology, traversal, CPU rotation trig or signed zoom power.

Qualification is generated even meshes with positive finite aspect factors. ProjectM::SetMeshSize rounds to even dimensions and bounds8–300; controls cover8x8 and48x32, unit and16:9 aspect. Nonfinite/unsupported aspects and odd direct internal meshes are not certified.

The original signed-zero rule is preserved rather than normalized: atan2f(+0,negative) is positive pi; atan2f(-0,negative) is negative pi. Public mesh generation produces the +0 case. Tests additionally inject a coherent frozen -0 position/angle pair into CPU cache storage and exercise the actual consumer. That stress control is not evidence of a naturally generated negative-zero device mesh.

Custom warp keeps its current equation producer and cached shader angle. The original custom VS is absent, so no original custom-path oracle is claimed. A failed custom compilation resets the same pointer used by the legacy branch, but actual compiled-custom/fallback GL qualification is still pending.

## Executable CPU/attribute proof

```sh
cmake -S build/audit/angle-seam-proposal -B build/audit/angle-seam-proposal/build -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/audit/angle-seam-proposal/build --target angle-seam-controls -j 8
build/audit/angle-seam-proposal/build/angle-seam-controls
ctest --test-dir build/audit/angle-seam-proposal/build --output-on-failure
```

Final RED uses `PerPixelMesh.before.cpp` in the isolated source: controls exit1 with136 failures, and the exact-stock scalar stage exits1 with1 failure. Final GREEN exits0 for both; isolated CTest passes2/2. `results.json`, `red-controls.log`, `red-stock.log`, `green-controls.log`, `green-stock.log` and `green-ctest.log` retain the results. Earlier red.log/green.log belong to the initial128-check version, before additional periodic-predicate controls.

Actual production Prepare executes real EEL and publishes its actual attribute data into a test-only GL upload sink. It verifies equation ang and above(ang,0), every off-axis/cached shader angle, signed-zero cache consumption, unchanged static upload counts/data, evaluation counts, emitted float CPU sin/cos and negative zoom power. A loaded custom producer exercises the existing non-null pointer branch; no custom program was GPU-compiled. No DrawAgain or raster replay was executed.

The test-only sink supplies constructor bookkeeping and captures buffer uploads; it creates no GL context and calls no driver. Existing constructor shader compilation fails into its unusable fallback. Full initial engine compilation emits inherited vendor/renderer warnings; the incremental mesh build retains the existing macOS unused-framebuffer-attachments warning.

Periodic limits need care: sin/cos at plus/minus a rounded float pi are mathematically periodic but not guaranteed bit-identical. Their sine can have tiny opposite signed errors, and a strict above(sin(ang),0) predicate can discriminate. Controls use the actual rounded-angle EEL producer as the expectation and a bounded2e-7 sine magnitude, rather than assuming which neighboring float pi a backend emits. Such candidates remain in the inventory.

## Stock refinement and scalar witness

`stock-refinement.json` re-identifies all204 handoff candidates; all current byte hashes match. Actual production parser/state loading partitions them into151 requesting custom warp,50 configured legacy, and3 whose selected y<.47 expression excludes the exact y=.5 axis output. These are source classifications, not runtime/affected counts. A requested custom program could fall back and must be checked on the actual backend.

The unchanged `Illusion & Rovastar - Dotty Mad Space (Jelly).milk` full per-pixel code, at explicitly file-default frame inputs, changes left-axis sy1.0999 to.8999. This is a bounded scalar witness. It is UV-inactive in that context: cy=.5 and pos.y=0 give v=.5, so stretching (v−cy)/sy+cy remains.5. Warp runs afterward and cannot recover the discarded stretch difference; its frame program also sets warp0. Rotation remains0 and translation is unchanged. Do not call this a rendered affected original.

More promising source-selected originals, all still unexecuted/unrendered here:

- Liquido.milk: file rot=.02; per-pixel line65 at y=.5 selects rot+=.1 for -pi and rot−=.1 for +pi. Later sx/sy lines66–67 require y<.2 and do not overwrite rot. Frame code changes warp/color/zoom inputs, not rot. Thus source-selected rotations.12/−.08 reach CPU trig and rotation of the nonzero left X vector. Bmelgren - Liquirdo 2.milk lines51–53 has the same bounded rot contract.
- ORB - Toy snakes hectic.milk: init state_rot0; frame lines303–307 force state_rot1 when0 and cycle nonzero states; line354 publishes q5. Pixel line360 writes final rot=.05*q5−.05*q5*ang for positive q5; later lines overwrite only dx/dy. At q5=1 the source-selected rotations are approximately.20708/−.10708. The left X vector is nonzero, so this is UV-active in principle. Exclude its sleepy sibling: pixel line349 overwrites q5=0 before rotation and eliminates the angle coefficient.
- Goody's Datura Bloom.milk: file rot=.02, cy=.53 and warp=.01. Bass>.8 enables the nested atan2 angle at pixel301; pixel302 applies sin(rot) as the final rotation. Pixel303 is a double-backslash comment discarded by LegacyEquationCode. Frame code resets sx/sy and edits cx, with no rot overwrite. This is a finite conditional rotation candidate requiring actual compile/evaluation and matched audio.
- fiShbRaiN - psychotic meltdown (peyote mix).milk: treble>1.4 lets frame301 move cy to a random decile and pixel309 adds a signed ang contribution to sy, with no later overwrite. A cy different from.5 and cos(2*time) different from0 makes that stretch UV-active; pixel303 also uses pow(treb,ang) in zoom for treble>1/time not at a sine zero. Freeze actual audio, center, time and entropy before interpreting a capture.

No additional evaluator/build work was run after the parent began isolated circle timing; subsequent candidate tracing was read-only.

## Rendering and acceptance still required

Start matched256x144 authored/output, mesh48x32, Native Standard, no transitions/detail/diffusion, fixed clock/FPS/frame/progress and matching unsigned mono PCM/seed identities. Use a known nonuniform feedback field and a finite branch fixture such as dx=.05*above(ang,0), not an integer wrap displacement on black feedback. Trace raw angle, equation angle and emitted attributes before final-output RGB capture.

Repeat Native Standard4K separately with actual authored/reference/output dimensions and generations recorded. Qualify actual custom compilation/fallback, center/right axis and adjacent rows, strict periodic predicates, prepared replay, no-equation behavior, unchanged original candidates and isolated cost. Freeze both source/artifact identities; source arithmetic is not Windows/D3D or cross-GPU appearance proof. No merge acceptance, workload guarantee or affected census is claimed.

## Parent production CGL proof

Live candidate0027 now has an actual GL control, not constructor sinks: default/compiled-custom/failed-custom fallback;8/9 grids;two frames;direct and prepared replay. Real EEL uses Liquido's angle predicate plus dx=ang*.01. Production attributes show the loaded angle reaching dx and the preserved float CPU sine/cosine buffers; transform feedback checks every emitted warp UV/original UV against independent math. Cached shader angle attributes stay unchanged, equation counts remain once per node, and DrawAgain leaves both outputs and counts unchanged. Blue-channel output at a covered point proves actual custom versus fallback program activity. Baseline fails exact legacy-axis node36; candidate passes51/51 normal renderer controls. [RED](production-cgl-red.txt) · [GREEN](production-cgl-green.txt) · [Normal51](production-normal51.txt).

The first whole-suite attempt failed its program-activity pixel check for odd-grid9 at the central gap in the existing quadrant index builder. The test now checks a covered point; this is a harness correction, not an odd-grid mesh repair. Odd-grid inputs/indexed vertex outputs are checked; complete odd-grid raster coverage is not certified.

Native4K unchanged-original/finite/custom/cost and final integration remain pending. The live candidate does not imply an affected-preset census. Frozen source proposals retain their historical identities.
