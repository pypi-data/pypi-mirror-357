# my3dengine/core.py
import sdl2
import sdl2.ext
from OpenGL.GL import *
import time
import numpy as np
import ctypes
from .camera import Camera

class Window:
    def __init__(
        self,
        title,
        width,
        height,
        move_speed: float = 5.0,
        mouse_sensitivity: float = 0.002,
    ):
        """
        :param move_speed: prędkość poruszania się kamery (jednostki na sekundę)
        :param mouse_sensitivity: czułość ruchu myszy (radiany na piksel)
        """
        # inicjalizacja SDL2 i OpenGL
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.window = sdl2.SDL_CreateWindow(
            title.encode("utf-8"),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            width,
            height,
            sdl2.SDL_WINDOW_OPENGL | sdl2.SDL_WINDOW_SHOWN,
        )
        self.context = sdl2.SDL_GL_CreateContext(self.window)
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, width, height)
        glClearColor(0.1, 0.1, 0.1, 1.0)

        # parametry sterowania
        self.move_speed = move_speed
        self.mouse_sensitivity = mouse_sensitivity

        # kamera
        aspect = width / float(height)
        self.camera = Camera(
            position=(0, 0, 3),
            target=(0, 0, 0),
            up=(0, 1, 0),
            fov=60,
            aspect=aspect,
            near=0.1,
            far=100.0,
        )

        # tryb myszy
        sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE)
        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)

    def set_camera_uniforms(self, shader_program):
        # ustawia macierze view i projection w shaderze (transpose=True dla numpy)
        view = self.camera.view_matrix
        proj = self.camera.projection_matrix
        glUseProgram(shader_program)
        loc_v = glGetUniformLocation(shader_program, "uView")
        loc_p = glGetUniformLocation(shader_program, "uProjection")
        glUniformMatrix4fv(loc_v, 1, GL_TRUE, view)
        glUniformMatrix4fv(loc_p, 1, GL_TRUE, proj)

    def handle_input(self, dt):
        # ruch WSAD + obrót kamery myszką
        speed = self.move_speed * dt
        keys = sdl2.SDL_GetKeyboardState(None)
        forward = self.camera.target - self.camera.position
        forward = forward / np.linalg.norm(forward)
        right = np.cross(forward, self.camera.up)
        right = right / np.linalg.norm(right)

        # WSAD
        if keys[sdl2.SDL_SCANCODE_W]:
            self.camera.move(forward * speed)
        if keys[sdl2.SDL_SCANCODE_S]:
            self.camera.move(-forward * speed)
        if keys[sdl2.SDL_SCANCODE_A]:
            self.camera.move(-right * speed)
        if keys[sdl2.SDL_SCANCODE_D]:
            self.camera.move(right * speed)

        # mysz - odczyt względny
        xrel = ctypes.c_int()
        yrel = ctypes.c_int()
        sdl2.SDL_GetRelativeMouseState(ctypes.byref(xrel), ctypes.byref(yrel))
        yaw = -xrel.value * self.mouse_sensitivity
        pitch = -yrel.value * self.mouse_sensitivity

        # obrót wektora offset
        def rotate(v, axis, angle):
            axis = axis / np.linalg.norm(axis)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            return v * cos_a + np.cross(axis, v) * sin_a + axis * np.dot(axis, v) * (1 - cos_a)

        offset = self.camera.target - self.camera.position
        # yaw wokół up
        offset = rotate(offset, self.camera.up, yaw)
        # pitch wokół osi prawej
        right = np.cross(offset, self.camera.up)
        offset = rotate(offset, right, pitch)
        self.camera.target = self.camera.position + offset

    def run(self, update_callback=None):
        last_time = time.time()
        event = sdl2.SDL_Event()
        while True:
            while sdl2.SDL_PollEvent(event):
                if event.type == sdl2.SDL_QUIT:
                    sdl2.SDL_DestroyWindow(self.window)
                    sdl2.SDL_Quit()
                    return

            now = time.time()
            dt = now - last_time
            last_time = now

            self.handle_input(dt)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

            # callback: w nim ustawiasz kamery + rysujesz modele
            if update_callback:
                update_callback(dt, self)

            sdl2.SDL_GL_SwapWindow(self.window)