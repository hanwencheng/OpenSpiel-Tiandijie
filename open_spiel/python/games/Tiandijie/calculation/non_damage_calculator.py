from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.Action import Action
    from primitives import Context
    from primitives.hero.Hero import Hero
from calculation.event_calculator import event_listener_calculator
from primitives.effects.Event import EventTypes


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
    target.take_healing(action.total_damage)
    pass


def apply_summon(actor: Hero, target: Hero or None, action: Action, context: Context):
    pass


def apply_teleport(actor: Hero, target: Hero or None, action: Action, context: Context):
    pass


def apply_self(actor: Hero, target: Hero or None, action: Action, context: Context):
    pass


def apply_support(actor_instance: Hero, counter_instances: Hero or None, action: Action, context: Context):
    pass