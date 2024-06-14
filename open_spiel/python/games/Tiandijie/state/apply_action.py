from __future__ import annotations

from calculation.damage_calculator import apply_counterattack_damage, apply_damage
from calculation.non_damage_calculator import *
from state.state_calculator import (
    check_if_counterattack_first,
    check_if_in_battle,
    check_protector,
    check_if_double_attack,
)

if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.Action import Action
    from primitives.hero.Hero import Hero

from typing import Callable

from calculation.event_calculator import event_listener_calculator, death_event_listener
from primitives.Action import ActionTypes

from primitives.effects.Event import EventTypes
from primitives.skill.SkillTemp import SkillTargetTypes

# move actor to the desired position


action_type_to_event_dict: dict[ActionTypes, tuple[EventTypes, EventTypes]] = {
    ActionTypes.HEAL: (EventTypes.heal_start, EventTypes.heal_end),
    ActionTypes.TELEPORT: (EventTypes.teleport_start, EventTypes.teleport_end),
    ActionTypes.SKILL_ATTACK: (
        EventTypes.skill_attack_start,
        EventTypes.skill_attack_end,
    ),
    ActionTypes.NORMAL_ATTACK: (
        EventTypes.normal_attack_start,
        EventTypes.normal_attack_end,
    ),
    ActionTypes.SUMMON: (EventTypes.summon_start, EventTypes.summon_end),
    ActionTypes.SELF: (EventTypes.self_start, EventTypes.self_end),
    ActionTypes.PASS: (EventTypes.pass_start, EventTypes.pass_end),
    ActionTypes.SUPPORT: (None, None),
    # ActionTypes.COUNTERATTACK: (EventTypes.counterattack_start, EventTypes.counterattack_end),
}

under_action_type_to_event_dict: dict[ActionTypes, tuple[EventTypes, EventTypes]] = {
    ActionTypes.HEAL: (EventTypes.under_heal_start, EventTypes.under_heal_end),
    ActionTypes.TELEPORT: (None, None),
    ActionTypes.SKILL_ATTACK: (
        EventTypes.skill_attack_start,
        EventTypes.skill_attack_end,
    ),
    ActionTypes.NORMAL_ATTACK: (
        EventTypes.under_normal_attack_start,
        EventTypes.under_normal_attack_end,
    ),
    ActionTypes.SUMMON: (None, None),
    ActionTypes.SELF: (None, None),
    # ActionTypes.PASS: (None, None),
}

skill_type_to_event_dict: dict[SkillTargetTypes, tuple[EventTypes, EventTypes]] = {
    SkillTargetTypes.ENEMY: (
        EventTypes.skill_single_damage_start,
        EventTypes.skill_single_damage_end,
    ),
    SkillTargetTypes.PARTNER: (
        EventTypes.skill_for_partner_start,
        EventTypes.skill_for_partner_end,
    ),
    SkillTargetTypes.TERRAIN: (
        EventTypes.skill_for_terrain_start,
        EventTypes.skill_for_terrain_end,
    ),
    SkillTargetTypes.SELF: (
        EventTypes.skill_for_self_start,
        EventTypes.skill_for_self_end,
    ),
}


def counterattack_actions(context: Context):
    action = context.get_last_action()
    counter_attacker = action.get_defender_hero_in_battle()
    actor = action.actor
    event_listener_calculator(
        counter_attacker, actor, EventTypes.counterattack_start, context
    )
    event_listener_calculator(
        actor, counter_attacker, EventTypes.counterattack_start, context
    )
    apply_counterattack_damage(counter_attacker, action.actor, action, context)
    event_listener_calculator(
        counter_attacker, actor, EventTypes.counterattack_end, context
    )
    event_listener_calculator(
        actor, counter_attacker, EventTypes.counterattack_end, context
    )


def double_attack_event(context: Context):
    action = context.get_last_action()
    target = action.get_defender_hero_in_battle()
    actor = action.actor
    event_listener_calculator(actor, target, EventTypes.double_attack_start, context)
    event_listener_calculator(target, actor, EventTypes.double_attack_start, context)
    apply_damage(actor, action.actor, action, context)
    event_listener_calculator(actor, target, EventTypes.double_attack_end, context)
    event_listener_calculator(target, actor, EventTypes.double_attack_end, context)


def calculation_events(
    actor: Hero,
    target: Hero,
    action: Action,
    context: Context,
    apply_func: Callable[[Hero, Hero or None, Action, Context], None],
):
    actions_start_event_type = action_type_to_event_dict[action.type][0]
    actions_end_event_type = action_type_to_event_dict[action.type][1]
    event_listener_calculator(actor, None, actions_start_event_type, context)
    apply_func(actor, target, action, context)
    event_listener_calculator(actor, None, actions_end_event_type, context)


def battle_events(actor: Hero, target: Hero, action: Action, context: Context):
    event_listener_calculator(actor, target, EventTypes.battle_start, context)
    if check_if_counterattack_first(action, context):
        counterattack_actions(context)  # take damage
        if is_hero_live(actor, target, context):
            attack_or_skill_events(actor, target, action, context, apply_damage)
            if check_if_double_attack(action, context):
                double_attack_event(context)
        event_listener_calculator(actor, target, EventTypes.battle_end, context)
        is_hero_live(target, actor, context)
    else:
        if is_hero_live(actor, target, context):
            attack_or_skill_events(actor, target, action, context, apply_damage)
        if check_if_double_attack(action, context):
            double_attack_event(context)
        if is_hero_live(target, actor, context):
            counterattack_actions(context)
        event_listener_calculator(actor, target, EventTypes.battle_end, context)
        event_listener_calculator(target, actor, EventTypes.battle_end, context)
        is_hero_live(actor, target, context)


