from contextlib import contextmanager
from typing import TYPE_CHECKING, Optional, Tuple

from arcade.gl import constants

if TYPE_CHECKING:
    from arcade.gl import Context


class Framebuffer:
    is_default = False

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

    def _get_viewport(self) -> Tuple[int, int, int, int]:
        return self._viewport

    def _set_viewport(self, value: Tuple[int, int, int, int]):
        if not isinstance(value, tuple) or len(value) != 4:
            raise ValueError("viewport should be a 4-component tuple")

        self._viewport = value

        # If the framebuffer is already bound we need to set the viewport
        # Otherwise it will be set on use()
        if self._ctx.active_framebuffer == self:
            self._ctx.gl.viewport(*self._viewport)
            if self._scissor is None:
                self._ctx.gl.scissor(*self._viewport)
            else:
                self._ctx.gl.scissor(*self._scissor)

    viewport = property(_get_viewport, _set_viewport)

    def _get_scissor(self) -> Optional[Tuple[int, int, int, int]]:
        return self._scissor

    def _set_scissor(self, value):
        self._scissor = value

        if self._scissor is None:
            if self._ctx.active_framebuffer == self:
                self._ctx.gl.scissor(*self._viewport)
        else:
            if self._ctx.active_framebuffer == self:
                self._ctx.gl.scissor(*self._scissor)

    scissor = property(_get_scissor, _set_scissor)

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
        with self.activate():
            scissor_values = self._scissor

            if viewport:
                self.scissor = viewport
            else:
                self.scissor = None

            if normalized:
                if len(color) == 3:
                    self._ctx.gl.clearColor(*color, 1.0)
                else:
                    self._ctx.gl.clearColor(*color)
            else:
                if len(color) == 3:
                    self._ctx.gl.clearColor(
                        color[0] / 255, color[1] / 255, color[2] / 255, 1.0
                    )
                else:
                    self._ctx.gl.clearColor(
                        color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255
                    )

            if self.depth_attachment:
                self._ctx.gl.clear(
                    constants.COLOR_BUFFER_BIT | constants.DEPTH_BUFFER_BIT
                )
            else:
                self._ctx.gl.clear(constants.COLOR_BUFFER_BIT)

            self.scissor = scissor_values

    @staticmethod
    def _check_completeness(ctx: "Context") -> None:
        states = {
            constants.FRAMEBUFFER_UNSUPPORTED: "Framebuffer unsupported. Try another format.",
            constants.FRAMEBUFFER_INCOMPLETE_ATTACHMENT: "Framebuffer incomplete attachment.",
            constants.FRAMEBUFFER_INCOMPLETE_MISSING_ATTACHMENT: "Frambuffer missing attachment.",
            constants.FRAMEBUFFER_INCOMPLETE_DIMENSIONS: "Framebuffer unsupported dimensions.",
            constants.FRAMEBUFFER_COMPLETE: "Framebuffer is complete.",
        }

        status = ctx.gl.checkFramebufferStatus(constants.FRAMEBUFFER)
        if status != constants.FRAMEBUFFER_COMPLETE:
            raise ValueError(
                "Framebuffer is incomplete. {}".format(
                    states.get(status, "Unknown error")
                )
            )


class DefaultFrameBuffer(Framebuffer):
    is_default = True

    def __init__(self, ctx: "Context"):
        self._ctx = ctx
        self._samples = 0
        self._color_attachments = []
        self._depth_attachment = None
        self._depth_mask = True

        self._glo = self._ctx.gl.getParameter(constants.DRAW_FRAMEBUFFER_BINDING)

        self._draw_buffers = None
        x, y, width, height = self._ctx.gl.getParameter(constants.SCISSOR_BOX)

        self._viewport = x, y, width, height
        self._scissor = None
        self._width = width
        self._height = height

        self._depth_attachment = True
