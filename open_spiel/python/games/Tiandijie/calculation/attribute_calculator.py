from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives import Context
    from open_spiel.python.games.Tiandijie.primitives.hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill
    from open_spiel.python.games.Tiandijie.primitives.Action import Action
from open_spiel.python.games.Tiandijie.primitives.hero.Element import (
    get_elemental_relationship,
    get_elemental_multiplier,
)

from open_spiel.python.games.Tiandijie.helpers import is_normal_attack_magic

from open_spiel.python.games.Tiandijie.primitives.ActionTypes import ActionTypes
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_targe_in_diamond_range
from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import (
    accumulate_attribute,
    get_level1_modified_result,
    get_level2_modifier,
    get_skill_modifier,
    accumulate_stone_attribute,
    accumulate_suit_stone_attribute
)

LIEXING_DAMAGE_REDUCTION = 4
LIEXING_DAMAGE_INCREASE = 4


def check_is_magic_action(skill: Skill or None, attacker_instance: Hero) -> bool:
    if skill is None:
        return is_normal_attack_magic(attacker_instance.temp.profession)
    else:
        return skill.temp.is_magic()


def normalize_value(v: float) -> float:
    return max(0, min(1, v))


# TODO Shenbin calculation is not included


def get_element_attacker_multiplier(
    attacker_instance: Hero, target_instance: Hero, action: Action, context: Context
) -> float:
    skill = action.skill
    attr_name = ma.element_attacker_multiplier
    if skill is not None:
        is_ignore_element = get_skill_modifier(
            "ignore_element_advantage", attacker_instance, target_instance, skill, context
        )
        if is_ignore_element:
            return 1
    basic_elemental_multiplier = get_elemental_multiplier(
        get_elemental_relationship(skill.temp.element if skill else attacker_instance.temp.element, target_instance.temp.element)
    )
    accumulated_skill_damage_modifier = 0
    if skill is not None:
        accumulated_skill_damage_modifier = get_skill_modifier(
            attr_name, attacker_instance, target_instance, skill, context
        )
    return normalize_value(
        basic_elemental_multiplier
        + accumulated_skill_damage_modifier
        + get_level2_modifier(attacker_instance, target_instance, attr_name, context)
    )


def get_element_defender_multiplier(
    attacker_instance: Hero, target_instance: Hero, action: Action, context: Context
) -> float:
    basic_elemental_multiplier = get_elemental_multiplier(
        get_elemental_relationship(
            target_instance.temp.element, attacker_instance.temp.element
        )
    )
    return normalize_value(
        basic_elemental_multiplier
        + get_level2_modifier(
            attacker_instance, target_instance, ma.element_defender_multiplier, context
        )
    )


def get_penetration_multiplier(
    hero_instance: Hero,
    counter_hero: Hero,
    skill: Skill or None,
    context: Context,
    is_basic: bool = False,
) -> float:
    is_magic = check_is_magic_action(skill, hero_instance)
    attr_name = (
        ma.magic_penetration_percentage
        if is_magic
        else ma.physical_penetration_percentage
    )
    accumulated_skill_damage_modifier = (
        0
        if skill is None
        else get_skill_modifier(attr_name, hero_instance, counter_hero, skill, context)
    )
    leve2_modifier = get_level2_modifier(
        hero_instance, counter_hero, attr_name, context
    )
    return normalize_value(leve2_modifier + accumulated_skill_damage_modifier)


def get_defense_with_penetration(
    attacker_instance: Hero,
    defender_instance: Hero,
    context: Context,
    is_basic: bool = False,
) -> float:
    skill = context.get_last_action().skill
    penetration = get_penetration_multiplier(
        attacker_instance, True, skill, context, is_basic
    )
    # calculate buffs
    basic_defense = get_defense(defender_instance, False, skill, context, is_basic)
    return basic_defense * (1 - normalize_value(penetration))


# TODO, calculate 先攻和反击上限，范围加成
def get_counter_attack_range(hero_instance: Hero, context: Context):
    counter_attack_range = hero_instance.temp.range
    return counter_attack_range


def check_in_battle(context: Context) -> bool:
    current_action = context.get_last_action()
    target = current_action.targets[0]
    if len(target) != 1:
        return False
    actor = current_action.actor
    if calculate_if_targe_in_diamond_range(
        actor, target, get_counter_attack_range(target, context)
    ):
        return True
    else:
        return False


def get_max_life(
    hero_instance: Hero, target_instance: Hero, context: Context, is_basic: bool = False
) -> float:
    life_attribute = hero_instance.initial_attributes.life
    basic_life = get_level1_modified_result(hero_instance, ma.life, life_attribute)
    return basic_life * (
        1
        + get_level2_modifier(
            hero_instance, target_instance, ma.life_percentage, context, is_basic
        )/100
    )


