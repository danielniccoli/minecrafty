import gzip
import io

from .nbt import TAG_COMPOUND, TagEnd, NbtTag


class LevelFileDecodeError(ValueError):
    pass


class Level:
    file: str
    nbt_tree: NbtTag
    is_compressed: bool

    _buffer: io.BytesIO

    def __init__(self, level_file: [str, io.BufferedIOBase]):
        """Takes a file path or a subclass if io.BufferedIOBase."""

        if isinstance(level_file, str):
            self.file = level_file
            with open(level_file, "rb") as f:
                self._buffer = io.BytesIO(f.read())
        elif isinstance(level_file, io.BufferedIOBase):
            self.file = level_file.name
            self._buffer = io.BytesIO(level_file.read())

        magic_bytes = self._buffer.getbuffer()[:2].tobytes()
        self.is_compressed = True if magic_bytes[:2] == b"\x1f\x8b" else False
        if self.is_compressed:
            self._buffer = io.BytesIO(gzip.decompress(self._buffer.read()))

        root_tag_type = int.from_bytes(self._buffer.read(1), "big")
        if isinstance(root_tag_type, TagEnd):
            raise LevelFileDecodeError(f"First byte of a level file file must not be {TAG_END:#x}!")
        if root_tag_type != TAG_COMPOUND:
            raise LevelFileDecodeError(f"First byte of a level file must be {TAG_COMPOUND:#x}, was {root_tag_type:#x}!")
        self.nbt_tree = NbtTag.get_nbt_class(root_tag_type)(self._buffer)

        if self._buffer.read():
            raise LevelFileDecodeError("Unexpected NBT tags found at the end of the file.")
