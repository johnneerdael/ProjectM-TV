"""Adapt the existing Preset Lab worker only inside a private host export."""


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("Mac worker instrumentation anchor missing/ambiguous: " + old[:80])
    return text.replace(old, new)


def adapt_worker(source, captures):
    source = once(source, '#include <cmath>', '#include <cmath>\n#include <chrono>\n#include <algorithm>\n#include <set>')
    source = once(source, '        engine.SetLineAntialiasing(cfg.value("line_antialiasing", false));', '''        engine.SetLineAntialiasing(cfg.value("line_antialiasing", false));
        const float feedback = cfg.at("feedback_detail");
#if NATIVE_TRAILS_DETAIL_AVAILABLE
        engine.SetFeedbackDetail(feedback);
#else
        if (feedback >= 0) throw std::runtime_error("baseline does not support enabled feedback detail");
#endif''')
    source = once(source, '        int error_frames = 0;', '''        int error_frames = 0;
        int gl_checks = 0;
        size_t selected_bytes = 0;
        std::set<int> detail_statuses;
        std::vector<double> frame_times;
        std::cout.sync_with_stdio(false);''')
    source = once(source, '            lab::clock_seconds = static_cast<double>(frame + 1) / fps;',
                  '            lab::clock_seconds = static_cast<double>(frame) / fps;')
    source = once(source, '            engine.RenderFrame(capture.framebuffer);', '''            const auto started = std::chrono::steady_clock::now();
            engine.RenderFrame(capture.framebuffer);
            glFinish();
            if (frame >= 120) frame_times.push_back(std::chrono::duration<double, std::milli>(
                std::chrono::steady_clock::now() - started).count());
            if (!engine.failure.empty()) throw std::runtime_error(engine.failure);
#if NATIVE_TRAILS_DETAIL_AVAILABLE
            detail_statuses.insert(engine.FeedbackDetailStatus());
#else
            detail_statuses.insert(-1);
#endif''')
    predicate = " || ".join("frame == %d" % frame for frame in captures)
    source = once(source, '            auto pixels = capture.Read();', '''            const bool selected = %s;
            std::vector<unsigned char> pixels;
            if (selected) {
                pixels = capture.Read();
                selected_bytes += pixels.size();
            }''' % predicate)
    source = once(source, '            if (glGetError() != GL_NO_ERROR) ++error_frames;',
                  '            ++gl_checks;\n            if (glGetError() != GL_NO_ERROR) ++error_frames;')
    source = once(source, '            std::cout.write(reinterpret_cast<char*>(pixels.data()), pixels.size());',
                  '            if (selected) std::cout.write(reinterpret_cast<char*>(pixels.data()), pixels.size());')
    source = once(source, '        json result = {{"status", error_frames ? "failed" : "success"},', '''        double frame_total = 0;
        for (auto value : frame_times) frame_total += value;
        std::sort(frame_times.begin(), frame_times.end());
        json result = {{"status", error_frames ? "failed" : "success"},
                       {"captures", json::array({%s})}, {"selected_bytes", selected_bytes},
                       {"gl_checks", gl_checks}, {"detail_statuses", detail_statuses},
                       {"detail_status_meaning", "-1 off; -2 unsupported/inactive canvas; -3 shader/resource fallback; positive actual scale"},
                       {"serialized_frame_mean_ms", frame_total / frame_times.size()},
                       {"serialized_frame_p90_ms", frame_times[static_cast<size_t>(std::ceil(.9 * frame_times.size())) - 1]},
                       {"timing_scope", "RenderFrame plus glFinish;360frames;excludes capture/pipe/metric/PNG work;concurrent host contexts,not Android app FPS"},
                       {"gl_vendor", reinterpret_cast<const char*>(glGetString(GL_VENDOR))},''' % ",".join(map(str, captures)))
    return source
