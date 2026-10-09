#include "image-harness/gl_capture.hpp"
#include <iostream>
int main() { try {
 GlCapture capture(32,32);
 GLuint sentinel=0; glGenFramebuffers(1,&sentinel);
 glBindFramebuffer(GL_READ_FRAMEBUFFER,sentinel);
 glReadBuffer(GL_NONE); glPixelStorei(GL_PACK_ALIGNMENT,8);
 const auto pixels=capture.Read();
 GLint read=0,buffer=0,pack=0;
 glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING,&read);glGetIntegerv(GL_READ_BUFFER,&buffer);glGetIntegerv(GL_PACK_ALIGNMENT,&pack);
 if(read!=static_cast<GLint>(sentinel)||buffer!=GL_NONE||pack!=8||pixels.size()!=32*32*3||glGetError()!=GL_NO_ERROR)throw std::runtime_error("readback caller state not restored");
 glBindFramebuffer(GL_READ_FRAMEBUFFER,capture.framebuffer);glDeleteFramebuffers(1,&sentinel);
 std::cout<<"PASS: readFramebuffer/readBuffer/packAlignment restored; RGB payload retained\n";return 0;
 }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 1;} }
