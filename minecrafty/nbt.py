import ctypes
import gzip
import io
import typing
from abc import abstractmethod, ABCMeta
from struct import unpack_from

TAG_END: int = 0
TAG_BYTE: int = 1
TAG_SHORT: int = 2
TAG_INT: int = 3
TAG_LONG: int = 4
TAG_FLOAT: int = 5
TAG_DOUBLE: int = 6
TAG_BYTE_ARRAY: int = 7
TAG_STRING: int = 8
TAG_LIST: int = 9
TAG_COMPOUND: int = 10
TAG_INT_ARRAY: int = 11
TAG_LONG_ARRAY: int = 12

_SIZE_TYPE_IDENTIFIER = 1
_SIZE_NAME_IDENTIFIER = 2
_SIZE_LIST_LENGTH_IDENTIFIER = 4


class NbtDecodeError(Exception):
    pass


class NbtTag(metaclass=ABCMeta):
    @property
    @abstractmethod
    def type(self) -> int:
        """Attribute: Return tag 'type'"""
        pass

    @property
    @abstractmethod
    def has_name(self):
        """Attribute: Return True if tag 'type' has name."""
        pass

    def __init__(self, stream, omit_name=False):
        self.omit_name = omit_name
        self.parse(stream)

    def __eq__(self, other: object) -> bool:
        if other.__class__ is self.__class__:
            return other.type == self.type
        elif other.__class__ is int:
            return other == self.type
        elif other.__class__ is bytes:
            return other == self.type.to_bytes(1, "big")
        else:
            return False

    @staticmethod
    def get_nbt_class(tag_type):
        if tag_type == TAG_END:
            return TagEnd
        if tag_type == TAG_BYTE:
            return TagByte
        elif tag_type == TAG_SHORT:
            return TagShort
        elif tag_type == TAG_INT:
            return TagInt
        elif tag_type == TAG_LONG:
            return TagLong
        elif tag_type == TAG_FLOAT:
            return TagFloat
        elif tag_type == TAG_DOUBLE:
            return TagDouble
        elif tag_type == TAG_BYTE_ARRAY:
            return TagByteArray
        elif tag_type == TAG_STRING:
            return TagString
        elif tag_type == TAG_LIST:
            return TagList
        elif tag_type == TAG_COMPOUND:
            return TagCompound
        elif tag_type == TAG_INT_ARRAY:
            return TagIntArray
        elif tag_type == TAG_LONG_ARRAY:
            return TagLongArray

    @abstractmethod
    def parse(self, stream: typing.BinaryIO = None):
        """
        Parses the stream and sets the tag class attributes.

        When overriding, first call super().parse() for automatic name parsing.
        """
        if not stream:
            raise TypeError("parse() missing required argument 'stream' (pos 2)")
        if self.has_name:
            if self.omit_name:
                self.name = ""
            else:
                self.name = self._parse_string(stream)

    def _parse_string(self, stream: typing.BinaryIO) -> str:
        """Parses the tag name."""
        length_of_name = int.from_bytes(stream.read(_SIZE_NAME_IDENTIFIER), "big")
        if length_of_name == 0:
            # raise ValueError(f"The length of the tag name must be greater than 1, not {length_of_name}")
            # ^ Apparently not ...
            pass
        else:
            utf8_bytes = stream.read(length_of_name)
            return utf8_bytes.decode("utf-8")

    def get_type(identifier: [int, bytes]):
        return NbtTag(identifier)
        # todo: check which errors are thrown for from types
        # raise ValueError("Not a valid identifier type: {identifier}. Must be of type int or bytes.")

    def __repr__(self):
        repr_name = ""
        repr_value = ""
        if self.has_name:
            repr_name = f" name={self.name}"
        if "value" in self.__dict__:
            repr_value = f" value={self.value}"
        return f"<{self.__class__.__name__}{repr_name}{repr_value}>"


class NbtNumericalTag(NbtTag):
    has_name = False
    _value: int = None

    data_type: ctypes._SimpleCData = None
    data_size: int = None  # Size of the data_type in bytes. Example: data_size=2 for ctypes.c_int16

    @property
    def data_size(self):
        if self.data_size is None:
            raise NotImplementedError("Subclass must set `data_size` attribute")

    @property
    def data_type(self):
        if self.data_type is None:
            raise NotImplementedError("Subclass must set `data_type` attribute")

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, obj: [int, float, complex, bytes]):
        if isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, complex):
            self._value = obj
        elif isinstance(obj, bytes):
            self._value = obj
            self._value = self.data_type(int.from_bytes(obj, "big")).value

    def parse(self, stream):
        super().parse(stream=stream)
        self.value = stream.read(self.data_size)

    def __mul__(self, other):
        if hasattr(other, "value"):
            return self.value * other.value
        else:
            return self.value * other

    def __add__(self, other):
        if hasattr(other, "value"):
            return self.value + other.value
        else:
            return self.value + other

    def __repr__(self):
        return str(self.value)


