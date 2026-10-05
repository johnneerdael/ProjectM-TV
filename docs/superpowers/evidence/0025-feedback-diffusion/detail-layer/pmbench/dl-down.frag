#version 300 es
precision highp float;
precision highp int;
uniform sampler2D src; uniform int S; layout(location = 0) out vec4 o; layout(location = 1) out vec4 o2;
void main() { ivec2 b = ivec2(gl_FragCoord.xy) * S; vec4 acc = vec4(0.0);
  for (int j = 0; j < S; ++j) for (int i = 0; i < S; ++i) acc += texelFetch(src, b + ivec2(i, j), 0);
  o = acc / float(S * S); o2 = o; }
