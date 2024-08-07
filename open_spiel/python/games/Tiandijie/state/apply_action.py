from __future__ import annotations

from open_spiel.python.games.Tiandijie.calculation.damage_calculator import (
    apply_counterattack_damage,
    apply_damage,
    apply_double_damage
)
from open_spiel.python.games.Tiandijie.calculation.non_damage_calculator import *
from open_spiel.python.games.Tiandijie.state.state_calculator import (
    check_if_counterattack_first,
    check_if_in_battle,
    check_protector,
    check_if_double_attack,
    check_if_chase_attack,
)
if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.Action import Action
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
from typing import Callable
from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator, death_event_listener, before_death_event_listener
from open_spiel.python.games.Tiandijie.primitives.ActionTypes import ActionTypes
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTemp import SkillTargetTypes
from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import get_a_modifier
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_target_in_diamond_range

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
    ActionTypes.EFFECT_ENEMY: (None, None),

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
    ActionTypes.PASS: (None, None),
    ActionTypes.SUPPORT: (None, None),
    ActionTypes.EFFECT_ENEMY: (None, None),
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
    SkillTargetTypes.DIRECTION: (
        EventTypes.skill_for_direction_start,
        EventTypes.skill_for_direction_end,
    ),
}


def counterattack_actions(action, context: Context, is_first: bool):
    counter_attacker = action.get_defender_hero_in_battle()
    actor = action.actor
    target = action.targets[0]
    if get_a_modifier("counterattack_disabled", target, None, context):
        return
    range_value = target.temp.profession.value[1] + get_a_modifier("counterattack_range", target, None, context)
    if not calculate_if_target_in_diamond_range(target.position, action.move_point, range_value):
        return

    if is_first:
        event_listener_calculator(
            counter_attacker, actor, EventTypes.counterattack_first_start, context
        )
        event_listener_calculator(
            actor, counter_attacker, EventTypes.under_counterattack_first_start, context
        )
    else:
        event_listener_calculator(
            counter_attacker, actor, EventTypes.counterattack_start, context
        )
        event_listener_calculator(
            actor, counter_attacker, EventTypes.under_counterattack_start, context
        )
    apply_counterattack_damage(counter_attacker, action.actor, action, context)
    if is_first:
        event_listener_calculator(
            counter_attacker, actor, EventTypes.counterattack_first_end, context
        )
        event_listener_calculator(
            actor, counter_attacker, EventTypes.under_counterattack_first_end, context
        )
    else:
        event_listener_calculator(
            counter_attacker, actor, EventTypes.counterattack_end, context
        )
        event_listener_calculator(
            counter_attacker, actor, EventTypes.under_counterattack_end, context
        )


def double_attack_event(double_attack_modifier: int, context: Context):
    action = context.get_last_action()
    target = action.get_defender_hero_in_battle()
    actor = action.actor
    event_listener_calculator(actor, target, EventTypes.double_attack_start, context)
    event_listener_calculator(target, actor, EventTypes.under_double_attack_start, context)
    apply_double_damage(actor, target, action, double_attack_modifier, context)
    event_listener_calculator(actor, target, EventTypes.double_attack_end, context)
    event_listener_calculator(target, actor, EventTypes.under_double_attack_end, context)


def calculation_events(
    actor: Hero,
    target: Hero,
    action: Action,
    context: Context,
    apply_func: Callable[[Hero, Hero or None, Action, Context], None],
):
    actions_start_event_type = action_type_to_event_dict[action.type][0]
    actions_end_event_type = action_type_to_event_dict[action.type][1]
    event_listener_calculator(actor, target, actions_start_event_type, context)
    apply_func(actor, target, action, context)
    event_listener_calculator(actor, target, actions_end_event_type, context)

