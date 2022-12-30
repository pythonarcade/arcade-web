import re
from typing import Iterable, List, Optional

from arcade.gl import Buffer, constants

_float_base_format = (0, constants.RED, constants.RG, constants.RGB, constants.RGBA)
_int_base_format = (
    0,
    constants.RED_INTEGER,
    constants.RG_INTEGER,
    constants.RGB_INTEGER,
    constants.RGBA_INTEGER,
)
pixel_formats = {
    "f1": (
        _float_base_format,
        (0, constants.R8, constants.RG8, constants.RGB8, constants.RGBA8),
        constants.UNSIGNED_BYTE,
        1,
    ),
    "f2": (
        _float_base_format,
        (0, constants.R16F, constants.RG16F, constants.RGB16F, constants.RGBA16F),
        constants.HALF_FLOAT,
        2,
    ),
    "f4": (
        _float_base_format,
        (0, constants.R32F, constants.RG32F, constants.RGB32F, constants.RGBA32F),
        constants.FLOAT,
        4,
    ),
    "i1": (
        _int_base_format,
        (0, constants.R8I, constants.RG8I, constants.RGB8I, constants.RGBA8I),
        constants.BYTE,
        1,
    ),
    "i2": (
        _int_base_format,
        (0, constants.R16I, constants.RG16I, constants.RGB16I, constants.RGBA16I),
        constants.SHORT,
        2,
    ),
    "i4": (
        _int_base_format,
        (0, constants.R32I, constants.RG32I, constants.RGB32I, constants.RGBA32I),
        constants.INT,
        4,
    ),
    "u1": (
        _int_base_format,
        (0, constants.R8UI, constants.RG8UI, constants.RGB8UI, constants.RGBA8UI),
        constants.UNSIGNED_BYTE,
        1,
    ),
    "u2": (
        _int_base_format,
        (0, constants.R16UI, constants.RG16UI, constants.RGB16UI, constants.RGBA16UI),
        constants.UNSIGNED_SHORT,
        2,
    ),
    "u4": (
        _int_base_format,
        (0, constants.R32UI, constants.RG32UI, constants.RGB32UI, constants.RGBA32UI),
        constants.UNSIGNED_INT,
        4,
    ),
}


class AttribFormat:
    """
    Represents an attribute in a BufferDescription or a Program.

    :param str name: Name of the attribute
    :param int gl_type: The WebGL enum type such as FLOAT, INT, etc
    :param int bytes_per_component: Number of bytes a single component takes
    :param int offset: (Optional offset for BufferDescription)
    :param int location: (Optional location for program attribute)
    """

    __slots__ = (
        "name",
        "gl_type",
        "components",
        "bytes_per_component",
        "offset",
        "location",
    )

    def __init__(
        self,
        name: str,
        gl_type: int,
        components: int,
        bytes_per_component: int,
        offset=0,
        location=0,
    ):
        self.name: str = name
        self.gl_type: int = gl_type
        self.components = components
        self.bytes_per_component = (bytes_per_component,)
        self.offset = offset
        self.lcoation = location

    @property
    def bytes_total(self) -> int:
        return self.components * self.bytes_per_component


class BufferDescription:

    _formats = {
        "f": (constants.FLOAT, 4),
        "f1": (constants.UNSIGNED_BYTE, 1),
        "f2": (constants.HALF_FLOAT, 2),
        "f4": (constants.FLOAT, 4),
        "i": (constants.INT, 4),
        "i1": (constants.BYTE, 1),
        "i2": (constants.SHORT, 2),
        "i4": (constants.INT, 4),
    }

    def __init__(
        self,
        buffer: Buffer,
        formats: str,
        attributes: Iterable[str],
        normalized: Optional[Iterable[str]] = None,
        instanced: bool = False,
    ):
        self.buffer = buffer
        self.attributes = attributes
        self.normalized = set() if normalized is None else set(normalized)
        self.instanced = instanced
        self.formats: List[AttribFormat] = []
        self.stride: int = -1
        self.num_vertices: int = -1

        formats_list = formats.split(" ")

        def zip_attrs(formats, attributes):
            attr_index = 0
            for f in formats:
                if "x" in f:
                    yield f, None
                else:
                    yield f, attributes[attr_index]
                    attr_index += 1

        self.stride = 0
        for attr_fmt, attr_name in zip_attrs(formats_list, self.attributes):
            try:
                components_str, data_type_str, data_size_str = re.split(
                    r"([fi])", attr_fmt
                )
                data_type = (
                    f"{data_type_str}{data_size_str}"
                    if data_size_str
                    else data_type_str
                )
                components = int(components_str) if components_str else 1
            except Exception as ex:
                raise ValueError(
                    f"Could not parse attribute format: '{attr_fmt} : {ex}'"
                )

            gl_type, byte_size = self._formats[data_type]
            self.formats.append(
                AttribFormat(
                    attr_name, gl_type, components, byte_size, offset=self.stride
                )
            )

            self.stride += byte_size * components

        self.num_vertices = self.buffer.size // self.stride


