# Quad Lines (projectM #682) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Draw projectM's waveforms, custom waves, shape outlines, dots and motion vectors as anti-aliased quads whose width follows the render size, so presets look the same at every quality level and lines are no longer aliased on Android.

**Architecture:** A new projectM patch (`0021-quad-lines.patch`) adds a per-instance setting `projectm_opengl_set_line_reference_height()`. With 0 (the library default), every line is drawn exactly as today; the frames stay bit-identical. With a height (the app uses 1080), a shared `LineRenderer` draws each line strip as one instanced draw: one instance per segment, a 4-vertex triangle strip expanded in pixel space in the vertex shader, with miter joins and a one-pixel anti-aliased edge in the fragment shader. MilkDrop's "thick" lines (drawn four times with 1 px or ½ px offsets) are emulated by a wider line drawn more than once, with constants calibrated by measurement. preset-lab gets a `line-compare` command that renders every preset in both modes on identical frames and compares brightness.

**Tech Stack:** C++14 (projectM), GLSL `#version 300 es` / `#version 330` (header prepended at runtime), OpenGL ES 3.0 instancing, GTest (host), Python 3 + numpy + OpenCV (preset-lab), Android NDK build through Gradle.

**Spec:** No separate spec. The **Design** section below is the spec. Background: the evaluation of projectM issue #682 in this session, https://github.com/projectM-visualizer/projectm/issues/682 and https://wwwtyro.net/2019/11/18/instanced-lines.html.

## Design

> **Amended 2026-10-03 during Task 4 (controller ruling, see the SDD ledger):** quad lines default to a **hard edge** (pixels whose centre is within `[-halfWidth, halfWidth)` of the line, at least 1 px wide, alpha × `min(2·halfWidth, 1)` for thinner lines). The 1 px anti-aliased edge of decision 3 is opt-in through `projectm_opengl_set_line_antialiasing(instance, bool)` (`RenderContext::lineAntialiasing`, default false), because measurement showed it darkens feedback presets (−14 % on a thin-wave preset at 1080) while the hard edge matches MilkDrop exactly. `LineRenderer::Begin` takes `(transformation, const Renderer::RenderContext&)`.

> **Noted 2026-10-03 (after implementation):** projectM issue #682 suggests round joins and end caps for waveforms (miters for shapes). All strips use miter joins and flat ends instead: the article's round joins draw a circle over every joint, which blends joint pixels twice and makes beads on translucent or additive waves (feedback presets amplify that); at 1 px (1080) and 2 px (2160) the join shape is sub-pixel; MilkDrop's own lines have no round joins, and miters let thin quad lines light exactly MilkDrop's pixels. Round end caps on open waveforms (no overlap) remain a cheap option if 4K images show rough wave ends.

> **Amended 2026-10-03 (after implementation, user-approved):** decision 1's width rule is clamped: `lineScale = max(1, viewportHeight / referenceHeight)`. At and below the reference height (1080) lines are drawn exactly as at it, MilkDrop's 1 px lines at full brightness; above it they widen in proportion (2 px at 2160, unchanged). Lines thinner than 1 px faded by their width made feedback presets go dark on the PC (`$$$ Royal - Mashup (191)` black at 480p, `(103)` 0.056 against 0.24 at 1080) and thick lines 8–34 % too bright at 480p. With the clamp, new 480p is within −5 % to +1 % of GL lines at 480p and 1080 renders are hash-identical to before. Decision 5's "below 1 px" case no longer occurs (scale ≥ 1). The 241-preset sample's ladder drift is now quoted between 1080 and 1440 (median 2.0 % quad against 4.3 % GL lines); between 720 and 1440 it is 10.0 % against 10.9 %, because 720 draws as GL lines.

> **Amended 2026-10-03 (after implementation, user-approved):** two simplifications. (a) Decision 4 for the main wave: the thick main wave is no longer two slope-aware bands (2 + t and 2 − t px); like thick custom waves and shape outlines it is MilkDrop's own scheme, the thin line drawn four times offset by (0, 0), (+x, 0), (+x, +y), (0, +y) with the main wave's increments (`2 / viewportSize` in its −1…1 coordinates, a pixel), scaled by `lineScale`. The slope term (`LineStyle::slopeHalfWidth`, `slope_half_width`, `SlopeHalfWidthForPass`) is gone. On synthetic presets the thick main wave matches GL lines within 0.13 % luma at 1080 (as the thin one does), and `$$$ Royal - Mashup (191)` at 1080 went from 0.73 to 1.008 of GL lines. (b) Decision 1, following projectM's main developer: the scale is area-based, `lineScale = max(1, sqrt((W·H) / (refW·refH)))`, so a line covers the same share of the picture at any size and aspect ratio. The API is `projectm_opengl_set_line_reference_size(instance, width, height)` (0 in either: GL lines, the default); the app passes 1920×1080. At 16:9 the scale equals the old height ratio exactly, and the frames of the fixed list and the synthetic presets at 1080, 1440 and 2160 are byte-identical to the height-based build.

> **Noted 2026-10-03 (after implementation):** the waveform's sample count follows the reference size too. MilkDrop's Line, DoubleLine, DerivativeLine and the 2077 Wave9/WaveX/Wave11 modes draw a third of their samples when `samples > viewportSizeX / 3` (160 instead of 480 dots below 1440 px), so at the reference 1024×768 MilkDrop draws 160 dots while 1080 and 2160 drew 480; sized as at the reference, three times the dots washed out feedback presets (`$$$ Royal - Mashup (103)`, main wave dots: 0.50 mean luma at 1080 against 0.22 for GL lines at 1024×768). With a reference size the rule now uses `SampleDecisionWidth()` (`LineGeometry`), render width / `lineScale` (1182 px at 1080 and 2160 with reference 1024×768), else the render width, so reference 0 is byte-identical; 103 is now 0.21 at 1080 and 0.23 at 2160.

> **Amended 2026-10-03 (after implementation, user-approved):** the reference is always MilkDrop's 1024×768; the *Advanced › Line thickness* setting (1024×768 or 1080p) is removed, and a saved value is ignored. Above the reference area two more of MilkDrop's render-size-bound quantities follow the reference: `Waveform::MaximizeColors` fades the spiro/hash modes by `MaximizeColorsTextureSize()` (max of the reference instead of the render size), and `BlurTexture::Update` builds blur1–3 as from a source of `BlurSourceFor()` (render size / `lineScale`, 1182×665 at 1080 and 2160), the first pass reading the previous frame's mipmaps (`glGenerateMipmap` per frame) at log2 of the scale. Both helpers are pure and unit-tested; reference 0 and renders at or below the reference area stay byte-identical. On 18 presets against GL lines at 1182×665 (16:9 with the reference's area), 17/18 are within ±10 % at 1080 and 14/18 at 2160 (10/18 before the blur rule). Not adopted: scaling the motion-vector minimum length (fixed one preset, worsened another). Not fixable this way: presets' own `texsize` use and the 4:3 → 16:9 aspect change.

> **Noted 2026-10-03 (follow-up check, no change):** custom waves, shape outlines and the main wave were re-measured on the canvas itself (fDecay 0, additive alpha 1/8, a comp shader that point-samples the canvas texel under each output pixel, so each value is an exact hit count). At 1080 and 2160 against GL lines at 1182×665 (shape outlines without `GL_LINE_SMOOTH`, as on GLES), thin and thick custom waves, thick shape outlines and the thick main wave are within ±1.3 % in energy and lit area, with the same hits-per-pixel histogram; alpha-blended thick custom waves are within 0.4 %. An earlier report of +21 % energy for thin custom waves and 16–29 % less lit area for thick ones was a measurement artefact: it rounded hit counts per pixel on the default composite output, which resamples the canvas with a small blur (about 0.47 centre, 0.1 sides). Rounding a blurred image is not linear, and the error depends on the band width and its sub-pixel position. The plain sum of the same output frames is within 0.7 %.

How lines are drawn in our build today (4.1.7 + patches 0001–0020):

| Element | File | Primitive | "Thick" |
|---|---|---|---|
| Main waveform | `MilkdropPreset/Waveform.cpp` | `GL_LINE_STRIP` / `GL_LINE_LOOP`, color via constant attribute 1 | 4 passes, offsets 0/+1/+1/0 px in x and y (`2 / viewportSize` in NDC) |
| Main waveform dots | same | `GL_POINTS`, size 1 | always 4 passes (2×2 px block) |
| Custom waves | `MilkdropPreset/CustomWaveform.cpp` | `GL_LINE_STRIP`, per-vertex color | 4 passes, offsets `1 / viewportSizeX` NDC (½ px in x, about ¼ px in y) |
| Custom wave dots | same | `GL_POINTS`, size 2 if thick else 1 | 1 pass |
| Shape outlines | `MilkdropPreset/CustomShape.cpp` (batched by patch 0006) | `GL_LINE_LOOP` | 4 passes, ½ px offsets |
| Motion vectors | `MilkdropPreset/MotionVectors.cpp` | `GL_LINES`, endpoints computed in `PresetMotionVectorsVertexShaderGlsl330.vert` | none |

`glLineWidth` is always 1, and `GL_LINE_SMOOTH` only exists outside `USE_GLES`, so on Android every line is aliased and covers 1 px whatever the render height. The app's automatic quality ladder (`QualityController`, 360–2160) therefore changes how much of the picture lines cover by up to 6×.

Decisions:

1. **Width rule.** `lineScale = viewportHeight / referenceHeight`. A thin line is `1 px × lineScale` wide. The app passes 1080, so the default render size looks like today (anti-aliased) and other sizes keep the same share of the picture. Lines thinner than 1 px stay correct through coverage (alpha falls with width).
2. **Geometry.** One instance per segment; attributes read the strip's point buffer four times, offset by one point each (previous, A, B, next), plus A's and B's colors. The CPU pads each strip (open: `[p0, p0…pn-1, pn-1]`; loop: `[pn-1, p0…pn-1, p0, p1]`) so no per-segment CPU work is needed. Joins are miters; where the bisector is more than 60° off the segment normal, and at strip ends, the segment's own normal is used. Segments never overlap at joins, so each pixel is blended once, like GL lines.
3. **Anti-aliasing.** The quad extends 1 px beyond the half width. The fragment alpha is multiplied by `clamp(halfWidth + 0.5 - |distance|, 0, 1)`, a box filter across the line.
4. **Thick emulation.** Thick = wider line × N passes, from one table in `LineGeometry.cpp`. Initial values: main wave 2 px × 2 passes; custom waves and shape outlines 1.5 px × 3 passes. Task 9 calibrates them.
5. **Dots** stay `GL_POINTS` with `gl_PointSize = base × lineScale` (base 2 for the main wave, 2 for thick custom waves, else 1). Below 1 px the size stays 1 and alpha is multiplied by the area (`size²`).
6. **Opt-in, legacy untouched.** Reference height 0 takes the existing code paths unchanged. preset-lab proves this with frame hashes against a baseline.
7. **Shader compile off the render thread.** `LineRenderer` compiles its program in the `PresetState` constructor, like the other built-in shaders, so the prewarm instance compiles it in the background and the program-binary cache (patch 0002) serves it afterwards.

## Global Constraints

- projectM changes go only into `tools/projectm-patches/0021-quad-lines.patch`. Never commit inside `third_party/projectm`; never edit patches 0001–0020.
- C++14 (projectM sets `CMAKE_CXX_STANDARD 14`): write `namespace libprojectM { namespace MilkdropPreset {`, not `namespace a::b`.
- Shader files have no `#version` line; `MilkdropStaticShaders` prepends `#version 300 es` (Android) or `#version 330` (desktop).
- GLES 3.0 only: `glDrawArraysInstanced`, `glVertexAttribDivisor`, `gl_VertexID`, `isnan`, `isinf` are fine; nothing from ES 3.1+.
- Uniforms used in both stages must have the same precision qualifier (GLSL ES link rule): declare `uniform highp float half_width;` in both shaders.
- Library default `line_reference_height` = 0 (legacy, bit-identical frames). The app sets 1080.
- Code style: match the surrounding projectM code (Allman braces, `m_` members, `//!<` member comments, `auto f() -> T` where the file uses it).
- Commits: end messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push unless the user asks.

## Review Focus

1. **GLES-only shader errors.** preset-lab renders with desktop OpenGL, which accepts things GLSL ES rejects (uniform precision mismatches between stages, implicit int/float conversions). Expected: the line program links on Mali and Tegra. Pinned by the glslang check in Task 4 and the logcat check in Task 11.
2. **Non-finite or huge coordinates from per-point code** (`x = 1e30`, division results). Expected: that segment is skipped or clipped; no full-screen streaks, no GL errors. Pinned by the extreme-preset worker run in Task 6.
3. **Degenerate strips:** 0 or 1 point, 2-point loops, repeated identical points. Expected: nothing drawn for zero-length segments, no out-of-bounds attribute reads. Pinned by the `LineBatch` tests in Task 2 and the shader guard in Task 4.
4. **Render size changes while a preset runs** (auto quality ladder, scaled transitions) and two presets drawing during a blend. Expected: line width follows the new size on the next frame; no stutter from shader compiles. Pinned by Task 11 step 5.
5. **Shapes with many instances** (up to 1024 instances × 100 sides). Expected: batches flush when either the fill buffer or the line batch is full; same draw order as today. Pinned by the instanced-shape preset in the fixed list (Tasks 3, 7).

## Files

