#version 330 core               // shader używa OpenGL w wersji 3.3

layout (location = 0) in vec3 in_position;  // pozycja wierzchołka w świecie
layout (location = 1) in int in_tex_id;     // numer tekstury
layout (location = 2) in int face_id;       // numer ściany voxela (front/back/top/bottom/right/left)
layout (location = 3) in int ao_id;
layout (location = 4) in int flip_id;

uniform mat4 m_proj, m_view;        // macierz projekcji oraz macierz kamery

flat out int tex_id;                // id warstwy tekstury
out vec2 uv;                        // współrzędne tekstury
out float shading;

const float ao_values[4] = float[4](0.3, 0.4, 0.6, 1.0);

//const float ao_values[4] = float[4](0.7, 0.8, 0.9, 1.0);

const float face_shading[6] = float[6](
    1.0, 0.95,   // flats
    0.9, 0.85,  // front back
    0.85, 0.8   // left right
);

// stałe UV - 4 narożniki kwadratu tekstury
const vec2 uv_coords[4] = vec2[4](
    vec2(0, 0), vec2(0, 1),
    vec2(1, 0), vec2(1, 1)
);

// kolejność UV dla dwóch typów ścian - bez tego jedna strona voxela byłaby "do góry nogami"
const int uv_indices[24] = int[24](
    1, 0, 2, 1, 2, 3,  // tex coords indices for vertices of an even face
    3, 0, 2, 3, 1, 0,   // odd face
    3,1,0,3,0,2,        //even flipped face
    1,2,3,1,0,2         // odd flipped face
);

void main() {
    tex_id = in_tex_id;

    // gl_VertexID % 6 - zwraca numer wierzchołka wewnątrz ściany
    // (face_id & 1) - sprawdza parzystość face_id
    // jeżeli face jest nieparzysty użyj drugiej połowy tabeli UV (inne obrócenie)
    // UV dla face parzystych - indeksy 0..5
    // UV dla face nieparzystych - indeksy 6..11

    int uv_index = gl_VertexID % 6  + ((face_id & 1) + flip_id * 2 ) * 6;
    uv = uv_coords[uv_indices[uv_index]];

    // shading = face_shading[face_id];
    shading = face_shading[face_id] * ao_values[ao_id];

    // transformacja pozycji
    gl_Position = m_proj * m_view * vec4(in_position, 1.0);
}
