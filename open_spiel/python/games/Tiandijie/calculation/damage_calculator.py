from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives import Context, Action

from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import *
from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes

CRIT_MULTIPLIER = 1.3


def apply_damage(actor: Hero, target: Hero, action: Action, context: Context):
    event_listener_calculator(actor, target, EventTypes.damage_start, context)
    calculate_skill_damage(actor, target, action, context)
    event_listener_calculator(actor, target, EventTypes.damage_end, context)


def apply_counterattack_damage(
    counter_attacker: Hero, attacker: Hero, action: Action, context: Context
):
    calculate_counterattack_damage(counter_attacker, attacker, action, context)


def calculate_skill_damage(
    attacker_instance: Hero, target_instance: Hero, action: Action, context: Context
):
    skill = action.skill
    is_magic = check_is_magic_action(skill, attacker_instance)

    attacker_elemental_multiplier = get_element_attacker_multiplier(
        attacker_instance, target_instance, action, context
    )  # 克制攻击加成

    # Calculating attack-defense difference
    attack_defense_difference = (
        get_attack(attacker_instance, target_instance, context, is_magic)
        * attacker_elemental_multiplier
        - get_defense_with_penetration(
            attacker_instance, target_instance, context
        )
    )
    # Calculating base damage

    actual_damage = (
            attack_defense_difference
            * get_a_damage_modifier(attacker_instance, target_instance, skill, is_magic, context)
            * get_b_damage_modifier(attacker_instance, target_instance, skill, is_magic, context)
    )
    if skill:
        damage_multiplier = skill.temp.multiplier
        actual_damage = actual_damage * damage_multiplier

    critical_probability = (
        get_critical_hit_probability(attacker_instance, target_instance, context, skill)
        + get_critical_hit_suffer(target_instance, attacker_instance, context)
    )

    critical_damage_multiplier = (
        CRIT_MULTIPLIER
        * get_critical_damage_modifier(attacker_instance, target_instance, context)
    )

    print("=======================================计算伤害==================================================")
    print("calculate_skill_damage111:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
    print("攻击面板", get_attack(attacker_instance, target_instance, context, is_magic), "\n",
          "克制伤害加成系数", attacker_elemental_multiplier, "\n",
          "防御面板", get_defense_with_penetration(attacker_instance, target_instance, context, is_magic), "\n",
          "基础伤害计算为", attack_defense_difference, "\n",
          "-\n",
          "暴击率", critical_probability, "\n",
          "技能名", skill.temp.id if skill else "无", "\n",
          "技能伤害系数", skill.temp.multiplier if skill else 0, "\n",
          "A类增减伤", get_a_damage_modifier(attacker_instance, target_instance, skill, is_magic, context), "\n",
          "B类增减伤", get_b_damage_modifier(attacker_instance, target_instance, skill, is_magic, context), "\n",
          # "暴击倍率", CRIT_MULTIPLIER, "\n",
          # "暴击伤害加成", get_critical_damage_modifier(attacker_instance, target_instance, context), "\n",
          # "暴击承伤加成", get_critical_damage_reduction_modifier(target_instance, attacker_instance, context)
          )












    if random() < critical_probability:
        # Critical hit occurs
        print("Critical hit occurs", actual_damage * critical_damage_multiplier)
        critical_damage = max(actual_damage * critical_damage_multiplier, 1)
        target_instance.take_harm(attacker_instance, critical_damage, context)
    else:
        # No critical hit
        print("No critical hit", actual_damage)
        actual_damage = max(actual_damage, 1)

        target_instance.take_harm(attacker_instance, actual_damage, context)


def calculate_fix_damage(
    damage, actor_instance: Hero, target_instance: Hero, context: Context
):
    defender_fix_damage_reduction = get_fixed_damage_reduction_modifier(
        target_instance, actor_instance, context
    )
    target_instance.take_harm(actor_instance, damage * defender_fix_damage_reduction, context)


def calculate_magic_damage(
    damage: float, actor_instance: Hero, defender_instance: Hero, context: Context
):
    actual_damage = damage * get_damage_reduction_modifier(
        defender_instance, actor_instance, True, context
    )
    defender_instance.take_harm(actor_instance, actual_damage, context)


def calculate_physical_damage(
    damage: float, actor_instance: Hero, defender_instance: Hero, context: Context
):
    actual_damage = damage * get_damage_reduction_modifier(
        defender_instance, actor_instance, False, context
    )
    defender_instance.take_harm(actor_instance, actual_damage, context)


def calculate_counterattack_damage(
    attacker_instance: Hero, target_instance: Hero, action: Action, context: Context
):
    is_magic = True if attacker_instance.temp.is_normal_attack_magic else False

    attacker_elemental_multiplier = get_element_attacker_multiplier(
        attacker_instance, target_instance, action, context
    )  # 克制攻击加成

    # Calculating attack-defense difference
    attack_defense_difference = (
        get_attack(attacker_instance, target_instance, context, is_magic)
        * attacker_elemental_multiplier
        - get_defense_with_penetration(
            attacker_instance, target_instance, context, is_magic
        )
    )
    # Calculating base damage

    actual_damage = (
            attack_defense_difference
            * get_a_damage_modifier(attacker_instance, target_instance, None, is_magic, context)
            * get_b_damage_modifier(attacker_instance, target_instance, None, is_magic, context)
    )

    critical_probability = (
        get_critical_hit_probability(attacker_instance, target_instance, context)
        + get_critical_hit_suffer(target_instance, attacker_instance, context)
    )

    critical_damage_multiplier = (
        CRIT_MULTIPLIER
        * get_critical_damage_modifier(attacker_instance, target_instance, context)
    )

    print("=======================================计算反击伤害==================================================")
    print("calculate_skill_damage111:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
    print("攻击面板", get_attack(attacker_instance, target_instance, context, is_magic), "\n",
          "克制伤害加成系数", attacker_elemental_multiplier, "\n",
          "防御面板", get_defense_with_penetration(attacker_instance, target_instance, context, is_magic), "\n",
          "基础伤害计算为", attack_defense_difference, "\n",
          "-\n",
          "暴击率", critical_probability, "\n",
          "A类增减伤", get_a_damage_modifier(attacker_instance, target_instance, None, is_magic, context), "\n",
          "B类增减伤", get_b_damage_modifier(attacker_instance, target_instance, None, is_magic, context), "\n",
          # "暴击倍率", CRIT_MULTIPLIER, "\n",
          # "暴击伤害加成", get_critical_damage_modifier(attacker_instance, target_instance, context), "\n",
          # "暴击承伤加成", get_critical_damage_reduction_modifier(target_instance, attacker_instance, context)
          )

    if random() < critical_probability:
        # Critical hit occurs
        print("Critical hit occurs of counterattack", attacker_instance.id, actual_damage * critical_damage_multiplier)
        critical_damage = max(actual_damage * critical_damage_multiplier, 1)
        target_instance.take_harm(attacker_instance, critical_damage, context)
    else:
        # No critical hit
        print("No critical hit of counterattack", attacker_instance.id, actual_damage)
        actual_damage = max(actual_damage, 1)
        target_instance.take_harm(attacker_instance, actual_damage, context)
