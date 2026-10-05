#pragma once

#include <algorithm>
#include <cmath>

namespace projectmtv {

constexpr bool kNativeRenderingEnabled = true;

constexpr int kCappedRenderHeight = 1330;

struct RenderDimensions { int width; int height; };

inline RenderDimensions RenderDimensionsFor(int surfaceWidth, int surfaceHeight, float scale) {
    RenderDimensions result{surfaceWidth, surfaceHeight};
    if (scale < 1.f) {
        result.width = std::max(2, static_cast<int>(std::lround(surfaceWidth * scale)) & ~1);
        result.height = std::max(2, static_cast<int>(std::lround(surfaceHeight * scale)) & ~1);
    }
    return result;
}

} // namespace projectmtv
