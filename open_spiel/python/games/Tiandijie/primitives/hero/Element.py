import enum


class Elements(enum.IntEnum):
    NONE = 0  # 无
    FIRE = 1  # 火
    WATER = 2  # 冰
    THUNDER = 3  # 雷
    LIGHT = 4  # 光
    DARK = 5  # 暗
    ETHEREAL = 6  # 幽


class ElementRelationships(enum.IntEnum):
    ADVANTAGE = 0
    DISADVANTAGE = 1
    NEUTRAL = 2


elemental_advantage = {
    Elements.FIRE: Elements.THUNDER,
    Elements.THUNDER: Elements.WATER,
    Elements.WATER: Elements.FIRE,
    Elements.LIGHT: Elements.DARK,
    Elements.DARK: Elements.ETHEREAL,
    Elements.ETHEREAL: Elements.LIGHT,
}

elemental_disadvantage = {
    Elements.FIRE: Elements.WATER,
    Elements.THUNDER: Elements.FIRE,
    Elements.WATER: Elements.THUNDER,
    Elements.LIGHT: Elements.ETHEREAL,
    Elements.DARK: Elements.LIGHT,
    Elements.ETHEREAL: Elements.DARK,
}

elemental_multiplier = {
    ElementRelationships.ADVANTAGE: 1.3,
    ElementRelationships.DISADVANTAGE: 0.75,
    ElementRelationships.NEUTRAL: 1,
}


def get_elemental_relationship(
    base_element: Elements, compare_element: Elements
) -> ElementRelationships:
    if (
        base_element in elemental_advantage
        and elemental_advantage[base_element] == compare_element
    ):
        return ElementRelationships.ADVANTAGE
    elif (
        base_element in elemental_disadvantage
        and elemental_disadvantage[base_element] == compare_element
    ):
        return ElementRelationships.DISADVANTAGE
    else:
        return ElementRelationships.NEUTRAL


def get_elemental_multiplier(elemental_relationship: ElementRelationships) -> float:
    return elemental_multiplier[elemental_relationship]
