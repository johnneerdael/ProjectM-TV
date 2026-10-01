#ifndef PRESET_LAB_ANALYSIS_HOOKS_HPP
#define PRESET_LAB_ANALYSIS_HOOKS_HPP
#include <cstdint>
#include <cstdlib>
#include <string>

// Apple's desktop OpenGL 4.1 lacks the GLES3 discard hint used by app patch 0009.
// Keeping those attachment contents is equivalent for rendering correctness.
#ifdef __APPLE__
#define glInvalidateFramebuffer(target, count, attachments) ((void)0)
#endif

// Present only in the analyzer's private projectM source copy.
namespace lab {
inline double clock_seconds = 0.0;
inline uint32_t Seed(uint32_t subsystem) {
    const char* configured = std::getenv("PRESET_LAB_SEED");
    uint32_t value = configured ? static_cast<uint32_t>(std::strtoul(configured, nullptr, 10)) : 12345u;
    return value ^ (subsystem * 0x9e3779b9u);
}
inline uint32_t StringSeed(const std::string& text) {
    uint32_t result = 2166136261u;
    for (unsigned char value : text) result = (result ^ value) * 16777619u;
    return result;
}
}
#endif
