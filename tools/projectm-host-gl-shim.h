#pragma once
#if !defined(__ANDROID__) && !defined(USE_GLES) && __has_include(<glad/gl.h>)
#include <glad/gl.h>
#endif
// Apple OpenGL4.1 and desktop declarations below GL4.3 lack this optional hint.
// Retain contents in host controls; Android/GLES keeps its real discard API.
#if defined(__APPLE__) || (!defined(__ANDROID__) && !defined(USE_GLES) && !defined(GL_VERSION_4_3))
#undef glInvalidateFramebuffer
#define glInvalidateFramebuffer(target, count, attachments) ((void)0)
#endif
