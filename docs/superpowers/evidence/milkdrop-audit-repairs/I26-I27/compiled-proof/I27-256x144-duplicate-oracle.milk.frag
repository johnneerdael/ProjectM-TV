#version 330
vec2 matrix_row0(mat2 m, int i) { return vec2( m[0][i], m[1][i] ); }
vec2 matrix_row0(mat2 m, float i_float) { int i=int(i_float); return vec2( m[0][i], m[1][i] ); }
vec2 matrix_row0(mat2x3 m, int i) { return vec2( m[0][i], m[1][i]); }
vec2 matrix_row0(mat2x3 m, float i_float) { int i=int(i_float); return vec2( m[0][i], m[1][i]); }
vec2 matrix_row0(mat2x4 m, int i) { return vec2( m[0][i], m[1][i]); }
vec2 matrix_row0(mat2x4 m, float i_float) { int i=int(i_float); return vec2( m[0][i], m[1][i]); }
vec3 matrix_row0(mat3 m, int i) { return vec3( m[0][i], m[1][i], m[2][i] ); }
vec3 matrix_row0(mat3 m, float i_float) { int i=int(i_float); return vec3( m[0][i], m[1][i], m[2][i] ); }
vec3 matrix_row0(mat3x2 m, int i) { return vec3( m[0][i], m[1][i], m[2][i] ); }
vec3 matrix_row0(mat3x2 m, float i_float) { int i=int(i_float); return vec3( m[0][i], m[1][i], m[2][i] ); }
vec3 matrix_row0(mat3x4 m, int i) { return vec3( m[0][i], m[1][i], m[2][i] ); }
vec3 matrix_row0(mat3x4 m, float i_float) { int i=int(i_float); return vec3( m[0][i], m[1][i], m[2][i] ); }
vec4 matrix_row0(mat4 m, int i) { return vec4( m[0][i], m[1][i], m[2][i], m[3][i] ); }
vec4 matrix_row0(mat4 m, float i_float) { int i=int(i_float); return vec4( m[0][i], m[1][i], m[2][i], m[3][i] ); }
vec4 matrix_row0(mat4x3 m, int i) { return vec4( m[0][i], m[1][i], m[2][i], m[3][i] ); }
vec4 matrix_row0(mat4x3 m, float i_float) { int i=int(i_float); return vec4( m[0][i], m[1][i], m[2][i], m[3][i] ); }
vec4 matrix_row0(mat4x2 m, int i) { return vec4( m[0][i], m[1][i], m[2][i], m[3][i] ); }
vec4 matrix_row0(mat4x2 m, float i_float) { int i=int(i_float); return vec4( m[0][i], m[1][i], m[2][i], m[3][i] ); }
float mult0(int i_x, int i_y) { float x=float(i_x); float y=float(i_y); if (x == 0.0 || y == 0.0) { return 0.0; } else { return (x * y); } }
float mult0(int i_x, float y) { float x=float(i_x); if (x == 0.0 || y == 0.0) { return 0.0; } else { return (x * y); } }
float mult0(float x, int i_y) { float y=float(i_y); if (x == 0.0 || y == 0.0) { return 0.0; } else { return (x * y); } }
float mult0(float x, float y) { if (x == 0.0 || y == 0.0) { return 0.0; } else { return (x * y); } }
vec2 mult0(vec2 x, vec2 y) { return vec2(mult0(x.x, y.x), mult0(x.y, y.y)); }
vec3 mult0(vec3 x, vec3 y) { return vec3(mult0(x.x, y.x), mult0(x.y, y.y), mult0(x.z, y.z)); }
vec4 mult0(vec4 x, vec4 y) { return vec4(mult0(x.x, y.x), mult0(x.y, y.y), mult0(x.z, y.z), mult0(x.w, y.w)); }
mat2 mult0(mat2 x, mat2 y) { return x * y; }
mat3 mult0(mat3 x, mat3 y) { return x * y; }
mat4 mult0(mat4 x, mat4 y) { return x * y; }
vec2  m_scalar_swizzle20(float x) { return  vec2(x, x); }
ivec2 m_scalar_swizzle20(int   x) { return ivec2(x, x); }
vec3  m_scalar_swizzle30(float x) { return  vec3(x, x, x); }
ivec3 m_scalar_swizzle30(int   x) { return ivec3(x, x, x); }
vec4  m_scalar_swizzle40(float x) { return  vec4(x, x, x, x); }
ivec4 m_scalar_swizzle40(int   x) { return ivec4(x, x, x, x); }
uvec2 m_scalar_swizzle20(uint  x) { return uvec2(x, x); }
uvec3 m_scalar_swizzle30(uint  x) { return uvec3(x, x, x); }
uvec4 m_scalar_swizzle40(uint  x) { return uvec4(x, x, x, x); }
vec2 bvecTernary0(bvec2 cond, vec2 trueExpr, vec2 falseExpr) { vec2 ret; ret.x = cond.x ? trueExpr.x : falseExpr.x; ret.y = cond.y ? trueExpr.y : falseExpr.y; return ret; }
vec3 bvecTernary0(bvec3 cond, vec3 trueExpr, vec3 falseExpr) { vec3 ret; ret.x = cond.x ? trueExpr.x : falseExpr.x; ret.y = cond.y ? trueExpr.y : falseExpr.y; ret.z = cond.z ? trueExpr.z : falseExpr.z; return ret; }
vec4 bvecTernary0(bvec4 cond, vec4 trueExpr, vec4 falseExpr) { vec4 ret; ret.x = cond.x ? trueExpr.x : falseExpr.x; ret.y = cond.y ? trueExpr.y : falseExpr.y; ret.z = cond.z ? trueExpr.z : falseExpr.z; ret.w = cond.w ? trueExpr.w : falseExpr.w; return ret; }
in vec4 frag_COLOR;
in vec2 frag_TEXCOORD0;
in vec2 frag_TEXCOORD1;
out vec4 rast_FragData[1];
uniform sampler2D sampler_main;
uniform vec4 texsize_main;
uniform vec4 rand_frame;
uniform vec4 rand_preset;
uniform vec4 _c0;
uniform vec4 _c1, _c2, _c3, _c4;
uniform vec4 _c5;
uniform vec4 _c6;
uniform vec4 _c7;
uniform vec4 _c8;
uniform vec4 _c9;
uniform vec4 _c10;
uniform vec4 _c11;
uniform vec4 _c12;
uniform vec4 _c13;
uniform vec4 _qa;
uniform vec4 _qb;
uniform vec4 _qc;
uniform vec4 _qd;
uniform vec4 _qe;
uniform vec4 _qf;
uniform vec4 _qg;
uniform vec4 _qh;
uniform mat3x4 rot_s1;
uniform mat3x4 rot_s2;
uniform mat3x4 rot_s3;
uniform mat3x4 rot_s4;
uniform mat3x4 rot_d1;
uniform mat3x4 rot_d2;
uniform mat3x4 rot_d3;
uniform mat3x4 rot_d4;
uniform mat3x4 rot_f1;
uniform mat3x4 rot_f2;
uniform mat3x4 rot_f3;
uniform mat3x4 rot_f4;
uniform mat3x4 rot_vf1;
uniform mat3x4 rot_vf2;
uniform mat3x4 rot_vf3;
uniform mat3x4 rot_vf4;
uniform mat3x4 rot_uf1;
uniform mat3x4 rot_uf2;
uniform mat3x4 rot_uf3;
uniform mat3x4 rot_uf4;
uniform mat3x4 rot_rand1;
uniform mat3x4 rot_rand2;
uniform mat3x4 rot_rand3;
uniform mat3x4 rot_rand4;
void PS(vec4 _vDiffuse, vec2 _uv, vec2 _rad_ang, out vec4 _return_value) {
    vec3 ret = vec3( 0 );
    (ret = (vec3(8, 8, 8) / vec3 (16)));
    (_return_value = vec4((ret).xyz, float(1.0)));
}
void main() {
    vec4 _vDiffuse;
    _vDiffuse = frag_COLOR;
    vec2 _uv;
    _uv = frag_TEXCOORD0;
    vec2 _rad_ang;
    _rad_ang = frag_TEXCOORD1;
    vec4 _return_value;
    PS(_vDiffuse, _uv, _rad_ang, _return_value);
    rast_FragData[0] = _return_value;
}
