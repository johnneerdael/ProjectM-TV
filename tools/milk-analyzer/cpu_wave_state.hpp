#pragma once
#include "Audio/FrameAudioData.hpp"
#include <array>
namespace milk_wave_cpu {
namespace Audio=libprojectM::Audio;
namespace Renderer {
struct RenderItem {struct Point {float x{},y{};};};
}
namespace MilkdropPreset {
struct PresetState {
    libprojectM::Audio::FrameAudioData audioData{};
    struct Context {int viewportSizeX{512},viewportSizeY{288};double time{};} renderContext;
    float waveScale{1},waveSmoothing{.75f};
    bool modWaveAlphaByvolume{false};
};
struct PerFrameContext {
    double x{.5},y{.5},mystery{},alpha{.8};
    double *wave_x{&x},*wave_y{&y},*wave_mystery{&mystery},*wave_a{&alpha};
};
}
}
