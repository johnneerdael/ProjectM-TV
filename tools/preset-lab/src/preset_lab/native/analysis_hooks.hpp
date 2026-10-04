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
// Keep shader random values private: linked GL/SDL code may consume libc rand().
// Park-Miller matches this lab's original macOS rand sequence. All platforms use
// this explicit algorithm now; a new instrumentation identity defines the oracle.
inline uint32_t shader_random_state = 0;
inline void ResetShaderRandom() { shader_random_state = Seed(1); }
inline uint32_t ShaderRandom() {
    if (shader_random_state == 0) shader_random_state = 123459876u;
    shader_random_state = static_cast<uint32_t>(
        (static_cast<uint64_t>(shader_random_state) * 16807u) % 2147483647u);
    return shader_random_state;
}
inline uint32_t StringSeed(const std::string& text) {
    uint32_t result = 2166136261u;
    for (unsigned char value : text) result = (result ^ value) * 16777619u;
    return result;
}
}
#endif
