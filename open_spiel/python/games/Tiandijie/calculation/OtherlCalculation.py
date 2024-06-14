from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Action import Action

from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import *


def calculate_fix_heal(
    heal, actor_instance: Hero, target_instance: Hero, context: Context
):
    defender_fix_heal_reduction = get_fixed_heal_reduction_modifier(
        target_instance, actor_instance, context
    )
    target_instance.take_healing(heal * defender_fix_heal_reduction)


def calculate_reset_hero_actionable(
    actor_instance: Hero, target_instance: Hero, context: Context
):
    target_instance.reset_actionable(context=context)


def calculate_fix_shield(
    shield_value, actor_instance: Hero, target_instance: Hero, context: Context
):
    fixed_shield_modifier = get_level2_modifier(
        target_instance, actor_instance, ma.shield_percentage, context
    )
    target_instance.add_shield(shield_value * fixed_shield_modifier)
