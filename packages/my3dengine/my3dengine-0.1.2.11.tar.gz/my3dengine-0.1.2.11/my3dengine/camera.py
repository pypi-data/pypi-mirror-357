# my3dengine/camera.py
import numpy as np

def normalize(v):
    return v / np.linalg.norm(v)

def look_at(eye, center, up):
    f = normalize(center - eye)
    s = normalize(np.cross(f, up))
    u = np.cross(s, f)

    mat = np.identity(4, dtype=np.float32)
    mat[0, :3] = s
    mat[1, :3] = u
    mat[2, :3] = -f
    mat[:3, 3] = -np.dot(mat[:3, :3], eye)
    return mat

def perspective(fov, aspect, near, far):
    f = 1.0 / np.tan(np.radians(fov) / 2)
    mat = np.zeros((4, 4), dtype=np.float32)
    mat[0, 0] = f / aspect
    mat[1, 1] = f
    mat[2, 2] = (far + near) / (near - far)
    mat[2, 3] = (2 * far * near) / (near - far)
    mat[3, 2] = -1
    return mat

class Camera:
    def __init__(self, position, target, up, fov, aspect, near=0.1, far=100.0):
        self.position = np.array(position, dtype=np.float32)
        self.target = np.array(target, dtype=np.float32)
        self.up = np.array(up, dtype=np.float32)
        self.fov = fov
        self.aspect = aspect
        self.near = near
        self.far = far

    @property
    def view_matrix(self):
        return look_at(self.position, self.target, self.up)

    @property
    def projection_matrix(self):
        return perspective(self.fov, self.aspect, self.near, self.far)

    def move(self, delta):
        self.position += delta
        self.target += delta
