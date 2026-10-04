#pragma once

#include <algorithm>
#include <cmath>

namespace projectmtv {

#ifdef PROJECTMTV_RENDERING_POLICY_CAPPED
constexpr bool kNativeRenderingEnabled = false;
#else
constexpr bool kNativeRenderingEnabled = true;
#endif

constexpr int kCappedRenderHeight = 1330;

struct RenderDimensions { int width; int height; };

inline RenderDimensions RenderDimensionsFor(int surfaceWidth, int surfaceHeight, float scale) {
    RenderDimensions result{surfaceWidth, surfaceHeight};
    if (scale < 1.f) {
        result.width = std::max(2, static_cast<int>(std::lround(surfaceWidth * scale)) & ~1);
        result.height = std::max(2, static_cast<int>(std::lround(surfaceHeight * scale)) & ~1);
    }
    if (!kNativeRenderingEnabled && result.height > kCappedRenderHeight) {
        result.width = std::max(2, static_cast<int>(std::lround(
                static_cast<double>(result.width) * kCappedRenderHeight / result.height)) & ~1);
        result.height = kCappedRenderHeight;
    }
    return result;
}

} // namespace projectmtv
