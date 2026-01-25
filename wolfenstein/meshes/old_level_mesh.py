import numpy
from meshes.base_mesh import BaseMesh
from meshes.old_level_mesh_builder import LevelMeshBuilder

# A VBO (Vertex Buffer Object) is the raw storage.
# It’s just a chunk of GPU memory that holds vertex data: positions, normals, colors, texture coordinates,
# whatever numbers you want to feed the vertex shader. A VBO does not describe what those numbers mean.
# It’s a box full of floats.

# A VAO (Vertex Array Object) is the instruction manual.
# It remembers how to interpret the data in VBOs: which VBO to read from, how many components per attribute,
# the stride, offsets, and which vertex attribute index in the shader gets which data

class LevelMesh():
    def __init__(self, eng):
        self.eng = eng              # engine
        self.ctx = eng.ctx          # kontekst ModernGL (API do GPU)
        self.program = eng.shader_program.level

        # format danych jednego wierzchołka
        # 3u2 oznacza: 3 komponenty unsigned short (2 bajty)
        self.vbo_format = '3u2 1u2 1u2 1u2 1u2'
        self.fmt_size = sum(int(fmt[:1]) for fmt in self.vbo_format.split())

        # nazwy atrybutów - muszą pasować do nazw w shaderze
        self.vbo_attrs = ('in_position', 'in_tex_id', 'face_id', 'ao_id', 'flip_id')
        # (x,y,z), id tekstury, która ściana, ambient oclusion, obrót UV

        # mesh builder generuje wszystkie dane wierzchołków
        self.mesh_builder = LevelMeshBuilder(self)
        self.vao = self.get_vao()


    def get_vao(self):
        vertex_data = self.get_vertex_data()    # dane generowane przez MeshBuilder
        vbo = self.ctx.buffer(vertex_data)      # wysłanie danych na kartę graficzną
        vao = self.ctx.vertex_array(            # VAO - przepis na rysowanie danych
            self.program,                       # here is only usage of the shader program
            [
                (vbo, self.vbo_format, *self.vbo_attrs)
            ],
            skip_errors=True
        )
        return vao

    def render(self):
        # to jedno polecenie powoduje w GPU
        # glUseProgram(program)
        # glBindVertexArray(vao)
        # glDrawArrays or glDrawElements
        self.vao.render()

    def get_vertex_data(self):
        vertex_data = self.mesh_builder.build_mesh()
        # print('Num level vertices: ', len(vertex_data) // 7 * 3)
        return vertex_data
