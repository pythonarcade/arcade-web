from typing import Optional, Sequence

from arcade.gl import Buffer, BufferDescription, Context, Program, constants


class VertexArray:
    def __init__(
        self,
        ctx: "Context",
        program: Program,
        content: Sequence[BufferDescription],
        index_buffer: Optional[Buffer] = None,
        index_element_size: int = 4,
    ):
        self._ctx = ctx
        self._program = program
        self._content = content
        self._glo = None

        self._build(program, content, index_buffer)

    def _build(
        self, program: Program, content: Sequence[BufferDescription], index_buffer
    ):
        gl = self._ctx.gl
        self._glo = gl.createVertexArray()
        gl.bindVertexArray(self._glo)

        if index_buffer is not None:
            gl.bindBuffer(constants.ELEMENT_ARRAY_BUFFER, index_buffer.glo)

        descr_attribs = {
            attr.name: (descr, attr) for descr in content for attr in descr.formats
        }

        for i, prog_attr in enumerate(program.attributes):
            if prog_attr.name.startswith("gl_"):
                continue
            try:
                buff_descr, attr_descr = descr_attribs[prog_attr.name]
            except KeyError:
                raise ValueError(
                    (
                        f"Program needs attribute '{prog_attr.name}', but is not "
                        f" in buffer descriptions. Buffer Descriptions: {content}"
                    )
                )

            if prog_attr.components != attr_descr.components:
                raise ValueError(
                    (
                        f"Program attribute '{prog_attr.name}' has {prog_attr.components} components "
                        f"while the buffer description has {attr_descr.components} components."
                    )
                )

            gl.enableVertexAttribArray(prog_attr.location)
            gl.bindBuffer(constants.ARRAY_BUFFER, buff_descr.buffer.glo)

            normalized = True if attr_descr.name in buff_descr.normalized else False
            gl.vertexAttribPointer(
                prog_attr.location,
                attr_descr.components,
                attr_descr.gl_type,
                normalized,
                buff_descr.stride,
                attr_descr.offset,
            )


class Geometry:
    def __init__(
        self,
        ctx: "Context",
        content: Optional[Sequence[BufferDescription]],
        index_buffer: Optional[Buffer] = None,
        mode: Optional[int] = None,
        index_element_size: int = 4,
    ):
        self._ctx = ctx
        self._content = content or []
        self._index_buffer = index_buffer
        self._index_element_size = index_element_size
        self._mode = mode if mode is not None else constants.TRIANGLES
        self._num_vertices: int = -1

        if self._index_buffer and self._index_element_size not in (1, 2, 4):
            raise ValueError("index_element_size must be 1, 2, or 4")

        if content:
            if self._index_buffer:
                self._num_vertices = self._index_buffer.size // self._index_element_size
            else:
                self._num_vertices = content[0].num_vertices
                for descr in self._content:
                    if descr.instanced:
                        continue
                    self._num_vertices = min(self._num_vertices, descr.num_vertices)

    def instance(self, program: Program) -> VertexArray:
        return self._generate_vao(program)

    def _generate_vao(self, program: Program) -> VertexArray:
        vao = VertexArray(
            self._ctx,
            program,
            self._content,
            index_buffer=self._index_buffer,
            index_element_size=self._index_element_size,
        )
        return vao
