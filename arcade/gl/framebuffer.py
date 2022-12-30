from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional, Tuple

from arcade.gl import constants

if TYPE_CHECKING:
    from arcade.gl import Context


class Framebuffer:
    def __init__(
        self, ctx: "Context", *, color_attachments=None, depth_attachment=None
    ):
        self._ctx = ctx
        self._glo = self._ctx.gl.createFramebuffer()

        self._color_attachments = (
            color_attachments
            if isinstance(color_attachments, list)
            else [color_attachments]
        )
        self._depth_attachment = depth_attachment
        self._samples = 0
        self._depth_mask = True
        self._prev_fbo = None

        self._ctx.gl.bindFramebuffer(constants.FRAMEBUFFER, self._glo)

        self._width, self._height = self._detect_size()
        self._viewport = 0, 0, self._width, self._height
        self._scissor: Optional[Tuple[int, int, int, int]] = None

        for i, tex in enumerate(self._color_attachments):
            self._ctx.gl.framebufferTexture2D(
                constants.FRAMEBUFFER,
                constants.COLOR_ATTACHMENT0 + i,
                tex._target,
                tex.glo,
                0,
            )

        if self.depth_attachment:
            self._ctx.gl.framebufferTexture2D(
                constants.FRAMEBUFFER,
                constants.DEPTH_ATTACHMENT,
                self.depth_attachment._target,
                self.depth_attachment.glo,
            )

        self._check_completeness()

        self._draw_buffers = [
            constants.COLOR_ATTACHMENT0 + i
            for i, _ in enumerate(self._color_attachments)
        ]

        self._ctx.active_framebuffer.use(force=True)

    @property
    def glo(self):
        return self._glo

    @contextmanager
    def activate(self):
        prev_fbo = self._ctx.active_framebuffer
        try:
            self.use()
            yield self
        finally:
            prev_fbo.use()

    def use(self, *, force: bool = False):
        self._use(force=force)
        self._ctx.active_framebuffer = self

    def _use(self, *, force: bool = False):
        if self._ctx.active_framebuffer == self and not force:
            return

        self._ctx.gl.bindFramebuffer(constants.FRAMEBUFFER, self._glo)

        if self._draw_buffers:
            self._ctx.gl.drawBuffers(self._draw_buffers)

        self._ctx.gl.depthMask(self._depth_mask)
        self._ctx.gl.viewport(*self._viewport)
        if self._scissor is not None:
            self._ctx.gl.scissor(*self._scissor)
        else:
            self._ctx.gl.scissor(*self._viewport)

    def clear(
        self,
        color=(0.0, 0.0, 0.0, 0.0),
        *,
        depth: float = 1.0,
        normalized: bool = False,
        viewport: Optional[Tuple[int, int, int, int]] = None
    ):
        pass
