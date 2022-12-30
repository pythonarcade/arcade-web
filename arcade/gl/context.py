from typing import Optional, Tuple

from arcade.gl import constants

from .program import Program


class Context:
    def __init__(self, canvas):
        self.gl = canvas.getContext("webgl2")
        self._limits = Limits(self)
        self.default_texture_unit = self._limits.MAX_TEXTURE_IMAGE_UNITS - 1

        self._screen = DefaultFrameBuffer(self)
        self.active_program: Optional[Program] = None
        self.active_framebuffer: Framebuffer = self._screen

    def clear(self, color: Tuple[float, float, float, float]):
        # Temporary
        self.gl.clearDepth(1.0)
        self.gl.enable(self.gl.DEPTH_TEST)
        self.gl.depthFunc(self.gl.LEQUAL)

        self.gl.clearColor(*color)
        self.gl.clear(self.gl.COLOR_BUFFER_BIT | self.gl.DEPTH_BUFFER_BIT)

    def program(self, *, vertex_shader: str, fragment_shader: str) -> Program:
        return Program.create(self, vertex_shader, fragment_shader)


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
