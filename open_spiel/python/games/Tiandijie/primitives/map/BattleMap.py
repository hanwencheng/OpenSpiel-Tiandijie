from typing import List

from open_spiel.python.games.Tiandijie.primitives.map.Terrain import Terrain
from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType
from open_spiel.python.games.Tiandijie.primitives.map.TerrainBuff import TerrainBuff

TerrainMap = List[List[Terrain]]


class BattleMap:
    def __init__(self, width, height, terrain_map):
        self.width = width
        self.height = height
        self.map: TerrainMap = [[self._init_terrain_by_type_id(terrain_map[j][i]) for i in range(width)] for j in
                                range(height)]

    @staticmethod
    def _init_terrain_by_type_id(type_id: int) -> Terrain:
        init_terrain_type = TerrainType.NORMAL
        for terrain_type in TerrainType:
            if terrain_type.value[0] == type_id:
                init_terrain_type = terrain_type
        return Terrain(init_terrain_type)

    def display_map(self):
        for row in self.map:
            print(' '.join(str(cell.terrain_type.value[0]) for cell in row))

    def set_map(self, terrain_map: List[List[int]]):
        if len(terrain_map) == self.height and len(terrain_map[0]) == self.width:
            self.map = [[self._init_terrain_by_type_id(terrain_map[j][i]) for i in range(len(terrain_map[0]))] for j in range(len(terrain_map))]

    def get_terrain(self, position):
        x, y = position
        if 0 <= y < len(self.map) and 0 <= x < len(self.map[0]):
            return self.map[position[1]][position[0]]
        return False

    def set_terrain(self, position, terrain_type):
        print("set_terrain", position)
        self.map[position[1]][position[0]].set_terrain(terrain_type)

    def set_terrain_type(self, position, terrain_type: TerrainType):
        self.map[position[1]][position[0]].terrain_type = terrain_type

    def add_hero(self, position):
        terrain_type = TerrainType.HERO_SPAWN
        self.map[position[1]][position[0]] = Terrain(terrain_type)

    def hero_move(self, start, end):
        if start == end:
            return
        self.map[end[1]][end[0]].set_terrain(TerrainType.HERO_SPAWN)
        self.map[start[1]][start[0]].set_terrain(TerrainType.NORMAL)

    def add_terrain_buff(self, position, buff, duration):
        self.map[position[1]][position[0]].buff = TerrainBuff(buff, duration, 1)

    def remove_terrain_buff_by_name(self, buff_id):
        for row in self.map:
            for cell in row:
                if cell.buff is not None and cell.buff.temp.id == buff_id:
                    cell.buff = None

    def remove_terrain_by_name(self, terrain_type):
        for row in self.map:
            for cell in row:
                if cell.terrain_type == terrain_type:
                    cell.terrain_type = TerrainType.NORMAL

    def remove_hero(self, position):
        self.map[position[1]][position[0]] = Terrain(TerrainType.NORMAL)
