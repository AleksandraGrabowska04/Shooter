from meshes.base_mesh import BaseMesh
from settings import *
import numpy as np


class TestMesh(BaseMesh):
    def __init__(self, eng, shader_program):
        super().__init__()
        self.eng = eng
        self.ctx = eng.ctx
        self.program = shader_program

        self.vbo_format = '3f 3f'
        self.vbo_attrs = ('in_position', 'in_color')
        self.vao = self.get_vao()

    def get_vao(self):
        vertex_data = self.get_vertex_data()
        vbo = self.ctx.buffer(vertex_data)
        vao = self.ctx.vertex_array(
            self.program,               # here is only usage of the shader program
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

        vertices = [
            (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0), (-0.5, -0.5, 0.0),
            (0.5, 0.5, 0.0), (-0.5, -0.5, 0.0), (0.5, -0.5, 0.0)
        ]
        colors = [
            (0, 1, 0), (1, 0, 0), (1, 1, 0),
            (0, 1, 0), (1, 1, 0), (0, 0, 1)
        ]
        vertex_data = np.hstack([vertices, colors], dtype='float32')

        return vertex_data
