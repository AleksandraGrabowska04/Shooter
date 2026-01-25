#version 330 core

out vec4 frag_color;
in vec2 uv;                                     // arrives interpolated from the vertex shader

// sampler2DArray - stack of 2D textures – all the same width, height, and format, indexed by an integer layer
uniform sampler2DArray u_texture_array_0;
// This tells the shader which layer to sample
uniform int tex_id;

void main() {
    frag_color = texture(u_texture_array_0, vec3(uv, tex_id));
}