| Path | Responsibility |
|---|---|
| `tools/projectm-host-gl-shim.h` (new) | No-op `glInvalidateFramebuffer` for the macOS host build |
| `tools/projectm-host-tests.sh` (new) | Build and run projectM's GTest suite on the host from the patched checkout |
| `tools/regen-projectm-patch.sh` (new) | Rewrite a patch from the submodule's unstaged changes, keeping its header |
| `tools/check-patch-series.sh` (new) | Apply the whole series to a clean export of v4.1.7 |
| `tools/projectm-patches/0021-quad-lines.patch` (new) | All projectM changes below |
| ↳ `src/libprojectM/MilkdropPreset/LineGeometry.{hpp,cpp}` (new) | Pure CPU: width rule, thick table, dot style, strip padding |
| ↳ `src/libprojectM/MilkdropPreset/LineRenderer.{hpp,cpp}` (new) | GL: buffer, VAO, instanced draws |
| ↳ `src/libprojectM/MilkdropPreset/Shaders/Line{Vertex,Fragment}ShaderGlsl330.*` (new) | Strip shaders |
| ↳ `src/libprojectM/MilkdropPreset/Shaders/MotionVectorLineVertexShaderGlsl330.vert` (new) | Motion-vector quad shader |
| ↳ `Waveform`, `CustomWaveform`, `CustomShape`, `MotionVectors`, `PresetState` | Use the renderer when `lineScale > 0` |
| ↳ `Renderer/RenderContext.hpp`, `ProjectM.{hpp,cpp}`, `ProjectMCWrapper.cpp`, `api/include/projectM-4/render_opengl.h` | The setting |
| ↳ `tests/libprojectM/LineGeometryTest.cpp` (new) | GTest for `LineGeometry` |
| `tools/preset-lab/src/preset_lab/line_compare.py` (new) | Two-mode rendering and brightness comparison |
| `tools/preset-lab/src/preset_lab/profiles/line-compare-presets.txt` (new) | Fixed fast-iteration preset list |
| `tools/preset-lab/src/preset_lab/native/worker.cpp` | Reads `line_reference_height` from the job |
| `tools/preset-lab/src/preset_lab/cli.py` | `line-compare` command |
| `tools/preset-lab/tests/test_line_compare.py` (new) | Unit tests for the comparison |
| `core/src/main/cpp/native-lib.cpp`, `core/src/test/native/engine_test.cpp` | App turns quad lines on |
| `README.md`, `docs/ARCHITECTURE.md` | Documentation |

## How projectM is edited in this plan

The worktree's submodule `third_party/projectm` has patches 0001–0020 applied (uncommitted). Task 1 stages them (`git add -A` inside the submodule, never `commit`), so `git -C third_party/projectm diff` shows only this plan's changes. `tools/regen-projectm-patch.sh 0021-quad-lines.patch` writes that diff into the patch file. The Android build's CMake (`core/src/main/cpp/CMakeLists.txt:46-74`) sees 0021 already applied and leaves the tree alone; preset-lab's worker builds from a clean `git archive` plus all patch files, so **always regenerate the patch before building the worker**.

Commands used throughout (run from the worktree root `/tmp/.worktrees/instanced-lines`):

- Host unit tests: `tools/projectm-host-tests.sh`
- Regenerate the patch: `tools/regen-projectm-patch.sh 0021-quad-lines.patch`
- Series check: `tools/check-patch-series.sh`
- preset-lab: `build/preset-lab-venv/bin/preset-lab …` (venv created in Task 3)

---

### Task 1: Host tooling for the patched engine

**Files:**
- Create: `tools/projectm-host-gl-shim.h`, `tools/projectm-host-tests.sh`, `tools/regen-projectm-patch.sh`, `tools/check-patch-series.sh`

**Interfaces:**
- Produces: the four commands listed under "How projectM is edited".

- [ ] **Step 1: Stage the applied series inside the submodule**

```bash
cd /tmp/.worktrees/instanced-lines
git -C third_party/projectm status --short | head -3   # expect " M ..." lines from patches 0001-0020
git -C third_party/projectm add -A
git -C third_party/projectm diff --stat | tail -1        # expect no output: nothing unstaged
git status --short                                       # expect clean: the submodule is ignore=dirty
```

- [ ] **Step 2: Write the GL shim**

`tools/projectm-host-gl-shim.h`:

```c
// Forced into the host build of projectM by tools/projectm-host-tests.sh. Apple's OpenGL 4.1 has no
// glInvalidateFramebuffer (used by patch 0009); a no-op stands in, as in preset-lab's worker.
#pragma once
#ifdef __APPLE__
#define glInvalidateFramebuffer(target, count, attachments) ((void)0)
#endif
```

- [ ] **Step 3: Write the host test script**

`tools/projectm-host-tests.sh`:

```bash
#!/bin/bash
# Builds projectM from third_party/projectm as it is (patches applied) for the host, with its GTest
# suite, and runs the suite. Extra arguments go to the test binary (e.g. --gtest_filter=LineBatch.*).
# Requirements: CMake, Ninja, a C++ compiler, GTest (Homebrew's: brew install googletest).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BUILD="$ROOT/build/projectm-host"
GTEST_DIR="${GTEST_DIR:-$(brew --prefix 2>/dev/null || echo /usr)/lib/cmake/GTest}"
cmake -S "$ROOT/third_party/projectm" -B "$BUILD" -G Ninja -DCMAKE_BUILD_TYPE=Debug \
    -DBUILD_TESTING=ON -DENABLE_SYSTEM_PROJECTM_EVAL=OFF -DENABLE_PLAYLIST=OFF \
    -DGTest_DIR="$GTEST_DIR" "-DCMAKE_CXX_FLAGS=-include $ROOT/tools/projectm-host-gl-shim.h" > /dev/null
cmake --build "$BUILD" --target projectM-unittest
"$BUILD/tests/libprojectM/projectM-unittest" "$@"
```

(`GTest_DIR` must be explicit: without it CMake found a miniconda GTest 1.11 on this Mac whose dylib does not load.)

- [ ] **Step 4: Write the patch regeneration script**

`tools/regen-projectm-patch.sh`:

```bash
#!/bin/bash
# Rewrites tools/projectm-patches/<name> from the unstaged changes in third_party/projectm, keeping the
# patch's header (its lines up to the first "---"). The patches before it must be applied and staged
# (git -C third_party/projectm add -A); new files are added with intent-to-add so the diff shows them.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PATCH="$ROOT/tools/projectm-patches/$1"
SUB="$ROOT/third_party/projectm"
git -C "$SUB" add -N -- src tests
HEADER=""
if [ -f "$PATCH" ]; then HEADER="$(sed -n '1,/^---$/p' "$PATCH")"; fi
DIFF="$(git -C "$SUB" diff)"
if [ -z "$DIFF" ]; then echo "no changes in $SUB" >&2; exit 1; fi
{ if [ -n "$HEADER" ]; then printf '%s\n' "$HEADER"; fi; printf '%s\n' "$DIFF"; } > "$PATCH.tmp"
mv "$PATCH.tmp" "$PATCH"
echo "wrote $PATCH ($(grep -c '^diff --git' "$PATCH") files)"
```

- [ ] **Step 5: Write the series check**

`tools/check-patch-series.sh`:

```bash
#!/bin/bash
# Applies every patch in tools/projectm-patches, in order, to a clean export of the pinned projectM
# (and its projectm-eval submodule), as preset-lab and a fresh clone do. Exit 1 names the first failure.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
git -C "$ROOT/third_party/projectm" archive HEAD | tar -x -C "$WORK"
git -C "$ROOT/third_party/projectm/vendor/projectm-eval" archive --prefix=vendor/projectm-eval/ HEAD | tar -x -C "$WORK"
for patch in "$ROOT"/tools/projectm-patches/*.patch; do
    (cd "$WORK" && GIT_CEILING_DIRECTORIES="$WORK/.." git apply "$patch") || { echo "FAIL $(basename "$patch")"; exit 1; }
done
echo "all $(ls "$ROOT"/tools/projectm-patches/*.patch | wc -l | tr -d ' ') patches apply"
```

- [ ] **Step 6: Run them**

```bash
chmod +x tools/projectm-host-tests.sh tools/regen-projectm-patch.sh tools/check-patch-series.sh
tools/projectm-host-tests.sh 2>&1 | tail -2
tools/check-patch-series.sh
```

Expected: `[  PASSED  ] 108 tests.` and `all 20 patches apply`.

- [ ] **Step 7: Commit**

```bash
git add tools/projectm-host-gl-shim.h tools/projectm-host-tests.sh tools/regen-projectm-patch.sh tools/check-patch-series.sh
git commit -m "tools: host test build, patch regeneration and series check for projectM

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 2: Line geometry (pure CPU) and patch 0021

**Files:**
- Create (in `third_party/projectm`): `src/libprojectM/MilkdropPreset/LineGeometry.hpp`, `src/libprojectM/MilkdropPreset/LineGeometry.cpp`, `tests/libprojectM/LineGeometryTest.cpp`
- Modify (in `third_party/projectm`): `src/libprojectM/MilkdropPreset/CMakeLists.txt` (source list), `tests/libprojectM/CMakeLists.txt` (test list)
- Create: `tools/projectm-patches/0021-quad-lines.patch`

**Interfaces:**
- Produces (namespace `libprojectM::MilkdropPreset`):
  - `enum class LineKind { MainWave, CustomWave, ShapeBorder, MotionVector };`
  - `struct LineStyle { float halfWidth; int passes; };`
  - `struct DotStyle { float size; float alphaScale; };`
  - `auto LineScale(int viewportHeight, int referenceHeight) -> float;` (0 = legacy)
  - `auto LineStyleFor(LineKind kind, bool thick, float scale) -> LineStyle;`
  - `auto DotStyleFor(LineKind kind, bool thick, float scale) -> DotStyle;`
  - `class LineBatch { struct Strip { int firstPoint; int segments; }; void Clear(); auto Append(const Renderer::RenderItem::ColoredPoint*, size_t count, bool loop) -> Strip; auto Points() const -> const std::vector<Renderer::RenderItem::ColoredPoint>&; };`

- [ ] **Step 1: Write the failing test**

`third_party/projectm/tests/libprojectM/LineGeometryTest.cpp`:

```cpp
#include <gtest/gtest.h>

#include <MilkdropPreset/LineGeometry.hpp>

#include <vector>

using libprojectM::MilkdropPreset::DotStyleFor;
using libprojectM::MilkdropPreset::LineBatch;
using libprojectM::MilkdropPreset::LineKind;
using libprojectM::MilkdropPreset::LineScale;
using libprojectM::MilkdropPreset::LineStyleFor;
using Point = libprojectM::Renderer::RenderItem::ColoredPoint;

namespace {

auto MakePoints(std::initializer_list<float> xs) -> std::vector<Point>
{
    std::vector<Point> points;
    for (float x : xs)
    {
        Point point;
        point.x = x;
        point.y = -x;
        point.a = 1.0f;
        points.push_back(point);
    }
    return points;
}

auto Xs(const LineBatch& batch) -> std::vector<float>
{
    std::vector<float> xs;
    for (const auto& point : batch.Points())
    {
        xs.push_back(point.x);
    }
    return xs;
}

} // namespace

TEST(LineGeometry, ScaleIsZeroWithoutReferenceOrViewport)
{
    EXPECT_EQ(LineScale(1080, 0), 0.0f);
    EXPECT_EQ(LineScale(1080, -1), 0.0f);
    EXPECT_EQ(LineScale(0, 1080), 0.0f);
    EXPECT_EQ(LineScale(-5, 1080), 0.0f);
}

TEST(LineGeometry, ScaleFollowsRenderHeight)
{
    EXPECT_FLOAT_EQ(LineScale(1080, 1080), 1.0f);
    EXPECT_FLOAT_EQ(LineScale(720, 1080), 720.0f / 1080.0f);
    EXPECT_FLOAT_EQ(LineScale(2160, 1080), 2.0f);
}

TEST(LineGeometry, ThinLinesAreOnePixelAtReference)
{
    for (auto kind : {LineKind::MainWave, LineKind::CustomWave, LineKind::ShapeBorder, LineKind::MotionVector})
    {
        const auto style = LineStyleFor(kind, false, 1.0f);
        EXPECT_FLOAT_EQ(style.halfWidth, 0.5f);
        EXPECT_EQ(style.passes, 1);
    }
}

TEST(LineGeometry, MainWaveThickIsTwoPixelsDrawnTwice)
{
    const auto style = LineStyleFor(LineKind::MainWave, true, 1.0f);
    EXPECT_FLOAT_EQ(style.halfWidth, 1.0f);
    EXPECT_EQ(style.passes, 2);
}

TEST(LineGeometry, WidthScalesButPassesDoNot)
{
    const auto style = LineStyleFor(LineKind::MainWave, true, 2.0f);
    EXPECT_FLOAT_EQ(style.halfWidth, 2.0f);
    EXPECT_EQ(style.passes, 2);
    EXPECT_FLOAT_EQ(LineStyleFor(LineKind::CustomWave, false, 0.5f).halfWidth, 0.25f);
}

TEST(LineGeometry, MotionVectorsIgnoreThick)
{
    const auto style = LineStyleFor(LineKind::MotionVector, true, 1.0f);
    EXPECT_FLOAT_EQ(style.halfWidth, 0.5f);
    EXPECT_EQ(style.passes, 1);
}

TEST(LineGeometry, MainWaveDotsAreTwoPixelBlocks)
{
    const auto dot = DotStyleFor(LineKind::MainWave, false, 1.0f);
    EXPECT_FLOAT_EQ(dot.size, 2.0f);
    EXPECT_FLOAT_EQ(dot.alphaScale, 1.0f);
}

TEST(LineGeometry, CustomWaveDotsAreTwoPixelsOnlyWhenThick)
{
    EXPECT_FLOAT_EQ(DotStyleFor(LineKind::CustomWave, false, 1.0f).size, 1.0f);
    EXPECT_FLOAT_EQ(DotStyleFor(LineKind::CustomWave, true, 1.0f).size, 2.0f);
}

TEST(LineGeometry, DotsBelowOnePixelFadeByArea)
{
    const auto dot = DotStyleFor(LineKind::CustomWave, false, 0.5f);
    EXPECT_FLOAT_EQ(dot.size, 1.0f);
    EXPECT_FLOAT_EQ(dot.alphaScale, 0.25f);
    const auto mainDot = DotStyleFor(LineKind::MainWave, false, 0.25f); // 2 px * 0.25
    EXPECT_FLOAT_EQ(mainDot.size, 1.0f);
    EXPECT_FLOAT_EQ(mainDot.alphaScale, 0.25f);
}

