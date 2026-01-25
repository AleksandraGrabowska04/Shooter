
#version 330 core                                       // GLSL pod OpenGL 3.3

// vertex attributes
layout (location = 0) in vec3 in_position;              // vertex position in model (local) space
layout (location = 1) in vec3 in_color;                 // vertex color

// uniform - same value for each vertex in the draw call
uniform mat4 m_proj;            // map 3D into clip space (projection/perspective)
uniform mat4 m_view;            // move the world relative to the camera
uniform mat4 m_model;           // place the object in the world

out vec3 color;                 // variable passed to fragment shader

void main() {
    // just pass the color
    color = in_color;
    // apply model, view and projection transforms, use w = 1.0 to interpret vec as a point not direction
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}
