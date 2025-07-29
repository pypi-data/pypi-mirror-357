import os
import sys

# Automatyczna ścieżka do SDL2.dll
dll_path = os.path.abspath(os.path.dirname(__file__))
os.environ["PYSDL2_DLL_PATH"] = dll_path

from .key import Key
from .core import Window
from .camera import Camera
from .mesh import Mesh
from .core import Vector3

__all__ = ['Window', 'Camera', 'Mesh', 'Key']