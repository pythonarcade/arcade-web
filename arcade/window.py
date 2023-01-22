from __future__ import annotations

from typing import Optional, Tuple

import js
from pyodide.ffi import create_proxy

from arcade import ArcadeContext
from arcade.arcade_types import Color

_window: Window = None


def get_window() -> Window:
    return _window


def set_window(window: Window) -> None:
    global _window
    _window = window


class Window:
    def __init__(self, width: int, height: int, title: str):
        self.width = width
        self.height = height

        js.document.title = title
        self._canvas = js.document.createElement("canvas")
        self._canvas.id = "arcade-window"
        self._canvas.width = width
        self._canvas.height = height
        js.document.body.appendChild(self._canvas)

        self.ctx = ArcadeContext(self)
        self.set_viewport(0, self.width, 0, self.height)

        self.run_proxy = create_proxy(self.run)
        self._then = 0

        set_window(self)

        self._background_color: Color = (0, 0, 0, 255)

    @property
    def canvas(self):
        return self._canvas

    @property
    def aspect_ratio(self):
        return self.width / self.height

    def on_update(self, delta_time):
        pass

    def on_draw(self):
        pass

    def clear(
        self,
        color: Optional[Color] = None,
        normalized: bool = False,
        viewport: Optional[Tuple[int, int, int, int]] = None,
    ):
        color = color if color is not None else self.background_color
        self.ctx.screen.clear(color, normalized=normalized, viewport=viewport)

    @property
    def background_color(self) -> Color:
        return self._background_color

    @background_color.setter
    def background_color(self, value: Color):
        self._background_color = value

    def get_size(self) -> Tuple[int, int]:
        return self.width, self.height

    def set_viewport(self, left, right, bottom, top):
        fbo = self.ctx.fbo
        if fbo.is_default:
            fbo.viewport = 0, 0, self.width, self.height

    def run(self, now):
        now = now * 0.001
        delta_time = now - self._then
        self._then = now

        self.on_draw()
        self.on_update(delta_time)

        js.requestAnimationFrame(self.run_proxy)

    def use(self):
        self.ctx.screen.use()


def run():
    js.requestAnimationFrame(get_window().run_proxy)
