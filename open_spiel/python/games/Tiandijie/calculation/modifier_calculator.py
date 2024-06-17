from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.calculation.Modifier import Modifier
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
    from open_spiel.python.games.Tiandijie.primitives.formation.Formation import Formation
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.Stone import Stone
    from open_spiel.python.games.Tiandijie.primitives.Passive import Passive
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_targe_in_diamond_range

from functools import reduce
from typing import List
from open_spiel.python.games.Tiandijie.calculation.BuffStack import (
    calculate_buff_with_max_stack,
    calculate_stone_with_max_stack,
)
from collections import Counter


def get_modifier_attribute_value(
    actor_instance, modifier_effect: dict, attr_name: str
) -> float:
    get_value: bool or float or int = modifier_effect.get(attr_name)
    if get_value is not None:
        if get_value is bool:
            return 1 if get_value else 0
        elif get_value is str:
            basic_name, percentage = get_value.split("_")
            return (actor_instance.initial_attributes[basic_name]) * int(percentage)
        else:
            return get_value
    return 0


def accumulate_attribute(modifiers: List[Modifier], attr_name: str) -> float:
    return reduce(lambda total, buff: total + getattr(buff, attr_name, 0), modifiers, 0)


def merge_modifier(total: Modifier, hero: Hero, attr_name: str) -> Modifier:
    setattr(
        total,
        attr_name,
        getattr(total, attr_name, 0) + getattr(hero.temp.talent, attr_name, 0),
    )
    return total


def accumulate_talents_modifier(
    attr_name: str, actor_instance: Hero, target_instance: Hero, context: Context
) -> float:
    modifier_value = 0
    for modifier_effect in actor_instance.temp.talent.modifier_effects:
        if attr_name in modifier_effect.modifier:
            is_requirement_meet = modifier_effect.requirement(
                actor_instance, target_instance, context, actor_instance.temp.talent
            )
            if is_requirement_meet > 0:
                bascic_modifier_value = get_modifier_attribute_value(
                    actor_instance, modifier_effect.modifier, attr_name
                )
                modifier_value += is_requirement_meet * bascic_modifier_value
    return modifier_value
    # partner_talents = reduce(
    #     lambda total, hero: total + getattr(hero.temp.talent, attr_name, 0),
    #     partner_heroes,
    #     float(0),
    # )
    # counter_talents = reduce(
    #     lambda total, hero: total + getattr(hero.temp.talent, attr_name, 0),
    #     counter_heroes,
    #     float(0),
    # )
    # return partner_talents + counter_talents


def get_formation_modifier(
    attr_name: str, actor_instance: Hero, target_instance: Hero, context: Context
) -> float:
    player_id = actor_instance.player_id
    current_formation: Formation = context.get_formation_by_player_id(player_id)
    basic_modifier_value = 0
    if current_formation and current_formation.is_active:
        basic_modifier_value = getattr(current_formation.temp.basic_modifier, attr_name)
        formation_modifier_effects: List[ModifierEffect] = (
            current_formation.temp.modifier_effects
        )
        for effect in formation_modifier_effects:
            if attr_name in effect.modifier:
                multiplier = effect.requirement(
                    actor_instance, target_instance, context, current_formation
                )
                if multiplier > 0:
                    basic_modifier_value += (
                        get_modifier_attribute_value(
                            actor_instance, effect.modifier, attr_name
                        )
                        * multiplier
                    )
    return basic_modifier_value


def get_buff_modifier(
    attr_name: str, actor_instance: Hero, target_instance: Hero or None, context: Context
) -> float:
    basic_modifier_value = 0
    for buff in actor_instance.buffs:
        buff_modifier_levels_effects = buff.temp.modifier_effects
        if len(buff_modifier_levels_effects) == 0:
            continue
        buff_modifier_effects: List[ModifierEffect] = buff_modifier_levels_effects[
            buff.level - 1
        ]
        for modifier_effects in buff_modifier_effects:
            if attr_name in modifier_effects.modifier:
                is_requirement_meet = modifier_effects.requirement(
                    actor_instance, target_instance, context, buff
                )
                if is_requirement_meet > 0:
                    modifier_value = get_modifier_attribute_value(
                        actor_instance, modifier_effects.modifier, attr_name
                    )
                    basic_modifier_value += (
                        is_requirement_meet
                        * calculate_buff_with_max_stack(buff, modifier_value, attr_name)
                    )
    for field_buff in context.fieldbuffs_temps.values():
        field_target_instances = context.get_hero_list_by_id(field_buff.caster_id)
        for (
            field_target_instance
        ) in field_target_instances:  # 双方同时上阵相同hero的情况
            if (
                field_target_instance
                and field_target_instance.get_field_buff_by_id(field_buff.id)
                and calculate_if_targe_in_diamond_range(
                    actor_instance, field_target_instance, field_buff.buff_range
                )
            ):
                field_buff_instance = field_target_instance.get_field_buff_by_id(
                    field_buff.id
                )
                field_buff_modifier_levels_effects = (
                    field_buff_instance.temp.modifier_effects
                )
                if len(field_buff_modifier_levels_effects) == 0:
                    continue
                field_buff_modifier_effects: List[ModifierEffect] = (
                    field_buff_modifier_levels_effects[field_buff_instance.level - 1]
                )
                for modifier_effects in field_buff_modifier_effects:
                    if attr_name in modifier_effects.modifier:
                        is_requirement_meet = modifier_effects.requirement(
                            actor_instance,
                            target_instance,
                            context,
                            field_buff_instance,
                        )
                        if is_requirement_meet > 0:
                            modifier_value = get_modifier_attribute_value(
                                actor_instance, modifier_effects.modifier, attr_name
                            )
                            basic_modifier_value += modifier_value

    return basic_modifier_value


