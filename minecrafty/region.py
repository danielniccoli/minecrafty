import datetime
import io
import os
import typing

from .chunk import Chunk


class Regions(dict):
    folder: str
    region_files: typing.Dict[typing.Tuple[int, int], str]

    def __init__(self, path_to_region_folder):
        self.folder = path_to_region_folder
        if not isinstance(self.folder, str):
            raise TypeError(f"{__class__} requires type {type(str)}, not '{type(path_to_world_folder)}'")

        for item in os.listdir(self.folder):
            split_item = item.split(".")
            extension = split_item[3]

            if extension == "mca":
                region_file = os.path.join(self.folder, item)
                x = split_item[1]
                z = split_item[2]
                self[x, z] = Region(region_file)
            else:
                raise TypeError("Unexpected file extension {item[-4:]}")


class Region(dict):
    _INDEX_SIZE = 4
    _TIMESTAMP_SIZE = 4
    _CHUNKS_IN_REGION = 32 * 32
    _SECTOR_SIZE = 4096

    file: str

    _buffer: io.BytesIO

    def __init__(self, region_file: [str, io.BufferedIOBase]):
        """Takes a file path or a subclass if io.BufferedIOBase."""

        if isinstance(region_file, str):
            self.file = region_file
            with open(region_file, "rb") as f:
                self._buffer = io.BytesIO(f.read())
        elif isinstance(region_file, io.BufferedIOBase):
            self.file = region_file.name
            self._buffer = io.BytesIO(region_file.read())
        else:
            raise TypeError(f"{__class__} requires type {type(str)} or {type(io.BufferedIOBase)}, "
                            f"not '{type(path_to_world_folder)}'")

        _indices_buffer = io.BytesIO(self._buffer.read(self._INDEX_SIZE * self._CHUNKS_IN_REGION))
        _timestamps_buffer = io.BytesIO(self._buffer.read(self._TIMESTAMP_SIZE * self._CHUNKS_IN_REGION))

        total_length = 0
        # Read chunk index (32(x) * 32(z) * 4 bytes)
        for x, z in [(x, z) for x in range(32) for z in range(32)]:
            offset = int.from_bytes(_indices_buffer.read(3), "big", signed=False) * self._SECTOR_SIZE
            size = int.from_bytes(_indices_buffer.read(1), "big", signed=False) * self._SECTOR_SIZE
            timestamp = int.from_bytes(_timestamps_buffer.read(4), "big", signed=False)
            if not offset and not size:
                continue  # Chunk does not exist
            timestamp = datetime.datetime.fromtimestamp(timestamp)

            self._buffer.seek(offset)
            self[x, z] = Chunk(self._buffer)