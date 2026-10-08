#include <MilkdropPreset/PerFrameContext.hpp>
#include "gl_context.hpp"
#include <MilkdropPreset/Border.hpp>
#include <Renderer/BlendMode.hpp>
#include <Renderer/ShaderCache.hpp>
#include <array>
#include <cmath>
#include <vector>
#include <iostream>
#include <stdexcept>
using namespace libprojectM::MilkdropPreset;
using namespace libprojectM::Renderer;
static void Check(bool v,const char*m){if(!v)throw std::runtime_error(m);}
struct Image {std::vector<unsigned char> rgba;};
static Image Render(int reference,float ob,float ib,float oa,float ia,int size){
 ShaderCache cache;PresetState state;auto& rc=state.renderContext;rc.shaderCache=&cache;rc.viewportSizeX=rc.viewportSizeY=size;state.LoadShaders();
 PerFrameContext frame(state.globalMemory,&state.globalRegisters);frame.RegisterBuiltinVariables();frame.LoadStateVariables(state);
 *frame.ob_size=ob;*frame.ib_size=ib;*frame.ob_r=*frame.ob_g=*frame.ob_b=1;*frame.ob_a=oa;*frame.ib_r=*frame.ib_g=*frame.ib_b=1;*frame.ib_a=ia;
 GLuint tex{},fbo{};glGenTextures(1,&tex);glBindTexture(GL_TEXTURE_2D,tex);glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA8,size,size,0,GL_RGBA,GL_UNSIGNED_BYTE,nullptr);
 glGenFramebuffers(1,&fbo);glBindFramebuffer(GL_FRAMEBUFFER,fbo);glFramebufferTexture2D(GL_FRAMEBUFFER,GL_COLOR_ATTACHMENT0,GL_TEXTURE_2D,tex,0);Check(glCheckFramebufferStatus(GL_FRAMEBUFFER)==GL_FRAMEBUFFER_COMPLETE,"target incomplete");glViewport(0,0,size,size);glDisable(GL_DITHER);glClearColor(0,0,0,0);glClear(GL_COLOR_BUFFER_BIT);
 if(!reference){Border border(state);border.Draw(frame);}else{
  Mesh mesh(VertexBufferUsage::StreamDraw);mesh.SetRenderPrimitiveType(Mesh::PrimitiveType::Triangles);mesh.SetVertexCount(reference==2?16:8);
  mesh.Indices().Set({{4,0,1,4,1,5,6,2,0,6,0,4,7,3,2,7,2,6,5,1,3,5,3,7}});
  if(reference==2)mesh.Indices().Set({{0,1,2,0,2,3,4,5,6,4,6,7,8,9,10,8,10,11,12,13,14,12,14,15}});
  auto shader=state.untexturedShader.lock();shader->Bind();shader->SetUniformMat4x4("vertex_transformation",PresetState::orthogonalProjection);shader->SetUniformFloat("vertex_point_size",1.f);
  BlendMode::Set(true,BlendMode::Function::SourceAlpha,BlendMode::Function::OneMinusSourceAlpha);
  for(int b=0;b<2;++b){float alpha=b?ia:oa;if(alpha<=.001f)continue;float outer=b?1-ob:1,inner=b?1-ob-ib:1-ob;
   glVertexAttrib4f(1,1,1,1,alpha);mesh.Vertices().Set({{outer,outer},{outer,-outer},{-outer,outer},{-outer,-outer},{inner,inner},{inner,-inner},{-inner,inner},{-inner,-inner}});if(reference==2){std::array<Point,4> vertices={Point{inner,inner},Point{outer,outer},Point{outer,-outer},Point{inner,-inner}};auto& dest=mesh.Vertices().Get();dest.resize(16);for(int rot=0;rot<4;++rot){for(int v=0;v<4;++v){dest[rot*4+v]=vertices[v];float x=vertices[v].X(),y=vertices[v].Y(),t=1.570796327f;vertices[v]=Point{x*cosf(t)-y*sinf(t),x*sinf(t)+y*cosf(t)};}}}
   mesh.Update();mesh.Draw();
  }Mesh::Unbind();Shader::Unbind();BlendMode::SetBlendActive(false);
 }
 glBindFramebuffer(GL_READ_FRAMEBUFFER,fbo);glReadBuffer(GL_COLOR_ATTACHMENT0);Image image;image.rgba.resize(size*size*4);glReadPixels(0,0,size,size,GL_RGBA,GL_UNSIGNED_BYTE,image.rgba.data());Check(glGetError()==GL_NO_ERROR,"GL error");glDeleteFramebuffers(1,&fbo);glDeleteTextures(1,&tex);return image;
}
int main(){try{GLContext gl;int failures=0,total=0;
 for(int size:{8,32})for(float ob:{-.25f,.1f,.5f,1.f,1.5f})for(float alpha:{0.f,.0005f,.5f,1.f}){
  auto a=Render(false,ob,0,alpha,0,size),b=Render(true,ob,0,alpha,0,size);auto rot=Render(2,ob,0,alpha,0,size);Check(rot.rgba==b.rgba,"actual float-rotation fan differs from exact-quarter fan");++total;bool same=a.rgba==b.rgba;std::cout<<"outer size="<<ob<<" alpha="<<alpha<<" target="<<size<<" current00="<<int(a.rgba[0])<<" originalfan00="<<int(b.rgba[0])<<" same="<<same<<'\n';if(!same)++failures;
 }
 for(float ob:{.1f,.5f})for(float ib:{.1f,.5f,1.5f}){auto a=Render(false,ob,ib,.3f,.5f,32),b=Render(true,ob,ib,.3f,.5f,32);++total;bool same=a.rgba==b.rgba;std::cout<<"inner ob="<<ob<<" ib="<<ib<<" same="<<same<<'\n';if(!same)++failures;}
 std::cout<<"border topology cases="<<total<<" failures="<<failures<<"; exact-quarter same-alpha originalfan oracle, not original packing/D3D\n";return failures?1:0;
 }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 2;}}
