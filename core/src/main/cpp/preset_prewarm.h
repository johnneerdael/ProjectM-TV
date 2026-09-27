// Compiles the shaders of the upcoming presets on a background thread, with its own EGL context and
// projectM instance. The translated and linked programs land in projectM's process-wide caches
// (projectM patches 0002 and 0005), so the switch on the render thread loads them in milliseconds instead of stalling
// on the GPU driver's shader compiler for most of a second.
#pragma once

#include <condition_variable>
#include <deque>
#include <functional>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

class PresetPrewarmer {
public:
    using Reader = std::function<std::string(const std::string& name)>;

    ~PresetPrewarmer() { Stop(); }

    // textureDir must be the main instance's texture search path: sampler declarations in the
    // generated shader code depend on the textures found, and the cache is keyed by that code.
    void Start(const std::string& textureDir, Reader reader);
    void Stop();

    // Compiles these presets next, in order, replacing requests that have not started yet. Presets
    // compiled recently are skipped (their programs are in the cache).
    void Request(const std::vector<std::string>& names);

    bool Running() const { return thread_.joinable(); }

private:
    void Run(std::string textureDir);

    std::thread thread_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::deque<std::string> pending_;
    std::deque<std::string> recent_;  // compiled lately, most recent last
    bool stop_ = false;
    Reader reader_;
};
