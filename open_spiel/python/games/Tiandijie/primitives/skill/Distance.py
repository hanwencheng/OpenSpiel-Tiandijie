from enum import Enum

from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Professions


class DistanceType(Enum):
    NORMAL = 0
    CROSS = 1
    ARCHER = 2


class Distance:
    def __init__(self, distance_type: DistanceType, distance_value: int):
        self.distance_type = distance_type
        self.distance_value = distance_value


distance_profession_dict = {
    profession: Distance(DistanceType.NORMAL, 1) if profession in [Professions.WARRIOR, Professions.SWORDSMAN, Professions.GUARD, Professions.RIDER] else Distance(DistanceType.ARCHER, 2)
    for profession in Professions
}
