from typing import TYPE_CHECKING

import js

from arcade.arcade_types import BufferProtocol
from arcade.gl import constants

if TYPE_CHECKING:
    from arcade.gl import Context

class Buffer:

    _usages = {
        "static": constants.STATIC_DRAW,
        "dynamic": constants.DYNAMIC_DRAW,
        "stream": constants.STREAM_DRAW,
    }

    def __init__(
        self,
        ctx: "Context",
        data: BufferProtocol,
        buffer_type: int = constants.ARRAY_BUFFER,
        usage: str = "static"
    ):
        self._ctx = ctx
        gl = self._ctx.gl
        self._glo = gl.createBuffer()
        self._usage = Buffer._usages[usage]
        self._buffer_type = buffer_type

        self._size = len(data) * data.itemsize

        js_array_buffer = js.ArrayBuffer.new(self._size)
        js_array_buffer.assign(data)

        gl.bindBuffer(buffer_type, self._glo)
        gl.bufferData(buffer_type, js_array_buffer, self._usage)

    @property
    def glo(self):
        return self._glo

    @property
    def size(self) -> int:
        return self._size

    def write(self, data: BufferProtocol, offset: int = 0) -> None:
        self._ctx.gl.bindBuffer(self._buffer_type, self._glo)

        js_array_buffer = js.ArrayBuffer.new(len(data) * data.itemsize)
        js_array_buffer.assign(data)

        self._ctx.gl.bufferSubData(self._buffer_type, offset, js_array_buffer)

    def copy_from_buffer(
        self,
        source: "Buffer",
        size: int = -1,
        offset: int = 0,
        source_offset: int = 0
    ) -> None:
        if size == -1:
            size = source.size

        if size + source_offset > source.size:
            raise ValueError("Attempting to read outside the range of source buffer")

        if size + offset > self._size:
            raise ValueError("Attempting to write outside the buffer size")

        self._ctx.gl.bindBuffer(constants.COPY_READ_BUFFER, source._glo)
        self._ctx.gl.bindBuffer(constants.COPY_WRITE_BUFFER, self._glo)
        self._ctx.gl.copyBufferSubData(
            constants.COPY_READ_BUFFER,
            constants.COPY_WRITE_BUFFER,
            source_offset,
            offset,
            size
        )


