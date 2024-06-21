from enum import Enum


class TerrainType(Enum):
    NORMAL = (0, True, True, "Normal")
    FLYABLE_OBSTACLE = (1, False, True, "Flyable Obstacle")  # cannot generate buff
    IMPASSABLE_OBSTACLE = (
        2,
        False,
        False,
        "Impassable Obstacle",
    )  # cannot generate buff
    HERO_SPAWN = (3, False, False, "Hero Spawn")
    EFFECT_SPAWN = (4, True, True, "Effect Spawn")
    ZHUOWU = (5, True, True, "DIE")
    JINWUQI = (6, False, False, "JINWUQI")
