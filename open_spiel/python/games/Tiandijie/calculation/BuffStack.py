from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
from typing import List
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma


class BuffStack:
    def __init__(self, max_stack: int, affected_attributes: List[str]):
        self.max_stack = max_stack
        self.affected_attributes = affected_attributes


buff_max_stack = {
    "xianzui": BuffStack(
        3, [ma.physical_damage_reduction_percentage, ma.physical_damage_percentage]
    ),
    "xiayi": BuffStack(3, []),
    "chongzhen": BuffStack(
        2,
        [
            ma.move_range,
            ma.physical_damage_percentage,
            ma.magic_damage_percentage,
            ma.physical_damage_reduction_percentage,
            ma.magic_damage_reduction_percentage,
        ],
    ),
    "ningbing": BuffStack(
        4,
        [
            ma.physical_damage_percentage,
            ma.magic_damage_percentage,
            ma.physical_penetration_percentage,
        ],
    ),
    "yudi": BuffStack(
        3,
        [
            ma.physical_damage_percentage,
            ma.magic_damage_percentage,
            ma.physical_damage_reduction_percentage,
            ma.magic_damage_reduction_percentage,
        ],
    ),
    "chuti": BuffStack(3, [ma.physical_damage_percentage, ma.critical_percentage]),
    "changming": BuffStack(4, [ma.magic_attack_percentage]),
    "zhinian": BuffStack(
        4,
        [
            ma.physical_damage_percentage,
            ma.magic_damage_percentage,
            ma.critical_percentage,
        ],
    ),
    "silie": BuffStack(7, []),
    "baofengyan": BuffStack(5, [ma.physical_damage_percentage, ma.critical_percentage]),
    "tuipi": BuffStack(
        4,
        [
            ma.life_percentage,
            ma.attack_percentage,
            ma.defense_percentage,
            ma.magic_attack_percentage,
            ma.magic_defense_percentage,
            ma.critical_percentage,
        ],
    ),
    "lingxi": BuffStack(14, []),
    "hunpozhili": BuffStack(5, []),
    "yingwei": BuffStack(6, []),
    "jianwei": BuffStack(3, []),
    "linghui": BuffStack(14, []),
    "juexin": BuffStack(
        5,
        [
            ma.life_percentage,
            ma.attack_percentage,
            ma.defense_percentage,
            ma.magic_attack_percentage,
            ma.magic_defense_percentage,
            ma.critical_percentage,
        ],
    ),
}


def calculate_buff_with_max_stack(buff: Buff, modifier_value: float, attr_name: str):
    if buff.temp.id in buff_max_stack:
        target_buff_stack = buff_max_stack[buff.temp.id]
        max_stack = target_buff_stack.max_stack
        if attr_name in target_buff_stack.affected_attributes:
            return modifier_value * min(buff.stack, max_stack)
    return modifier_value


def get_buff_max_stack(buff_id: str):
    return buff_max_stack[buff_id][0] if buff_id in buff_max_stack else 1


stone_max_stack = {
    "wanghuan": BuffStack(5, [
        ma.attack_percentage,
        ma.magic_attack_percentage,
        ma.defense_percentage,
        ma.magic_defense_percentage,
        ma.luck_percentage,]),
}


def calculate_stone_with_max_stack(stone, modifier_value: float, attr_name: str):
    if stone.id in stone_max_stack:
        target_buff_stack = stone_max_stack[stone.id]
        max_stack = target_buff_stack.max_stack
        if attr_name in target_buff_stack.affected_attributes:
            return modifier_value * min(stone.stack, max_stack)
    return modifier_value

