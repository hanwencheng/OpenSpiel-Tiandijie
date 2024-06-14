from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.hero.Hero import Hero
from calculation.Range import calculate_if_targe_in_diamond_range
from primitives.buff.BuffTemp import BuffTypes


def _is_attacker(actor_hero: Hero, context: Context) -> int:
    if actor_hero.id == context.get_last_action().actor.id:
        return 1
    else:
        return 0


def check_buff_in_range(
    range_value: int,
    actor_hero: Hero,
    context: Context,
    buff_type: BuffTypes,
    is_partner: bool,
) -> int:
    actor_position = actor_hero.position
    for hero in context.heroes:
        if hero.id == actor_hero.id:
            continue
        if (
            hero.player_id == actor_hero.player_id
            if is_partner
            else hero.player_id != actor_hero.player_id
        ):
            for buff in hero.buffs:
                if buff.temp.type == buff_type:
                    if calculate_if_targe_in_diamond_range(
                        actor_position, hero.position, range_value
                    ):
                        return 1
    return 0


def check_buff_on_target(
    actor_hero: Hero, target_hero: Hero, buff_type: BuffTypes, is_self: bool
) -> int:
    check_hero = actor_hero if is_self else target_hero
    for buff in check_hero.buffs:
        if buff.temp.type == buff_type:
            return 1
    return 0
