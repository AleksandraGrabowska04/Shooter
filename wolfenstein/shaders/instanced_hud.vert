#version 330 core

layout (location = 0) in vec4 in_position;  // per vertex
layout (location = 1) in vec2 in_uv;        // per vertex

// mat4 = 4 x vec4, per instance
layout (location = 2) in vec4 m_model_0;
layout (location = 3) in vec4 m_model_1;
layout (location = 4) in vec4 m_model_2;
layout (location = 5) in vec4 m_model_3;

layout (location = 6) in int in_tex_id;      // per instance

out vec2 uv;
flat out int tex_id;


void main() {
    uv = in_uv;
    tex_id = in_tex_id;

    mat4 m_model = mat4(
        m_model_0,
        m_model_1,
        m_model_2,
        m_model_3
    );

    gl_Position = m_model * in_position;
}