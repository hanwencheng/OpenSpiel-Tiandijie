import string
from typing import Tuple, Union

from open_spiel.python.games.Tiandijie.primitives.hero.BasicAttributes import (
    JishenProfessions,
    ShenbinProfessions,
    HuazhenProfessions,
    XingpanProfessions,
    HuazhenAmplifier,
    XingpanAmplifier,
    AttributesTuple,
    NeigongAmplifier,
)
from open_spiel.python.games.Tiandijie.wunei import WuneiProfessions

MAXIMUM_LEVEL = 70
WUNEI_AMPLIFIERS = (25, 25, 25, 25, 25, 0)
JISHEN_AMPLIFIERS = (10, 0, 10, 0, 10, 0)
XINGYAO_AMPLIFIERS = (4, 4, 4, 4, 4, 0)
ATTRIBUTE_NAMES = ["life", "attack", "defense", "magic_attack", "magic_defense", "luck"]


def get_neigong_enum_value(identifier):
    return NeigongAmplifier[identifier].value


def get_enum_value(enum_class, identifier: Union[int, str]):
    if isinstance(identifier, int):
        # Fetch by index
        return list(enum_class)[identifier].value[1:]
    elif isinstance(identifier, str):
        # Fetch by name
        return enum_class[identifier].value[1:]
    else:
        raise ValueError("Identifier must be an enum name or index")


class ProfessionAttributes:
    def __init__(
        self, wunei, jishen, shenbin, huazhen, xingpan, huazhen_amp, xingpan_amp
    ):
        self.wunei: AttributesTuple = wunei
        self.jishen: AttributesTuple = jishen
        self.shenbin: AttributesTuple = shenbin
        self.huazhen: AttributesTuple = huazhen
        self.xingpan: AttributesTuple = xingpan
        self.huazhen_amp: AttributesTuple = huazhen_amp
        self.xingpan_amp: AttributesTuple = xingpan_amp


def get_profession_values(profession_identifier: string, temp_id: string = None) -> ProfessionAttributes:
    if temp_id == "mohuahuangfushen":
        wunei = get_enum_value(WuneiProfessions, "MOHUAHUANGFUSHEN")
    elif temp_id == "jianxie":
        wunei = get_enum_value(WuneiProfessions, "JIANXIE")
    else:
        wunei = get_enum_value(WuneiProfessions, profession_identifier.name)

    jishen = get_enum_value(JishenProfessions, profession_identifier.name)
    shenbin = get_enum_value(ShenbinProfessions, profession_identifier.name)
    huazhen = get_enum_value(HuazhenProfessions, profession_identifier.name)
    xingpan = get_enum_value(XingpanProfessions, profession_identifier.name)
    huazhen_amp = get_enum_value(HuazhenAmplifier, profession_identifier.name)
    xingpan_amp = get_enum_value(XingpanAmplifier, profession_identifier.name)

    # Assuming you want to return these as a single object (like a dictionary)
    return ProfessionAttributes(
        wunei, jishen, shenbin, huazhen, xingpan, huazhen_amp, xingpan_amp
    )


class Attributes(tuple):
    def __new__(cls, life, attack, defense, magic_attack, magic_defense, luck):
        return super(Attributes, cls).__new__(
            cls, (life, attack, defense, magic_attack, magic_defense, luck)
        )

    def __init__(self, life, attack, defense, magic_attack, magic_defense, luck):
        self.life: int = life
        self.attack: int = attack
        self.defense: int = defense
        self.magic_attack: int = magic_attack
        self.magic_defense: int = magic_defense
        self.luck: int = luck

    def __len__(self):
        return 6

    def __getitem__(self, index):
        if index == "life":
            return self.life
        elif index == "attack":
            return self.attack
        elif index == "defense":
            return self.defense
        elif index == "magic_attack":
            return self.magic_attack
        elif index == "magic_defense":
            return self.magic_defense
        elif index == "luck":
            return self.luck
        else:
            raise IndexError("Index out of range")
        # return self.values[index]  # Implement subscriptability directly on the class

    @property
    def value(self):
        return self.values


def calculate_max_added_value(
    wunei_profession: AttributesTuple,
    jishen_profession: AttributesTuple,
    shenbin_profession: AttributesTuple,
    huazhen_profession: AttributesTuple,
    xingpan_profession: AttributesTuple,
) -> AttributesTuple:

    calculated_values = tuple(
        jishen_profession[i]
        + shenbin_profession
        [i] * (69 / 10 + 1)
        + huazhen_profession[i]
        + sum(wunei_profession[i])
        + xingpan_profession[i]
        for i in range(6)
    )

    return calculated_values


def generate_max_level_attributes(
    initial_attributes: Attributes,
    growth_coefficient_tuple: AttributesTuple,
    profession_identifier: string or int,
    temp_id: string,
) -> Attributes:
    profession_values = get_profession_values(profession_identifier, temp_id)
    added_attributes_tuple = calculate_max_added_value(
        profession_values.wunei,
        profession_values.jishen,
        profession_values.shenbin,
        profession_values.huazhen,
        profession_values.xingpan,
    )
    value_list = []
    for attr_name, growth_coefficient, added_value in zip(
        ATTRIBUTE_NAMES, growth_coefficient_tuple, added_attributes_tuple
    ):
        initial_value = getattr(initial_attributes, attr_name)
        value_list.append(
            initial_value + MAXIMUM_LEVEL * growth_coefficient + added_value
        )

    return Attributes(*value_list)


def multiply_attributes(basic_attributes: Attributes, identifier: string) -> Attributes:
    profession_values = get_profession_values(identifier)
    xingpan_amplifiers = profession_values.xingpan_amp
    huazhen_amplifiers = profession_values.huazhen_amp
    new_attributes_value_list = []
    for (
        attr_name,
        xingpan_amplifier,
        huazhen_amplifier,
        wunei_amplifier,
        jishen_amplifier,
        xingyao_amplifier,
    ) in zip(
        ATTRIBUTE_NAMES,
        xingpan_amplifiers,
        huazhen_amplifiers,
        WUNEI_AMPLIFIERS,
        JISHEN_AMPLIFIERS,
        XINGYAO_AMPLIFIERS,
    ):
        current_value = getattr(basic_attributes, attr_name)
        new_attributes_value_list.append(
            round(
                current_value
                * (
                    1
                    + xingpan_amplifier / 100
                    + huazhen_amplifier / 100
                    + wunei_amplifier / 100
                    + jishen_amplifier / 100
                    + xingyao_amplifier / 100
                )
            )
        )

    return Attributes(*new_attributes_value_list)
