from typing import TYPE_CHECKING, Optional, Tuple

from arcade import BufferProtocol
from arcade.gl import constants

from .types import pixel_formats

if TYPE_CHECKING:
    from arcade.gl import Context


class Texture:
    def __init__(
        self,
        ctx: "Context",
        size: Tuple[int, int],
        *,
        components: int = 4,
        dtype: str = "f1",
        data: Optional[BufferProtocol] = None,
        filter: Optional[Tuple[int, int]] = None,
        wrap_x: Optional[int] = None,
        wrap_y: Optional[int] = None,
        target=constants.TEXTURE_2D,
        depth=False,
    ):
        self._ctx = ctx
        self._target = constants.TEXTURE_2D
        self._width, self._height = size
        self._dtype = dtype
        self._components = components
        self._alignment = 1
        self._target = target
        self._depth = depth
        self._compare_func: Optional[str] = None
        self._anisotropy = 1.0

        if "f" in self._dtype:
            self._filter = constants.LINEAR, constants.LINEAR
        else:
            self._filter = constants.NEAREST, constants.NEAREST

        self._wrap_x = constants.REPEAT
        self._wrap_y = constants.REPEAT

        self._ctx.gl.activeTexture(constants.TEXTURE0 + self._ctx.default_texture_unit)
        self._glo = self._ctx.gl.createTexture()
        self._ctx.gl.bindTexture(self._target, self._glo)

        self._texture_2d(data)

    @property
    def glo(self):
        return self._glo

    def _texture_2d(self, data):
        try:
            format_info = pixel_formats[self._dtype]
        except KeyError:
            raise ValueError(
                f"dtype '{self._dtype}' not supported. Supported types are: {tuple(pixel_formats.keys())}"
            )
        _format, _internal_format, self._type, self._component_size = format_info

        self._ctx.gl.pixelStorei(constants.UNPACK_ALIGNMENT, self._alignment)
        self._ctx.gl.pixelStorei(constants.PACK_ALIGNMENT, self._alignment)

        if self._depth:
            self._ctx.gl.texImage2D(
                self._target,
                0,
                constants.DEPTH_COMPONENT24,
                self._width,
                self._height,
                0,
                constants.DEPTH_COMPONENT,
                constants.UNSIGNED_INT,
                data,
            )
            self.compare_func = "<="
        else:
            self._format = _format[self._components]
            self._internal_format = _internal_format[self._components]

            self._ctx.gl.texImage2D(
                self._target,
                0,
                self._internal_format,
                self._width,
                self._height,
                0,
                self._format,
                self._type,
                data,
            )
