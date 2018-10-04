import typing
import os.path

from .level import LevelFile


class World:
    level: LevelFile

    def __init__(self, path_to_world_folder: str):
        if not isinstance(path_to_world_folder, str):
            raise TypeError(f"a string is required, not '{type(path_to_world_folder)}'")

        self.level_file = os.path.join(path_to_world_folder, "level.dat")
        self.level = LevelFile(self.level_file)

    def __str__(self):
        return str(self.level.nbt_tree["Data"]["LevelName"])

    def __repr__(self):
        return repr(self.level.nbt_tree["Data"]["LevelName"])
