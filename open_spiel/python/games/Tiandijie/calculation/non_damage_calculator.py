from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Action import Action
    from open_spiel.python.games.Tiandijie.primitives import Context
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes


def apply_move(actor: Hero, action: Action, context: Context):
    actor = action.actor
    actor.update_position(action.move_point)


def apply_additional_move(actor: Hero, action: Action, context: Context):
    actor = action.actor
    actor.update_position(action.additional_move)


def apply_additional_skill(
    actor: Hero, target: Hero or None, action: Action, context: Context
):
    actor = context.get_last_action().actor


def apply_heal(actor: Hero, target: Hero or None, action: Action, context: Context):
    from open_spiel.python.games.Tiandijie.calculation.OtherlCalculation import calculate_skill_heal
    event_listener_calculator(actor, target, EventTypes.heal_start, context)
    calculate_skill_heal(actor, target, action, context)
    event_listener_calculator(actor, target, EventTypes.heal_end, context)


def apply_summon(actor: Hero, target: Hero or None, action: Action, context: Context):
    pass


def apply_teleport(actor: Hero, target: Hero or None, action: Action, context: Context):
    pass


def apply_self(actor: Hero, target: Hero or None, action: Action, context: Context):
    pass


def apply_support(actor_instance: Hero, counter_instances: Hero or None, action: Action, context: Context):
    pass


def apply_effect_enemy(actor_instance: Hero, counter_instances: Hero or None, action: Action, context: Context):
    pass
