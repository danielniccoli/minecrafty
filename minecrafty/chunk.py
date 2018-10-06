import io
import zlib

from minecrafty.nbt import NbtTag


class Chunk:
    _buffer: str

    def __init__(self, buffer: [io.BufferedIOBase]):
        """Takes a file path or a subclass if io.BufferedIOBase."""
        if isinstance(buffer, io.BufferedIOBase):
            self._buffer = buffer
        else:
            raise TypeError(f"{__class__} requires type {type(str)} or {type(io.BufferedIOBase)}, "
                            f"not '{type(path_to_world_folder)}'")

        size = int.from_bytes(self._buffer.read(4), "big", signed=False)
        compression_type = int.from_bytes(self._buffer.read(1), "big", signed=False)

        if compression_type == 2:
            self._buffer = io.BytesIO(zlib.decompress(self._buffer.read(size)))
        else:
            raise ValueError("Unexpected compression type.")

        root_nbt_tag = int.from_bytes(self._buffer.read(1), "big", signed=False)
        root_nbt_class = NbtTag.get_nbt_class(root_nbt_tag)
        self.nbt_tree = root_nbt_class(self._buffer)


