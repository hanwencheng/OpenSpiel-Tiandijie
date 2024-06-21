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
        self.caster_id = None

    def remove_buff(self):
        self.buff = None

    def set_terrain(self, terrain_type: 'TerrainType', caster_id):
        self.terrain_type = terrain_type
        self.caster_id = caster_id

    def remove_terrain(self):
        self.terrain_type = TerrainType.NORMAL
        self.caster_id = None

    def get_terrain_caster_id(self):
        return self.caster_id

    def set_hero_spawn(self):
        self.terrain_type = TerrainType.HERO_SPAWN

    def init_terrain_type(self, init_type=TerrainType.NORMAL):
        self.terrain_type = init_type
        self.caster_id = None
