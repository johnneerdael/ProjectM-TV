# I15 — retain motion-vector visibility minimum

**Disposition: retain the aspect-aware visibility minimum and existing diffusion policy. No engine patch.** Actual endpoint/uniform controls and repeated Native4K current/width-reference images qualify this owner decision.

Original uses1/width. Current base threshold is sqrt((1.25/W)^2+(1.25/H)^2), scaled by the line reference only when diffusion runs. At16:9, zero displacement assigns both normalized components to the minimum, giving roughly(2.55,1.43)current pixel components versus(1,.5625)original. Its total normalized length is sqrt(2)×minimum. Small nonzero vectors preserve direction; long vectors remain unchanged. Authored and Native targets have distinct minima and diffusion admission.

[Actual production controls](production-cgl-controls.txt) record minimum/length uniforms, selected previous texture, shader endpoints, alpha and counts for square/nonsquare/reference/diffusion profiles. Zero-alpha submits nothing; long displacement is unchanged. These component controls do not invent a GetUV API or certify the separate disabled-frame freshness bug.

The shared44Nativejobs and [four unchanged Rovastar runs](minimum-stock/native-results.json) pass per-frame GL/name/cleanup/finalREAD0 and exact selected-RGB repeats. API34ARM64/GLES3/hostGPU, current27/ac3, output3840×2160/Standard1280×720, commonPCM/seed12345/30FPS/mesh48×32 remain frozen. The second source role changes only the base minimum to1/viewportWidth, retaining current diffusion, line styles, sampling and all preset bytes. It is not original Windows/D3D playback.

| Rovastar - Parallelogram Bin2 Native4K | Image |
|---|---|
| Current visibility policy | [Current](minimum-stock/native-captures/minimum-original-Rovastar---Parallelogram-Bin-2-before-0/frame-239.png) |
| Original-width threshold on current pipeline | [Width-minimum reference](minimum-stock/native-captures/minimum-original-Rovastar---Parallelogram-Bin-2-after-0/frame-239.png) |

[Comparison](minimum-stock/minimum-comparison.json) records actual image deltas. The preset forces mv_l0 with an enabled dense vector grid, so this is a strong minimum-branch source witness. Its original axis equations have undefined/nonfinite domains; they are unchanged and no cleaned full-original oracle or whole-shader finite claim is made. Finite endpoint-wave siblings visualize arithmetic only and use a different primitive path; they are not full motion renderer references.

Retaining the current visibility policy preserves existing Native4K appearance and adds no shipping work. Reverting to the smaller threshold substantially changes accumulated vector visibility, so it is an explicit owner compatibility choice rather than an incidental rendering correction. Any future option must distinguish physical/authored/reference sizes and diffusion, preserve line widths and all previous-frame/texture ownership rules, and qualify target feedback/performance. Physical-TV timing, Windows output and an affected-corpus census remain unmeasured. I14 interpolation and I16 freshness remain separate.
