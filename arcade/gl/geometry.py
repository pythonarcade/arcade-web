from arcade.gl import BufferDescription, Context


def _get_active_context() -> Context:
    ctx = Context.active
    if not ctx:
        raise RuntimeError("No context is currently activated")
    return ctx