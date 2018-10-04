# minecrafty

An extensive Minecraft worlds parser in the making.

## How it works

Right now you can completely load a single or multi player world (read-only). 

### Loading a saved world

```python
from minecrafty import World

# Choose a single player world from your computer …
world_folder = r"C:\…\.minecraft\saves\New World" 

# or a multi player world from your server.
world_folder = "/opt/minecraft/world" 

# Pass the folder to `minecrafty.World`.
world = World(world_folder)
```

### Accessing the NBT data

```python
# The NBT data is stored in the `nbt_tree` attribute of the level.
print(world.level.nbt_tree["Data"]["LevelName"])
New World
```


