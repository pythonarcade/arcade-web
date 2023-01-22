from typing import List, Optional, Sequence, Set, Tuple, Union

from arcade.arcade_types import BufferProtocol
from arcade.gl import constants

from .buffer import Buffer
from .framebuffer import DefaultFrameBuffer, Framebuffer
from .program import Program
from .texture import Texture
from .types import BufferDescription
from .vertex_array import Geometry


class Context:

    active: Optional["Context"] = None

    BLEND = constants.BLEND
    DEPTH_TEST = constants.DEPTH_TEST
    CULL_FACE = constants.CULL_FACE

    BLEND_DEFAULT = constants.SRC_ALPHA, constants.ONE_MINUS_SRC_ALPHA
    BLEND_ADDITIVE = constants.ONE, constants.ONE
    BLEND_PREMULTIPLIED_ALPHA = constants.SRC_ALPHA, constants.ONE

    def __init__(self, canvas):
        self.gl = canvas.getContext("webgl2")
        self._anisotropy_ext = self.gl.getExtension("EXT_texture_filter_anisotropic")
        self._limits = Limits(self)
        Context.activate(self)
        self.default_texture_unit = self._limits.MAX_TEXTURE_IMAGE_UNITS - 1

        self._screen = DefaultFrameBuffer(self)
        self.active_program: Optional[Program] = None
        self.active_framebuffer: Framebuffer = self._screen

        self.gl.enable(constants.SCISSOR_TEST)

        self._blend_func: Union[Tuple[int, int], Tuple[int, int, int, int]] = (
            constants.SRC_ALPHA,
            constants.ONE_MINUS_SRC_ALPHA,
        )
        self._point_size = 1.0
        self._flags: Set[int] = set()

        self._uniform_setters = None
        self._build_uniform_setters()

    def _build_uniform_setters(self):
        self._uniform_setters = {
            # Integers
            constants.INT: (int, self.gl.uniform1i, 1, 1),
            constants.INT_VEC2: (int, self.gl.uniform2iv, 2, 1),
            constants.INT_VEC3: (int, self.gl.uniform3iv, 3, 1),
            constants.INT_VEC4: (int, self.gl.uniform4iv, 4, 1),
            # Bools
            constants.BOOL: (bool, self.gl.uniform1i, 1, 1),
            constants.BOOL_VEC2: (bool, self.gl.uniform2iv, 2, 1),
            constants.BOOL_VEC3: (bool, self.gl.uniform3iv, 3, 1),
            constants.BOOL_VEC4: (bool, self.gl.uniform4iv, 4, 1),
            # Floats
            constants.FLOAT: (float, self.gl.uniform1f, 1, 1),
            constants.FLOAT_VEC2: (float, self.gl.uniform2fv, 2, 1),
            constants.FLOAT_VEC3: (float, self.gl.uniform3fv, 3, 1),
            constants.FLOAT_VEC4: (float, self.gl.uniform4fv, 4, 1),
            # Matrices
            constants.FLOAT_MAT2: (float, self.gl.uniformMatrix2fv, 4, 1),
            constants.FLOAT_MAT3: (float, self.gl.uniformMatrix3fv, 9, 1),
            constants.FLOAT_MAT4: (float, self.gl.uniformMatrix4fv, 16, 1),
            # 2D Samplers
            constants.SAMPLER_2D: (int, self.gl.uniform1i, 1, 1),
            constants.INT_SAMPLER_2D: (int, self.gl.uniform1i, 1, 1),
            constants.UNSIGNED_INT_SAMPLER_2D: (int, self.gl.uniform1i, 1, 1),
            # Array
            constants.SAMPLER_2D_ARRAY: (
                int,
                self.gl.uniform1iv,
                self.gl.uniform1iv,
                1,
                1,
            ),
        }

    def clear(self, color: Tuple[float, float, float, float]):
        self.gl.clearColor(*color)
        self.gl.clear(self.gl.COLOR_BUFFER_BIT)

    @property
    def blend_func(self) -> Union[Tuple[int, int], Tuple[int, int, int, int]]:
        return self._blend_func

    @blend_func.setter
    def blend_func(self, value: Union[Tuple[int, int], Tuple[int, int, int, int]]):
        self._blend_func = value
        if len(value) == 2:
            self.gl.blendFunc(*value)
        elif len(value) == 4:
            self.gl.blendFuncSeparate(*value)
        else:
            ValueError("blend_func takes a tuple of 2 or 4 values")

    @property
    def screen(self) -> Framebuffer:
        return self._screen

    @property
    def fbo(self) -> Framebuffer:
        return self.active_framebuffer

    @classmethod
    def activate(cls, ctx: "Context"):
        cls.active = ctx

    def enable(self, *flags):
        self._flags.update(flags)

        for flag in flags:
            self.gl.enable(flag)

    def enable_only(self, *args):
        self._flags = set(args)

        if constants.BLEND in self._flags:
            self.gl.enable(constants.BLEND)
        else:
            self.gl.disable(constants.BLEND)

        if constants.DEPTH_TEST in self._flags:
            self.gl.enable(constants.DEPTH_TEST)
        else:
            self.gl.disable(constants.DEPTH_TEST)

        if constants.CULL_FACE in self._flags:
            self.gl.enable(constants.CULL_FACE)
        else:
            self.gl.disable(constants.CULL_FACE)

    def disable(self, *flags):
        self._flags -= set(flags)
        for flag in flags:
            self.gl.disable(flag)

    def is_enabled(self, flag) -> bool:
        return flag in self._flags

    @property
    def viewport(self) -> Tuple[int, int, int, int]:
        return self.active_framebuffer.viewport

    @viewport.setter
    def viewport(self, value: Tuple[int, int, int, int]):
        self.active_framebuffer.viewport = value

    def program(self, *, vertex_shader: str, fragment_shader: str) -> Program:
        return Program(
            self, vertex_shader=vertex_shader, fragment_shader=fragment_shader
        )

    def buffer(self, *, data: Optional[BufferProtocol] = None, usage: str = "static"):
        return Buffer(self, data, usage=usage)

    def framebuffer(
        self,
        *,
        color_attachments: Optional[Union[Texture, List[Texture]]] = None,
        depth_attachment: Optional[Texture] = None,
    ) -> Framebuffer:
        return Framebuffer(
            self, color_attachments=color_attachments, depth_attachment=depth_attachment
        )

    def texture(
        self,
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: Optional[BufferProtocol] = None,
        wrap_x: Optional[int] = None,
        wrap_y: Optional[int] = None,
        filter: Optional[Tuple[int, int]] = None,
    ) -> Texture:
        return Texture(
            self,
            size,
            components=components,
            data=data,
            dtype=dtype,
            wrap_x=wrap_x,
            wrap_y=wrap_y,
        )

    def depth_texture(
        self, size: Tuple[int, int], *, data: Optional[BufferProtocol] = None
    ) -> Texture:
        return Texture(self, size, data=data, depth=True)

    def geometry(
        self,
        content: Optional[Sequence[BufferDescription]] = None,
        index_buffer: Optional[Buffer] = None,
        mode: Optional[int] = None,
        index_element_size: int = 4,
    ):
        return Geometry(
            self,
            content,
            index_buffer=index_buffer,
            mode=mode,
            index_element_size=index_element_size,
        )


