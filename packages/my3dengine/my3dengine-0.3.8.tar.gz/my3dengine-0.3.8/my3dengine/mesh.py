from OpenGL.GL import *
import numpy as np
from .shader import basic_shader
from PIL import Image
import ctypes

class Mesh:
    def __init__(self, vertices, shader):
        self.shader = shader
        self.vertex_count = len(vertices) // 8  # 3 pos + 3 col + 2 uv
        self.position = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.scale = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        self.texture = None

        self.uv_tiling = np.array([1.0, 1.0], dtype=np.float32)
        self.uv_offset = np.array([0.0, 0.0], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        data = np.array(vertices, dtype=np.float32)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(24))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def set_uv_transform(self, tiling=(1.0, 1.0), offset=(0.0, 0.0)):
        self.uv_tiling = np.array(tiling, dtype=np.float32)
        self.uv_offset = np.array(offset, dtype=np.float32)

    def draw(self):
        model = np.identity(4, dtype=np.float32)
        model[0, 0] = self.scale[0]
        model[1, 1] = self.scale[1]
        model[2, 2] = self.scale[2]
        model[:3, 3] = self.position

        glUseProgram(self.shader)
        glUniformMatrix4fv(glGetUniformLocation(self.shader, "uModel"), 1, GL_TRUE, model)
        glUniform2fv(glGetUniformLocation(self.shader, "uUVTiling"), 1, self.uv_tiling)
        glUniform2fv(glGetUniformLocation(self.shader, "uUVOffset"), 1, self.uv_offset)

        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glUniform1i(glGetUniformLocation(self.shader, "uTexture"), 0)
            glUniform1i(glGetUniformLocation(self.shader, "useTexture"), 1)
        else:
            glUniform1i(glGetUniformLocation(self.shader, "useTexture"), 0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
        glBindVertexArray(0)

    @staticmethod
    def from_obj(path, color=(1, 1, 1)):
        positions = []
        texcoords = []
        faces = []

        with open(path, "r") as f:
            for line in f:
                if line.startswith("v "):  # vertex position
                    parts = line.strip().split()
                    positions.append(tuple(map(float, parts[1:4])))
                elif line.startswith("vt "):  # texture coordinate
                    parts = line.strip().split()
                    texcoords.append(tuple(map(float, parts[1:3])))
                elif line.startswith("f "):  # face
                    parts = line.strip().split()[1:]
                    face = []
                    for p in parts:
                        vals = p.split('/')
                        vi = int(vals[0]) - 1
                        ti = int(vals[1]) - 1 if len(vals) > 1 and vals[1] else 0
                        face.append((vi, ti))
                    faces.append(face)

        verts = []
        for face in faces:
            if len(face) >= 3:
                for i in range(1, len(face) - 1):
                    for idx in [0, i, i + 1]:
                        vi, ti = face[idx]
                        pos = positions[vi]
                        uv = texcoords[ti] if texcoords else (0.0, 0.0)
                        verts.extend([*pos, *color, *uv])

        return Mesh(verts, basic_shader())

    def set_texture(self, path):
        image = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert('RGBA')
        img_data = np.array(image, dtype=np.uint8)

        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    def set_uniforms(self, shader_program):
        model = np.identity(4, dtype=np.float32)
        model[0, 0] = self.scale[0]
        model[1, 1] = self.scale[1]
        model[2, 2] = self.scale[2]
        model[:3, 3] = self.position

        loc_model = glGetUniformLocation(shader_program, "uModel")
        if loc_model != -1:
            glUniformMatrix4fv(loc_model, 1, GL_TRUE, model)

    def set_position(self, x, y, z):
        self.position = np.array([x, y, z], dtype=np.float32)

    def set_scale(self, x, y, z):
        self.scale = np.array([x, y, z], dtype=np.float32)

    def scale_uniform(self, factor):
        self.scale = np.array([factor, factor, factor], dtype=np.float32)

    @staticmethod
    def cube(color=(1, 1, 1)):
        # Pozycje wierzchołków sześcianu
        p = [(-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),  # front
             (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5)]  # back

        # UV mapowanie na jedną ścianę (powtarzane dla każdej)
        uv = [(0, 0), (1, 0), (1, 1), (0, 1)]

        # Indeksy do rysowania ścian (każda ściana: 2 trójkąty)
        faces = [
            (0, 1, 2, 3),  # front
            (5, 4, 7, 6),  # back
            (4, 0, 3, 7),  # left
            (1, 5, 6, 2),  # right
            (3, 2, 6, 7),  # top
            (4, 5, 1, 0)  # bottom
        ]

        verts = []
        for face in faces:
            idx = [face[0], face[1], face[2], face[0], face[2], face[3]]
            uv_idx = [0, 1, 2, 0, 2, 3]
            for i in range(6):
                pos = p[idx[i]]
                tex = uv[uv_idx[i]]
                verts.extend([*pos, *color, *tex])

        return Mesh(verts, basic_shader())

    @staticmethod
    def sphere(radius=0.5, lat_segments=16, lon_segments=16, color=(1, 1, 1)):
        verts = []
        for i in range(lat_segments):
            theta1 = np.pi * (i / lat_segments - 0.5)
            theta2 = np.pi * ((i + 1) / lat_segments - 0.5)
            for j in range(lon_segments):
                phi1 = 2 * np.pi * (j / lon_segments)
                phi2 = 2 * np.pi * ((j + 1) / lon_segments)

                def get_pos(theta, phi):
                    return (
                        radius * np.cos(theta) * np.cos(phi),
                        radius * np.sin(theta),
                        radius * np.cos(theta) * np.sin(phi)
                    )

                # Wierzchołki
                p1 = get_pos(theta1, phi1)
                p2 = get_pos(theta2, phi1)
                p3 = get_pos(theta2, phi2)
                p4 = get_pos(theta1, phi2)

                # UV mapping (prosty sferyczny)
                uv1 = (j / lon_segments, i / lat_segments)
                uv2 = (j / lon_segments, (i + 1) / lat_segments)
                uv3 = ((j + 1) / lon_segments, (i + 1) / lat_segments)
                uv4 = ((j + 1) / lon_segments, i / lat_segments)

                # Trójkąty
                for vtx, uv in zip([p1, p2, p3], [uv1, uv2, uv3]):
                    verts.extend([*vtx, *color, *uv])
                for vtx, uv in zip([p1, p3, p4], [uv1, uv3, uv4]):
                    verts.extend([*vtx, *color, *uv])
        return Mesh(verts, basic_shader())

    @staticmethod
    def capsule(radius=0.25, height=1.0, segments=16, color=(1, 1, 1)):
        verts = []
        half = height / 2

        # === Cylinder środkowy ===
        for j in range(segments):
            theta1 = 2 * np.pi * (j / segments)
            theta2 = 2 * np.pi * ((j + 1) / segments)

            x1, z1 = np.cos(theta1), np.sin(theta1)
            x2, z2 = np.cos(theta2), np.sin(theta2)

            p1 = (radius * x1, -half, radius * z1)
            p2 = (radius * x1, half, radius * z1)
            p3 = (radius * x2, half, radius * z2)
            p4 = (radius * x2, -half, radius * z2)

            uv = [(j / segments, 0.0), (j / segments, 0.5), ((j + 1) / segments, 0.5), ((j + 1) / segments, 0.0)]
            for vtx, tex in zip([p1, p2, p3], [uv[0], uv[1], uv[2]]):
                verts.extend([*vtx, *color, *tex])
            for vtx, tex in zip([p1, p3, p4], [uv[0], uv[2], uv[3]]):
                verts.extend([*vtx, *color, *tex])

        # === Półsfera górna ===
        for i in range(segments // 2):
            theta1 = (np.pi / 2) * (i / (segments // 2))
            theta2 = (np.pi / 2) * ((i + 1) / (segments // 2))
            for j in range(segments):
                phi1 = 2 * np.pi * (j / segments)
                phi2 = 2 * np.pi * ((j + 1) / segments)

                def pos(theta, phi):
                    return (
                        radius * np.cos(theta) * np.cos(phi),
                        radius * np.sin(theta) + half,
                        radius * np.cos(theta) * np.sin(phi)
                    )

                p1 = pos(theta1, phi1)
                p2 = pos(theta2, phi1)
                p3 = pos(theta2, phi2)
                p4 = pos(theta1, phi2)

                uv1 = (j / segments, 0.5 + (i / (segments * 2)))
                uv2 = (j / segments, 0.5 + ((i + 1) / (segments * 2)))
                uv3 = ((j + 1) / segments, 0.5 + ((i + 1) / (segments * 2)))
                uv4 = ((j + 1) / segments, 0.5 + (i / (segments * 2)))

                for vtx, tex in zip([p1, p2, p3], [uv1, uv2, uv3]):
                    verts.extend([*vtx, *color, *tex])
                for vtx, tex in zip([p1, p3, p4], [uv1, uv3, uv4]):
                    verts.extend([*vtx, *color, *tex])

        # === Półsfera dolna ===
        for i in range(segments // 2):
            theta1 = (np.pi / 2) * (i / (segments // 2))
            theta2 = (np.pi / 2) * ((i + 1) / (segments // 2))
            for j in range(segments):
                phi1 = 2 * np.pi * (j / segments)
                phi2 = 2 * np.pi * ((j + 1) / segments)

                def pos(theta, phi):
                    return (
                        radius * np.cos(theta) * np.cos(phi),
                        -radius * np.sin(theta) - half,
                        radius * np.cos(theta) * np.sin(phi)
                    )

                p1 = pos(theta1, phi1)
                p2 = pos(theta2, phi1)
                p3 = pos(theta2, phi2)
                p4 = pos(theta1, phi2)

                uv1 = (j / segments, 0.5 - (i / (segments * 2)))
                uv2 = (j / segments, 0.5 - ((i + 1) / (segments * 2)))
                uv3 = ((j + 1) / segments, 0.5 - ((i + 1) / (segments * 2)))
                uv4 = ((j + 1) / segments, 0.5 - (i / (segments * 2)))

                # UWAGA: zamieniona kolejność rysowania — PRAWIDŁOWY winding
                for vtx, tex in zip([p1, p3, p2], [uv1, uv3, uv2]):
                    verts.extend([*vtx, *color, *tex])
                for vtx, tex in zip([p1, p4, p3], [uv1, uv4, uv3]):
                    verts.extend([*vtx, *color, *tex])

        return Mesh(verts, basic_shader())

    @staticmethod
    def plane(size=1.0, color=(1, 1, 1)):
        hs = size / 2
        positions = [(-hs, 0, -hs), (hs, 0, -hs), (hs, 0, hs), (-hs, 0, hs)]
        uvs = [(0, 0), (1, 0), (1, 1), (0, 1)]
        indices = [(0, 1, 2), (0, 2, 3)]  # front
        back_indices = [(2, 1, 0), (3, 2, 0)]  # back side (odwrócone)

        verts = []
        for face in indices + back_indices:
            for idx in face:
                verts.extend([*positions[idx], *color, *uvs[idx]])
        return Mesh(verts, basic_shader())