TEST(LineBatch, OpenStripRepeatsItsEndPoints)
{
    LineBatch batch;
    const auto points = MakePoints({1, 2, 3});
    const auto strip = batch.Append(points.data(), points.size(), false);
    EXPECT_EQ(strip.firstPoint, 0);
    EXPECT_EQ(strip.segments, 2);
    EXPECT_EQ(Xs(batch), (std::vector<float>{1, 1, 2, 3, 3}));
}

TEST(LineBatch, LoopWrapsAround)
{
    LineBatch batch;
    const auto points = MakePoints({1, 2, 3});
    const auto strip = batch.Append(points.data(), points.size(), true);
    EXPECT_EQ(strip.segments, 3);
    EXPECT_EQ(Xs(batch), (std::vector<float>{3, 1, 2, 3, 1, 2}));
}

TEST(LineBatch, TwoPointLoopHasTwoSegments)
{
    LineBatch batch;
    const auto points = MakePoints({1, 2});
    const auto strip = batch.Append(points.data(), points.size(), true);
    EXPECT_EQ(strip.segments, 2);
    EXPECT_EQ(Xs(batch), (std::vector<float>{2, 1, 2, 1, 2}));
}

TEST(LineBatch, FewerThanTwoPointsDrawNothing)
{
    LineBatch batch;
    const auto one = MakePoints({1});
    EXPECT_EQ(batch.Append(one.data(), one.size(), false).segments, 0);
    EXPECT_EQ(batch.Append(one.data(), one.size(), true).segments, 0);
    EXPECT_EQ(batch.Append(nullptr, 0, false).segments, 0);
    EXPECT_TRUE(batch.Points().empty());
}

TEST(LineBatch, StripsFollowEachOther)
{
    LineBatch batch;
    const auto first = MakePoints({1, 2});
    const auto second = MakePoints({5, 6, 7});
    batch.Append(first.data(), first.size(), false);
    const auto strip = batch.Append(second.data(), second.size(), true);
    EXPECT_EQ(strip.firstPoint, 4);
    EXPECT_EQ(batch.Points().size(), 4u + 6u);
}

TEST(LineBatch, LastInstanceReadsInsideItsStrip)
{
    // Instance i reads points firstPoint + i ... firstPoint + i + 3.
    for (bool loop : {false, true})
    {
        LineBatch batch;
        const auto points = MakePoints({1, 2, 3, 4, 5});
        const auto strip = batch.Append(points.data(), points.size(), loop);
        EXPECT_EQ(static_cast<size_t>(strip.firstPoint + (strip.segments - 1) + 3), batch.Points().size() - 1);
    }
}

TEST(LineBatch, KeepsColors)
{
    LineBatch batch;
    auto points = MakePoints({1, 2});
    points[1].r = 0.25f;
    points[1].a = 0.5f;
    batch.Append(points.data(), points.size(), false);
    EXPECT_FLOAT_EQ(batch.Points()[2].r, 0.25f);
    EXPECT_FLOAT_EQ(batch.Points()[3].a, 0.5f);
}

TEST(LineBatch, ClearEmpties)
{
    LineBatch batch;
    const auto points = MakePoints({1, 2});
    batch.Append(points.data(), points.size(), false);
    batch.Clear();
    EXPECT_TRUE(batch.Points().empty());
    EXPECT_EQ(batch.Append(points.data(), points.size(), false).firstPoint, 0);
}
```

Add `LineGeometryTest.cpp` to the `add_executable(projectM-unittest …)` list in `third_party/projectm/tests/libprojectM/CMakeLists.txt`, after `HLSLModuloTest.cpp`.

- [ ] **Step 2: Run the test to verify it fails**

Run: `tools/projectm-host-tests.sh --gtest_filter='LineGeometry.*:LineBatch.*' 2>&1 | tail -5`
Expected: compile error, `MilkdropPreset/LineGeometry.hpp` not found.

- [ ] **Step 3: Write the header**

`third_party/projectm/src/libprojectM/MilkdropPreset/LineGeometry.hpp`:

```cpp
#pragma once

#include <Renderer/RenderItem.hpp>

#include <cstddef>
#include <vector>

namespace libprojectM {
namespace MilkdropPreset {

/**
 * @brief The kinds of lines a preset draws. Each emulates MilkDrop's "thick" lines differently.
 */
enum class LineKind
{
    MainWave,
    CustomWave,
    ShapeBorder,
    MotionVector
};

/**
 * @brief Width and pass count of a quad line.
 */
struct LineStyle
{
    float halfWidth{0.0f}; //!< Half the line width in render pixels.
    int passes{1};         //!< How often the line is drawn (MilkDrop blends most pixels of thick lines more than once).
};

/**
 * @brief Size of a dot drawn as a GL point.
 */
struct DotStyle
{
    float size{1.0f};       //!< gl_PointSize in render pixels, at least 1.
    float alphaScale{1.0f}; //!< Alpha factor for dots smaller than one pixel (their area).
};

/**
 * @brief Line width factor: the render height over the reference height.
 * @return 0 when quad lines are off (no reference height) or the viewport is empty.
 */
auto LineScale(int viewportHeight, int referenceHeight) -> float;

/**
 * @brief Quad line style matching MilkDrop's thin (1 px) or thick line of this kind, at this scale.
 */
auto LineStyleFor(LineKind kind, bool thick, float scale) -> LineStyle;

/**
 * @brief Point size matching MilkDrop's dots of this kind, at this scale.
 */
auto DotStyleFor(LineKind kind, bool thick, float scale) -> DotStyle;

/**
 * @brief Collects line strips for one upload, padded for instanced drawing.
 *
 * Every segment is one instance that reads four consecutive stored points: the point before the
 * segment, its two ends, and the point after it. A strip's first and last point are repeated (an
 * open strip ends flat there), a loop's are wrapped around.
 */
class LineBatch
{
public:
    using ColoredPoint = Renderer::RenderItem::ColoredPoint;

    /**
     * @brief Where a strip's points start in the batch and how many segments it has.
     */
    struct Strip
    {
        int firstPoint{0}; //!< Index of the strip's leading pad point.
        int segments{0};   //!< Number of segments (instances); 0 draws nothing.
    };

    void Clear();

    /**
     * @brief Adds a strip of points.
     * @param points The strip's points; may be null if count is 0.
     * @param count Number of points. Fewer than two draw nothing.
     * @param loop True to connect the last point back to the first.
     */
    auto Append(const ColoredPoint* points, size_t count, bool loop) -> Strip;

    auto Points() const -> const std::vector<ColoredPoint>&;

private:
    std::vector<ColoredPoint> m_points; //!< All strips, padded, in append order.
};

} // namespace MilkdropPreset
} // namespace libprojectM
```

- [ ] **Step 4: Write the implementation**

`third_party/projectm/src/libprojectM/MilkdropPreset/LineGeometry.cpp`:

```cpp
#include "LineGeometry.hpp"

namespace libprojectM {
namespace MilkdropPreset {

namespace {

// MilkDrop draws a thick line four times, offset by a pixel (main wave) or half a pixel (custom
// waves, shape outlines), so most pixels of the wider line are blended two or more times. These
// are the width and pass count of the quad line that gives the same brightness, measured with
// preset-lab's line-compare command.
struct ThickEmulation
{
    float thickHalfWidth;
    int thickPasses;
};

constexpr ThickEmulation MainWaveThick{1.0f, 2};
constexpr ThickEmulation CustomWaveThick{0.75f, 3};
constexpr ThickEmulation ShapeBorderThick{0.75f, 3};

constexpr float ThinHalfWidth = 0.5f; //!< MilkDrop's lines are 1 px wide.

} // namespace

auto LineScale(int viewportHeight, int referenceHeight) -> float
{
    if (viewportHeight <= 0 || referenceHeight <= 0)
    {
        return 0.0f;
    }
    return static_cast<float>(viewportHeight) / static_cast<float>(referenceHeight);
}

auto LineStyleFor(LineKind kind, bool thick, float scale) -> LineStyle
{
    ThickEmulation emulation{ThinHalfWidth, 1};
    switch (kind)
    {
        case LineKind::MainWave:
            emulation = MainWaveThick;
            break;
        case LineKind::CustomWave:
            emulation = CustomWaveThick;
            break;
        case LineKind::ShapeBorder:
            emulation = ShapeBorderThick;
            break;
        case LineKind::MotionVector:
            thick = false;
            break;
    }

    LineStyle style;
    style.halfWidth = (thick ? emulation.thickHalfWidth : ThinHalfWidth) * scale;
    style.passes = thick ? emulation.thickPasses : 1;
    return style;
}

auto DotStyleFor(LineKind kind, bool thick, float scale) -> DotStyle
{
    // MilkDrop's main wave always draws its dots as 2x2 pixel blocks, custom waves only when thick.
    const float base = (kind == LineKind::MainWave || thick) ? 2.0f : 1.0f;
    const float size = base * scale;

    DotStyle style;
    if (size >= 1.0f)
    {
        style.size = size;
    }
    else
    {
        // Points are at least one pixel: fade the dot by the area it should cover instead.
        style.alphaScale = size * size;
    }
    return style;
}

void LineBatch::Clear()
{
    m_points.clear();
}

auto LineBatch::Append(const ColoredPoint* points, size_t count, bool loop) -> Strip
{
    Strip strip;
    strip.firstPoint = static_cast<int>(m_points.size());
    if (points == nullptr || count < 2)
    {
        return strip;
    }

    if (loop)
    {
        m_points.push_back(points[count - 1]);
        m_points.insert(m_points.end(), points, points + count);
        m_points.push_back(points[0]);
        m_points.push_back(points[1]);
        strip.segments = static_cast<int>(count);
    }
    else
    {
        m_points.push_back(points[0]);
        m_points.insert(m_points.end(), points, points + count);
        m_points.push_back(points[count - 1]);
        strip.segments = static_cast<int>(count - 1);
    }
    return strip;
}

auto LineBatch::Points() const -> const std::vector<ColoredPoint>&
{
    return m_points;
}

} // namespace MilkdropPreset
} // namespace libprojectM
```

Add `LineGeometry.cpp` and `LineGeometry.hpp` to `add_library(MilkdropPreset OBJECT …)` in `third_party/projectm/src/libprojectM/MilkdropPreset/CMakeLists.txt`, in alphabetical order (after `FinalComposite.hpp`).

- [ ] **Step 5: Run the tests to verify they pass**

Run: `tools/projectm-host-tests.sh 2>&1 | tail -2`
Expected: `[  PASSED  ] 125 tests.` (108 + 17 new).

- [ ] **Step 6: Create patch 0021 with its header**

```bash
cat > tools/projectm-patches/0021-quad-lines.patch <<'EOF'
Subject: [PATCH] projectM TV: lines as anti-aliased quads that scale with the render size

projectM issue #682. MilkDrop draws waveforms, custom waves, shape outlines and motion vectors as
1 px GL lines (thick ones four times, offset by up to a pixel). On GLES they are not anti-aliased,
and their share of the picture changes with the render size, so a preset that feeds its image back
gets brighter at low and darker at high resolutions.
projectm_opengl_set_line_reference_height() draws them as quads instead: one instance per segment,
miter joins, an anti-aliased edge, 1 px wide at the reference height and in proportion at other
sizes. Thick lines are wider and drawn more than once, matched to MilkDrop's brightness. Dots scale
the same way. 0, the default, keeps the GL lines.
---
EOF
tools/regen-projectm-patch.sh 0021-quad-lines.patch
tools/check-patch-series.sh
```

Expected: `wrote …/0021-quad-lines.patch (5 files)` and `all 21 patches apply`.

- [ ] **Step 7: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): line geometry for quad lines (patch 0021, projectM #682)

Width rule, thick-line emulation table, dot sizes and padded strips for instanced
segments, with host unit tests. Nothing draws with them yet.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 3: The setting, preset-lab `line-compare`, and the legacy baseline

**Files:**
- Modify (projectM): `src/libprojectM/Renderer/RenderContext.hpp`, `src/libprojectM/ProjectM.hpp`, `src/libprojectM/ProjectM.cpp`, `src/libprojectM/ProjectMCWrapper.cpp`, `src/api/include/projectM-4/render_opengl.h`
- Modify: `tools/preset-lab/src/preset_lab/native/worker.cpp`, `tools/preset-lab/src/preset_lab/cli.py`
- Create: `tools/preset-lab/src/preset_lab/line_compare.py`, `tools/preset-lab/src/preset_lab/profiles/line-compare-presets.txt`, `tools/preset-lab/tests/test_line_compare.py`

**Interfaces:**
- Consumes: nothing from Task 2 yet.
- Produces:
  - `Renderer::RenderContext::lineReferenceHeight` (`int`, default 0)
  - `void ProjectM::SetLineReferenceHeight(int height);`
  - C API `void projectm_opengl_set_line_reference_height(projectm_handle instance, uint32_t reference_height);`
  - Worker job config key `line_reference_height` (int, default 0)
  - `preset-lab line-compare [--preset NAME]… [--preset-list FILE] [--sample-every N] [--heights 1080,720,1440] [--baseline report.json] [--concurrency N] [--work DIR] [--worker PATH]`. Writes `<work>/report.json` (`{"summary", "presets", "engine"}`) and `<work>/frames/<sha16>/{legacy,quad}-1080.png`; prints the summary; exit 1 if any run failed or any legacy frame hash differs from the baseline.

- [ ] **Step 1: Set up preset-lab in the worktree and confirm its tests pass**

```bash
python3 -m venv build/preset-lab-venv
build/preset-lab-venv/bin/python -m pip install -q './tools/preset-lab[test]'
build/preset-lab-venv/bin/python -m pytest tools/preset-lab/tests -q 2>&1 | tail -2
```

Expected: all tests pass. If any fail before your change, stop and report.

- [ ] **Step 2: Write the failing Python tests**

`tools/preset-lab/tests/test_line_compare.py`:

```python
from dataclasses import asdict

import numpy as np
import pytest

from preset_lab.line_compare import (LineRunConfig, ladder_drift, line_features, luma_ratio,
                                     mean_luma, summarize)


def test_mean_luma_of_white_is_one_and_of_black_zero():
    assert mean_luma(np.full((4, 4, 3), 255, np.uint8)) == pytest.approx(1)
    assert mean_luma(np.zeros((4, 4, 3), np.uint8)) == 0


