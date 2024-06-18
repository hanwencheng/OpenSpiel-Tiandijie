from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.map.TerrainBuff import TerrainBuff
    from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType


class Collectable:
    pass


class Terrain:
    def __init__(self, terrain_type: 'TerrainType'):
        self.terrain_type = terrain_type
        self.buff: 'TerrainBuff' or None = None
        self.collectable: 'Collectable' or None = None

    def remove_buff(self):
        self.buff = None

    def set_terrain(self, terrain_type: 'TerrainType'):
        self.terrain_type = terrain_type