def get_defense(
    hero_instance: Hero,
    counter_instance: Hero,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:
    # calculate buffs
    attr_name = ma.magic_defense if is_magic else ma.defense
    defense_attribute = (
        hero_instance.initial_attributes.defense
        if is_magic
        else hero_instance.initial_attributes.magic_defense
    )

    basic_defense = get_level1_modified_result(
        hero_instance, attr_name, defense_attribute
    )
    return basic_defense * (1 + get_level2_modifier(
        hero_instance, counter_instance, attr_name, context, is_basic
    )/100)


def get_attack(
    actor_instance: Hero,
    target_instance: Hero,
    context: Context,
    is_magic_input=None,
    is_basic: bool = False,
) -> float:
    action = context.get_last_action()
    if is_magic_input is not None:
        is_magic = is_magic_input
    else:
        is_magic = action.is_magic
    # calculate buffs
    attr_name = "magic_attack" if is_magic else "attack"
    attack_attribute = (
        actor_instance.initial_attributes.attack
        if not is_magic
        else actor_instance.initial_attributes.magic_attack
    )
    basic_attack = get_level1_modified_result(
        actor_instance, attr_name, attack_attribute
    )
    return basic_attack * (1 + get_level2_modifier(
        actor_instance, target_instance, attr_name, context, is_basic
        )/100)


def get_damage_modifier(
    attacker_instance: Hero,
    counter_instance: Hero,
    skill: Skill or None,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:
    attr_name = (
        ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage
    )
    accumulated_skill_damage_modifier = (
        0
        if skill is None
        else get_skill_modifier(
            attr_name, attacker_instance, counter_instance, skill, context
        )
    )
    accumulated_passive_damage_modifier = accumulate_attribute(
        attacker_instance.temp.passives, attr_name
    )
    accumulated_stones_percentage_damage_modifier = accumulate_stone_attribute(
        attacker_instance.stones, attr_name
    )

    level2_damage_modifier = 1 + (
        get_level2_modifier(
            attacker_instance, counter_instance, attr_name, context, is_basic
        )
        + accumulated_skill_damage_modifier
        + accumulated_passive_damage_modifier
        + get_action_type_damage_modifier(attacker_instance, counter_instance, context)
    )

    # B-type damage increase (Additive)
    level1_damage_modifier = (
        1
        + (LIEXING_DAMAGE_INCREASE + accumulated_stones_percentage_damage_modifier)
        + (LIEXING_DAMAGE_INCREASE)
        / 100
    )
    return level1_damage_modifier * level2_damage_modifier


def get_action_type_damage_modifier(
    actor: Hero, target: Hero, context: Context
) -> float:
    current_action = context.get_last_action()
    action_type = current_action.type
    action_type_modifier = 0
    if action_type == ActionTypes.SKILL_ATTACK:
        action_type_modifier += get_level2_modifier(
            actor, target, ma.skill_damage_percentage, context
        )
        skill_target_type = context.get_last_action().skill.temp.range_instance.range_value
        if skill_target_type == 0:
            action_type_modifier += get_level2_modifier(
                actor, target, ma.single_target_skill_damage_percentage, context
            )
        elif skill_target_type > 0:
            action_type_modifier += get_level2_modifier(
                actor, target, ma.range_skill_damage_percentage, context
            )
    elif action_type == ActionTypes.NORMAL_ATTACK:
        action_type_modifier += get_level2_modifier(
            actor, target, ma.normal_attack_damage_percentage, context
        )

    if current_action.is_in_battle:
        action_type_modifier += get_level2_modifier(
            actor, target, ma.battle_damage_percentage, context
        )

    return action_type_modifier


def get_action_type_damage_reduction_modifier(
    defender: Hero, attacker: Hero, context: Context
) -> float:
    current_action = context.get_last_action()
    action_type = current_action.type
    action_type_modifier = 0
    if action_type == ActionTypes.SKILL_ATTACK:
        skill_target_type = context.get_last_action().skill.temp.range_instance.range_value
        if skill_target_type == 0:
            action_type_modifier += get_level2_modifier(
                defender,
                attacker,
                ma.single_target_skill_damage_reduction_percentage,
                context,
            )
        elif skill_target_type > 0:
            action_type_modifier += get_level2_modifier(
                defender, attacker, ma.range_skill_damage_reduction_percentage, context
            )
    elif action_type == ActionTypes.NORMAL_ATTACK:
        action_type_modifier += get_level2_modifier(
            defender, attacker, ma.normal_attack_damage_reduction_percentage, context
        )

    if current_action.is_in_battle:
        action_type_modifier += get_level2_modifier(
            defender, attacker, ma.battle_damage_reduction_percentage, context
        )

    return action_type_modifier


def get_damage_reduction_modifier(
    defense_instance: Hero,
    counter_instance: Hero,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:
    attr_name = (
        ma.magic_damage_reduction_percentage
        if is_magic
        else ma.physical_damage_reduction_percentage
    )
    accumulated_passives_damage_reduction_modifier = accumulate_attribute(
        defense_instance.temp.passives, attr_name
    )
    accumulated_stones_damage_reduction_percentage_modifier = accumulate_stone_attribute(
        defense_instance.stones, attr_name
    )
    formation_damage_reduction_modifier = 0
    if context.formation:
        from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_formation_modifier
        formation_damage_reduction_modifier = (
            get_formation_modifier(attr_name, defense_instance, counter_instance, context)
        )
        #     (
        #     context.formation.magic_damage_reduction_percentage
        #     if is_magic
        #     else context.formation.physical_damage_reduction_percentage
        # )

    # A-type damage increase (Additive)
    a_type_damage_reduction = (
        1
        - (
            get_level2_modifier(
                defense_instance, counter_instance, attr_name, context, is_basic
            )
            + get_action_type_damage_reduction_modifier(
                defense_instance, counter_instance, context
            )
            + accumulated_passives_damage_reduction_modifier
            + formation_damage_reduction_modifier
        )
        / 100
    )

    # B-type damage increase (Additive)
    b_type_damage_reduction = (
        1
        - (
            LIEXING_DAMAGE_REDUCTION
            + accumulated_stones_damage_reduction_percentage_modifier
        )
        / 100
    )
    return a_type_damage_reduction * b_type_damage_reduction


def get_critical_hit_probability(
    actor_hero: Hero, counter_instance: Hero, context: Context, is_basic: bool = False
) -> float:
    critical_stones_percentage_modifier = accumulate_stone_attribute(
        actor_hero.stones, ma.critical_percentage
    )
    # TODO
    #  add stones suit effect

    luck_attribute = actor_hero.initial_attributes.luck
    total_luck = luck_attribute * (
        1
        + get_level2_modifier(actor_hero, counter_instance, ma.luck, context, is_basic)
    )
    level2_critical_modifier = get_level2_modifier(
        actor_hero, counter_instance, ma.critical_percentage, context
    )
    total_critical = (
        total_luck / 10 + level2_critical_modifier + critical_stones_percentage_modifier
    )
    return total_critical / 100


def get_critical_hit_resistance(
    actor_hero: Hero, counter_instance: Hero, context: Context, is_basic: bool = False
) -> float:
    # Calculate buffs
    level_2_hit_resistance = get_level2_modifier(
        actor_hero,
        counter_instance,
        ma.critical_percentage_reduction,
        context,
        is_basic,
    )
    critical_stones_percentage_modifier = accumulate_stone_attribute(
        actor_hero.stones, ma.critical_percentage_reduction
    )
    # TODO
    #  add stones suit effect
    return (level_2_hit_resistance + critical_stones_percentage_modifier) / 100


def get_critical_hit_suffer(
    actor_hero: Hero, counter_instance: Hero, context: Context, is_basic: bool = False
) -> float:
    # Calculate buffs
    level_2_hit_suffer = get_level2_modifier(
        actor_hero,
        counter_instance,
        ma.suffer_critical_percentage,
        context,
        is_basic,
    )
    suffer_critical_stones_percentage_modifier = accumulate_stone_attribute(
        actor_hero.stones, ma.suffer_critical_percentage
    )
    # TODO
    #  add stones suit effect

    return (level_2_hit_suffer + suffer_critical_stones_percentage_modifier) / 100


def get_critical_damage_modifier(
    actor_hero: Hero, counter_instance: Hero, context: Context
) -> float:
    return (
        1
        + get_level2_modifier(
            actor_hero, counter_instance, ma.critical_damage_percentage, context
        )
        / 100
    )


def get_critical_damage_reduction_modifier(
    actor_hero: Hero, counter_instance: Hero, context: Context
) -> float:
    return (
        1
        - get_level2_modifier(
            actor_hero,
            counter_instance,
            ma.critical_damage_reduction_percentage,
            context,
        )
        / 100
    )


def get_fixed_damage_reduction_modifier(
    hero_instance: Hero, counter_instance: Hero, context: Context
) -> float:
    accumulated_passives_damage_reduction_modifier = accumulate_attribute(
        hero_instance.temp.passives, ma.fixed_damage_reduction_percentage
    )
    accumulated_passives_damage_modifier = accumulate_attribute(
        hero_instance.temp.passives, ma.fixed_damage_percentage
    )
    return (
        1
        - (
            (
                get_level2_modifier(
                    hero_instance,
                    counter_instance,
                    ma.fixed_damage_reduction_percentage,
                    context,
                )
                + accumulated_passives_damage_reduction_modifier
            )
            - (
                (
                    get_level2_modifier(
                        hero_instance,
                        counter_instance,
                        ma.fixed_damage_percentage,
                        context,
                    )
                    + accumulated_passives_damage_reduction_modifier
                )
                + accumulated_passives_damage_modifier
            )
        )
        / 100
    )


def get_fixed_heal_reduction_modifier(
    hero_instance: Hero, counter_instance: Hero, context: Context
) -> float:
    accumulated_passives_heal_reduction_modifier = accumulate_attribute(
        hero_instance.temp.passives, ma.heal_percentage
    )
    return (
        1
        + (
            get_level2_modifier(
                hero_instance,
                counter_instance,
                ma.heal_percentage,
                context,
            )
            + accumulated_passives_heal_reduction_modifier
        )
        / 100
    )
