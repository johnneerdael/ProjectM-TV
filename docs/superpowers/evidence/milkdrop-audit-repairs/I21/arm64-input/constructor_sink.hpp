#pragma once
#include <Renderer/OpenGL.h>
#include <stdexcept>
// CPU diagnostic only. Constructors require GL object bookkeeping; no context,
// GL resolver, driver function or draw is invoked. Compilation fails intentionally.
namespace input_sink {
inline unsigned calls=0;inline GLuint nextId=1;
inline GLuint Id(){++calls;return nextId++;}
inline GLuint ShaderId(GLenum){return Id();}
inline void Gen(GLsizei n,GLuint* ids){++calls;for(int i=0;i<n;++i)ids[i]=nextId++;}
inline void Delete(GLsizei,const GLuint*){++calls;}
inline void Bind(GLuint){++calls;}
inline void BindBuffer(GLenum,GLuint){++calls;}
inline void Parameter(GLuint,GLenum,GLint){++calls;}
inline void Data(GLenum,GLsizeiptr,const void*,GLenum){++calls;}
inline void SubData(GLenum,GLintptr,GLsizeiptr,const void*){++calls;}
inline void DrawBuffers(GLsizei,const GLenum*){++calls;}
inline void Attrib(GLuint,GLint,GLenum,GLboolean,GLsizei,const void*){++calls;}
inline void ShaderSource(GLuint,GLsizei,const GLchar* const*,const GLint*){++calls;}
inline void ShaderState(GLuint,GLenum,GLint* v){++calls;*v=0;}
inline void ShaderLog(GLuint,GLsizei,GLsizei* written,GLchar* text){++calls;if(written)*written=0;if(text)*text=0;}
inline const GLubyte* String(GLenum){++calls;return nullptr;}
inline void ForbiddenElements(GLenum,GLsizei,GLenum,const void*){throw std::runtime_error("forbidden GL draw in CPU producer");}
inline void ForbiddenArrays(GLenum,GLint,GLsizei){throw std::runtime_error("forbidden GL draw in CPU producer");}
inline void ForbiddenInstanced(GLenum,GLint,GLsizei,GLsizei){throw std::runtime_error("forbidden GL draw in CPU producer");}
inline void Install(){
 glad_glGenFramebuffers=Gen;glad_glDeleteFramebuffers=Delete;glad_glBindFramebuffer=BindBuffer;glad_glDrawBuffers=DrawBuffers;
 glad_glGenSamplers=Gen;glad_glDeleteSamplers=Delete;glad_glSamplerParameteri=Parameter;
 glad_glGenTextures=Gen;glad_glDeleteTextures=Delete;glad_glBindTexture=BindBuffer;
 glad_glBufferData=Data;glad_glBufferSubData=SubData;glad_glCreateProgram=Id;glad_glCreateShader=ShaderId;
 glad_glGenBuffers=Gen;glad_glGenVertexArrays=Gen;glad_glDeleteBuffers=Delete;glad_glDeleteVertexArrays=Delete;
 glad_glBindVertexArray=Bind;glad_glBindBuffer=BindBuffer;glad_glVertexAttribPointer=Attrib;
 glad_glEnableVertexAttribArray=Bind;glad_glDisableVertexAttribArray=Bind;glad_glShaderSource=ShaderSource;
 glad_glCompileShader=Bind;glad_glGetShaderiv=ShaderState;glad_glGetShaderInfoLog=ShaderLog;
 glad_glDeleteShader=Bind;glad_glDeleteProgram=Bind;glad_glGetString=String;
 glad_glDrawElements=ForbiddenElements;glad_glDrawArrays=ForbiddenArrays;glad_glDrawArraysInstanced=ForbiddenInstanced;
}
}