def test_mean_luma_weights_green_most():
    green = np.zeros((2, 2, 3), np.uint8)
    green[..., 1] = 255
    blue = np.zeros((2, 2, 3), np.uint8)
    blue[..., 2] = 255
    assert mean_luma(green) == pytest.approx(.7152, abs=1e-4)
    assert mean_luma(blue) == pytest.approx(.0722, abs=1e-4)


def test_mean_luma_rejects_non_rgb_frames():
    with pytest.raises(ValueError):
        mean_luma(np.zeros((2, 2), np.uint8))
    with pytest.raises(ValueError):
        mean_luma(np.zeros((2, 2, 3), np.float32))


def test_ratio_and_drift_skip_black_images():
    assert luma_ratio(0.0, .5) is None
    assert luma_ratio(.2, .3) == pytest.approx(1.5)
    assert ladder_drift(.1, 0.0) is None
    assert ladder_drift(.09, .1) == pytest.approx(.1)


def test_run_config_carries_line_reference_height():
    assert asdict(LineRunConfig(width=1920, height=1080, line_reference_height=1080))["line_reference_height"] == 1080
    assert asdict(LineRunConfig())["line_reference_height"] == 0


def test_features_use_first_key_and_enabled_elements():
    text = ("bWaveThick=1\nbWaveThick=0\n"
            "wavecode_0_enabled=1\nwavecode_0_bDrawThick=1\n"
            "wavecode_1_enabled=1\nwavecode_1_bUseDots=1\n"
            "shapecode_0_enabled=1\nshapecode_0_border_a=0.5\nshapecode_0_thickOutline=1\n"
            "mv_a=0.4\n")
    assert line_features(text) == ["main_thick", "custom_dots", "custom_thick", "shape_thick", "motion_vectors"]


def test_disabled_waves_and_borderless_shapes_have_no_features():
    text = ("wavecode_0_enabled=0\nwavecode_0_bDrawThick=1\n"
            "shapecode_0_enabled=1\nshapecode_0_border_a=0\nshapecode_0_thickOutline=1\n")
    assert line_features(text) == ["main_thin"]


def test_motion_vectors_from_the_legacy_switch_unless_mv_a_is_zero():
    assert "motion_vectors" in line_features("bMotionVectorsOn=1\n")
    assert "motion_vectors" not in line_features("bMotionVectorsOn=1\nmv_a=0\n")


def test_features_ignore_unparsable_values():
    assert line_features("bWaveThick=e\nbWaveDots=1\n") == ["main_dots"]


def _entry(name, ratio, legacy_hash="a", features=("main_thin",), drift=None):
    runs = {"legacy-1080": {"status": "success", "mean_luma": .2, "frames_sha256": legacy_hash},
            "quad-1080": {"status": "success", "mean_luma": .2 * (ratio or 0), "frames_sha256": "q"}}
    entry = {"preset": name, "status": "success", "features": list(features), "runs": runs, "ratio": ratio}
    if drift is not None:
        entry["drift"] = drift
    return entry


def test_summary_flags_presets_beyond_tolerance_and_groups_by_feature():
    entries = [_entry("a", 1.0), _entry("b", 1.05), _entry("c", 1.2, features=("main_thick",)), _entry("d", None)]
    summary = summarize(entries, None)
    assert summary["beyond_tolerance"] == ["c"]
    assert summary["share_beyond_tolerance"] == pytest.approx(1 / 3)
    assert summary["median_deviation"] == pytest.approx(.05)
    assert summary["median_ratio_by_feature"] == {"main_thick": pytest.approx(1.2), "main_thin": pytest.approx(1.025)}
    assert summary["failed"] == 0


def test_summary_reports_changed_legacy_frames_against_baseline():
    baseline = {"presets": [_entry("a", 1.0, legacy_hash="old"), _entry("b", 1.0)]}
    summary = summarize([_entry("a", 1.0, legacy_hash="new"), _entry("b", 1.0), _entry("new", 1.0)], baseline)
    assert summary["legacy_changed"] == ["a legacy-1080"]


def test_summary_medians_drift_per_mode():
    entries = [_entry("a", 1.0, drift={"legacy": .3, "quad": .02}),
               _entry("b", 1.0, drift={"legacy": .1, "quad": None})]
    assert summarize(entries, None)["median_drift"] == {"legacy": pytest.approx(.2), "quad": pytest.approx(.02)}


def test_failed_presets_are_counted():
    entry = _entry("a", 1.0)
    entry["status"] = "failed"
    summary = summarize([entry], None)
    assert summary["failed"] == 1
    assert summary["median_deviation"] is None
```

- [ ] **Step 3: Run them to verify they fail**

Run: `build/preset-lab-venv/bin/python -m pytest tools/preset-lab/tests/test_line_compare.py -q 2>&1 | tail -3`
Expected: `ModuleNotFoundError: No module named 'preset_lab.line_compare'`.

- [ ] **Step 4: Write `line_compare.py`**

`tools/preset-lab/src/preset_lab/line_compare.py`:

```python
"""Compare projectM's GL lines with quad lines (projectM issue #682) on identical frames.

Each preset renders with the same synthetic audio, clock and seeds twice per render height: with
line_reference_height 0 (MilkDrop's 1 px GL lines) and with quad lines scaled to the 1080 reference.
Mean luma over the measurement window compares the two. The legacy frames' hash, checked against an
earlier report, proves the GL-line path unchanged. Line features are read statically from the preset
file (first occurrence of a key wins, as in the engine); per-frame code can still change them.
"""
import hashlib
import re
import statistics
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from .bass_screen import bass_signals
from .identity import canonical_json
from .models import EngineIdentity, JobSpec, PresetRecord, RunConfig
from .worker import render_job

VERSION = "line-compare-v1"
REFERENCE_HEIGHT = 1080
FIDELITY_TOLERANCE = .10
WARMUP_SECONDS = 4
MEASUREMENT_SECONDS = 4
LUMA = np.array([.2126, .7152, .0722], dtype=np.float32)
_KEY = re.compile(r"^\s*([A-Za-z0-9_]+)\s*=\s*(\S+)", re.M)


@dataclass(frozen=True, slots=True)
class LineRunConfig(RunConfig):
    line_reference_height: int = 0


def mean_luma(frame: np.ndarray) -> float:
    if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[-1] != 3:
        raise ValueError("RGB uint8 frame required")
    return float((frame.astype(np.float32) @ LUMA).mean() / 255)


def luma_ratio(legacy: float, quad: float) -> float | None:
    """Quad over legacy brightness; None when the legacy image is (nearly) black."""
    return None if legacy < 1e-3 else quad / legacy


def ladder_drift(low: float, high: float) -> float | None:
    """How much brightness changes between two render heights (0 = not at all)."""
    return None if high < 1e-3 else abs(low / high - 1)


def _values(text: str) -> dict[str, float]:
    values = {}
    for key, value in _KEY.findall(text):
        try:
            values.setdefault(key.lower(), float(value))
        except ValueError:
            continue
    return values


def line_features(text: str) -> list[str]:
    values = _values(text)
    def on(key):
        return values.get(key, 0) != 0
    waves = [i for i in range(4) if on(f"wavecode_{i}_enabled")]
    shapes = [i for i in range(4) if on(f"shapecode_{i}_enabled") and values.get(f"shapecode_{i}_border_a", 0) > 0]
    features = ["main_dots" if on("bwavedots") else "main_thick" if on("bwavethick") else "main_thin"]
    if any(on(f"wavecode_{i}_busedots") for i in waves):
        features.append("custom_dots")
    if any(not on(f"wavecode_{i}_busedots") and on(f"wavecode_{i}_bdrawthick") for i in waves):
        features.append("custom_thick")
    if any(not on(f"wavecode_{i}_busedots") and not on(f"wavecode_{i}_bdrawthick") for i in waves):
        features.append("custom_thin")
    if any(on(f"shapecode_{i}_thickoutline") for i in shapes):
        features.append("shape_thick")
    if any(not on(f"shapecode_{i}_thickoutline") for i in shapes):
        features.append("shape_thin")
    if values.get("mv_a", 1.0 if on("bmotionvectorson") else 0.0) > 0:
        features.append("motion_vectors")
    return features


def _config(height: int, reference: int) -> LineRunConfig:
    return LineRunConfig(width=round(height * 16 / 9), height=height, fps=30, warmup_seconds=WARMUP_SECONDS,
                         measurement_seconds=MEASUREMENT_SECONDS, line_reference_height=reference)


def measure_run(worker: Path, record: PresetRecord, repo: Path, work: Path, identity: EngineIdentity,
                config: LineRunConfig, pcm: Path, png: Path | None, timeout: float) -> dict:
    job = JobSpec(record, "line-compare", pcm, config, identity, repo / "core/src/main/assets/presets",
                  repo / "core/src/main/assets/textures", work / "jobs")
    warmup = round(config.warmup_seconds * config.fps)
    lumas, frames, index, last = [], hashlib.sha256(), 0, None
    def observe(frame):
        nonlocal index, last
        frames.update(frame.tobytes())
        if index >= warmup:
            lumas.append(mean_luma(frame))
        last = frame
        index += 1
    result = render_job(worker, job, observe, timeout)
    if result.status != "success":
        return {"status": result.status, "diagnostics": str(result.diagnostics_path)}
    if png is not None and last is not None:
        png.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(png), cv2.cvtColor(last, cv2.COLOR_RGB2BGR))
    return {"status": "success", "mean_luma": float(np.mean(lumas)), "frames_sha256": frames.hexdigest()}


def compare_preset(record: PresetRecord, repo: Path, work: Path, worker: Path, identity: EngineIdentity,
                   heights: tuple[int, ...], pcm: Path, timeout: float) -> dict:
    text = (repo / "core/src/main/assets/presets" / record.path).read_text(errors="replace")
    slug = hashlib.sha256(record.path.encode()).hexdigest()[:16]
    entry = {"preset": record.path, "frames": slug, "features": line_features(text), "runs": {}}
    for height in heights:
        for mode, reference in (("legacy", 0), ("quad", REFERENCE_HEIGHT)):
            png = work / "frames" / slug / f"{mode}-{height}.png" if height == REFERENCE_HEIGHT else None
            entry["runs"][f"{mode}-{height}"] = measure_run(worker, record, repo, work, identity,
                                                            _config(height, reference), pcm, png, timeout)
    runs = entry["runs"]
    entry["status"] = "success" if all(run["status"] == "success" for run in runs.values()) else "failed"
    if entry["status"] == "success":
        entry["ratio"] = luma_ratio(runs[f"legacy-{REFERENCE_HEIGHT}"]["mean_luma"],
                                    runs[f"quad-{REFERENCE_HEIGHT}"]["mean_luma"])
        others = sorted(h for h in heights if h != REFERENCE_HEIGHT)
        if len(others) == 2:
            low, high = others
            entry["drift"] = {mode: ladder_drift(runs[f"{mode}-{low}"]["mean_luma"], runs[f"{mode}-{high}"]["mean_luma"])
                              for mode in ("legacy", "quad")}
    return entry


def summarize(entries: list[dict], baseline: dict | None) -> dict:
    done = [e for e in entries if e["status"] == "success"]
    measured = [e for e in done if e.get("ratio") is not None]
    deviations = [abs(e["ratio"] - 1) for e in measured]
    flagged = sorted(e["preset"] for e in measured if abs(e["ratio"] - 1) > FIDELITY_TOLERANCE)
    by_feature: dict[str, list[float]] = {}
    for e in measured:
        for feature in e["features"]:
            by_feature.setdefault(feature, []).append(e["ratio"])
    drift = {mode: [e["drift"][mode] for e in done if e.get("drift") and e["drift"][mode] is not None]
             for mode in ("legacy", "quad")}
    changed = []
    if baseline is not None:
        previous = {e["preset"]: e for e in baseline.get("presets", [])}
        for e in done:
            old_runs = previous.get(e["preset"], {}).get("runs", {})
            for key, run in sorted(e["runs"].items()):
                if key.startswith("legacy-") and key in old_runs and old_runs[key].get("frames_sha256") != run["frames_sha256"]:
                    changed.append(f"{e['preset']} {key}")
    return {"version": VERSION, "presets": len(entries), "failed": len(entries) - len(done),
            "median_deviation": statistics.median(deviations) if deviations else None,
            "share_beyond_tolerance": len(flagged) / len(measured) if measured else None,
            "beyond_tolerance": flagged,
            "median_ratio_by_feature": {f: statistics.median(r) for f, r in sorted(by_feature.items())},
            "median_drift": {m: statistics.median(d) if d else None for m, d in drift.items()},
            "legacy_changed": changed}


def run_line_compare(records: list[PresetRecord], repo: Path, work: Path, worker: Path, identity: EngineIdentity,
                     heights: tuple[int, ...] = (1080, 720, 1440), baseline: dict | None = None,
                     concurrency: int = 1, timeout: float = 300) -> dict:
    if REFERENCE_HEIGHT not in heights:
        raise ValueError(f"the reference height {REFERENCE_HEIGHT} must be measured")
    signals = bass_signals(RunConfig(width=1920, height=1080, fps=30, warmup_seconds=WARMUP_SECONDS,
                                     measurement_seconds=MEASUREMENT_SECONDS), work / "signals")
    pcm = signals["bass-0.30"]
    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        entries = list(pool.map(lambda r: compare_preset(r, repo, work, worker, identity, heights, pcm, timeout), records))
    report = {"summary": summarize(entries, baseline), "presets": entries, "engine": asdict(identity)}
    work.mkdir(parents=True, exist_ok=True)
    (work / "report.json").write_text(canonical_json(report))
    return report
```

- [ ] **Step 5: Run the Python tests to verify they pass**

Run: `build/preset-lab-venv/bin/python -m pytest tools/preset-lab/tests -q 2>&1 | tail -2`
Expected: all pass, including the 13 new ones.

- [ ] **Step 6: Add the setting to projectM**

`src/libprojectM/Renderer/RenderContext.hpp`, after `invAspectY`:

```cpp
    int lineReferenceHeight{0}; //!< Render height at which quad lines are 1 px wide; 0 draws MilkDrop's GL lines.
