from OpenGL.GL import *
import numpy as np

basic_vertex_src = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
layout(location = 2) in vec2 aUV;

uniform mat4 uModel;
uniform mat4 uView;
uniform mat4 uProjection;

uniform vec2 uUVTiling;   // np. (1.0, 1.0)
uniform vec2 uUVOffset;   // np. (0.0, 0.0)

out vec3 vColor;
out vec2 vUV;

void main() {
    gl_Position = uProjection * uView * uModel * vec4(aPos, 1.0);
    vColor = aColor;
    vUV = aUV * uUVTiling + uUVOffset;
}
"""

basic_fragment_src = """
#version 330 core
in vec3 vColor;
in vec2 vUV;
uniform sampler2D uTexture;
uniform int useTexture;
out vec4 FragColor;

void main() {
    if (useTexture == 1)
        FragColor = texture(uTexture, vUV);
    else
        FragColor = vec4(vColor, 1.0);
}
"""

def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        error = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compile error: {error}")
    return shader

def create_shader(vertex_src, fragment_src):
    vert = compile_shader(vertex_src, GL_VERTEX_SHADER)
    frag = compile_shader(fragment_src, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vert)
    glAttachShader(program, frag)
    glLinkProgram(program)

    if glGetProgramiv(program, GL_LINK_STATUS) != GL_TRUE:
        error = glGetProgramInfoLog(program).decode()
        raise RuntimeError(f"Program link error: {error}")

    glDeleteShader(vert)
    glDeleteShader(frag)
    return program

def basic_shader():
    return create_shader(basic_vertex_src, basic_fragment_src)
