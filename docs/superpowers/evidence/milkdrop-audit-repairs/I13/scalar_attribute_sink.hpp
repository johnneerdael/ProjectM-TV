#pragma once
#include <Renderer/OpenGL.h>
#include <map>
#include <vector>
#include <cstring>
// No context is created and no GPU/driver function is called. Constructors
// require GL object bookkeeping; these test-only sinks supply it. Shader
// compilation intentionally fails so no rendering path can become usable.
static GLuint Id(){return 1;}
static GLuint ShaderId(GLenum){return 1;}
static GLuint nextId=1;
static void Gen(GLsizei n,GLuint* ids){for(int i=0;i<n;++i)ids[i]=nextId++;}
static void Delete(GLsizei,const GLuint*){}
static void Bind(GLuint){}
static std::map<GLenum,GLuint> bound;
static std::map<GLuint,std::vector<unsigned char>> uploaded;
static std::map<GLuint,const void*> cpuPointers;
static std::map<GLuint,int> uploads;
static std::map<GLuint,GLuint> attributeBuffers;
static void BindBuffer(GLenum target,GLuint id){bound[target]=id;}
static void Parameter(GLuint,GLenum,GLint){}
static void Data(GLenum target,GLsizeiptr count,const void*data,GLenum){auto id=bound[target];auto*b=static_cast<const unsigned char*>(data);uploaded[id].assign(b,b+count);cpuPointers[id]=data;++uploads[id];}
static void SubData(GLenum target,GLintptr offset,GLsizeiptr count,const void*data){auto id=bound[target];std::memcpy(uploaded[id].data()+offset,data,count);cpuPointers[id]=data;++uploads[id];}
static void DrawBuffers(GLsizei,const GLenum*){}
static void Attrib(GLuint attr,GLint,GLenum,GLboolean,GLsizei,const void*){attributeBuffers[attr]=bound[GL_ARRAY_BUFFER];}
static void ShaderSource(GLuint,GLsizei,const GLchar* const*,const GLint*){}
static void ShaderState(GLuint,GLenum,GLint* value){*value=0;}
static void ShaderLog(GLuint,GLsizei,GLsizei*,GLchar* value){*value=0;}
static const GLubyte* String(GLenum){return nullptr;}
static void ScalarSink(){
 glad_glGenFramebuffers=Gen;glad_glDeleteFramebuffers=Delete;glad_glBindFramebuffer=BindBuffer;glad_glDrawBuffers=DrawBuffers;
 glad_glGenSamplers=Gen;glad_glDeleteSamplers=Delete;glad_glSamplerParameteri=Parameter;
 glad_glGenTextures=Gen;glad_glDeleteTextures=Delete;glad_glBindTexture=BindBuffer;
 glad_glBufferData=Data;glad_glBufferSubData=SubData;
 glad_glCreateProgram=Id;glad_glCreateShader=ShaderId;
 glad_glGenBuffers=Gen;glad_glGenVertexArrays=Gen;
 glad_glDeleteBuffers=Delete;glad_glDeleteVertexArrays=Delete;
 glad_glBindVertexArray=Bind;glad_glBindBuffer=BindBuffer;
 glad_glVertexAttribPointer=Attrib;glad_glEnableVertexAttribArray=Bind;glad_glDisableVertexAttribArray=Bind;
 glad_glShaderSource=ShaderSource;glad_glCompileShader=Bind;
 glad_glGetShaderiv=ShaderState;glad_glGetShaderInfoLog=ShaderLog;
 glad_glDeleteShader=Bind;glad_glDeleteProgram=Bind;glad_glGetString=String;
}
