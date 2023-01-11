from pathlib import Path
from typing import Optional, Union

from arcade.gl import Context, Program


class ArcadeContext(Context):
    def __init__(self, window):
        super().__init__(window.canvas)

    def load_program(
        self,
        *,
        vertex_shader: Union[str, Path],
        fragment_shader: Optional[Union[str, Path]] = None,
    ) -> Program:
        from arcade.resources import resolve_resource_path

        vertex_shader_src = resolve_resource_path(vertex_shader).read_text()
        print(vertex_shader_src)
        fragment_shader_src = resolve_resource_path(fragment_shader).read_text()

        return self.program(
            vertex_shader=vertex_shader_src, fragment_shader=fragment_shader_src
        )