```

`src/libprojectM/ProjectM.hpp`, after the `SetDirectOutput` declaration:

```cpp
    /**
     * @brief Draws lines as anti-aliased quads, 1 px wide at this render height (see
     * projectm_opengl_set_line_reference_height()). 0 keeps MilkDrop's GL lines.
     */
    void SetLineReferenceHeight(int height);
```

and next to `m_directOutput`:

```cpp
    int m_lineReferenceHeight{0}; //!< Render height at which quad lines are 1 px wide; 0 for GL lines.
```

`src/libprojectM/ProjectM.cpp`, after `ProjectM::SetDirectOutput`:

```cpp
void ProjectM::SetLineReferenceHeight(int height)
{
    m_lineReferenceHeight = height > 0 ? height : 0;
}
```

and in `ProjectM::GetRenderContext()`, before `return ctx;`:

```cpp
    ctx.lineReferenceHeight = m_lineReferenceHeight;
```

`src/api/include/projectM-4/render_opengl.h`, after the `projectm_opengl_set_direct_output` declaration:

```c
/**
 * @brief Draws waveforms, shape outlines, dots and motion vectors as anti-aliased quads that scale
 *        with the render size.
 *
 * Lines are 1 px wide (thick ones wider) at the given render height and proportionally wider or
 * thinner at other heights, so a preset covers the same share of the picture at every resolution.
 * 0, the default, keeps MilkDrop's 1 px GL lines.
 *
 * @param instance The projectM instance handle.
 * @param reference_height Render height in pixels at which lines are 1 px wide, or 0.
 */
PROJECTM_EXPORT void projectm_opengl_set_line_reference_height(projectm_handle instance, uint32_t reference_height);
```

`src/libprojectM/ProjectMCWrapper.cpp`, after `projectm_opengl_set_direct_output`:

```cpp
void projectm_opengl_set_line_reference_height(projectm_handle instance, uint32_t reference_height)
{
    auto projectMInstance = handle_to_instance(instance);
    projectMInstance->SetLineReferenceHeight(static_cast<int>(std::min<uint32_t>(reference_height, 65535)));
}
```

(Add `#include <algorithm>` at the top of `ProjectMCWrapper.cpp` if it is not there.)

- [ ] **Step 7: Let the worker pass the setting through**

`tools/preset-lab/src/preset_lab/native/worker.cpp`, after `engine.SetMeshSize(48, 32);`:

```cpp
        engine.SetLineReferenceHeight(cfg.value("line_reference_height", 0));
```

- [ ] **Step 8: Add the CLI command**

`tools/preset-lab/src/preset_lab/cli.py`, after the `bass-select` parser definition:

```python
    command = commands.add_parser("line-compare", help="Compare GL lines with quad lines (projectM #682) on identical frames")
    command.add_argument("--repo", type=Path, default=Path.cwd())
    command.add_argument("--work", type=Path, default=Path("build/preset-lab/line-compare"))
    command.add_argument("--worker", type=Path)
    command.add_argument("--preset", action="append", default=[])
    command.add_argument("--preset-list", type=Path)
    command.add_argument("--sample-every", type=int)
    command.add_argument("--heights", default="1080,720,1440")
    command.add_argument("--baseline", type=Path)
    command.add_argument("--concurrency", type=int, default=1)
```

and before `if args.command=="run":`:

```python
        if args.command == "line-compare":
            from .build_worker import build_worker
            from .identity import load_json
            from .line_compare import run_line_compare
            from .models import EngineIdentity
            repo = args.repo.resolve()
            records, _ = inventory(repo/"core/src/main/assets/presets", repo/"core/src/main/assets/presets.idx",
                                   repo/"core/src/main/assets/textures")
            records.sort(key=lambda r: r.path)
            names = list(args.preset)
            if args.preset_list:
                names += [line.strip() for line in args.preset_list.read_text().splitlines()
                          if line.strip() and not line.startswith("#")]
            if names:
                missing = set(names) - {r.path for r in records}
                if missing:
                    raise ValueError(f"unknown presets: {sorted(missing)}")
                records = [r for r in records if r.path in set(names)]
            if args.sample_every:
                records = records[::args.sample_every]
            heights = tuple(int(h) for h in args.heights.split(",") if h)
            worker = (args.worker or build_worker(repo, args.work / "engine")).resolve()
            identity = EngineIdentity(**load_json(worker.parent / "build-identity.json"))
            baseline = load_json(args.baseline) if args.baseline else None
            report = run_line_compare(records, repo, args.work, worker, identity, heights, baseline, args.concurrency)
            json.dump(report["summary"], sys.stdout, allow_nan=False)
            sys.stdout.write("\n")
            return 1 if report["summary"]["failed"] or report["summary"]["legacy_changed"] else 0
```

- [ ] **Step 9: Write the fixed preset list**

`tools/preset-lab/src/preset_lab/profiles/line-compare-presets.txt`:

```
# One or two presets per line kind, for fast iteration (found by scanning the bundled presets).
# main wave, thin
$$$ Royal - Mashup (106).milk
# main wave, thick
$$$ Royal - Mashup (191).milk
# main wave dots (also motion vectors)
$$$ Royal - Mashup (1).milk
# custom wave, thick
$$$ Royal - Mashup (162).milk
# custom wave dots
$$$ Royal - Mashup (10).milk
# shape, thick outline
$$$ Royal - Mashup (397).milk
# shape with many instances and an outline
Benjam and Zylot - Tie-Dye Supernova (Sunspots Mix) flx mrt - flx rnz.milk
# motion vectors
$$$ Royal - Mashup (103).milk
```

- [ ] **Step 10: Regenerate the patch, run the host tests, record the baseline**

```bash
tools/regen-projectm-patch.sh 0021-quad-lines.patch && tools/check-patch-series.sh
tools/projectm-host-tests.sh 2>&1 | tail -1
build/preset-lab-venv/bin/preset-lab line-compare --preset-list tools/preset-lab/src/preset_lab/profiles/line-compare-presets.txt \
    --work build/preset-lab/line-fixed --concurrency 4
cp build/preset-lab/line-fixed/report.json build/preset-lab/line-fixed-baseline.json
```

Expected: `all 21 patches apply`, `PASSED` (125 tests), and a summary with `"failed": 0`, `"median_deviation": 0.0`, `"beyond_tolerance": []`. Nothing draws quads yet, so quad and legacy frames must be identical; confirm with:

```bash
jq -r '.presets[] | .runs as $r | "\(.preset): \([$r | to_entries[] | select(.key|startswith("legacy")) | .value.frames_sha256 == $r[(.key|sub("legacy";"quad"))].frames_sha256] | all)"' build/preset-lab/line-fixed/report.json
```

Expected: every line ends in `true`.

- [ ] **Step 11: Record the broad baseline (background, ~30–60 min)**

```bash
build/preset-lab-venv/bin/preset-lab line-compare --sample-every 40 --work build/preset-lab/line-sample --concurrency 4 \
    > build/preset-lab/line-sample-summary.json
cp build/preset-lab/line-sample/report.json build/preset-lab/line-sample-baseline.json
```

Expected: about 240 presets, `"failed": 0` (if some presets fail in both modes, list them in the commit message; they are excluded from later comparisons automatically). Run it in the background and continue with Task 4.

- [ ] **Step 12: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch tools/preset-lab/src/preset_lab/line_compare.py \
    tools/preset-lab/src/preset_lab/profiles/line-compare-presets.txt tools/preset-lab/src/preset_lab/cli.py \
    tools/preset-lab/src/preset_lab/native/worker.cpp tools/preset-lab/tests/test_line_compare.py
git commit -m "feat(preset-lab): line-compare renders GL and quad lines on identical frames

Adds projectm_opengl_set_line_reference_height() to patch 0021 (no effect yet)
and passes it through the worker. The fixed list gives identical frames in both
modes, the baseline for checking that the GL-line path stays unchanged.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 4: `LineRenderer`, the line shaders, and the main waveform

**Files:**
- Create (projectM): `src/libprojectM/MilkdropPreset/LineRenderer.hpp`, `src/libprojectM/MilkdropPreset/LineRenderer.cpp`, `src/libprojectM/MilkdropPreset/Shaders/LineVertexShaderGlsl330.vert`, `src/libprojectM/MilkdropPreset/Shaders/LineFragmentShaderGlsl330.frag`
- Modify (projectM): `src/libprojectM/MilkdropPreset/CMakeLists.txt`, `PresetState.hpp`, `Waveform.hpp`, `Waveform.cpp`

**Interfaces:**
- Consumes: `LineBatch`, `LineStyle`, `LineStyleFor`, `LineScale` (Task 2); `RenderContext::lineReferenceHeight` (Task 3).
- Produces:
  - `class LineRenderer { void Upload(const LineBatch&); void Begin(const glm::mat4& transformation, int viewportWidth, int viewportHeight); void Draw(const LineBatch::Strip&, const LineStyle&); void End(); };`. `Draw` binds the shader, VAO and buffer itself, so other draws may run between `Begin` and `Draw`. Blending is the caller's.
  - `PresetState::lineRenderer` (`LineRenderer`)
  - Static shader accessors `GetLineVertexShader()`, `GetLineFragmentShader()` (generated from the file names)

- [ ] **Step 1: Write the vertex shader**

`src/libprojectM/MilkdropPreset/Shaders/LineVertexShaderGlsl330.vert`:

```glsl
precision highp float;
precision highp int;

// One instance per segment A-B of a line strip, drawn as a 4-vertex triangle strip. The points
// before and after the segment shape its ends: a miter where the strip continues, a flat end where
// the neighbour repeats the end point (see LineBatch). Positions are expanded in render pixels.
layout(location = 0) in vec2 point_previous;
layout(location = 1) in vec2 point_a;
layout(location = 2) in vec2 point_b;
layout(location = 3) in vec2 point_next;
layout(location = 4) in vec4 color_a;
layout(location = 5) in vec4 color_b;

uniform mat4 vertex_transformation;
uniform vec2 viewport_size;
uniform highp float half_width;

out vec4 fragment_color;
out float edge_distance;

vec2 ToPixels(vec2 position)
{
    return (vertex_transformation * vec4(position, 0.0, 1.0)).xy * 0.5 * viewport_size;
}

void main()
{
    vec2 a = ToPixels(point_a);
    vec2 b = ToPixels(point_b);
    vec2 direction = b - a;
    float segmentLength = length(direction);

    // A zero-length or non-finite segment draws nothing: all corners go outside the clip volume.
    if (!(segmentLength > 0.0001) || isinf(segmentLength))
    {
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
        fragment_color = vec4(0.0);
        edge_distance = 0.0;
        return;
    }

    direction /= segmentLength;
    vec2 normal = vec2(-direction.y, direction.x);

    bool atA = gl_VertexID < 2;
    float side = (gl_VertexID % 2 == 0) ? -1.0 : 1.0;
    vec2 corner = atA ? a : b;
    vec2 neighbourDirection = atA ? corner - ToPixels(point_previous) : ToPixels(point_next) - corner;

    // Miter join: offset along the bisector, lengthened so both edges stay half_width away. Turns
    // sharper than 120 degrees and strip ends keep the segment's own normal, which leaves a gap or
    // overlap of under a pixel at that corner.
    vec2 offsetDirection = normal;
    float neighbourLength = length(neighbourDirection);
    if (neighbourLength > 0.0001 && !isinf(neighbourLength))
    {
        vec2 tangentSum = neighbourDirection / neighbourLength + direction;
        float tangentLength = length(tangentSum);
        if (tangentLength > 0.0001)
        {
            vec2 tangent = tangentSum / tangentLength;
            vec2 miter = vec2(-tangent.y, tangent.x);
            float cosine = dot(miter, normal);
            if (cosine > 0.5)
            {
                offsetDirection = miter / cosine;
            }
        }
    }

    // One extra pixel on each side holds the anti-aliased edge.
    float extent = half_width + 1.0;
    vec2 position = corner + offsetDirection * side * extent;
    gl_Position = vec4(position / (0.5 * viewport_size), 0.0, 1.0);
    edge_distance = side * extent;
    fragment_color = atA ? color_a : color_b;
}
```

- [ ] **Step 2: Write the fragment shader**

`src/libprojectM/MilkdropPreset/Shaders/LineFragmentShaderGlsl330.frag`:

```glsl
precision mediump float;

in vec4 fragment_color;
in float edge_distance;

uniform highp float half_width;

out vec4 color;

void main()
{
    // How much of this pixel a line 2 * half_width wide covers (a box filter across the line).
    float coverage = clamp(half_width + 0.5 - abs(edge_distance), 0.0, 1.0);
    color = vec4(fragment_color.rgb, fragment_color.a * coverage);
}
```

Add both files to `SHADER_FILES` in `src/libprojectM/MilkdropPreset/CMakeLists.txt` (alphabetical: after `Blur*`/before `PresetCompVertexShaderGlsl330.vert`).

- [ ] **Step 3: Check the shaders as GLSL ES 3.00**

```bash
command -v glslangValidator || brew install glslang
S=third_party/projectm/src/libprojectM/MilkdropPreset/Shaders
T=$(mktemp -d)
{ echo '#version 300 es'; cat $S/LineVertexShaderGlsl330.vert; } > $T/line.vert
{ echo '#version 300 es'; cat $S/LineFragmentShaderGlsl330.frag; } > $T/line.frag
glslangValidator $T/line.vert && glslangValidator $T/line.frag && glslangValidator -l $T/line.vert $T/line.frag
```

