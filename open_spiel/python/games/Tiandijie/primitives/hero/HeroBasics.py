import enum


class Gender(enum.IntEnum):
    MALE = 1
    FEMALE = 2
    OTHER = 3


class Professions(enum.Enum):
    # ID，RANGE, MOVE
    GUARD = (1, 1, 3)  # 护卫
    SWORDSMAN = (2, 1, 3)  # 侠客
    SORCERER = (3, 2, 3)  # 咒师
    PRIEST = (4, 2, 3)  # 祝由
    ARCHER = (5, 2, 3)  # 羽士
    RIDER = (6, 1, 5)  # 御风
    WARRIOR = (7, 1, 4)  # 斗将


class HideProfessions(enum.Enum):
    # ID，RANGE, MOVE
    GUARD_PROTECT = (1, 1, 3)  # 护卫
    GUARD_STRIKE = (1, 1, 3)  # 反击护卫
    SWORDSMAN = (2, 1, 3)  # 侠客
    SORCERER_ASSIST = (3, 2, 3)  # 辅助咒师
    SORCERER_DAMAGE = (3, 2, 3)  # 输出咒师
    PRIEST = (4, 2, 3)  # 祝由
    ARCHER = (5, 2, 3)  # 羽士
    RIDER_HIGH_DAMAGE = (6, 1, 5)  # 暴击御风
    RIDER_BALANCE = (6, 1, 5)  # 均衡御风
    WARRIOR = (7, 1, 4)  # 斗将
