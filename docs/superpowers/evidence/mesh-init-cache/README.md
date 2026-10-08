# Mesh initialization cache (patch 0016)

Measured 2026-10-08 on the user-authorized Ugoos AM6 (`192.168.50.80`, Android 9, 32-bit `armeabi-v7a`, Mali-G52),
profile build of this repository (`:app:assembleProfile`), user 0, default settings (Auto resolution, 30 fps cap),
pinned preset `$$$ Royal - Mashup (102).milk` (`debug.projectmtv.preset`, cleared afterwards), no audio playing.
Baseline = `main` at `120547f3`; candidate = same plus patch 0016.

simpleperf `cpu-clock -f 1000 -g` on the app process, 40 s per run, only runs that stayed at `surface=1920x1080` / 30 fps:

| | samples (ms of CPU in 40 s) |
|---|---|
| baseline run 1 / 2 | 8,619 / 8,455 |
| candidate run 1 / 2 | 7,706 / 7,352 |

Mean 8,537 → 7,529 ms (−11.8 %). In the baseline `PerPixelMesh::InitializeMesh`, `FinalComposite::InitializeMesh`,
`VertexIndexArray::operator[]` and the `hypotf`/`atan2f`/`atanf` calls they make accounted for roughly 12 % of samples;
in the candidate `InitializeMesh` no longer appears and `hypotf` falls to 0.5 %.

Limits: one preset, one device, silence, two runs per side; run-to-run spread is about 2 %. GPU time and
4K/Native resolution were not measured. A first baseline run was not comparable because Auto raised the resolution
mid-run. Pixel identity is established by the host tests and the `MeshCacheControls` control in
`warp_rotation_test.cpp` (a reused mesh matches a fresh mesh across viewport and grid changes), not by on-device image comparison.
