#version 330 core

layout (location = 0) in vec4 in_position;
layout (location = 1) in vec2 in_uv;

layout (location = 2) in vec4 m_model_0;
layout (location = 3) in vec4 m_model_1;
layout (location = 4) in vec4 m_model_2;
layout (location = 5) in vec4 m_model_3;

layout (location = 6) in int in_tex_id;

uniform mat4 m_proj, m_view;

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

    mat4 m_model_view = m_view * m_model;

    // remove rotation, keep scale
    m_model_view[0].xyz = vec3(length(m_model[0].xyz), 0.0, 0.0);
    m_model_view[1].xyz = vec3(0.0, length(m_model[1].xyz), 0.0);
    // m_model_view[2].xyz = vec3(0.0, 0.0, length(m_model[2].xyz));

    gl_Position = m_proj * m_model_view * in_position;
}
