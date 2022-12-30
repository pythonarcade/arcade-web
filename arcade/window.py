from __future__ import annotations

from typing import Tuple

import js
from pyodide.ffi import create_proxy

from arcade.gl import Context

_window: Window = None

def get_window() -> Window:
    return _window


def set_window(window: Window) -> None:
    global _window
    _window = window

class Window:
    def __init__(self, title: str, width: int, height: int):
        self.width = width
        self.height = height

        js.document.title = title
        self._canvas = js.document.createElement("canvas")
        self._canvas.id = "arcade-window"
        self._canvas.width = width
        self._canvas.height = height
        js.document.body.appendChild(self._canvas)

        self.context = Context(self._canvas)

        self.run_proxy = create_proxy(self.run)
        self._then = 0

        set_window(self)

    def on_update(self, delta_time):
        pass

    def on_draw(self):
        pass

    def clear(self, color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0)):
        self.context.clear(color)

    def run(self, now):
        now = now * 0.001
        delta_time = now - self._then
        self._then = now

        self.on_draw()
        self.on_update(delta_time)

        js.requestAnimationFrame(self.run_proxy)

def run():
    js.requestAnimationFrame(get_window().run_proxy)


