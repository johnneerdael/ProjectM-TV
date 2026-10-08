#pragma once
#include <EGL/egl.h>
#include <Renderer/OpenGL.h>
#include <Renderer/Platform/GLResolver.hpp>
#include <Renderer/Platform/GladLoader.hpp>
#include <algorithm>
#include <stdexcept>
#include <vector>
#include <iostream>
class GlCapture {
public:
 EGLDisplay display=EGL_NO_DISPLAY; EGLContext context=EGL_NO_CONTEXT; EGLSurface surface=EGL_NO_SURFACE;
 GLuint framebuffer=0, texture=0; int width,height;
 GlCapture(int w,int h):width(w),height(h) {
  display=eglGetDisplay(EGL_DEFAULT_DISPLAY);
  if(!eglInitialize(display,nullptr,nullptr)||!eglBindAPI(EGL_OPENGL_ES_API)) throw std::runtime_error("EGL init failed");
  EGLint attrs[]={EGL_SURFACE_TYPE,EGL_PBUFFER_BIT,EGL_RENDERABLE_TYPE,EGL_OPENGL_ES3_BIT,EGL_RED_SIZE,8,EGL_GREEN_SIZE,8,EGL_BLUE_SIZE,8,EGL_ALPHA_SIZE,8,EGL_NONE};
  EGLConfig config; EGLint count;
  if(!eglChooseConfig(display,attrs,&config,1,&count)||count!=1) throw std::runtime_error("EGL config failed");
  EGLint size[]={EGL_WIDTH,1,EGL_HEIGHT,1,EGL_NONE}; surface=eglCreatePbufferSurface(display,config,size);
  EGLint ca[]={EGL_CONTEXT_CLIENT_VERSION,3,EGL_NONE}; context=eglCreateContext(display,config,EGL_NO_CONTEXT,ca);
  if(surface==EGL_NO_SURFACE||context==EGL_NO_CONTEXT||!eglMakeCurrent(display,surface,surface,context)) throw std::runtime_error("EGL context failed");
  if(!libprojectM::Renderer::Platform::GLResolver::Instance().Initialize(nullptr,nullptr)) throw std::runtime_error("GL resolver failed");
  if(!libprojectM::Renderer::Platform::GladLoader::Instance().Initialize()) throw std::runtime_error("GL loader requirements failed");
  std::cerr << "GPU " << glGetString(GL_VENDOR) << " / " << glGetString(GL_RENDERER) << " / " << glGetString(GL_VERSION) << std::endl;
  glGenFramebuffers(1,&framebuffer);glGenTextures(1,&texture);glBindTexture(GL_TEXTURE_2D,texture);
  glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,w,h,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
  glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR);glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR);
  glBindFramebuffer(GL_FRAMEBUFFER,framebuffer);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,texture,0);
  if(glCheckFramebufferStatus(GL_FRAMEBUFFER)!=GL_FRAMEBUFFER_COMPLETE||glGetError()!=GL_NO_ERROR) throw std::runtime_error("FBO allocation failed");
  glClearColor(0,0,0,1);glClear(GL_COLOR_BUFFER_BIT);glPixelStorei(GL_PACK_ALIGNMENT,1);
 }
 std::vector<unsigned char> Read() {
  std::vector<unsigned char> rgba(width*height*4),rgb(width*height*3);
  glBindFramebuffer(GL_READ_FRAMEBUFFER,framebuffer);glReadBuffer(GL_COLOR_ATTACHMENT0);
  glReadPixels(0,0,width,height,GL_RGBA,GL_UNSIGNED_BYTE,rgba.data());
  for(int y=0;y<height;++y) for(int x=0;x<width;++x) for(int c=0;c<3;++c) rgb[(y*width+x)*3+c]=rgba[((height-1-y)*width+x)*4+c];
  return rgb;
 }
 ~GlCapture(){if(context!=EGL_NO_CONTEXT){glDeleteFramebuffers(1,&framebuffer);glDeleteTextures(1,&texture);eglMakeCurrent(display,EGL_NO_SURFACE,EGL_NO_SURFACE,EGL_NO_CONTEXT);eglDestroyContext(display,context);}if(surface!=EGL_NO_SURFACE)eglDestroySurface(display,surface);if(display!=EGL_NO_DISPLAY)eglTerminate(display);}
};