#  若先攻： 先攻 -> 攻击 -> 连击（不触发追击）
#  非先攻： 攻击 -> 连击 -> 反击 —> 追击
def battle_events(actor: Hero, target: Hero, action: Action, context: Context):
    if action.skill:
        event_listener_calculator(
            actor, target, EventTypes.skill_start, context
        )

    event_listener_calculator(actor, target, EventTypes.battle_start, context)
    event_listener_calculator(target, actor, EventTypes.battle_start, context)
    if check_if_counterattack_first(action, context):       # 先攻
        counterattack_actions(action, context, True)  # take damage
        if is_hero_live(actor, target, context):
            calculation_events(
                actor, target, action, context, apply_damage
            )
            if is_hero_live(actor, target, context):
                double_attack_modifier = check_if_double_attack(action, context)
                if double_attack_modifier:
                    double_attack_event(double_attack_modifier, context)
        event_listener_calculator(actor, target, EventTypes.battle_end, context)
    else:
        calculation_events(
            actor, target, action, context, apply_damage
        )
        if is_hero_live(target, target, context):
            double_attack_modifier = check_if_double_attack(action, context)
            if double_attack_modifier:
                double_attack_event(double_attack_modifier, context)
            if is_hero_live(target, actor, context):
                counterattack_actions(action, context, False)
            if is_hero_live(actor, target, context):
                if check_if_chase_attack(action, context):  # 追击
                    # chase_attack_event(context) todo
                    pass
        event_listener_calculator(actor, target, EventTypes.battle_end, context)
        event_listener_calculator(target, actor, EventTypes.battle_end, context)

    is_hero_live(actor, target, context)

    if action.skill:
        event_listener_calculator(
            actor, target, EventTypes.skill_end, context
        )




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
    if hero_instance.get_current_life(context) <= 0:
        before_death_event_listener(
            hero_instance, counter_instance, EventTypes.before_hero_death, context
        )
        if hero_instance.get_current_life(context) <= 0:
            death_event_listener(
                hero_instance, counter_instance, EventTypes.hero_death, context
            )
            context.set_hero_died(hero_instance)
        return False
    return True


def move_event(
    actor: Hero,
    action: Action,
    context: Context,
    apply_func: Callable[[Hero, Action, Context], None],
):
    if action.move_point != action.initial_position:
        event_listener_calculator(actor, None, EventTypes.move_start, context)
        apply_func(actor, action, context)
        event_listener_calculator(actor, None, EventTypes.move_end, context)


def apply_action(context: Context, action: Action):
    # TODO: turn start and end is not calculated here

    if not action.actionable:
        return
    # if action.has_additional_action:
    #     action.has_additional_action = False

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
        action.update_is_in_battle(check_if_in_battle(action, context))
        if action.is_in_battle:
            check_protector(context)
            target = action.get_defender_hero_in_battle()
            battle_events(action.actor, target, action, context)
            is_hero_live(action.actor, True, context)
        else:
            range_skill_events(actor, action.targets, action, context, apply_damage)

        # check liveness of all the heroes
        for hero in context.heroes:
            if hero.id != actor.id:
                is_hero_live(hero, None, context)

    elif action.type == ActionTypes.HEAL:
        heal_event(actor, None, action, context, apply_heal)

    elif action.type == ActionTypes.SUMMON:
        attack_or_skill_events(actor, None, action, context, apply_summon)

    elif action.type == ActionTypes.SELF:
        for target in action.targets:
            attack_or_skill_events(actor, target, action, context, apply_self)

    elif action.type == ActionTypes.TELEPORT:
        attack_or_skill_events(actor, None, action, context, apply_teleport)

    elif action.type == ActionTypes.SUPPORT:
        test(actor, action.targets[0], action, context, apply_support)

    elif action.type == ActionTypes.EFFECT_ENEMY:
        attack_or_skill_events(actor, action.targets[0], action, context, apply_effect_enemy)
    #
    # elif action.type == ActionTypes.PASS:
    #     pass

    # TODO Calculate Critical Damage Events
    event_listener_calculator(actor, None, EventTypes.before_action_end, context)
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
    skill_start_event_type, skill_end_event_type = skill_type_to_event_dict[action.skill.temp.target_type]

    def trigger_event(event_type):
        event_listener_calculator(actor_instance, None, event_type, context)

    if not counter_instances:
        trigger_event(EventTypes.skill_start)
        trigger_event(skill_start_event_type)
        trigger_event(skill_end_event_type)
        trigger_event(EventTypes.skill_end)
    else:
        trigger_event(EventTypes.skill_start)
        trigger_event(skill_start_event_type)

        for counter_instance in counter_instances:
            calculation_events(actor_instance, counter_instance, action, context, apply_func)

        trigger_event(skill_end_event_type)
        trigger_event(EventTypes.skill_end)


def heal_event(actor_instance, counter_instance, action, context, apply_func):
    event_listener_calculator(
        actor_instance, counter_instance, EventTypes.skill_start, context
    )
    for target in action.targets:
        calculation_events(
            actor_instance, target, action, context, apply_heal
        )
    event_listener_calculator(
        actor_instance, counter_instance, EventTypes.skill_end, context
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
