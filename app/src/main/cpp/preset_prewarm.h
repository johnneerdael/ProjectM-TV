// Compiles the shaders of the upcoming preset on a background thread, with its own EGL context and
// projectM instance. The linked programs land in projectM's process-wide program cache (projectM
// patch 0004), so the switch on the render thread loads them in milliseconds instead of stalling
// on the GPU driver's shader compiler for most of a second.
#pragma once

#include <condition_variable>
#include <functional>
#include <mutex>
#include <string>
#include <thread>

class PresetPrewarmer {
public:
    using Reader = std::function<std::string(const std::string& name)>;

    ~PresetPrewarmer() { Stop(); }

    // textureDir must be the main instance's texture search path: sampler declarations in the
    // generated shader code depend on the textures found, and the cache is keyed by that code.
    void Start(const std::string& textureDir, Reader reader);
    void Stop();

    // Compiles this preset next, replacing a request that has not started yet.
    void Request(const std::string& name);

    bool Running() const { return thread_.joinable(); }

private:
    void Run(std::string textureDir);

    std::thread thread_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::string pending_;
    std::string last_;
    bool stop_ = false;
    Reader reader_;
};
