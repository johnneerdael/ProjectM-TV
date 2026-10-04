// Research-only helper compiled into isolated snapshot. Primary shader/output untouched.
#include <fstream>
#include <cstdlib>
#include <cstdio>
#include <algorithm>
#include <vector>

inline std::string AcidSidecarSource(const std::string& original) {
    std::string s=original;
    if (s.find("uv_dy") == std::string::npos) {
      if(s.find("rad_lq")==std::string::npos) return {};
      auto pos=s.find("uniform ");
      s.insert(pos,"uniform vec4 acid_diag_lattice;\n uniform int acid_diag_mode;\n");
      pos=s.find("vec3 ret =");
      s.insert(pos,"_uv=(floor(_uv*acid_diag_lattice.xy)+vec2(.5))/acid_diag_lattice.xy;\n");
      pos=s.find("_return_value =");pos=s.find(';',pos)+1;
      s.insert(pos,R"(
        vec3 acid_P=texture(sampler_pc_main,_uv).xyz;
        vec3 acid_B1=texture(sampler_blur1,_uv).xyz*_c5.x+vec3(_c5.y);
        vec3 acid_B3=texture(sampler_blur3,_uv).xyz*_c6.x+vec3(_c6.y);
        vec3 acid_D=acid_P-acid_B3;
        vec3 acid_product=clamp(acid_B1,0.0,1.0)*acid_D;
        vec3 acid_lum=vec3(.2126,.7152,.0722);
        if(acid_diag_mode==8) _return_value=vec4(acid_P,dot(acid_B1,acid_lum));
        if(acid_diag_mode==9) _return_value=vec4(acid_D,dot(acid_product,acid_lum));
        if(acid_diag_mode==10) _return_value=vec4(ret,dot(abs(acid_product),acid_lum));
        if(acid_diag_mode==11) _return_value=vec4(acid_B3,dot(abs(acid_D),acid_lum));
        if(acid_diag_mode==12) _return_value=vec4(acid_B1,dot(abs(acid_product),acid_lum));
      )");
      return s;
    }
    auto pos=s.find("uniform ");
    if(pos==std::string::npos) throw std::runtime_error("sidecar missing uniforms");
    s.insert(pos,"uniform vec4 acid_diag_lattice;\nuniform int acid_diag_mode;\n");
    const std::string start="vec3 ret =";
    pos=s.find(start);
    if(pos==std::string::npos) throw std::runtime_error("sidecar missing ret");
    s.insert(pos,R"(
    vec2 acid_delta=(floor(_uv.zw*acid_diag_lattice.xy)+vec2(.5))/acid_diag_lattice.xy-_uv.zw;
    _uv.xy += acid_delta.x*dFdx(_uv.xy)/dFdx(_uv.z)+acid_delta.y*dFdy(_uv.xy)/dFdy(_uv.w);
    _uv.zw += acid_delta;
)");
    const auto assignment=s.find("_return_value =");
    if(assignment==std::string::npos) throw std::runtime_error("sidecar missing return");
    const auto end=s.find(';',assignment)+1;
    s.insert(end,R"(
    vec3 acid_A=texture(sampler_main,uv_dy).xyz;
    vec3 acid_M=texture(sampler_main,_uv.xy).xyz;
    vec3 acid_B=texture(sampler_blur1,_uv.xy).xyz*_c5.x+vec3(_c5.y);
    vec3 acid_H=(acid_M-acid_B)*.1;
    float acid_C=.004*pow(acid_M.x*acid_M.y*acid_M.z,.333)/_qb.w+
      .0008*_qg.w*(sqrt(_c3.z)*acid_M.x*acid_M.y+sqrt(_c3.y)*acid_M.x*acid_M.z+sqrt(_c3.x)*acid_M.y*acid_M.z);
    vec2 acid_fr=fract(uv_dy*acid_diag_lattice.xy-vec2(.5));
    vec2 acid_fa=fract((uv_dy-_uv.zw)*acid_diag_lattice.zw);
    vec3 acid_lum=vec3(.2126,.7152,.0722);
    if(acid_diag_mode==1) _return_value=vec4(acid_fr,acid_fa);
    if(acid_diag_mode==2) _return_value=vec4(acid_A,dot(acid_M,acid_lum));
    if(acid_diag_mode==3) _return_value=vec4(acid_H,dot(acid_B,acid_lum));
    if(acid_diag_mode==4) _return_value=vec4(acid_C,dot(ret,acid_lum),dot(vec3(lessThan(ret,vec3(0))),vec3(1.0/3)),dot(vec3(greaterThan(ret,vec3(1))),vec3(1.0/3)));
    if(acid_diag_mode==5) _return_value=vec4(acid_M,dot(texture(sampler_pw_main,_uv.xy).xyz,acid_lum));
    if(acid_diag_mode==6) _return_value=vec4(ret,acid_C);
    if(acid_diag_mode==7) _return_value=vec4(acid_B,dot(texture(sampler_pc_main,_uv.zw).xyz,acid_lum));
)");
    return s;
}

inline void AcidCopyUniforms(GLuint from,GLuint to) {
    GLint n=0;glGetProgramiv(from,GL_ACTIVE_UNIFORMS,&n);
    for(GLint i=0;i<n;i++) {
        char name[256];GLsizei length=0;GLint count=0;GLenum type=0;
        glGetActiveUniform(from,i,256,&length,&count,&type,name);
        GLint a=glGetUniformLocation(from,name),b=glGetUniformLocation(to,name);
        if(a<0||b<0)continue;
        GLfloat f[256]{};GLint v[256]{};
        switch(type) {
          case GL_SAMPLER_2D:case GL_SAMPLER_3D:case GL_INT:case GL_BOOL:
            glGetUniformiv(from,a,v);glUniform1iv(b,count,v);break;
          case GL_FLOAT:glGetUniformfv(from,a,f);glUniform1fv(b,count,f);break;
          case GL_FLOAT_VEC2:glGetUniformfv(from,a,f);glUniform2fv(b,count,f);break;
          case GL_FLOAT_VEC3:glGetUniformfv(from,a,f);glUniform3fv(b,count,f);break;
          case GL_FLOAT_VEC4:glGetUniformfv(from,a,f);glUniform4fv(b,count,f);break;
          case GL_FLOAT_MAT3:glGetUniformfv(from,a,f);glUniformMatrix3fv(b,count,GL_FALSE,f);break;
          case GL_FLOAT_MAT4:glGetUniformfv(from,a,f);glUniformMatrix4fv(b,count,GL_FALSE,f);break;
          case GL_FLOAT_MAT3x4:glGetUniformfv(from,a,f);glUniformMatrix3x4fv(b,count,GL_FALSE,f);break;
          case GL_FLOAT_MAT4x3:glGetUniformfv(from,a,f);glUniformMatrix4x3fv(b,count,GL_FALSE,f);break;
          default:throw std::runtime_error("unsupported sidecar uniform type");
        }
    }
}
