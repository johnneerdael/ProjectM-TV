#include "gl_capture.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cassert>
GLuint shader(GLenum type,const std::string& s){GLuint id=glCreateShader(type);const char* p=s.c_str();glShaderSource(id,1,&p,nullptr);glCompileShader(id);GLint ok=0;glGetShaderiv(id,GL_COMPILE_STATUS,&ok);if(!ok){char log[4096];glGetShaderInfoLog(id,4096,nullptr,log);throw std::runtime_error(log);}return id;}
int main(int argc,char** argv){try{
 GlCapture c(16,16);std::ifstream in(argv[1]);std::stringstream stream;stream<<in.rdbuf();
 const std::string vertex="#version 330 core\nout vec2 uv;void main(){vec2 p[3]=vec2[3](vec2(-1,-1),vec2(3,-1),vec2(-1,3));gl_Position=vec4(p[gl_VertexID],0,1);uv=p[gl_VertexID]*.5+.5;}";
 const std::string fragment="#version 330 core\nin vec2 uv;out vec4 color;uniform sampler2D sampler_fw_main;uniform sampler2D sampler_main;uniform int choice;"+stream.str()+"\nvoid main(){color=choice==1?texture(sampler_main,uv):projectm_point_main(sampler_fw_main,uv+(choice==2?vec2(1,0):vec2(0)));}";
 GLuint vs=shader(GL_VERTEX_SHADER,vertex),fs=shader(GL_FRAGMENT_SHADER,fragment),p=glCreateProgram();glAttachShader(p,vs);glAttachShader(p,fs);glLinkProgram(p);GLint ok=0;glGetProgramiv(p,GL_LINK_STATUS,&ok);assert(ok);glUseProgram(p);GLuint vao=0;glGenVertexArrays(1,&vao);glBindVertexArray(vao);
 GLuint tex[2],sam[3];glGenTextures(2,tex);glGenSamplers(3,sam);std::vector<float> raw(8*8*4),blue(8*8*4);
 for(int y=0;y<8;y++)for(int x=0;x<8;x++){int i=(y*8+x)*4;raw[i]=y<4?.75:.125;raw[i+1]=y<4?.125:.75;raw[i+2]=x%2?.75:.25;raw[i+3]=1;blue[i+2]=1;blue[i+3]=1;}
 for(int i=0;i<2;i++){glActiveTexture(GL_TEXTURE0+i);glBindTexture(GL_TEXTURE_2D,tex[i]);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA32F,8,8,0,GL_RGBA,GL_FLOAT,(i?blue:raw).data());}
 for(GLuint id:sam){glSamplerParameteri(id,GL_TEXTURE_MIN_FILTER,GL_LINEAR);glSamplerParameteri(id,GL_TEXTURE_MAG_FILTER,GL_LINEAR);glSamplerParameteri(id,GL_TEXTURE_WRAP_S,GL_REPEAT);glSamplerParameteri(id,GL_TEXTURE_WRAP_T,GL_REPEAT);}
 glBindSampler(0,sam[0]);glBindSampler(1,sam[1]);glUniform1i(glGetUniformLocation(p,"sampler_fw_main"),0);glUniform1i(glGetUniformLocation(p,"sampler_main"),1);
 auto draw=[&](int flip,int choice){glUniform1i(glGetUniformLocation(p,"projectm_point_main_flip"),flip);glUniform1i(glGetUniformLocation(p,"choice"),choice);glViewport(0,0,16,16);glDrawArrays(GL_TRIANGLES,0,3);std::vector<float> out(16*16*4);glReadPixels(0,0,16,16,GL_RGBA,GL_FLOAT,out.data());return out;};
 auto bottom=[](const std::vector<float>& v,int chan){return v[(3*16+5)*4+chan];};
 auto a=draw(0,0),b=draw(1,0),filtered=draw(0,1),repeat=draw(0,2);
 assert(bottom(a,0)>.70&&bottom(a,1)<.15);assert(bottom(b,0)<.15&&bottom(b,1)>.70);assert(bottom(filtered,0)==0&&bottom(filtered,2)==1);assert(a==repeat);
 glActiveTexture(GL_TEXTURE0);glBindTexture(GL_TEXTURE_2D,tex[1]);glBindSampler(0,sam[2]);auto broken=draw(1,0);assert(bottom(broken,0)==0&&bottom(broken,2)==1);
 GLint texture=0,sampler=0,min=0,mag=0,wrapS=0,wrapT=0;glGetIntegerv(GL_TEXTURE_BINDING_2D,&texture);glGetIntegerv(GL_SAMPLER_BINDING,&sampler);assert(texture==GLint(tex[1])&&sampler==GLint(sam[2]));
 glBindTexture(GL_TEXTURE_2D,tex[0]);glBindSampler(0,sam[0]);auto fixed=draw(1,0);assert(fixed==b);
 glGetSamplerParameteriv(sam[0],GL_TEXTURE_MIN_FILTER,&min);glGetSamplerParameteriv(sam[0],GL_TEXTURE_MAG_FILTER,&mag);glGetSamplerParameteriv(sam[0],GL_TEXTURE_WRAP_S,&wrapS);glGetSamplerParameteriv(sam[0],GL_TEXTURE_WRAP_T,&wrapT);assert(min==GL_LINEAR&&mag==GL_LINEAR&&wrapS==GL_REPEAT&&wrapT==GL_REPEAT);assert(glGetError()==GL_NO_ERROR);
 std::cout<<"{\"shader_compile_success\":true,\"distinct_sources_verified\":true,\"raw_checker_orientation_verified\":true,\"repeat_wrap_verified\":true,\"unit0_texture_and_sampler_overwrite_reproduced\":true,\"descriptor_restoration_verified\":true,\"min_filter\":"<<min<<",\"mag_filter\":"<<mag<<",\"wrap_s\":"<<wrapS<<",\"wrap_t\":"<<wrapT<<"}\n";
 }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;} }
