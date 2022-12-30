from typing import TYPE_CHECKING, Iterable

from arcade.gl import constants

from .types import AttribFormat, GLTypes

if TYPE_CHECKING:
    from arcade.gl import Context


class Program:
    def __init__(self, ctx: "Context", *, vertex_shader: str, fragment_shader: str):
        self._ctx = ctx
        self._glo = self._ctx.gl.createProgram()
        self._geometry_info = (0, 0, 0)
        self._attributes = []

        raw_shaders = [
            (vertex_shader, constants.VERTEX_SHADER),
            (fragment_shader, constants.FRAGMENT_SHADER),
        ]

        shaders = []
        for raw_shader, shader_type in raw_shaders:
            shader = Program.compile_shader(self._ctx.gl, raw_shader, shader_type)
            self._ctx.gl.attachShader(self._glo, shader)
            shaders.append(shader)

        Program.link(self._glo)

        for shader in shaders:
            self._ctx.gl.detachShader(self._glo, shader)
            self._ctx.gl.deleteShader(shader)

        self._introspect_attributes()

    @property
    def attributes(self) -> Iterable[AttribFormat]:
        return self._attributes

    def _introspect_attributes(self):
        num_attrs = self._ctx.gl.getProgramParameter(
            self._glo, constants.ACTIVE_ATTRIBUTES
        )

        for i in range(num_attrs):
            info = self._ctx.gl.getActiveAttrib(self._glo, i)
            location = self._ctx.gl.getAttribLocation(self._glo, info.name)

            type_info = GLTypes.get(info.type)

            self._attributes.append(
                AttribFormat(
                    info.name,
                    type_info.gl_type,
                    type_info.components,
                    type_info.gl_size,
                    location=location,
                )
            )

    @staticmethod
    def compile_shader(gl, source: str, type: int):
        shader = gl.createShader(type)
        gl.shaderSource(shader, source)
        gl.compileShader(shader)

        if not gl.getShaderParameter(shader, gl.COMPILE_STATUS):
            print(
                f"Error occurred while compiling shaders: {gl.getShaderInfoLog(shader)}"
            )
            gl.deleteShader(shader)
            return None

        return shader

    @staticmethod
    def link(gl, glo):
        gl.linkProgram(glo)

        if not gl.getProgramParameter(glo, constants.LINK_STATUS):
            raise RuntimeError(
                f"Error occured while linking program: {gl.getProgramInfoLog(glo)}"
            )
