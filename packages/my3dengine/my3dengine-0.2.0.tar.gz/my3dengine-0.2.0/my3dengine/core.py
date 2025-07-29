# my3dengine/core.py
import sdl2
import sdl2.ext
from OpenGL.GL import *
import time
import numpy as np
import ctypes
from .camera import Camera
from enum import IntEnum

class Key(IntEnum):
    # Strzałki
    UP = sdl2.SDL_SCANCODE_UP
    DOWN = sdl2.SDL_SCANCODE_DOWN
    LEFT = sdl2.SDL_SCANCODE_LEFT
    RIGHT = sdl2.SDL_SCANCODE_RIGHT

    # Klawisze literowe
    A = sdl2.SDL_SCANCODE_A
    B = sdl2.SDL_SCANCODE_B
    C = sdl2.SDL_SCANCODE_C
    D = sdl2.SDL_SCANCODE_D
    E = sdl2.SDL_SCANCODE_E
    F = sdl2.SDL_SCANCODE_F
    G = sdl2.SDL_SCANCODE_G
    H = sdl2.SDL_SCANCODE_H
    I = sdl2.SDL_SCANCODE_I
    J = sdl2.SDL_SCANCODE_J
    K = sdl2.SDL_SCANCODE_K
    L = sdl2.SDL_SCANCODE_L
    M = sdl2.SDL_SCANCODE_M
    N = sdl2.SDL_SCANCODE_N
    O = sdl2.SDL_SCANCODE_O
    P = sdl2.SDL_SCANCODE_P
    Q = sdl2.SDL_SCANCODE_Q
    R = sdl2.SDL_SCANCODE_R
    S = sdl2.SDL_SCANCODE_S
    T = sdl2.SDL_SCANCODE_T
    U = sdl2.SDL_SCANCODE_U
    V = sdl2.SDL_SCANCODE_V
    W = sdl2.SDL_SCANCODE_W
    X = sdl2.SDL_SCANCODE_X
    Y = sdl2.SDL_SCANCODE_Y
    Z = sdl2.SDL_SCANCODE_Z

    # Klawisze numeryczne
    NUMBER_0 = sdl2.SDL_SCANCODE_0
    NUMBER_1 = sdl2.SDL_SCANCODE_1
    NUMBER_2 = sdl2.SDL_SCANCODE_2
    NUMBER_3 = sdl2.SDL_SCANCODE_3
    NUMBER_4 = sdl2.SDL_SCANCODE_4
    NUMBER_5 = sdl2.SDL_SCANCODE_5
    NUMBER_6 = sdl2.SDL_SCANCODE_6
    NUMBER_7 = sdl2.SDL_SCANCODE_7
    NUMBER_8 = sdl2.SDL_SCANCODE_8
    NUMBER_9 = sdl2.SDL_SCANCODE_9

    # Klawisze funkcyjne
    F1 = sdl2.SDL_SCANCODE_F1
    F2 = sdl2.SDL_SCANCODE_F2
    F3 = sdl2.SDL_SCANCODE_F3
    F4 = sdl2.SDL_SCANCODE_F4
    F5 = sdl2.SDL_SCANCODE_F5
    F6 = sdl2.SDL_SCANCODE_F6
    F7 = sdl2.SDL_SCANCODE_F7
    F8 = sdl2.SDL_SCANCODE_F8
    F9 = sdl2.SDL_SCANCODE_F9
    F10 = sdl2.SDL_SCANCODE_F10
    F11 = sdl2.SDL_SCANCODE_F11
    F12 = sdl2.SDL_SCANCODE_F12

    # Inne ważne
    SPACE = sdl2.SDL_SCANCODE_SPACE
    ESCAPE = sdl2.SDL_SCANCODE_ESCAPE
    RETURN = sdl2.SDL_SCANCODE_RETURN
    TAB = sdl2.SDL_SCANCODE_TAB
    SHIFT = sdl2.SDL_SCANCODE_LSHIFT
    CTRL = sdl2.SDL_SCANCODE_LCTRL
    ALT = sdl2.SDL_SCANCODE_LALT
    BACKSPACE = sdl2.SDL_SCANCODE_BACKSPACE
    CAPSLOCK = sdl2.SDL_SCANCODE_CAPSLOCK

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
        self.mouse_locked = True

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

    def is_key_pressed(self, key: Key) -> bool:
        keys = sdl2.SDL_GetKeyboardState(None)
        return keys[key] != 0

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

    def toggle_mouse_lock(self):
        self.mouse_locked = not self.mouse_locked
        if self.mouse_locked:
            sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE)
            sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
        else:
            sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_FALSE)
            sdl2.SDL_ShowCursor(sdl2.SDL_ENABLE)

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