def attack_or_skill_events(
    actor_instance: Hero,
    counter_instance: Hero or None,
    action: Action,
    context: Context,
    apply_func: Callable[[Hero, Hero or None, Action, Context], None],
):
    if action.skill:
        skill_start_event_type = skill_type_to_event_dict[
            action.skill.temp.target_type
        ][0]
        skill_end_event_type = skill_type_to_event_dict[
            action.skill.temp.target_type
        ][1]
        event_listener_calculator(
            actor_instance, counter_instance, EventTypes.skill_start, context
        )
        event_listener_calculator(
            actor_instance, counter_instance, skill_start_event_type, context
        )
        calculation_events(
            actor_instance, counter_instance, action, context, apply_func
        )
        event_listener_calculator(
            actor_instance, counter_instance, skill_end_event_type, context
        )
        event_listener_calculator(
            actor_instance, counter_instance, EventTypes.skill_end, context
        )
    else:
        calculation_events(
            actor_instance, counter_instance, action, context, apply_func
        )


def is_hero_live(hero_instance: Hero, counter_instance: Hero or None, context: Context):
    if hero_instance.current_life <= 0:
        death_event_listener(
            hero_instance, counter_instance, EventTypes.hero_death, context
        )
        if hero_instance.current_life <= 0:
            context.set_hero_died(hero_instance)
        return False
    return True


def move_event(
    actor: Hero,
    action: Action,
    context: Context,
    apply_func: Callable[[Hero, Action, Context], None],
):
    if action.movable:
        event_listener_calculator(actor, None, EventTypes.move_start, context)
        apply_func(actor, action, context)
        event_listener_calculator(actor, None, EventTypes.move_end, context)


def apply_action(context: Context, action: Action):
    # TODO: turn start and end is not calculated here

    if not action.actionable:
        return
    if action.has_additional_action:
        action.has_additional_action = False

    actor = action.actor
    context.add_action(action)
    event_listener_calculator(actor, None, EventTypes.action_start, context)
    move_event(actor, action, context, apply_move)
    action.refresh_move_point(context.battlemap)
    # events_check_order: battle events -> damage skill events -> damage events
    if (
        action.type == ActionTypes.NORMAL_ATTACK
        or action.type == ActionTypes.SKILL_ATTACK
    ):
        check_protector(context)
        action.update_is_in_battle(check_if_in_battle(action, context))
        if action.is_in_battle:
            target = action.get_defender_hero_in_battle()
            battle_events(action.actor, target, action, context)
            is_hero_live(action.actor, True, context)
        else:
            range_skill_events(actor, action.targets, action, context, apply_damage)
            # for target in action.targets:
            #     attack_or_skill_events(actor, target, action, context, apply_damage)
            #     is_hero_live(target, actor, context)

        # check liveness of all the heroes
        for hero in context.heroes:
            if hero.id != actor.id:
                is_hero_live(hero, None, context)

    elif action.type == ActionTypes.HEAL:
        for target in action.targets:
            attack_or_skill_events(actor, target, action, context, apply_heal)

    elif action.type == ActionTypes.SUMMON:
        attack_or_skill_events(actor, None, action, context, apply_summon)

    elif action.type == ActionTypes.SELF:
        for target in action.targets:
            attack_or_skill_events(actor, target, action, context, apply_self)

    elif action.type == ActionTypes.TELEPORT:
        attack_or_skill_events(actor, None, action, context, apply_teleport)

    elif action.type == ActionTypes.SUPPORT:
        test(actor, action.targets[0], action, context, apply_support)
    #
    # elif action.type == ActionTypes.PASS:
    #     pass

    # TODO Calculate Critical Damage Events
    event_listener_calculator(actor, None, EventTypes.action_end, context)

    # 将此类event改写成fieldbuff光环效果
    # for hero in context.heroes:
    #     if hero.player_id == context.get_heroes_by_player_id(actor.player_id):
    #         event_listener_calculator(
    #             hero, actor, EventTypes.partner_action_end, context
    #         )
    #     else:
    #         event_listener_calculator(hero, actor, EventTypes.enemy_action_end, context)
    # context.battlemap.display_map()


def generate_legal_actions():
    pass


def range_skill_events(actor_instance, counter_instances, action, context, apply_func):
    skill_start_event_type = skill_type_to_event_dict[
        action.skill.temp.target_type
    ][0]
    skill_end_event_type = skill_type_to_event_dict[
        action.skill.temp.target_type
    ][1]
    event_listener_calculator(
        actor_instance, counter_instances[0], EventTypes.skill_start, context
    )
    event_listener_calculator(
        actor_instance, counter_instances[0], skill_start_event_type, context
    )
    for counter_instance in counter_instances:
        calculation_events(
            actor_instance, counter_instance, action, context, apply_func
        )
    event_listener_calculator(
        actor_instance, counter_instances[0], skill_end_event_type, context
    )
    event_listener_calculator(
        actor_instance, counter_instances[0], EventTypes.skill_end, context
    )


def test(actor_instance, counter_instance, action, context, apply_func):
    event_listener_calculator(
        actor_instance, counter_instance, EventTypes.skill_start, context
    )
    calculation_events(
        actor_instance, counter_instance, action, context, apply_func
    )
    event_listener_calculator(
        actor_instance, counter_instance, EventTypes.skill_end, context
    )
