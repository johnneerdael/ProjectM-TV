// What the engine was last doing, kept in a small file that outlives a crash of the process: the next
// launch shows it next to Android's exit record for the same process ID (Settings › Advanced ›
// Last exit). One fixed-size line per writer thread, overwritten in place with pwrite, so writers
// never block each other and a crash can at most leave one line half-written.
#pragma once

#include <fcntl.h>
#include <time.h>
#include <unistd.h>

#include <algorithm>
#include <atomic>
#include <cstdarg>
#include <cstdio>
#include <cstring>

namespace projectmtv {

enum TrailSlot { kTrailRender = 0, kTrailPrewarm = 1, kTrailSlots = 2 };
constexpr size_t kTrailLineBytes = 384;

inline std::atomic<int>& TrailFd() {
    static std::atomic<int> fd{-1};
    return fd;
}

// Opens (or creates) the trail file without truncating it: a process that never renders, e.g. one
// started only for the notification listener, leaves the previous process's lines in place.
inline void OpenTrail(const char* path) {
    int fd = open(path, O_WRONLY | O_CREAT | O_CLOEXEC, 0600);
    if (fd < 0) return;
    int old = TrailFd().exchange(fd);
    if (old >= 0) close(old);
}

// Writes "<slot> pid=<pid> ms=<wall clock ms> <message>" as this slot's line. A thread writes only
// its own slot.
inline void WriteTrail(TrailSlot slot, const char* format, ...) {
    int fd = TrailFd().load();
    if (fd < 0) return;
    char line[kTrailLineBytes];
    timespec now{};
    clock_gettime(CLOCK_REALTIME, &now);
    long long ms = static_cast<long long>(now.tv_sec) * 1000 + now.tv_nsec / 1000000;
    int used = snprintf(line, sizeof(line), "%s pid=%d ms=%lld ", slot == kTrailRender ? "render" : "prewarm",
                        static_cast<int>(getpid()), ms);
    if (used < 0) return;
    va_list args;
    va_start(args, format);
    int more = vsnprintf(line + used, sizeof(line) - used, format, args);
    va_end(args);
    size_t length = more < 0 ? used : std::min(sizeof(line) - 1, static_cast<size_t>(used + more));
    // Pad to the fixed width (a shorter line must cover the previous one) and end with a newline.
    memset(line + length, ' ', sizeof(line) - 1 - length);
    for (size_t i = 0; i < sizeof(line) - 1; ++i)
        if (line[i] == '\n' || line[i] == '\0') line[i] = ' ';
    line[sizeof(line) - 1] = '\n';
    ssize_t ignored = pwrite(fd, line, sizeof(line), static_cast<off_t>(slot) * kTrailLineBytes);
    (void) ignored;
}

}  // namespace projectmtv
