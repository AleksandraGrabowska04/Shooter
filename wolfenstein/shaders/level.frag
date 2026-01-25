#version 330 core       // shader używa OpenGL w wersji 3.3

out vec4 frag_color;    // wyjściowy kolor piksela (fragmentu)

in vec2 uv;             // współrzędne tekstury, pochodzą z vertex shadera
in float shading;
flat in int tex_id;     // numer tekstury z tablicy tekstur

uniform sampler2DArray u_texture_array_0;       // tablica tekstur

void main() {
    // pobierz piksel z tekstury o numerze tex_id, w miejscu uv
    // .rgb powoduje pobranie koloru bez kanału alfa
    vec3 tex_col = texture(u_texture_array_0, vec3(uv, tex_id)).rgb;
    // kanał alfa ustawia na 1.0 (całkowicie nieprzezroczysty).
//    tex_col = vec3(0.5,0.5,0.5);
    tex_col *= shading;

    //fog
    float fog_dist = gl_FragCoord.z / gl_FragCoord.w;
    tex_col = mix(tex_col, vec3(0.05), (1.0 - exp2(-0.015 * fog_dist * fog_dist)));

    frag_color = vec4(tex_col, 1.0);
//    frag_color = vec4(0.5,0.5,0.5,1.0);
}