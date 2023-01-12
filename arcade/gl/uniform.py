from arcade.gl import constants


class Uniform:
    def __init__(self, ctx, program, location, name, data_type, array_length):
        self._ctx = ctx
        self._program = program
        self._location = location
        self._name = name
        self._data_type = data_type
        self._array_length = array_length
        self._components = 0
        self.setter = None
        self._setup_getters_and_setters()

    @property
    def location(self) -> int:
        return self._location

    @property
    def name(self) -> str:
        return self._name

    @property
    def array_length(self) -> int:
        return self._array_length

    @property
    def components(self) -> int:
        return self._components

    def _setup_getters_and_setters(self):
        gl_type, gl_setter, length, count = self._ctx._uniform_setters[self._data_type]
        self._components = length

        is_matrix = self._data_type in (
            constants.FLOAT_MAT2,
            constants.FLOAT_MAT3,
            constants.FLOAT_MAT4,
        )

        self.setter = Uniform._create_setter_func(
            self._ctx, self._program, self._location, gl_setter, is_matrix
        )

    @staticmethod
    def _create_setter_func(ctx, program, location, gl_setter, is_matrix):
        if is_matrix:

            def setter_func(value):
                ctx.gl.useProgram(program)
                gl_setter(location, False, value)

        else:

            def setter_func(value):
                ctx.gl.useProgram(program)
                gl_setter(location, value)

        return setter_func


class UniformBlock:
    def __init__(self, ctx, glo, index: int, size: int, name: str):
        self._ctx = ctx
        self.glo = glo
        self.index = index
        self.size = size
        self.name = name

    @property
    def binding(self):
        return self._ctx.gl.getActiveUniformBlockParameter(
            self.glo, self.index, constants.UNIFORM_BLOCK_BINDING
        )

    @binding.setter
    def binding(self, binding: int):
        self._ctx.gl.uniformBlockBinding(self.glo, self.index, binding)

    def getter(self):
        return self

    def setter(self, value: int):
        self.binding = value
