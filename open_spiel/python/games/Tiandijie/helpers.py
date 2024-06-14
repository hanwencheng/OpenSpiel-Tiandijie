from __future__ import annotations

import random
from typing import TYPE_CHECKING, List

# if TYPE_CHECKING:
from primitives.hero.HeroBasics import Professions

is_magic_profession_dict = {
    profession: True if profession in [Professions.SORCERER, Professions.PRIEST, Professions.WARRIOR] else False
    for profession in Professions
}


def random_select(target_list: List, num: int):
    return random.sample(target_list, min(len(target_list), num))


def is_normal_attack_magic(profession: Professions) -> bool:
    return is_magic_profession_dict[profession]


def compose_hero_id(hero_temp_id: str, player_id: int) -> str:
    return hero_temp_id + str(player_id)
