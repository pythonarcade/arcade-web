"""
Simple 3D Example
If Python and Arcade are installed, this example can be run from the command line with:
python -m arcade.examples.gl.3d_cube
"""
import arcade
from arcade.gl import geometry
from arcade.math import Mat4


class MyGame(arcade.Window):
    def __init__(self, title, width, height):
        super().__init__(title, width, height)
        # Use the standard cube
        self.cube = geometry.cube()
        # Simple color lighting program
        self.program = self.ctx.program(
            vertex_shader="""#version 300 es
            precision highp float;
            uniform mat4 projection;
            uniform mat4 modelview;
            in vec3 in_position;
            in vec3 in_normal;
            out vec3 normal;
            out vec3 pos;
            void main() {
                vec4 p = modelview * vec4(in_position, 1.0);
                gl_Position = projection * p;
                mat3 m_normal = transpose(inverse(mat3(modelview)));
                normal = m_normal * in_normal;
                pos = p.xyz;
            }
            """,
            fragment_shader="""#version 300 es
            precision highp float;
            out vec4 fragColor;
            in vec3 normal;
            in vec3 pos;
            void main()
            {
                fragColor = vec4(abs(pos) * normal, 1.0);
            }
            """,
        )
        self.on_resize(self.width, self.height)
        self.time = 0

    def on_draw(self):
        self.clear()
        self.ctx.enable_only(self.ctx.gl.CULL_FACE, self.ctx.gl.DEPTH_TEST)

        translate = Mat4.from_translation((0, 0, -1.75))
        rx = Mat4.from_rotation(self.time, (1, 0, 0))
        ry = Mat4.from_rotation(self.time * 0.77, (0, 1, 0))
        modelview = translate @ rx @ ry
        self.program["modelview"] = modelview

        self.cube.render(self.program)

    def on_update(self, dt):
        self.time += dt

    def on_resize(self, width, height):
        """Set up viewport and projection"""
        self.ctx.viewport = 0, 0, width, height
        self.program["projection"] = Mat4.perspective_projection(
            self.aspect_ratio, 0.1, 100, fov=60
        )


def run():
    MyGame("3D Cube", 800, 600)
    arcade.run()
