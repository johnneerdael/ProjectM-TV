// Lightweight preset transition: a still copy of the outgoing frame, faded out (with a slow zoom)
// over the incoming preset. Costs one full-screen textured pass per frame while it runs, instead
// of projectM's soft cut, which renders both presets for the whole transition.
//
// GL thread only. The texture exists only between Capture() and the end of the fade.
#pragma once

#include <GLES3/gl3.h>

class SnapshotFade {
public:
    // Copies the frame that was just rendered to the window (default framebuffer) into a
    // texture. Returns false if the copy or the shader is unavailable.
    bool Capture(int width, int height);

    // Starts fading the captured frame out over `seconds`. Needs a successful Capture().
    void Start(double now, double seconds);

    bool Active() const { return active_; }

    // Draws the snapshot over the current window contents; ends the fade when it is done.
    // Restores the GL state it changes, so projectM's next frame is unaffected.
    void Draw(double now);

    // Ends the fade (or drops an unused capture) and frees the texture.
    void Stop();

    // The GL context is gone: forget all object names without deleting them.
    void Forget();

    // Frees everything; the context must be current.
    void Release();

private:
    bool EnsureProgram();

    GLuint texture_ = 0;
    GLuint program_ = 0;
    GLuint vao_ = 0;
    GLint alphaLoc_ = -1;
    GLint scaleLoc_ = -1;
    int width_ = 0;
    int height_ = 0;
    bool programFailed_ = false;
    bool active_ = false;
    double start_ = 0;
    double duration_ = 0;
};
