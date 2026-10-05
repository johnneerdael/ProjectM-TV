#version 300 es
precision highp float;
precision highp int;
uniform sampler2D Lw; uniform sampler2D Hw; uniform sampler2D D; uniform float alpha; layout(location = 0) out vec4 o; layout(location = 1) out vec4 o2;
void main() { vec2 uv = gl_FragCoord.xy / vec2(textureSize(Hw, 0)); vec4 h = texelFetch(Hw, ivec2(gl_FragCoord.xy), 0);
  o = texture(Lw, uv) + alpha * (h - texture(D, uv)); o2 = o; }
