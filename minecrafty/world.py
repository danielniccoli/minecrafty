import os.path

from .region import Regions
from .level import Level


class World:
    folder: str
    level: Level
    regions: Regions

    def __init__(self, path_to_world_folder: str):
        self.folder = path_to_world_folder
        if not isinstance(self.folder, str):
            raise TypeError(f"{__class__} requires type {type(str)}, not '{type(path_to_world_folder)}'")

        self.level_file = os.path.join(self.folder, "level.dat")
        self.level = Level(self.level_file)

        regions_folder = os.path.join(self.folder, "region")
        self.regions = Regions(regions_folder)

    def __str__(self):
        return str(self.level.nbt_tree["Data"]["LevelName"])

    def __repr__(self):
        return repr(self.level.nbt_tree["Data"]["LevelName"])