Expected: no errors. (This checks each stage's ES rules; uniform precision matching across stages is confirmed on a device in Task 11.)

- [ ] **Step 4: Write `LineRenderer`**

`src/libprojectM/MilkdropPreset/LineRenderer.hpp`:

```cpp
#pragma once

#include "LineGeometry.hpp"

#include <Renderer/Shader.hpp>

#include <projectM-opengl.h>

#include <glm/mat4x4.hpp>

#include <cstddef>

namespace libprojectM {
namespace MilkdropPreset {

/**
 * @brief Draws line strips as anti-aliased quads, one instance per segment (projectM issue #682).
 *
 * Upload() a LineBatch, Begin() once for its transformation and viewport, then Draw() its strips.
 * Other draws may run between Begin() and Draw(): Draw() binds its own program and buffers. The
 * caller sets blending.
 */
class LineRenderer
{
public:
    LineRenderer();
    ~LineRenderer();

    LineRenderer(const LineRenderer&) = delete;
    auto operator=(const LineRenderer&) -> LineRenderer& = delete;

    void Upload(const LineBatch& batch);
    void Begin(const glm::mat4& transformation, int viewportWidth, int viewportHeight);
    void Draw(const LineBatch::Strip& strip, const LineStyle& style);
    void End();

private:
    Renderer::Shader m_shader;  //!< Line program, compiled with the preset (off the render thread when prewarmed).
    GLuint m_vaoId{0};          //!< Vertex array with six per-instance attributes.
    GLuint m_vboId{0};          //!< Padded strip points.
    size_t m_capacity{0};       //!< Buffer size in points.
    bool m_ready{false};        //!< Begin() found an uploaded batch and a usable viewport.
};

} // namespace MilkdropPreset
} // namespace libprojectM
```

`src/libprojectM/MilkdropPreset/LineRenderer.cpp`:

```cpp
#include "LineRenderer.hpp"

#include "MilkdropStaticShaders.hpp"

#include <algorithm>
#include <cstdint>

namespace libprojectM {
namespace MilkdropPreset {

using ColoredPoint = LineBatch::ColoredPoint;

LineRenderer::LineRenderer()
{
    auto staticShaders = MilkdropStaticShaders::Get();
    m_shader.CompileProgram(staticShaders->GetLineVertexShader(), staticShaders->GetLineFragmentShader());
}

LineRenderer::~LineRenderer()
{
    if (m_vboId != 0)
    {
        glDeleteBuffers(1, &m_vboId);
    }
    if (m_vaoId != 0)
    {
        glDeleteVertexArrays(1, &m_vaoId);
    }
}

void LineRenderer::Upload(const LineBatch& batch)
{
    const auto& points = batch.Points();
    if (points.empty())
    {
        return;
    }

    if (m_vaoId == 0)
    {
        glGenVertexArrays(1, &m_vaoId);
        glGenBuffers(1, &m_vboId);
        glBindVertexArray(m_vaoId);
        glBindBuffer(GL_ARRAY_BUFFER, m_vboId);
        for (GLuint location = 0; location < 6; location++)
        {
            glEnableVertexAttribArray(location);
            glVertexAttribDivisor(location, 1);
        }
        glBindVertexArray(0);
    }

    // Orphan the buffer so the GPU can keep reading the previous upload.
    m_capacity = std::max(m_capacity, points.size());
    glBindBuffer(GL_ARRAY_BUFFER, m_vboId);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(sizeof(ColoredPoint) * m_capacity), nullptr, GL_STREAM_DRAW);
    glBufferSubData(GL_ARRAY_BUFFER, 0, static_cast<GLsizeiptr>(sizeof(ColoredPoint) * points.size()), points.data());
}

void LineRenderer::Begin(const glm::mat4& transformation, int viewportWidth, int viewportHeight)
{
    m_ready = m_vaoId != 0 && viewportWidth > 0 && viewportHeight > 0;
    if (!m_ready)
    {
        return;
    }
    m_shader.Bind();
    m_shader.SetUniformMat4x4("vertex_transformation", transformation);
    m_shader.SetUniformFloat2("viewport_size", glm::vec2(static_cast<float>(viewportWidth), static_cast<float>(viewportHeight)));
}

void LineRenderer::Draw(const LineBatch::Strip& strip, const LineStyle& style)
{
    if (!m_ready || strip.segments <= 0 || style.passes <= 0)
    {
        return;
    }

    m_shader.Bind();
    glBindVertexArray(m_vaoId);
    glBindBuffer(GL_ARRAY_BUFFER, m_vboId);

    // Instance i reads the strip's points i (previous), i + 1 (A), i + 2 (B) and i + 3 (next).
    const auto stride = static_cast<GLsizei>(sizeof(ColoredPoint));
    const auto pointer = [&](int point, size_t member) {
        return reinterpret_cast<const void*>(static_cast<uintptr_t>(strip.firstPoint + point) * sizeof(ColoredPoint) + member);
    };
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, stride, pointer(0, offsetof(ColoredPoint, x)));
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, stride, pointer(1, offsetof(ColoredPoint, x)));
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, pointer(2, offsetof(ColoredPoint, x)));
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, stride, pointer(3, offsetof(ColoredPoint, x)));
    glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, stride, pointer(1, offsetof(ColoredPoint, r)));
    glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, stride, pointer(2, offsetof(ColoredPoint, r)));

    m_shader.SetUniformFloat("half_width", style.halfWidth);
    for (int pass = 0; pass < style.passes; pass++)
    {
        glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, strip.segments);
    }
}

void LineRenderer::End()
{
    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
    Renderer::Shader::Unbind();
    m_ready = false;
}

} // namespace MilkdropPreset
} // namespace libprojectM
```

(Add `#include <cstddef>` for `offsetof` if your compiler asks.) Add `LineRenderer.cpp`/`LineRenderer.hpp` to the `MilkdropPreset` source list after `LineGeometry.hpp`.

`PresetState.hpp`: `#include "LineRenderer.hpp"` after `#include "BlurTexture.hpp"`, and after `texturedShader`:

```cpp
    LineRenderer lineRenderer; //!< Draws waveforms, custom waves and shape outlines as quads (when lineReferenceHeight > 0).
```

- [ ] **Step 5: Draw the main waveform's lines with it**

`Waveform.hpp`: add `#include "LineGeometry.hpp"` and `#include <glm/vec4.hpp>`; change the `MaximizeColors` declaration to

```cpp
    auto MaximizeColors(const PerFrameContext& presetPerFrameContext) -> glm::vec4;
```

and add

```cpp
    /**
     * @brief Draws the waveform lines as quads (lineReferenceHeight > 0, not dots).
     */
    void DrawQuadLines(const PerFrameContext& presetPerFrameContext, float lineScale);

    LineBatch m_lineBatch;                                       //!< This frame's waveform strips.
    std::vector<Renderer::RenderItem::ColoredPoint> m_coloredWave; //!< One wave with its color, for the batch.
```

`Waveform.cpp`:
- At the end of `MaximizeColors`, replace `glVertexAttrib4f(1, waveR, waveG, waveB, m_tempAlpha);` with `return {waveR, waveG, waveB, m_tempAlpha};` and change its signature to match.
- In the legacy loop, replace `MaximizeColors(presetPerFrameContext);` with

```cpp
        const auto color = MaximizeColors(presetPerFrameContext);
        glVertexAttrib4f(1, color.r, color.g, color.b, color.a);
```

- In `Waveform::Draw`, right after the `m_waveformMath` null check:

```cpp
    const float lineScale = LineScale(m_presetState.renderContext.viewportSizeY, m_presetState.renderContext.lineReferenceHeight);
    if (lineScale > 0.0f && !m_presetState.waveDots)
    {
        DrawQuadLines(presetPerFrameContext, lineScale);
        return;
    }
```

- Add:

```cpp
void Waveform::DrawQuadLines(const PerFrameContext& presetPerFrameContext, float lineScale)
{
    auto waves = m_waveformMath->GetVertices(m_presetState, presetPerFrameContext);

    m_lineBatch.Clear();
    std::vector<LineBatch::Strip> strips;
    for (const auto& wave : waves)
    {
        if (wave.empty())
        {
            continue;
        }

        m_tempAlpha = static_cast<float>(*presetPerFrameContext.wave_a);
        const auto color = MaximizeColors(presetPerFrameContext);

        m_coloredWave.resize(wave.size());
        for (size_t point = 0; point < wave.size(); point++)
        {
            auto& colored = m_coloredWave[point];
            colored.x = wave[point].x;
            colored.y = wave[point].y;
            colored.r = color.r;
            colored.g = color.g;
            colored.b = color.b;
            colored.a = color.a;
        }
        strips.push_back(m_lineBatch.Append(m_coloredWave.data(), m_coloredWave.size(), m_waveformMath->IsLoop()));
    }

    if (m_lineBatch.Points().empty())
    {
        return;
    }

    glEnable(GL_BLEND);
    if (m_presetState.additiveWaves)
    {
        glBlendFunc(GL_SRC_ALPHA, GL_ONE);
    }
    else
    {
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    }

    auto& lines = m_presetState.lineRenderer;
    lines.Upload(m_lineBatch);
    lines.Begin(PresetState::orthogonalProjectionFlipped, m_presetState.renderContext);
    const auto style = LineStyleFor(LineKind::MainWave, m_presetState.waveThick, lineScale);
    for (const auto& strip : strips)
    {
        lines.Draw(strip, style);
    }
    lines.End();

    glDisable(GL_BLEND);
}
```

- [ ] **Step 6: Build and check**

```bash
tools/regen-projectm-patch.sh 0021-quad-lines.patch && tools/check-patch-series.sh
tools/projectm-host-tests.sh 2>&1 | tail -1
build/preset-lab-venv/bin/preset-lab line-compare --preset-list tools/preset-lab/src/preset_lab/profiles/line-compare-presets.txt \
    --work build/preset-lab/line-fixed --baseline build/preset-lab/line-fixed-baseline.json --concurrency 4
jq -r '.presets[] | "\(.ratio)\t\(.features|join(","))\t\(.preset)"' build/preset-lab/line-fixed/report.json
```

Expected: 21 patches apply; 125 tests pass; summary `"failed": 0`, `"legacy_changed": []` (the GL-line path is unchanged). The ratios for the `main_thin` and `main_thick` presets are within 0.90–1.10 (thick may be further off until Task 9). Open the image pair of the main-wave presets and look at them: `build/preset-lab/line-fixed/frames/<frames>/legacy-1080.png` and `quad-1080.png` (the `frames` field of each report entry). The quad wave must sit in the same place with the same color and look smooth, not doubled or offset.

If the waves are mirrored vertically or offset, the transformation passed to `Begin` is wrong (main waveform uses `orthogonalProjectionFlipped`). If nothing shows, check `glGetError` in the worker manifest (`gl_error_frames`) and that `GetLineVertexShader` exists in the generated `MilkdropStaticShaders.hpp`.

- [ ] **Step 7: Build the Android library**

Run: `./gradlew :core:assembleDebug -q 2>&1 | tail -5`
Expected: success (this compiles the patch with `USE_GLES` for both ABIs).

- [ ] **Step 8: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): draw the main waveform as quad lines (patch 0021)

LineRenderer draws one instance per segment with miter joins and an
anti-aliased edge; the main waveform uses it when a line reference height is
set. GL lines are unchanged (preset-lab legacy frames identical).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 5: Dots that scale

**Files:**
- Modify (projectM): `src/libprojectM/MilkdropPreset/Waveform.cpp`, `src/libprojectM/MilkdropPreset/CustomWaveform.cpp`

**Interfaces:**
- Consumes: `DotStyleFor`, `LineScale` (Task 2); the `MaximizeColors` return value (Task 4).

- [ ] **Step 1: Main waveform dots**

In `Waveform::Draw` (legacy branch, which now also handles dots when `lineScale > 0`), replace

```cpp
    m_presetState.untexturedShader.SetUniformFloat("vertex_point_size", 1.0f);
```

with

```cpp
    // Quad-line mode draws the main wave's 2x2 pixel dots as one scaled point instead of four.
    const bool scaledDots = lineScale > 0.0f && m_presetState.waveDots;
    const auto dot = DotStyleFor(LineKind::MainWave, true, lineScale);
    m_presetState.untexturedShader.SetUniformFloat("vertex_point_size", scaledDots ? dot.size : 1.0f);
```

replace `const auto iterations = m_presetState.waveThick || m_presetState.waveDots ? 4 : 1;` with

```cpp
        const auto iterations = scaledDots ? 1 : (m_presetState.waveThick || m_presetState.waveDots ? 4 : 1);
```

and the color line from Task 4 with

```cpp
        const auto color = MaximizeColors(presetPerFrameContext);
        glVertexAttrib4f(1, color.r, color.g, color.b, scaledDots ? color.a * dot.alphaScale : color.a);
```

(`lineScale` is computed before the quad-line branch in Task 4; the legacy path is reached with `lineScale == 0` or with dots.)

- [ ] **Step 2: Custom wave dots**

In `CustomWaveform::Draw`, before the `glLineWidth(1)` block, add

```cpp
    const float lineScale = LineScale(m_presetState.renderContext.viewportSizeY, m_presetState.renderContext.lineReferenceHeight);
    const bool scaledDots = lineScale > 0.0f && m_useDots;
    const auto dot = DotStyleFor(LineKind::CustomWave, m_drawThick, lineScale);
    if (scaledDots && dot.alphaScale < 1.0f)
    {
        for (int point = 0; point < smoothedVertexCount; point++)
        {
            pointsSmoothed[point].a *= dot.alphaScale;
        }
    }
```

and replace

```cpp
    m_presetState.untexturedShader.SetUniformFloat("vertex_point_size", m_drawThick ? 2.0f : 1.0f);
```

with

```cpp
    m_presetState.untexturedShader.SetUniformFloat("vertex_point_size", scaledDots ? dot.size : (m_drawThick ? 2.0f : 1.0f));
```

Add `#include "LineGeometry.hpp"` to `CustomWaveform.cpp`.

- [ ] **Step 3: Check**

Same commands as Task 4 Step 6. Expected: `"legacy_changed": []`; the `main_dots` and `custom_dots` presets within 0.90–1.10; their image pairs show dots of the same size at 1080.

- [ ] **Step 4: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): scale waveform dots with the render size (patch 0021)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 6: Custom waves, and extreme coordinates

**Files:**
- Modify (projectM): `src/libprojectM/MilkdropPreset/CustomWaveform.hpp`, `src/libprojectM/MilkdropPreset/CustomWaveform.cpp`

**Interfaces:**
- Consumes: `LineRenderer` via `m_presetState.lineRenderer` (Task 4); `lineScale`, `scaledDots` from Task 5's block.

