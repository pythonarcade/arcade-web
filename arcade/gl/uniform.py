class Uniform:
    def __init__(self, ctx, program, location, name, data_type, array_length):
        self._ctx = ctx
        self._program_glo = (program,)
        self._location = (location,)
        self._name = name
        self._data_type = (data_type,)
        self._array_length = (array_length,)
        self._components = 0

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
        return self._components
