from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.map.TerrainBuff import TerrainBuff
    from primitives.map.TerrainType import TerrainType


class Collectable:
    pass


class Terrain:
    def __init__(self, terrain_type: 'TerrainType'):
        self.terrain_type = terrain_type
        self.buff: 'TerrainBuff' or None = None
        self.collectable: 'Collectable' or None = None

    def remove_buff(self):
        self.buff = None
