import os
import sys

# Automatyczna ścieżka do SDL2.dll
dll_path = os.path.abspath(os.path.dirname(__file__))
os.environ["PYSDL2_DLL_PATH"] = dll_path

from .core import Window
from .mesh import Mesh