class TagEnd(NbtTag):
    type: int = TAG_END
    has_name: bool = False

    def parse(self, buffer):
        pass


class TagByte(NbtNumericalTag):
    type: int = TAG_BYTE
    data_type: ctypes._SimpleCData = ctypes.c_int8
    data_size = 1
    has_name: bool = True
    name: str = None

    def __repr__(self):
        return

    def __str__(self):
        return str(self.value)


class TagShort(NbtNumericalTag):
    type: int = TAG_SHORT
    data_type: ctypes._SimpleCData = ctypes.c_int16
    data_size = 2
    has_name: bool = True
    name: str = None


class TagInt(NbtNumericalTag):
    type: int = TAG_SHORT
    data_type: ctypes._SimpleCData = ctypes.c_int32
    data_size = 4
    has_name: bool = True
    name: str = None


class TagLong(NbtNumericalTag):
    type: int = TAG_LONG
    data_type: ctypes._SimpleCData = ctypes.c_int64
    data_size = 8
    has_name: bool = True
    name: str = None


class TagFloat(NbtNumericalTag):
    type: int = TAG_FLOAT
    data_type: ctypes._SimpleCData = ctypes.c_float
    data_size = 4
    has_name: bool = True
    name: str = None


class TagDouble(NbtNumericalTag):
    type: int = TAG_DOUBLE
    data_type: ctypes._SimpleCData = ctypes.c_double
    data_size = 8
    has_name: bool = True
    name: str = None


class TagString(NbtTag):
    type: int = TAG_STRING
    has_name: bool = True
    name: str = None
    value: str = None

    def parse(self, stream: typing.BinaryIO = None):
        super().parse(stream)
        self.value = self._parse_string(stream)

    def __str__(self):
        return self.value


class TagByteArray(NbtTag, bytearray):
    type: int = TAG_BYTE_ARRAY
    has_name: bool = True
    name: str = None

    def parse(self, stream: typing.BinaryIO = None):
        super().parse(stream)
        array_length = int.from_bytes(stream.read(_SIZE_LIST_LENGTH_IDENTIFIER), "big")
        self[:] = stream.read(array_length)

    def __repr__(self):
        pass

    def __str__(self):
        pass


class TagList(NbtTag, list):
    type: int = TAG_LIST
    has_name: bool = True
    name: str = None

    def parse(self, stream: typing.BinaryIO = None):
        super().parse(stream)
        list_type = int.from_bytes(stream.read(_SIZE_TYPE_IDENTIFIER), "big")
        list_length = int.from_bytes(stream.read(_SIZE_LIST_LENGTH_IDENTIFIER), "big")
        for i in range(list_length):
            tag_class = NbtTag.get_nbt_class(list_type)
            self.append(tag_class(stream, omit_name=True))


class TagCompound(NbtTag, dict):
    type: int = TAG_COMPOUND
    has_name: bool = True

    def parse(self, stream: typing.BinaryIO = None):
        super().parse(stream)
        while True:
            next_tag_type = int.from_bytes(stream.read(_SIZE_TYPE_IDENTIFIER), "big")
            if next_tag_type == TAG_END:
                break
            tag_class = NbtTag.get_nbt_class(next_tag_type)
            child = tag_class(stream)
            self[child.name] = child

    def __repr__(self):
        # TODO Figure out how to call super / OrderedDict.__repr__()
        return f"<TagCompound name='{self.name}' [..HELP..]>"


class TagIntArray(NbtTag, list):
    type: int = TAG_INT_ARRAY
    has_name: bool = True

    def parse(self, stream: typing.BinaryIO = None):
        super().parse(stream)
        array_length = int.from_bytes(stream.read(_SIZE_LIST_LENGTH_IDENTIFIER), "big")
        self[:] = unpack_from(f">{array_length}i", stream.read(array_length * TagInt.data_size))
        i = 0


class TagLongArray(NbtTag, list):
    type: int = TAG_LONG_ARRAY
    has_name: bool = True

    def parse(self, stream: typing.BinaryIO = None):
        super().parse(stream)
        array_length = int.from_bytes(stream.read(_SIZE_LIST_LENGTH_IDENTIFIER), "big")
        self[:] = unpack_from(f">{array_length}q", stream.read(array_length * TagLong.data_size))

# class Nbt:
#     def __init__(self, buffer):
#         """Takes either one of file path, binary file object or binary buffered object."""
#
#         tag_tree = []  # return value
#         with self.get_buffer(cached=False) as stream:
#             while True:
#                 next_byte = stream.read(_SIZE_TYPE_IDENTIFIER)
#                 if not next_byte:
#                     break
#                 next_tag_type = int.from_bytes(next_byte, "big")
#
#                 if next_tag_type == TAG_END and stream.tell() == 1:
#                     raise NbtDecodeError(f"First byte of a NBT file must not be {TAG_END:#x}!")
#
#                 tag_class = NbtTag.get_nbt_class(next_tag_type)
#                 tag_tree.append(tag_class(stream))
#
#         return tag_tree