class TypeInfo:
    def __init__(
        self, name: str, enum: int, gl_type: int, gl_size: int, components: int
    ):
        self.name = name
        self.enum = enum
        self.gl_type = gl_type
        self.gl_size = gl_size
        self.components = components

    @property
    def size(self) -> int:
        return self.gl_size * self.components


class GLTypes:
    types = {
        # Floats
        constants.FLOAT: TypeInfo("FLOAT", constants.FLOAT, constants.FLOAT, 4, 1),
        constants.FLOAT_VEC2: TypeInfo(
            "FLOAT_VEC2", constants.FLOAT_VEC2, constants.FLOAT, 4, 2
        ),
        constants.FLOAT_VEC3: TypeInfo(
            "FLOAT_VEC3", constants.FLOAT_VEC3, constants.FLOAT, 4, 3
        ),
        constants.FLOAT_VEC4: TypeInfo(
            "FLOAT_VEC4", constants.FLOAT_VEC4, constants.FLOAT, 4, 4
        ),
        # Booleans (ubyte)
        constants.BOOL: TypeInfo("BOOL", constants.BOOL, constants.BOOL, 1, 1),
        constants.BOOL_VEC2: TypeInfo(
            "BOOL_VEC2", constants.BOOL_VEC2, constants.BOOL, 1, 2
        ),
        constants.BOOL_VEC3: TypeInfo(
            "BOOL_VEC3", constants.BOOL_VEC3, constants.BOOL, 1, 3
        ),
        constants.BOOL_VEC4: TypeInfo(
            "BOOL_VEC4", constants.BOOL_VEC4, constants.BOOL, 1, 4
        ),
        # Integers
        constants.INT: TypeInfo("INT", constants.INT, constants.INT, 4, 1),
        constants.INT_VEC2: TypeInfo(
            "INT_VEC2", constants.INT_VEC2, constants.INT, 4, 2
        ),
        constants.INT_VEC3: TypeInfo(
            "INT_VEC3", constants.INT_VEC3, constants.INT, 4, 3
        ),
        constants.INT_VEC4: TypeInfo(
            "INT_VEC4", constants.INT_VEC4, constants.INT, 4, 4
        ),
        # Unsigned Integers
        constants.UNSIGNED_INT: TypeInfo(
            "UNSIGNED_INT", constants.UNSIGNED_INT, constants.UNSIGNED_INT, 4, 1
        ),
        constants.UNSIGNED_INT_VEC2: TypeInfo(
            "UNSIGNED_INT_VEC2",
            constants.UNSIGNED_INT_VEC2,
            constants.UNSIGNED_INT,
            4,
            2,
        ),
        constants.UNSIGNED_INT_VEC3: TypeInfo(
            "UNSIGNED_INT_VEC3",
            constants.UNSIGNED_INT_VEC3,
            constants.UNSIGNED_INT,
            4,
            3,
        ),
        constants.UNSIGNED_INT_VEC4: TypeInfo(
            "UNSIGNED_INT_VEC4",
            constants.UNSIGNED_INT_VEC4,
            constants.UNSIGNED_INT,
            4,
            4,
        ),
        # Unsigned short (mostly used for short index buffers)
        constants.UNSIGNED_SHORT: TypeInfo(
            "UNSIGNED_SHORT", constants.UNSIGNED_SHORT, constants.UNSIGNED_SHORT, 2, 2
        ),
        # Byte
        constants.BYTE: TypeInfo("BYTE", constants.BYTE, constants.BYTE, 1, 1),
        constants.UNSIGNED_BYTE: TypeInfo(
            "UNSIGNED_BYTE", constants.UNSIGNED_BYTE, constants.UNSIGNED_BYTE, 1, 1
        ),
    }

    @classmethod
    def get(cls, enum: int):
        try:
            return cls.types[enum]
        except KeyError:
            raise ValueError(
                f"Unknown GL type {enum}. It may needed added to arcade.gl.types"
            )
