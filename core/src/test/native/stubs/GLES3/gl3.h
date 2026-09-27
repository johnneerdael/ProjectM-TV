#pragma once
#include <cstddef>
#include <cstdint>
typedef unsigned int GLenum; typedef int GLint; typedef unsigned int GLuint; typedef int GLsizei; typedef void GLvoid;
typedef unsigned int GLbitfield; typedef std::ptrdiff_t GLsizeiptr; typedef std::ptrdiff_t GLintptr;
typedef uint64_t GLuint64; typedef struct __GLsync* GLsync;
#define GL_RGBA 0x1908
#define GL_UNSIGNED_BYTE 0x1401
#define GL_READ_FRAMEBUFFER 0x8CA8
#define GL_READ_FRAMEBUFFER_BINDING 0x8CAA
#define GL_PIXEL_PACK_BUFFER 0x88EB
#define GL_PIXEL_PACK_BUFFER_BINDING 0x88ED
#define GL_PACK_ALIGNMENT 0x0D05
#define GL_STREAM_READ 0x88E1
#define GL_MAP_READ_BIT 0x0001
#define GL_SYNC_GPU_COMMANDS_COMPLETE 0x9117
#define GL_ALREADY_SIGNALED 0x911A
#define GL_TIMEOUT_EXPIRED 0x911B
#define GL_CONDITION_SATISFIED 0x911C
#define GL_WAIT_FAILED 0x911D
#define GL_TEXTURE_2D 0x0DE1
#define GL_RGBA8 0x8058
#define GL_TEXTURE_MIN_FILTER 0x2801
#define GL_TEXTURE_MAG_FILTER 0x2800
#define GL_LINEAR 0x2601
#define GL_FRAMEBUFFER 0x8D40
#define GL_DRAW_FRAMEBUFFER 0x8CA9
#define GL_COLOR_ATTACHMENT0 0x8CE0
#define GL_FRAMEBUFFER_COMPLETE 0x8CD5
#define GL_COLOR_BUFFER_BIT 0x00004000
extern "C" {
void glViewport(GLint, GLint, GLsizei, GLsizei);
void glReadPixels(GLint, GLint, GLsizei, GLsizei, GLenum, GLenum, GLvoid*);
void glBindFramebuffer(GLenum, GLuint);
void glGetIntegerv(GLenum, GLint*);
void glGenBuffers(GLsizei, GLuint*);
void glDeleteBuffers(GLsizei, const GLuint*);
void glBindBuffer(GLenum, GLuint);
void glBufferData(GLenum, GLsizeiptr, const void*, GLenum);
void glPixelStorei(GLenum, GLint);
void* glMapBufferRange(GLenum, GLintptr, GLsizeiptr, GLbitfield);
unsigned char glUnmapBuffer(GLenum);
GLsync glFenceSync(GLenum, GLbitfield);
GLenum glClientWaitSync(GLsync, GLbitfield, GLuint64);
void glDeleteSync(GLsync);
void glFlush(void);
void glGenFramebuffers(GLsizei, GLuint*);
void glDeleteFramebuffers(GLsizei, const GLuint*);
void glGenTextures(GLsizei, GLuint*);
void glDeleteTextures(GLsizei, const GLuint*);
void glBindTexture(GLenum, GLuint);
void glTexImage2D(GLenum, GLint, GLint, GLsizei, GLsizei, GLint, GLenum, GLenum, const void*);
void glTexParameteri(GLenum, GLenum, GLint);
void glFramebufferTexture2D(GLenum, GLenum, GLenum, GLuint, GLint);
GLenum glCheckFramebufferStatus(GLenum);
void glBlitFramebuffer(GLint, GLint, GLint, GLint, GLint, GLint, GLint, GLint, GLbitfield, GLenum);
}
