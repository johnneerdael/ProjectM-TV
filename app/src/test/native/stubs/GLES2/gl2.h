#pragma once
typedef unsigned int GLenum; typedef int GLint; typedef int GLsizei; typedef void GLvoid;
#define GL_RGBA 0x1908
#define GL_UNSIGNED_BYTE 0x1401
extern "C" { void glViewport(GLint,GLint,GLsizei,GLsizei); void glReadPixels(GLint,GLint,GLsizei,GLsizei,GLenum,GLenum,GLvoid*); }