- [ ] **Step 1: Draw custom waves as quads**

`CustomWaveform.hpp`: add `#include "LineGeometry.hpp"` and the member

```cpp
    LineBatch m_lineBatch; //!< This frame's strip, for the quad-line renderer.
```

`CustomWaveform.cpp`, right after Task 5's `scaledDots` block:

```cpp
    if (lineScale > 0.0f && !m_useDots)
    {
        m_lineBatch.Clear();
        const auto strip = m_lineBatch.Append(pointsSmoothed.data(), static_cast<size_t>(smoothedVertexCount), false);
        if (strip.segments == 0)
        {
            return;
        }

        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, m_additive ? GL_ONE : GL_ONE_MINUS_SRC_ALPHA);

        auto& lines = m_presetState.lineRenderer;
        lines.Upload(m_lineBatch);
        lines.Begin(PresetState::orthogonalProjection, m_presetState.renderContext);
        lines.Draw(strip, LineStyleFor(LineKind::CustomWave, m_drawThick, lineScale));
        lines.End();

        glDisable(GL_BLEND);
        return;
    }
```

- [ ] **Step 2: Check the fixed list**

Same commands as Task 4 Step 6. Expected: `"legacy_changed": []`; `custom_thick` presets render their waves in place (compare the image pair); ratios may be off until Task 9 but within 0.80–1.20.

- [ ] **Step 3: Run a preset with extreme coordinates through the worker**

```bash
T=$(mktemp -d)
cat > "$T/extreme.milk" <<'EOF'
[preset00]
fDecay=0.98
wavecode_0_enabled=1
wavecode_0_samples=512
wavecode_0_bDrawThick=1
wavecode_0_bAdditive=1
wavecode_0_a=1
wave_0_per_point1=x = if(below(sample, 0.3), 1e30, if(below(sample, 0.6), sample, -1e30));
wave_0_per_point2=y = if(below(sample, 0.5), 0.5, 1/(sample - 0.75));
wave_0_per_point3=r = 1; g = 1; b = 1;
EOF
python3 - "$T" <<'EOF'
import json, sys, numpy as np, pathlib
t = pathlib.Path(sys.argv[1])
np.zeros(60 * 1470, dtype='<f4').tofile(t / "pcm.f32")
json.dump({"schema_version": 1, "preset_path": str(t / "extreme.milk"),
           "texture_root": str(pathlib.Path("core/src/main/assets/textures").resolve()),
           "pcm_path": str(t / "pcm.f32"), "manifest_path": str(t / "manifest.json"), "bands_path": str(t / "bands.jsonl"),
           "identity": {}, "config": {"width": 640, "height": 360, "fps": 30, "warmup_seconds": 1,
           "measurement_seconds": 1, "seed": 1, "line_reference_height": 1080}}, open(t / "job.json", "w"))
EOF
WORKER=$(ls -t build/preset-lab/line-fixed/engine/native-build/*/preset-lab-worker | head -1)
"$WORKER" --job "$T/job.json" > /dev/null; echo "exit $?"; cat "$T/manifest.json"
```

Expected: `exit 0` and `"gl_error_frames":0`. A run that hangs, crashes or reports GL errors is a bug in the shader's non-finite guard.

- [ ] **Step 4: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): draw custom waves as quad lines (patch 0021)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 7: Shape outlines in the batch

**Files:**
- Modify (projectM): `src/libprojectM/MilkdropPreset/CustomShape.hpp`, `src/libprojectM/MilkdropPreset/CustomShape.cpp`

**Interfaces:**
- Consumes: `LineBatch`, `LineStyleFor`, `LineScale` (Task 2); `LineRenderer` (Task 4).

- [ ] **Step 1: Members**

`CustomShape.hpp`: add `#include "LineGeometry.hpp"`; in `struct InstanceDraw` add

```cpp
        LineBatch::Strip borderStrip; //!< The outline in m_lineBatch (quad lines).
```

and members

```cpp
    LineBatch m_lineBatch;                                     //!< Outlines of the current batch (quad lines).
    std::vector<Renderer::RenderItem::ColoredPoint> m_borderPoints; //!< One outline, for the line batch.
    bool m_quadBorders{false};                                 //!< This frame draws outlines as quads.
    LineStyle m_borderStyle;                                   //!< Outline width and passes this frame.
    bool m_linesBegun{false};                                  //!< LineRenderer::Begin() called for this batch.
```

- [ ] **Step 2: Collect outlines into the line batch**

In `CustomShape::Draw`, after `m_lastBlendDestination = 0;`:

```cpp
    const float lineScale = LineScale(m_presetState.renderContext.viewportSizeY, m_presetState.renderContext.lineReferenceHeight);
    m_quadBorders = lineScale > 0.0f;
    m_borderStyle = LineStyleFor(LineKind::ShapeBorder, m_thickOutline, lineScale);
    m_lineBatch.Clear();
```

Replace

```cpp
        draw.borderIterations = *m_perFrameContext.border_a > 0.0001f ? (m_thickOutline ? 4 : 1) : 0;

        size_t needed = static_cast<size_t>(sides + 2 + draw.borderIterations * sides);
        if (m_vertices.size() + needed > maxBatchVertices)
        {
            FlushBatch();
        }
```

with

```cpp
        // Quad outlines draw thick lines in one call (m_borderStyle); GL lines four times, offset.
        draw.borderIterations = *m_perFrameContext.border_a > 0.0001f ? (m_quadBorders ? 1 : (m_thickOutline ? 4 : 1)) : 0;

        const size_t neededVertices = static_cast<size_t>(sides + 2 + (m_quadBorders ? 0 : draw.borderIterations * sides));
        const size_t neededLinePoints = m_quadBorders && draw.borderIterations > 0 ? static_cast<size_t>(sides + 3) : 0;
        if (m_vertices.size() + neededVertices > maxBatchVertices || m_lineBatch.Points().size() + neededLinePoints > maxBatchVertices)
        {
            FlushBatch();
        }
```

Change `if (draw.borderIterations > 0)` (the block that builds the offset outline vertices) to `if (draw.borderIterations > 0 && !m_quadBorders)`, and add after that block:

```cpp
        if (draw.borderIterations > 0 && m_quadBorders)
        {
            m_borderPoints.resize(static_cast<size_t>(sides));
            for (int i = 0; i < sides; i++)
            {
                const TexturedPoint& corner = m_vertices[draw.fillFirst + i + 1];
                auto& point = m_borderPoints[static_cast<size_t>(i)];
                point.x = corner.x;
                point.y = corner.y;
                point.r = static_cast<float>(*m_perFrameContext.border_r);
                point.g = static_cast<float>(*m_perFrameContext.border_g);
                point.b = static_cast<float>(*m_perFrameContext.border_b);
                point.a = static_cast<float>(*m_perFrameContext.border_a);
            }
            draw.borderStrip = m_lineBatch.Append(m_borderPoints.data(), m_borderPoints.size(), true);
        }
```

- [ ] **Step 3: Draw them in `FlushBatch`, in instance order**

In `CustomShape::FlushBatch`, after the `glBufferSubData` of `m_vertices`:

```cpp
    if (m_quadBorders && !m_lineBatch.Points().empty())
    {
        m_presetState.lineRenderer.Upload(m_lineBatch);
    }
    m_linesBegun = false;
```

Replace the outline draw

```cpp
        if (draw.borderIterations > 0)
        {
            m_presetState.untexturedShader.Bind();
            glBindVertexArray(m_vaoIdUntextured);
            for (int iteration = 0; iteration < draw.borderIterations; iteration++)
            {
                glDrawArrays(GL_LINE_LOOP, draw.borderFirst + iteration * draw.sides, draw.sides);
            }
        }
```

with

```cpp
        if (draw.borderIterations > 0 && m_quadBorders)
        {
            auto& lines = m_presetState.lineRenderer;
            if (!m_linesBegun)
            {
                lines.Begin(PresetState::orthogonalProjection, m_presetState.renderContext);
                m_linesBegun = true;
            }
            lines.Draw(draw.borderStrip, m_borderStyle);
        }
        else if (draw.borderIterations > 0)
        {
            m_presetState.untexturedShader.Bind();
            glBindVertexArray(m_vaoIdUntextured);
            for (int iteration = 0; iteration < draw.borderIterations; iteration++)
            {
                glDrawArrays(GL_LINE_LOOP, draw.borderFirst + iteration * draw.sides, draw.sides);
            }
        }
```

and before `m_vertices.clear();` at the end of `FlushBatch`:

```cpp
    if (m_linesBegun)
    {
        m_presetState.lineRenderer.End();
        m_linesBegun = false;
    }
    m_lineBatch.Clear();
```

The next instance's fill binds `untexturedShader`/`texturedShader` and its VAO itself, so interleaving with `LineRenderer::Draw` is safe.

- [ ] **Step 4: Check**

Same commands as Task 4 Step 6. Expected: `"legacy_changed": []`; no failed runs for the instanced-shape preset (`Benjam and Zylot …`); outlines in place in its image pair; `shape_thick` within 0.80–1.20 before calibration.

- [ ] **Step 5: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): draw shape outlines as quad lines in the shape batch (patch 0021)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 8: Motion vectors

**Files:**
- Create (projectM): `src/libprojectM/MilkdropPreset/Shaders/MotionVectorLineVertexShaderGlsl330.vert`
- Modify (projectM): `src/libprojectM/MilkdropPreset/CMakeLists.txt`, `MotionVectors.hpp`, `MotionVectors.cpp`

**Interfaces:**
- Consumes: `LineStyleFor(LineKind::MotionVector, …)`, `LineScale` (Task 2); `GetLineFragmentShader()` (Task 4).
- Produces: static accessor `GetMotionVectorLineVertexShader()`.

- [ ] **Step 1: Write the shader**

`src/libprojectM/MilkdropPreset/Shaders/MotionVectorLineVertexShaderGlsl330.vert`:

```glsl
precision highp float;
precision highp int;

// One instance per motion vector: a flat-ended quad from the grid point to where the u/v map says
// the image came from, as in PresetMotionVectorsVertexShaderGlsl330.vert. Used with the line
// fragment shader.
layout(location = 0) in vec2 vector_start;
layout(location = 1) in vec4 vector_color;

uniform mat4 vertex_transformation;
uniform vec2 viewport_size;
uniform highp float half_width;
uniform float length_multiplier;
uniform float minimum_length;
uniform sampler2D warp_coordinates;

out vec4 fragment_color;
out float edge_distance;

vec2 ToPixels(vec2 texturePosition)
{
    // Texture coordinates (0...1, top-down) to the usual -1...1, then to render pixels.
    vec2 position = texturePosition * 2.0 - 1.0;
    position.y = -position.y;
    return (vertex_transformation * vec4(position, 0.0, 1.0)).xy * 0.5 * viewport_size;
}

void main()
{
    vec2 start = vector_start;
    vec2 oldUV = texture(warp_coordinates, vec2(start.x, 1.0 - start.y)).xy;

    // Enforce the minimum trail length, as the GL-line shader does.
    vec2 dist = (oldUV - start) * length_multiplier;
    float len = length(dist);
    if (len > minimum_length)
    {
    }
    else if (len > 0.00000001)
    {
        dist *= minimum_length / len;
    }
    else
    {
        dist = vec2(minimum_length);
    }

    vec2 a = ToPixels(start);
    vec2 b = ToPixels(start + dist);
    vec2 direction = b - a;
    float segmentLength = length(direction);
    if (!(segmentLength > 0.0001) || isinf(segmentLength))
    {
        gl_Position = vec4(2.0, 2.0, 2.0, 1.0);
        fragment_color = vec4(0.0);
        edge_distance = 0.0;
        return;
    }
    vec2 normal = vec2(-direction.y, direction.x) / segmentLength;

    float side = (gl_VertexID % 2 == 0) ? -1.0 : 1.0;
    float extent = half_width + 1.0;
    vec2 position = (gl_VertexID < 2 ? a : b) + normal * side * extent;
    gl_Position = vec4(position / (0.5 * viewport_size), 0.0, 1.0);
    edge_distance = side * extent;
    fragment_color = vector_color;
}
```

Add it to `SHADER_FILES` and run the Task 4 Step 3 glslang check on it, linked with the line fragment shader:

```bash
S=third_party/projectm/src/libprojectM/MilkdropPreset/Shaders; T=$(mktemp -d)
{ echo '#version 300 es'; cat $S/MotionVectorLineVertexShaderGlsl330.vert; } > $T/mv.vert
{ echo '#version 300 es'; cat $S/LineFragmentShaderGlsl330.frag; } > $T/line.frag
glslangValidator -l $T/mv.vert $T/line.frag
```

Expected: no errors.

- [ ] **Step 2: Draw all vectors in one instanced call**

