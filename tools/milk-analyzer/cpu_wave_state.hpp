#pragma once
#include "Audio/FrameAudioData.hpp"
#include "Renderer/RenderContext.hpp"
#include <array>
namespace milk_wave_cpu {
namespace Audio=libprojectM::Audio;
namespace Renderer {
struct RenderItem {
    struct Point {float x{},y{};};
    struct ColoredPoint {float x{},y{},r{},g{},b{},a{};};
};
}
namespace MilkdropPreset {
struct PresetState {
    libprojectM::Audio::FrameAudioData audioData{};
    libprojectM::Renderer::RenderContext renderContext;
    float waveScale{1},waveSmoothing{.75f};
    bool modWaveAlphaByvolume{false};
};
struct PerFrameContext {
    double x{.5},y{.5},mystery{},alpha{.8};
    double *wave_x{&x},*wave_y{&y},*wave_mystery{&mystery},*wave_a{&alpha};
};
}
}