class Limits:
    def __init__(self, ctx):
        self._ctx = ctx
        self.VENDOR = self.get_param(constants.VENDOR)
        self.RENDERER = self.get_param(constants.RENDERER)
        self.SAMPLE_BUFFERS = self.get_param(constants.SAMPLE_BUFFERS)
        self.SUBPIXEL_BITS = self.get_param(constants.SUBPIXEL_BITS)
        self.UNIFORM_BUFFER_OFFSET_ALIGNMENT = self.get_param(
            constants.UNIFORM_BUFFER_OFFSET_ALIGNMENT
        )
        self.MAX_ARRAY_TEXTURE_LAYERS = self.get_param(
            constants.MAX_ARRAY_TEXTURE_LAYERS
        )
        self.MAX_3D_TEXTURE_SIZE = self.get_param(constants.MAX_3D_TEXTURE_SIZE)
        self.MAX_COLOR_ATTACHMENTS = self.get_param(constants.MAX_COLOR_ATTACHMENTS)
        self.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS = self.get_param(
            constants.MAX_COMBINED_FRAGMENT_UNIFORM_COMPONENTS
        )
        self.MAX_COMBINED_TEXTURE_IMAGE_UNITS = self.get_param(
            constants.MAX_COMBINED_TEXTURE_IMAGE_UNITS
        )
        self.MAX_COMBINED_UNIFORM_BLOCKS = self.get_param(
            constants.MAX_COMBINED_UNIFORM_BLOCKS
        )
        self.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS = self.get_param(
            constants.MAX_COMBINED_VERTEX_UNIFORM_COMPONENTS
        )
        self.MAX_CUBE_MAP_TEXTURE_SIZE = self.get_param(
            constants.MAX_CUBE_MAP_TEXTURE_SIZE
        )
        self.MAX_DRAW_BUFFERS = self.get_param(constants.MAX_DRAW_BUFFERS)
        self.MAX_ELEMENT_INDICES = self.get_param(constants.MAX_ELEMENTS_INDICES)
        self.MAX_ELEMENT_VERTICES = self.get_param(constants.MAX_ELEMENTS_VERTICES)
        self.MAX_FRAGMENT_INPUT_COMPONENTS = self.get_param(
            constants.MAX_FRAGMENT_INPUT_COMPONENTS
        )
        self.MAX_FRAGMENT_UNIFORM_COMPONENTS = self.get_param(
            constants.MAX_FRAGMENT_INPUT_COMPONENTS
        )
        self.MAX_FRAGMENT_UNIFORM_VECTORS = self.get_param(
            constants.MAX_FRAGMENT_UNIFORM_VECTORS
        )
        self.MAX_FRAGMENT_UNIFORM_BLOCKS = self.get_param(
            constants.MAX_FRAGMENT_UNIFORM_BLOCKS
        )
        self.MAX_SAMPLES = self.get_param(constants.MAX_SAMPLES)
        self.MAX_RENDERBUFFER_SIZE = self.get_param(constants.MAX_RENDERBUFFER_SIZE)
        self.MAX_UNIFORM_BUFFER_BINDINGS = self.get_param(
            constants.MAX_UNIFORM_BUFFER_BINDINGS
        )
        self.MAX_TEXTURE_SIZE = self.get_param(constants.MAX_TEXTURE_SIZE)
        self.MAX_UNIFORM_BLOCK_SIZE = self.get_param(constants.MAX_UNIFORM_BLOCK_SIZE)
        self.MAX_VARYING_VECTORS = self.get_param(constants.MAX_VARYING_VECTORS)
        self.MAX_VERTEX_ATTRIBS = self.get_param(constants.MAX_VERTEX_ATTRIBS)
        self.MAX_VERTEX_TEXTURE_IMAGE_UNITS = self.get_param(
            constants.MAX_VERTEX_TEXTURE_IMAGE_UNITS
        )
        self.MAX_VERTEX_UNIFORM_COMPONENTS = self.get_param(
            constants.MAX_VERTEX_UNIFORM_COMPONENTS
        )
        self.MAX_VERTEX_UNIFORM_VECTORS = self.get_param(
            constants.MAX_VERTEX_UNIFORM_VECTORS
        )
        self.MAX_VERTEX_OUTPUT_COMPONENTS = self.get_param(
            constants.MAX_VERTEX_OUTPUT_COMPONENTS
        )
        self.MAX_VERTEX_UNIFORM_BLOCKS = self.get_param(
            constants.MAX_VERTEX_UNIFORM_BLOCKS
        )
        self.MAX_TEXTURE_IMAGE_UNITS = self.get_param(constants.MAX_TEXTURE_IMAGE_UNITS)
        print(self.MAX_TEXTURE_IMAGE_UNITS)
        self.MAX_TEXTURE_MAX_ANISOTROPY = self.get_param(
            constants.MAX_TEXTURE_MAX_ANISOTROPY_EXT
        )
        self.MAX_VIEWPORT_DIMS = self.get_param(constants.MAX_VIEWPORT_DIMS)
        self.MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS = self.get_param(
            constants.MAX_TRANSFORM_FEEDBACK_SEPARATE_ATTRIBS
        )
        self.POINT_SIZE_RANGE = self.get_param(constants.ALIASED_POINT_SIZE_RANGE)

    def get_param(self, enum: int):
        return self._ctx.gl.getParameter(enum)
        return self._ctx.gl.getParameter(enum)
