
uniform bool projectm_point_main_flip;
highp vec4 projectm_point_main(lowp sampler2D source, highp vec2 uv) {
    if (projectm_point_main_flip) uv.y = 1.0 - uv.y;
    return texture(source, uv);
}
highp vec4 projectm_point_main(lowp sampler2D source, highp vec2 uv, highp float bias) {
    if (projectm_point_main_flip) uv.y = 1.0 - uv.y;
    return texture(source, uv, bias);
}
