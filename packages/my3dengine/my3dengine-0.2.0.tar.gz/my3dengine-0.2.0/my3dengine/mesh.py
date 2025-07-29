# my3dengine/mesh.py
from OpenGL.GL import *
import numpy as np
from .shader import basic_shader
import ctypes

class Mesh:
    def __init__(self, vertices, shader):
        self.shader = shader
        self.vertex_count = len(vertices) // 6  # 3 coords + 3 color
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        data = np.array(vertices, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        # position
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # color
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self):
        glUseProgram(self.shader)

        # Ustawienie model matrix (translacja)
        model = np.identity(4, dtype=np.float32)
        model[:3, 3] = self.position
        model_loc = glGetUniformLocation(self.shader, "uModel")
        glUniformMatrix4fv(model_loc, 1, GL_TRUE, model)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    def set_position(self, x, y, z):
        self.position = np.array([x, y, z], dtype=np.float32)

    @staticmethod
    def cube(color=None):
        p = [(-0.5,-0.5, 0.5),(0.5,-0.5,0.5),(0.5,0.5,0.5),(-0.5,0.5,0.5),
             (-0.5,-0.5,-0.5),(0.5,-0.5,-0.5),(0.5,0.5,-0.5),(-0.5,0.5,-0.5)]
        faces = [(0,1,2,0,2,3),(5,4,7,5,7,6),(4,0,3,4,3,7),
                 (1,5,6,1,6,2),(3,2,6,3,6,7),(4,5,1,4,1,0)]
        verts = []
        for face in faces:
            for idx in face:
                pos = p[idx]
                col = color if color is not None else tuple((np.array(pos)+0.5).tolist())
                verts.extend([*pos, *col])
        return Mesh(verts, basic_shader())

    @staticmethod
    def sphere(radius=0.5, lat_segments=16, lon_segments=16, color=(1,1,1)):
        verts = []
        for i in range(lat_segments):
            theta1 = np.pi * (i / lat_segments - 0.5)
            theta2 = np.pi * ((i+1) / lat_segments - 0.5)
            for j in range(lon_segments):
                phi1 = 2 * np.pi * (j / lon_segments)
                phi2 = 2 * np.pi * ((j+1) / lon_segments)
                p1 = (radius * np.cos(theta1)*np.cos(phi1),
                      radius * np.sin(theta1),
                      radius * np.cos(theta1)*np.sin(phi1))
                p2 = (radius * np.cos(theta2)*np.cos(phi1),
                      radius * np.sin(theta2),
                      radius * np.cos(theta2)*np.sin(phi1))
                p3 = (radius * np.cos(theta2)*np.cos(phi2),
                      radius * np.sin(theta2),
                      radius * np.cos(theta2)*np.sin(phi2))
                p4 = (radius * np.cos(theta1)*np.cos(phi2),
                      radius * np.sin(theta1),
                      radius * np.cos(theta1)*np.sin(phi2))
                for tri in [(p1,p2,p3),(p1,p3,p4)]:
                    for v in tri:
                        verts.extend([*v, *color])
        return Mesh(verts, basic_shader())

    @staticmethod
    def capsule(radius=0.25, height=1.0, segments=16, color=(1,1,1)):
        # cylinder body
        verts = []
        half = height/2
        for j in range(segments):
            theta = 2*np.pi * (j/segments)
            next_t = 2*np.pi * ((j+1)/segments)
            p1 = (radius*np.cos(theta), -half, radius*np.sin(theta))
            p2 = (radius*np.cos(theta),  half, radius*np.sin(theta))
            p3 = (radius*np.cos(next_t), half, radius*np.sin(next_t))
            p4 = (radius*np.cos(next_t), -half, radius*np.sin(next_t))
            # two tris for quad
            for tri in [(p1,p2,p3),(p1,p3,p4)]:
                for v in tri: verts.extend([*v, *color])
        # hemispheres
        def hemi(sign):
            for i in range(segments//2):
                phi1 = np.pi*(i/(segments)-0.5)
                phi2 = np.pi*((i+1)/(segments)-0.5)
                for j in range(segments):
                    th1 = 2*np.pi*(j/segments)
                    th2 = 2*np.pi*((j+1)/segments)
                    def p(phi, th): return (radius*np.cos(phi)*np.cos(th),
                                              radius*np.sin(phi)*sign + sign*half,
                                              radius*np.cos(phi)*np.sin(th))
                    q1 = p(phi1, th1); q2 = p(phi2, th1)
                    q3 = p(phi2, th2); q4 = p(phi1, th2)
                    for tri in [(q1,q2,q3),(q1,q3,q4)]:
                        for v in tri: verts.extend([*v, *color])
        hemi(1); hemi(-1)
        return Mesh(verts, basic_shader())

    @staticmethod
    def plane(size=1.0, color=(1,1,1)):
        hs = size/2
        p = [(-hs,0,-hs),(hs,0,-hs),(hs,0,hs),(-hs,0,hs)]
        faces = [(0,1,2),(0,2,3)]
        verts=[]
        for face in faces:
            for idx in face:
                verts.extend([*p[idx], *color])
        return Mesh(verts, basic_shader())