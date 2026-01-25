#version 330 core

layout (location = 0) out vec4 fragColor;

// for each fragment, color is interpolated across the triangle from the three vertex colors provided earlier
in vec3 color;

void main() {
    // add an alpha value of 1.0 to the interpolated RGB color and write it to the framebuffer
    fragColor = vec4(color, 1.0);
}