`MotionVectors.hpp`: add `#include "LineGeometry.hpp"`, a destructor declaration `~MotionVectors() override;` (`RenderItem`'s destructor is virtual), and members:

```cpp
    void DrawQuads(const PerFrameContext& presetPerFrameContext, float lineScale, float minimumLength);

    Renderer::Shader m_motionVectorQuadShader;  //!< Quad-line motion vectors.
    GLuint m_quadVaoId{0};                      //!< Per-instance start points.
    GLuint m_quadVboId{0};
    std::vector<Point> m_vectorStarts;          //!< This frame's grid points.
```

`MotionVectors.cpp`:
- In the constructor, after `m_motionVectorShader.CompileProgram(...)`:

```cpp
    m_motionVectorQuadShader.CompileProgram(staticShaders->GetMotionVectorLineVertexShader(),
                                            staticShaders->GetLineFragmentShader());
```

- Destructor:

```cpp
MotionVectors::~MotionVectors()
{
    if (m_quadVboId != 0)
    {
        glDeleteBuffers(1, &m_quadVboId);
    }
    if (m_quadVaoId != 0)
    {
        glDeleteVertexArrays(1, &m_quadVaoId);
    }
}
```

- In `Draw`, after `minimumLength` is computed:

```cpp
    const float lineScale = LineScale(m_presetState.renderContext.viewportSizeY, m_presetState.renderContext.lineReferenceHeight);
    const bool quadLines = lineScale > 0.0f;
    m_vectorStarts.clear();
```

- In the row loop, replace the "Draw a row of lines." block's beginning so that in quad mode the row's start points are collected instead of drawn:

```cpp
            if (quadLines)
            {
                for (int v = 0; v < vertex; v += 2)
                {
                    m_vectorStarts.emplace_back(lineVertices[v].x, lineVertices[v].y);
                }
                continue;
            }

            // Draw a row of lines.
```

- After the row loop (before `glBindBuffer(GL_ARRAY_BUFFER, 0);`):

```cpp
    if (quadLines)
    {
        DrawQuads(presetPerFrameContext, lineScale, minimumLength);
    }
```

- Add:

```cpp
void MotionVectors::DrawQuads(const PerFrameContext& presetPerFrameContext, float lineScale, float minimumLength)
{
    if (m_vectorStarts.empty())
    {
        return;
    }

    if (m_quadVaoId == 0)
    {
        glGenVertexArrays(1, &m_quadVaoId);
        glGenBuffers(1, &m_quadVboId);
        glBindVertexArray(m_quadVaoId);
        glBindBuffer(GL_ARRAY_BUFFER, m_quadVboId);
        glEnableVertexAttribArray(0);
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, sizeof(Point), nullptr);
        glVertexAttribDivisor(0, 1);
        glDisableVertexAttribArray(1); // The color is the constant attribute set in Draw().
    }

    glBindVertexArray(m_quadVaoId);
    glBindBuffer(GL_ARRAY_BUFFER, m_quadVboId);
    glBufferData(GL_ARRAY_BUFFER, static_cast<GLsizeiptr>(sizeof(Point) * m_vectorStarts.size()), m_vectorStarts.data(), GL_STREAM_DRAW);

    m_motionVectorQuadShader.Bind();
    m_motionVectorQuadShader.SetUniformMat4x4("vertex_transformation", PresetState::orthogonalProjection);
    m_motionVectorQuadShader.SetUniformFloat2("viewport_size", glm::vec2(static_cast<float>(m_presetState.renderContext.viewportSizeX),
                                                                         static_cast<float>(m_presetState.renderContext.viewportSizeY)));
    m_motionVectorQuadShader.SetUniformFloat("half_width", LineStyleFor(LineKind::MotionVector, false, lineScale).halfWidth);
    m_motionVectorQuadShader.SetUniformFloat("antialias", m_presetState.renderContext.lineAntialiasing ? 1.0f : 0.0f);
    m_motionVectorQuadShader.SetUniformFloat("length_multiplier", static_cast<float>(*presetPerFrameContext.mv_l));
    m_motionVectorQuadShader.SetUniformFloat("minimum_length", minimumLength);
    m_motionVectorQuadShader.SetUniformInt("warp_coordinates", 0);

    glDrawArraysInstanced(GL_TRIANGLE_STRIP, 0, 4, static_cast<GLsizei>(m_vectorStarts.size()));
}
```

(The motion texture is still bound to unit 0 and blending is enabled by `Draw` before the loop. Verify the name of the per-frame context parameter in `Draw`'s signature and use it.)

- [ ] **Step 3: Check**

Same commands as Task 4 Step 6. Expected: `"legacy_changed": []`; the motion-vector presets (`$$$ Royal - Mashup (103).milk`, `(1).milk`) within 0.90–1.10, vectors in the same grid positions and directions in the image pairs.

- [ ] **Step 4: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): draw motion vectors as quads in one instanced call (patch 0021)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 9: Calibrate thick lines and run the full comparison

**Files:**
- Modify (projectM): `src/libprojectM/MilkdropPreset/LineGeometry.cpp` (the `*Thick` constants only), `tests/libprojectM/LineGeometryTest.cpp` (expected values of the thick tests)

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Run the sample against the baseline**

```bash
tools/regen-projectm-patch.sh 0021-quad-lines.patch
build/preset-lab-venv/bin/preset-lab line-compare --sample-every 40 --work build/preset-lab/line-sample \
    --baseline build/preset-lab/line-sample-baseline.json --concurrency 4 | tee build/preset-lab/line-sample-summary.json
```

Expected: `"failed"` equal to the baseline's, `"legacy_changed": []`. Note `median_ratio_by_feature` for `main_thick`, `custom_thick`, `shape_thick`.

- [ ] **Step 2: Calibrate each thick kind outside 0.95–1.05**

For each of `main_thick`, `custom_thick`, `shape_thick` whose median ratio `r` is outside 0.95–1.05:

```bash
jq -r '.presets[] | select(.features | index("custom_thick")) | .preset' build/preset-lab/line-sample/report.json \
    > build/preset-lab/custom_thick.txt
```

Change that kind's `thickHalfWidth` in `LineGeometry.cpp` to `thickHalfWidth × (1 + 2 × (1 − r))`, clamped to 0.5–1.5. (Whole-frame luma moves less than line energy, so the correction is doubled.) Then rerun only those presets at the reference height:

```bash
tools/regen-projectm-patch.sh 0021-quad-lines.patch
build/preset-lab-venv/bin/preset-lab line-compare --preset-list build/preset-lab/custom_thick.txt --heights 1080 \
    --work build/preset-lab/line-cal --concurrency 4 | jq '.median_ratio_by_feature.custom_thick'
```

Repeat at most three times per kind. If it is still outside 0.95–1.05, try `thickPasses` ±1 with the best width. Record each attempt (width, passes, median ratio) for the commit message.

- [ ] **Step 3: Update the unit tests to the calibrated values**

Change the expected values in `MainWaveThickIsTwoPixelsDrawnTwice` (and add equivalent `CustomWaveThick…`/`ShapeBorderThick…` tests if their constants changed) so they state the calibrated width and passes. Run `tools/projectm-host-tests.sh 2>&1 | tail -1`. Expected: PASSED.

- [ ] **Step 4: Final full run and the gate**

```bash
tools/regen-projectm-patch.sh 0021-quad-lines.patch && tools/check-patch-series.sh
build/preset-lab-venv/bin/preset-lab line-compare --sample-every 40 --work build/preset-lab/line-sample \
    --baseline build/preset-lab/line-sample-baseline.json --concurrency 4 | tee build/preset-lab/line-sample-summary.json
```

Pass criteria (all of them):
- `failed` equals the baseline's, `legacy_changed` is empty.
- `median_deviation` ≤ 0.02 and `share_beyond_tolerance` ≤ 0.05.
- Every thick feature median within 0.95–1.05.
- `median_drift.quad` < `median_drift.legacy` (quad lines keep brightness steadier across 720/1440).

Look at the image pairs of every preset in `beyond_tolerance` and note in the commit message whether the difference is the anti-aliasing (expected) or a defect.

**Stop and report to the user** instead of continuing if `median_drift.legacy` is below 0.02 (the brightness problem this feature fixes barely exists in our build) or if the drift criterion fails. The quad lines would then only bring anti-aliasing, which is a different trade-off.

- [ ] **Step 5: Commit**

```bash
git add tools/projectm-patches/0021-quad-lines.patch
git commit -m "feat(core): calibrate thick quad lines against MilkDrop's (patch 0021)

<per kind: width, passes, median ratio before/after; overall median deviation,
share beyond 10 %, median drift legacy vs quad; notes on presets beyond tolerance>

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 10: Turn it on in the app, and document

**Files:**
- Modify: `core/src/main/cpp/native-lib.cpp`, `core/src/test/native/engine_test.cpp`, `README.md`, `docs/ARCHITECTURE.md`

**Interfaces:**
- Consumes: `projectm_opengl_set_line_reference_height` (Task 3).

- [ ] **Step 1: Write the failing engine test**

`core/src/test/native/engine_test.cpp`, next to the `projectm_opengl_set_direct_output` stub (line ~113):

```cpp
uint32_t g_lineReferenceHeight = 0;
void projectm_opengl_set_line_reference_height(projectm_handle, uint32_t height) { g_lineReferenceHeight = height; }
```

and right after the first `Java_nl_neerdael_projectm_core_ProjectMJNI_onSurfaceCreated(nullptr, nullptr);` (line ~231):

```cpp
  printf("lines are quads, 1 px at 1080p\n");
  CHECK(g_lineReferenceHeight == 1080);
```

- [ ] **Step 2: Run it to verify it fails**

Run: `bash core/src/test/native/run_native_tests.sh 2>&1 | grep -E "FAIL|lines are quads" | head -3`
Expected: `FAIL …engine_test.cpp:… g_lineReferenceHeight == 1080`. (If it fails at `engine_test.cpp:538` instead, that is the known intermittent test on `main`; rerun.)

- [ ] **Step 3: Set it in the engine**

`core/src/main/cpp/native-lib.cpp`, in `onSurfaceCreated` after `projectm_set_beat_sensitivity(g_engine.pm, 1.0f);`:

```cpp
    // Lines as anti-aliased quads, 1 px wide at 1080p and in proportion at other render sizes, so a
    // preset looks the same at every quality level (patch 0021, projectM issue #682).
    projectm_opengl_set_line_reference_height(g_engine.pm, 1080);
```

- [ ] **Step 4: Run the tests**

```bash
bash core/src/test/native/run_native_tests.sh > /dev/null 2>&1; echo "native $?"
./gradlew -q testDebugUnitTest; echo "jvm $?"
./gradlew -q :app:assembleDebug; echo "build $?"
```

Expected: `native 0` (rerun once if it fails at line 538), `jvm 0`, `build 0`. Run `git checkout -- build/reports/problems/problems-report.html` afterwards if Gradle modified that tracked file.

- [ ] **Step 5: Document**

`README.md` (the patch list in the "projectM is built from source" paragraph): after "less memory traffic per frame on tile-based GPUs: …the final image drawn straight to the screen", add "; and lines drawn as anti-aliased quads that keep their share of the picture at every render size ([#682](https://github.com/projectM-visualizer/projectm/issues/682))".

`docs/ARCHITECTURE.md`, a new paragraph after "Memory traffic per frame (patches 0009–0016)":

```markdown
**Lines (patch 0021).** projectM draws waveforms, custom waves, shape outlines and motion vectors as
1 px GL lines, thick ones four times with an offset. On GLES they are not anti-aliased, and their share
of the picture changes with the render size, so presets that feed their image back got brighter at low
and darker at high quality levels. `projectm_opengl_set_line_reference_height(1080)` draws them as quads
instead: one instance per segment, miter joins, a one-pixel anti-aliased edge, 1 px wide at 1080 and in
proportion elsewhere. Thick lines are a wider line drawn more than once, calibrated against MilkDrop's
with preset-lab (`preset-lab line-compare`: <results from Task 9>). Dots scale the same way. With 0 the
GL lines are drawn as before, frame for frame.
```

- [ ] **Step 6: Commit**

```bash
git add core/src/main/cpp/native-lib.cpp core/src/test/native/engine_test.cpp README.md docs/ARCHITECTURE.md
git commit -m "feat: draw lines as anti-aliased quads that scale with the render size

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```

---

### Task 11: Device verification

**Files:** none (results go into the final summary and, if they change numbers, `docs/ARCHITECTURE.md`).

- [ ] **Step 1: Ask the user which TV may be used** (AM6 at 192.168.50.80:5555 is rooted; the SHIELD is not; never wake a TV remotely). Wait for the answer.

- [ ] **Step 2: Install the profile build next to the release app**

```bash
./gradlew -q :app:assembleProfile
adb -s 192.168.50.80:5555 install -r app/build/outputs/apk/profile/app-profile.apk
adb -s 192.168.50.80:5555 shell pm grant nl.neerdael.projectmtv.profile android.permission.RECORD_AUDIO
```

- [ ] **Step 3: Shader check on the device**

```bash
adb -s 192.168.50.80:5555 logcat -c
adb -s 192.168.50.80:5555 shell setprop debug.projectmtv.preset "'\$\$\$ Royal - Mashup (191)'"
adb -s 192.168.50.80:5555 shell am start -S -n nl.neerdael.projectmtv.profile/com.example.projectm.visualizer.MainActivity
sleep 15; adb -s 192.168.50.80:5555 logcat -d | grep -iE "shader|link|compile|GL error" | head -20
```

Expected: no shader compile or link errors. A precision-mismatch link error here means the `half_width` qualifiers differ between the stages.

- [ ] **Step 4: Frame rate against the release app**

For each fixed-list preset that runs on the TV, pin it (`setprop debug.projectmtv.preset '<name prefix>'`), set `render_height` to 1080 through the shared-prefs method in the `am6-gpu-benchmarking` memory, and read 60 s of `VisualizerRenderer: STATS` lines from both the profile app and the release app. Expected: the profile build's fps is within 2% of the release app's (the method is reproducible to ±1%), or higher.

- [ ] **Step 5: Quality ladder and transitions**

With a pinned thick-line preset, change the quality setting 720 → 1080 → 1440 while it runs, then unpin and let a few transitions run. Expected: lines change width with the render size on the next frame, no stutter beyond the existing transition behaviour (`TRANSITION … slow_frames` unchanged), and `adb exec-out screencap -p > shot-<h>.png` screenshots show smooth, anti-aliased lines.

- [ ] **Step 6: Clean up**

```bash
adb -s 192.168.50.80:5555 shell setprop debug.projectmtv.preset "''"
```

Restore the shared prefs you changed. Report the fps table, the screenshots and any errors to the user; ask them to try the profile APK on the SHIELD.

---

## Self-review notes

- Coverage: width rule (Tasks 2, 4), geometry and joins (4), anti-aliasing (4), thick emulation (2, 9), dots (5), opt-in with unchanged legacy path (3 baseline, checked in 4–9), off-thread compile (4: `PresetState` member), app default 1080 (10), docs (10), device (11).
- Review Focus pins: GLES shader errors → Task 4 Step 3, Task 8 Step 1, Task 11 Step 3; extreme coordinates → Task 6 Step 3; degenerate strips → Task 2 tests and the shader guard; render size changes and blends → Task 11 Step 5; many shape instances → fixed list in Tasks 3 and 7.
- Merge note: the worktree `feat/macos-rank-comparison` also changes preset-lab; rebase this branch on main before merging if that lands first (`cli.py` is the likely conflict).
