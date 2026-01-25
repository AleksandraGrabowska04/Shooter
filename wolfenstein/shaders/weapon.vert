#version 330 core

// vertex attributes
layout (location = 0) in vec4 in_position;          // vertex position in model (local) space
layout (location = 1) in vec2 in_uv;                // texture coordinates

// uniform - same value for each vertex in the draw call
uniform mat4 m_model;                               // place the object in the world
                                                    // the shader is intentionally not responsible for projection

out vec2 uv;                                        // variable passed to fragment shader

void main() {
    uv = in_uv;
    gl_Position = m_model * in_position;
}