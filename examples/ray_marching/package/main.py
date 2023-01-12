"""
Simple instancing example.

We draw a triangle N times using instancing.
A position offset and color is passed in per instance.
To make things a bit more interesting we also rotate the triangle.

If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.instancing
"""
from pathlib import Path

import arcade
from arcade.gl import geometry

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Ray Marching"

CURRENT_DIR = Path(__file__).parent.resolve()


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        self.program = self.ctx.load_program(
            vertex_shader=CURRENT_DIR / "resources" / "ray_marching_vs.glsl",
            fragment_shader=CURRENT_DIR / "resources" / "ray_marching_fs.glsl",
        )
        self.quad_fs = geometry.quad_2d_fs()
        self.set_aspect_ratio(self.width, self.height)
        self.time = 0

    def on_draw(self):
        self.quad_fs.render(self.program)

    def on_update(self, delta_time: float):
        self.time += delta_time
        self.program["iTime"] = self.time

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.set_aspect_ratio(width, height)

    def set_aspect_ratio(self, width, height):
        self.program["aspect_ratio"] = width / height


def run():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
