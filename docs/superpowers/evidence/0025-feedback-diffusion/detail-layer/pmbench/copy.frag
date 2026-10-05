#version 300 es
precision highp float;
in highp vec4 frag_TEXCOORD0;
uniform sampler2D source;
layout(location = 0) out vec4 raw;
layout(location = 1) out vec4 color;
void main() { raw = texelFetch(source, ivec2(gl_FragCoord.xy), 0); color = raw; }
