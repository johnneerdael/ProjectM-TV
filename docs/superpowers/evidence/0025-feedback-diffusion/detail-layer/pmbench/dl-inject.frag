#version 300 es
precision highp float;
precision highp int;
uniform sampler2D Lw; uniform sampler2D Hp; uniform sampler2D Hc; uniform int S; layout(location = 0) out vec4 o; layout(location = 1) out vec4 o2;
void main() { ivec2 c = ivec2(gl_FragCoord.xy); ivec2 p = c * S + ivec2(S / 2);
  o = texelFetch(Lw, c, 0) + texelFetch(Hp, p, 0) - texelFetch(Hc, p, 0); o2 = o; }
