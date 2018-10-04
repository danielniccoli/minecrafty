# minecrafty

An extensive Minecraft worlds parser in the making.

## How it works

Right now you can completely load a single or multi player world (read-only). 

### Loading a saved world

To load the entire world, call `minecrafty.World()`.

```python
from minecrafty import World

# Choose a single player world from your computer …
world_folder = r".\.minecraft\saves\New World" 

# or a multi player world from your server.
world_folder = "./minecraft/world" 

# Pass the folder to `minecrafty.World`.
world = World(world_folder)
```

### Loading a level.dat directly

You may also call `minecrafty.Level()` directly. 

```python
from minecrafty import Level

# Choose a single player world from your computer …
level_file = r".\.minecraft\saves\New World\level.dat" 

# or a multi player world from your server.
level_file = "./minecraft/world/level.dat" 

# Pass the folder to `minecrafty.World`.
level = Level(level_file)
```

### Accessing the NBT data

```python
# The NBT data is stored in the `nbt_tree` attribute of the level.
print(world.level.nbt_tree["Data"]["LevelName"])
New World

# Or if you loaded the `Level()` directly:
print(level.nbt_tree["Data"]["LevelName"])
New World
```


