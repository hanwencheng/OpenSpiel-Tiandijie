import enum

MoveRange = (int, int)  # (move_type, move_range, attack_range)
AttributesTuple = (
    float, float, float, float, float, float)  # (life, attack, defense, magic_attack, magic_defense, luck)


class MovesRanges(enum.Enum):
    SWORDSMAN = (0, 3, 1)
    SWORDSMAN_WITH_MAGIC = (1, 3, 1)  # LIFE, ATTACK, DEFENSE, MAGIC_ATTACK, MAGIC_DEFENSE, LUCK
    PRIEST = (2, 3, 2)
    ARCHER = (3, 3, 2)
    RIDER_HIGH_DAMAGE = (4, 5, 1)
    RIDER_BALANCE = (5, 5, 1)
    GUARD_STRIKE = (6, 3, 1)
    GUARD_PROTECT = (7, 3, 1)
    SORCERER_DAMAGE = (8, 3, 2)
    SORCERER_ASSIST = (9, 3, 2)
    WARRIOR = (10, 4, 1)


class JishenProfessions(enum.Enum):
    SWORDSMAN = (0, 867, 268, 335, 0, 202, 0)
    SWORDSMAN_WITH_MAGIC = (1, 867, 0, 335, 268, 202, 0)  # LIFE, ATTACK, DEFENSE, MAGIC_ATTACK, MAGIC_DEFENSE, LUCK
    PRIEST = (2, 991, 0, 310, 0, 366, 0)
    ARCHER = (3, 643, 251, 299, 0, 224, 155)
    RIDER_HIGH_DAMAGE = (4, 659, 244, 288, 0, 275, 200)
    RIDER_BALANCE = (5, 683, 259, 266, 0, 297, 133)
    GUARD_STRIKE = (6, 1219, 155, 377, 0, 193, 0)
    GUARD_PROTECT = (7, 1370, 0, 397, 0, 211, 0)
    SORCERER_DAMAGE = (8, 732, 0, 262, 259, 350, 0)
    SORCERER_ASSIST = (9, 770, 0, 280, 244, 375, 0)
    WARRIOR = (10, 810, 0, 288, 259, 308, 0)


class ShenbinProfessions(enum.Enum):
    SWORDSMAN = (0, 85, 79, 0, 0, 0, 0)
    SWORDSMAN_WITH_MAGIC = (1, 85, 0, 0, 79, 0, 0)
    PRIEST = (2, 77, 0, 0, 63, 0, 0)
    ARCHER = (3, 76, 74, 0, 0, 0, 0)
    RIDER_HIGH_DAMAGE = (4, 78, 73, 0, 0, 0, 0)
    RIDER_BALANCE = (5, 81, 77, 0, 0, 0, 0)
    GUARD_STRIKE = (6, 90, 75, 0, 0, 0, 0)
    GUARD_PROTECT = (7, 98, 73, 0, 0, 0, 0)  # include wuxiang.mifu
    SORCERER_DAMAGE = (8, 71, 0, 0, 77, 0, 0)
    SORCERER_ASSIST = (9, 76, 0, 0, 73, 0, 0)
    WARRIOR = (10, 76, 0, 0, 73, 0, 0)


class HuazhenProfessions(enum.Enum):
    SWORDSMAN = (0, 96, 45, 34, 0, 21, 35)
    SWORDSMAN_WITH_MAGIC = (1, 96, 0, 34, 45, 21, 35)
    PRIEST = (2, 84, 0, 29, 36, 38, 30)
    ARCHER = (3, 86, 42, 30, 0, 23, 40)
    RIDER_HIGH_DAMAGE = (4, 88, 41, 29, 0, 28, 46)
    RIDER_BALANCE = (5, 88, 41, 29, 0, 28, 45)
    GUARD_STRIKE = (6, 114, 39, 41, 0, 21, 30)
    GUARD_PROTECT = (7, 114, 39, 41, 0, 21, 30)
    SORCERER_DAMAGE = (8, 80, 0, 27, 43, 36, 35)
    SORCERER_ASSIST = (9, 80, 0, 27, 43, 36, 35)
    WARRIOR = (10, 84, 0, 30, 43, 33, 30)


class XingpanProfessions(enum.Enum):
    SWORDSMAN = (0, 120, 45, 20, 0, 15, 0)
    SWORDSMAN_WITH_MAGIC = (1, 100, 0, 15, 42, 22, 0)
    PRIEST = (2, 105, 0, 18, 36, 24, 0)
    ARCHER = (3, 110, 42, 18, 0, 15, 0)
    RIDER_HIGH_DAMAGE = (4, 115, 42, 17, 0, 17, 0)
    RIDER_BALANCE = (5, 115, 42, 17, 0, 17, 0)
    GUARD_STRIKE = (6, 145, 36, 25, 0, 15, 0)
    GUARD_PROTECT = (7, 145, 36, 25, 0, 15, 0)
    SORCERER_DAMAGE = (8, 100, 0, 15, 42, 22, 0)
    SORCERER_ASSIST = (9, 100, 0, 15, 42, 22, 0)
    WARRIOR = (10, 105, 0, 18, 40, 18, 0)


class HuazhenAmplifier(enum.Enum):
    SWORDSMAN = (0, 4, 2, 2, 0, 2, 2)
    SWORDSMAN_WITH_MAGIC = (1, 4, 0, 2, 2, 2, 2)
    PRIEST = (2, 4, 0, 2, 2, 2, 2)
    ARCHER = (3, 4, 2, 2, 0, 2, 2)
    RIDER_HIGH_DAMAGE = (4, 4, 2, 2, 0, 2, 2)
    RIDER_BALANCE = (5, 4, 2, 2, 0, 2, 2)
    GUARD_STRIKE = (6, 4, 2, 2, 0, 2, 2)
    GUARD_PROTECT = (7, 4, 2, 2, 0, 2, 2)
    SORCERER_DAMAGE = (8, 4, 0, 2, 2, 2, 2)
    SORCERER_ASSIST = (9, 4, 0, 2, 2, 2, 2)
    WARRIOR = (10, 4, 0, 2, 2, 2, 2)


class XingpanAmplifier(enum.Enum):
    SWORDSMAN = (0, 12, 12, 20, 10, 20, 0)
    SWORDSMAN_WITH_MAGIC = (1, 12, 10, 20, 12, 20, 0)
    PRIEST = (2, 12, 10, 20, 12, 20, 0)
    ARCHER = (3, 12, 12, 20, 10, 20, 0)
    RIDER_HIGH_DAMAGE = (4, 12, 12, 20, 10, 20, 0)
    RIDER_BALANCE = (5, 12, 12, 20, 10, 20, 0)
    GUARD_STRIKE = (6, 12, 12, 20, 10, 20, 0)
    GUARD_PROTECT = (7, 12, 12, 20, 10, 20, 0)
    SORCERER_DAMAGE = (8, 12, 10, 20, 12, 20, 0)
    SORCERER_ASSIST = (9, 12, 10, 20, 12, 20, 0)
    WARRIOR = (10, 12, 10, 20, 12, 20, 0)
