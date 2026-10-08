# MilkDrop audit repairs — active ledger

The playback target is Native 4K Android TV. Preserve all existing TV improvements. This ledger covers all 33 supplied findings; pending entries are unfinished work.

Baseline: `120547f3fafe475c86ffc3392fb94389841d08f0` (15 TV patches). Both MilkDrop 2 renderer files are byte-identical; MilkDrop 3 remains a separately identified reference. All 33 handoff hashes and all 9,606 preset byte hashes match the supplied inventory.

| ID | Finding | Lexical candidates | Status |
|---|---|---:|---|
| I17 | Built-in opacity replacement and thresholds differ | 5300 | Implemented 0016; focused 4K acceptance passed; review pending |
| I19 | Line-mode raw sample counts differ at matched canvases | 3643 | Source investigated; 4K tradeoff measurement pending |
| I08 | Custom oscilloscope windows are not centered or channel-separated | 508 | Pending investigation |
| I22 | Custom dot waves gain interpolated points | 1875 | Pending investigation |
| I10 | Legacy warp deformation sees the opposite physical Y argument | 1737 | Pending investigation |
| I11 | Legacy warp physical triangle diagonal is reversed | 878 | Pending investigation |
| I12 | Stateful per-pixel equations traverse opposite physical rows | 10 | Pending investigation |
| I14 | Motion reverse propagation uses different interpolation and storage | 794 | Pending investigation |
| I05 | Per-pixel aspect inputs use factors instead of inverse factors | 248 | Pending investigation |
| I16 | Disabling motion vectors leaves a stale target UV map | 435 | Pending investigation |
| I06 | Custom-wave points inherit modified main-frame read-only inputs | 1 | Pending investigation |
| I24 | Shape live thick equations do not select target outline style | 14 | Pending investigation |
| I23 | Thick custom-wave and shape-outline offsets differ | 4951 | Pending investigation |
| I20 | Circle angular spacing and closure smoothing differ | 2736 | Pending investigation |
| I13 | Left-axis equation angle seam changes sign | 204 | Pending investigation |
| I18 | Wave brightening omits original preliminary clamp | 0 | Pending investigation |
| I03 | Small finite divisions and reciprocal powers collapse to zero | 0 | Pending investigation |
| I04 | Signed remainder differs from original absolute-value remainder | 0 | Pending investigation |
| M02 | Inverted-radius border topology differs from target library | 0 | Pending investigation |
| M01 | Negative custom-wave enable executes in predictor but not library | 0 | Pending investigation |
| I25 | Shape/custom-wave colour fractions survive original byte truncation | 5347 | Pending investigation |
| I30 | Display diffuse colours retain floats instead of original byte packing | 155 | Pending investigation |
| I29 | Negative odd echo orientation omits original horizontal flip | 0 | Pending investigation |
| I15 | Minimum motion trails are larger and aspect-dependent | 794 | Pending investigation |
| I09 | EEL named constants round to float before double evaluation | 0 | Pending investigation |
| I31 | Gamma-only pass-count epsilon differs | 68 | Pending investigation |
| I01 | Preset keys are case-insensitive in library/predictor | 2 | Pending investigation |
| I02 | Negative boolean settings use >0 rather than nonzero | 0 | Pending investigation |
| I07 | Stereo bands average channels rather than left only | 8985 | Pending investigation |
| I21 | Extra waveform modes change original modulo aliases | 4 | Pending investigation |
| I26 | Shader vol/vol_att differ from original comma expression | 97 | Pending investigation |
| I27 | mip_y uses height rather than original repeated width | 0 | Pending investigation |
| I28 | Near-equal blur bounds expand instead of collapsing | 8 | Pending investigation |

I17 confirms one affected original with repeatable Native 4K captures and no observed slowdown in that witness. No full affected census or universal performance claim is established. See `ledger.json` for source and handoff identities.
