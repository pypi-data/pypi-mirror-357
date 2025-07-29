import sdl2
import sdl2.ext
from OpenGL.GL import *
import time
from .key import Key

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def to_list(self):
        return [self.x, self.y, self.z]

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"

class Window:
    def __init__(self, title, width, height):
        sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
        self.width = width
        self.height = height
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

        self.mouse_locked = True
        sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE)
        sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)

    def is_key_pressed(self, key: Key) -> bool:
        keys = sdl2.SDL_GetKeyboardState(None)
        return keys[key] != 0

    def toggle_mouse_lock(self):
        self.mouse_locked = not self.mouse_locked
        if self.mouse_locked:
            sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_TRUE)
            sdl2.SDL_ShowCursor(sdl2.SDL_DISABLE)
        else:
            sdl2.SDL_SetRelativeMouseMode(sdl2.SDL_FALSE)
            sdl2.SDL_ShowCursor(sdl2.SDL_ENABLE)

    def prepare_frame(self):
        glViewport(0, 0, self.width, self.height)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

    def run(self, update_callback=None, cameras=[]):
        last_time = time.time()
        event = sdl2.SDL_Event()
        running = True
        while running:
            while sdl2.SDL_PollEvent(event):
                if event.type == sdl2.SDL_QUIT:
                    running = False
                elif event.type == sdl2.SDL_KEYDOWN:
                    if event.key.keysym.scancode == sdl2.SDL_SCANCODE_ESCAPE:
                        self.toggle_mouse_lock()

            now = time.time()
            dt = now - last_time
            last_time = now

            self.prepare_frame()
            if update_callback:
                update_callback(dt, self)

            sdl2.SDL_GL_SwapWindow(self.window)
            glFlush()

        sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()
