import numpy as np
from OpenGL.GL import *
import ctypes
import time

class WaterMesh:
    def __init__(self, size=10.0, resolution=100):
        self.size = size
        self.resolution = resolution
        self.vertices = self.generate_vertices()
        self.vertex_count = len(self.vertices) // 8

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_DYNAMIC_DRAW)

        stride = 8 * 4
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))   # pos
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))  # color
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))  # uv
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        self.start_time = time.time()

    def generate_vertices(self):
        step = self.size / self.resolution
        verts = []

        for z in range(self.resolution):
            for x in range(self.resolution):
                # cztery rogi jednego kwadratu
                x0 = x * step - self.size / 2
                x1 = (x + 1) * step - self.size / 2
                z0 = z * step - self.size / 2
                z1 = (z + 1) * step - self.size / 2

                uv0 = (x / self.resolution, z / self.resolution)
                uv1 = ((x + 1) / self.resolution, z / self.resolution)
                uv2 = ((x + 1) / self.resolution, (z + 1) / self.resolution)
                uv3 = (x / self.resolution, (z + 1) / self.resolution)

                color = (0.2, 0.4, 1.0)

                # dwa trójkąty
                verts += [x0, 0, z0, *color, *uv0]
                verts += [x1, 0, z0, *color, *uv1]
                verts += [x1, 0, z1, *color, *uv2]

                verts += [x0, 0, z0, *color, *uv0]
                verts += [x1, 0, z1, *color, *uv2]
                verts += [x0, 0, z1, *color, *uv3]

        return np.array(verts, dtype=np.float32)

    def update(self):
        time_now = time.time() - self.start_time
        verts = self.vertices

        for i in range(0, len(verts), 8):
            x = verts[i]
            z = verts[i + 2]
            verts[i + 1] = np.sin(x * 0.5 + time_now) * 0.2 + np.cos(z * 0.5 + time_now) * 0.2

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, verts.nbytes, verts)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw(self, shader):
        shader.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    def destroy(self):
        glDeleteVertexArrays(1, [self.vao])
        glDeleteBuffers(1, [self.vbo])