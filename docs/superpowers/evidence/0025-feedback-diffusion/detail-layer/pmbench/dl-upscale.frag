#version 300 es
precision highp float;
precision highp int;
uniform sampler2D Lw; uniform sampler2D Hw; layout(location = 0) out vec4 o; layout(location = 1) out vec4 o2;
void main() { o = texture(Lw, gl_FragCoord.xy / vec2(textureSize(Hw, 0))); o2 = o; }
