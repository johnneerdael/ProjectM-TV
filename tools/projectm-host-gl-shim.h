#pragma once
#if __has_include(<glad/gl.h>)
#include <glad/gl.h>
#endif
// macOS OpenGL 4.1 lacks the framebuffer-discard hint. Retaining contents is safe.
#ifdef __APPLE__
#undef glInvalidateFramebuffer
#define glInvalidateFramebuffer(target, count, attachments) ((void)0)
#endif
