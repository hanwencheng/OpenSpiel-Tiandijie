from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives import Context, Action

from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import *
from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes

CRIT_MULTIPLIER = 1.3
LIEXING_DAMAGE_REDUCTION = 4
LIEXING_DAMAGE_INCREASE = 4


def apply_damage(actor: Hero, target: Hero, action: Action, context: Context):
    event_listener_calculator(actor, target, EventTypes.damage_start, context)
    calculate_skill_damage(actor, target, action, context)
    event_listener_calculator(actor, target, EventTypes.damage_end, context)


def apply_counterattack_damage(
    counter_attacker: Hero, attacker: Hero, action: Action, context: Context
):
    calculate_skill_damage(counter_attacker, attacker, action, context)


def calculate_skill_damage(
    attacker_instance: Hero, target_instance: Hero, action: Action, context: Context
):
    hero_id = attacker_instance.id
    is_attacker = action.is_attacker(hero_id)
    skill = action.skill
    is_magic = action.is_magic

    attacker_elemental_multiplier = get_element_attacker_multiplier(
        attacker_instance, target_instance, action, context
    )  # 克制攻击加成
    defender_elemental_multiplier = get_element_defender_multiplier(
        attacker_instance, target_instance, action, context
    )  # 克制防御加成

    # Calculating attack-defense difference
    attack_defense_difference = (
        get_attack(attacker_instance, target_instance, context, is_magic)
        * attacker_elemental_multiplier
        - get_defense_with_penetration(
            attacker_instance, target_instance, context, is_magic
        )
        * defender_elemental_multiplier
    )

    # Calculating base damage

    if skill:
        damage_multiplier = skill.temp.multiplier
        actual_damage = (
            attack_defense_difference
            * damage_multiplier
            * get_damage_modifier(attacker_instance, target_instance, skill, is_magic, context)
            * get_damage_reduction_modifier(
                target_instance, attacker_instance, is_magic, context
            )
        )
    else:
        actual_damage = attack_defense_difference

    critical_probability = (
        get_critical_hit_probability(attacker_instance, target_instance, context)
        - get_critical_hit_resistance(attacker_instance, target_instance, context)
        + get_critical_hit_suffer(target_instance, attacker_instance, context)
    )

    critical_damage_multiplier = (
        CRIT_MULTIPLIER
        * get_critical_damage_modifier(attacker_instance, is_attacker, context)
        * get_critical_damage_reduction_modifier(
            target_instance, not is_attacker, context
        )
    )

    if random() < critical_probability:
        # Critical hit occurs
        target_instance.take_harm(actual_damage * critical_damage_multiplier)
    else:
        # No critical hit
        target_instance.take_harm(actual_damage)


def calculate_fix_damage(
    damage, actor_instance: Hero, target_instance: Hero, context: Context
):
    defender_fix_damage_reduction = get_fixed_damage_reduction_modifier(
        target_instance, actor_instance, context
    )
    target_instance.take_harm(damage * defender_fix_damage_reduction)


def calculate_magic_damage(
    damage: float, actor_instance: Hero, defender_instance: Hero, context: Context
):
    actual_damage = damage * get_damage_reduction_modifier(
        defender_instance, actor_instance, True, context
    )
    defender_instance.take_harm(actual_damage)


def calculate_physical_damage(
    damage: float, actor_instance: Hero, defender_instance: Hero, context: Context
):
    actual_damage = damage * get_damage_reduction_modifier(
        defender_instance, actor_instance, False, context
    )
    defender_instance.take_harm(actual_damage)