def get_passives_modifier(passives: List[Passive], attr_name: str) -> float:
    return 0


def get_level1_modified_result(
    hero_instance: Hero, value_attr_name: str, basic: float
) -> float:
    accumulated_stones_value_modifier = accumulate_stone_attribute(
        hero_instance.stones, value_attr_name
    )
    accumulated_stones_percentage_modifier = accumulate_stone_attribute(
        hero_instance.stones, value_attr_name + "_percentage"
    )
    return (
        basic * (1 + accumulated_stones_percentage_modifier)
        + accumulated_stones_value_modifier
    )


def get_level2_modifier(
    actor_instance: Hero,
    counter_instance: Hero or None,
    attr_name: str,
    context: Context,
    is_basic: bool = False,
) -> float:
    accumulated_buffs_modifier = (
        get_buff_modifier(attr_name, actor_instance, counter_instance, context)
        if not is_basic
        else 0
    )
    accumulated_stones_effect_modifier = accumulate_suit_stone_attribute(
        actor_instance, counter_instance, attr_name, context
    )
    accumulated_talents_modifier = accumulate_talents_modifier(
        attr_name, actor_instance, counter_instance, context
    )
    accumulated_equipments_modifier = accumulate_equipments_modifier(
        attr_name, actor_instance, counter_instance, context
    )
    formation_modifier = get_formation_modifier(
        attr_name, actor_instance, counter_instance, context
    )
    accumulated_passives_modifier = get_passives_modifier(
        actor_instance.enabled_passives, attr_name
    )

    return (
        accumulated_talents_modifier
        + accumulated_buffs_modifier
        + accumulated_stones_effect_modifier
        + accumulated_equipments_modifier
        + formation_modifier
        + accumulated_passives_modifier
    )


def get_modifier(
    attr_name: str, actor_instance: Hero, counter_instance: Hero or None, context: Context
) -> float:
    accumulated_buffs_modifier = get_buff_modifier(
        attr_name, actor_instance, counter_instance, context
    )
    accumulated_talents_modifier = accumulate_talents_modifier(
        attr_name, actor_instance, counter_instance, context
    )
    accumulated_equipments_modifier = accumulate_attribute(
        actor_instance.equipments, attr_name
    )
    accumulated_passives_modifier = get_passives_modifier(
        actor_instance.enabled_passives, attr_name
    )

    return (
        accumulated_talents_modifier
        + accumulated_buffs_modifier
        + accumulated_equipments_modifier
        + accumulated_passives_modifier
    )


def get_skill_modifier(
    attr_name: str,
    actor_instance: Hero,
    counter_instance: Hero,
    skill: Skill,
    context: Context,
) -> float:
    basic_modifier_value = 0
    for effect in skill.temp.modifier_effects:
        if hasattr(effect.modifier, attr_name):
            multiplier = effect.requirement(actor_instance, counter_instance, context)
            if multiplier > 0:
                basic_modifier_value += (
                    get_modifier_attribute_value(
                        actor_instance, effect.modifier, attr_name
                    )
                    * multiplier
                )
    return basic_modifier_value


def accumulate_stone_attribute(stones: List[Stone], attr_name: str) -> float:
    return reduce(
        lambda total, indexed_stone: total
        + indexed_stone[1].effect[indexed_stone[0]].get(attr_name, 0),
        enumerate(stones),
        float(0),
    )


def accumulate_suit_stone_attribute(
    actor_instance, target_instance, attr_name: str, context
) -> float:
    suit_stone_modifier_effects_list = []
    stone_suit = None
    counter = Counter(actor_instance.stones)
    for stone, count in counter.items():
        if count >= 2:
            suit_stone_modifier_effects_list.append(stone.value[count - 2])
            stone_suit = stone
            if count > 2:
                suit_stone_modifier_effects_list.append(stone.value[count - 3])
    if stone_suit is not None:
        for modifier_effects_list in suit_stone_modifier_effects_list:
            for modifier_effects in modifier_effects_list:
                if attr_name in modifier_effects.modifier:
                    is_requirement_meet = modifier_effects.requirement(
                        actor_instance, target_instance, context, stone_suit
                    )
                    if is_requirement_meet > 0:
                        modifier_value = get_modifier_attribute_value(
                            actor_instance, modifier_effects.modifier, attr_name
                        )
                        return is_requirement_meet * calculate_stone_with_max_stack(
                            stone_suit, modifier_value, attr_name
                        )
    return 0


def accumulate_equipments_modifier(
    attr_name: str, actor_instance: Hero, target_instance: Hero, context: Context
) -> float:
    modifier_value = 0
    for equipment in actor_instance.equipments:
        for modifier_effect in equipment.modifier_effects:
            if attr_name in modifier_effect.modifier:
                is_requirement_meet = modifier_effect.requirement(
                    actor_instance, target_instance, context, equipment
                )
                if is_requirement_meet > 0:
                    bascic_modifier_value = get_modifier_attribute_value(
                        actor_instance, modifier_effect.modifier, attr_name
                    )
                    modifier_value += is_requirement_meet * bascic_modifier_value
    return modifier_value