from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Action import Action

from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import *


# 治疗量=法攻×倍率×(1+角色天赋+角色技能+魂石套装效果(尸魔)+治疗职业的武器强化+饰品)×(1+列星)


def calculate_skill_heal(
    actor_instance: Hero, target_instance: Hero, action: Action, context: Context
):
    from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_buff_modifier
    is_heal_disabled = get_buff_modifier("is_heal_disabled", target_instance, actor_instance, context)
    if not is_heal_disabled:
        skill = action.skill
        skill_multiplier = skill.temp.multiplier
        magic_attack = get_attack(actor_instance, target_instance, context, True)

        actual_healing = magic_attack * skill_multiplier * get_fixed_heal_modifier(actor_instance, target_instance, context) * (1 + LIEXING_HEAL_INCREASE / 100)
        actual_healing = round(actual_healing)
        context.get_last_action().record_action.append(
            {"actor_id": target_instance.id, "value_type": "heal", "value": actual_healing, "from": skill.temp.id}
        )
        target_instance.take_healing(actual_healing, context)


def calculate_fix_heal(
    heal, actor_instance: Hero, target_instance: Hero, context: Context, heal_from
):    # 固定治疗不受词条影响
    from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_buff_modifier
    is_heal_disabled = get_buff_modifier("is_heal_disabled", target_instance, actor_instance, context)
    if not is_heal_disabled:
        if context.get_last_action():
            context.get_last_action().record_action.append(
                {"actor_id": target_instance.id, "value_type": "heal", "value": heal, "from": heal_from}
            )
        target_instance.take_healing(heal, context)


def calculate_reset_hero_actionable(
    actor_instance: Hero, target_instance: Hero, context: Context
):
    target_instance.reset_actionable(context=context)


def calculate_fix_shield(
    shield_value, actor_instance: Hero, target_instance: Hero, context: Context
):
    fixed_shield_modifier = 1 + get_level2_modifier(
        target_instance, actor_instance, ma.shield_percentage, context
    )/100
    target_instance.add_shield(shield_value * fixed_shield_modifier)


def calculate_add_buff(
    buff_temp, duration, level, caster: Hero, target: Hero, context: Context
):
    from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
    from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTypes
    from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
    from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
    from open_spiel.python.games.Tiandijie.primitives.buff.BuffImmuneList import (
        prevent_all_harm_list, prevent_all_benefit_list, immune_dict, immune_all_harm_list, immune_all_benefit_list)
    event_listener_calculator(target, caster, EventTypes.get_buff_start, context)
    prevent = False
    for immune_buff in target.buffs:
        if (
            immune_buff.temp.id in prevent_all_harm_list
            and buff_temp.type == BuffTypes.Harm
        ):
            prevent = True
        if (
            immune_buff.temp.id in prevent_all_benefit_list
            and buff_temp.type == BuffTypes.Benefit
        ):
            prevent = True
        if (
            immune_buff.temp.id in immune_dict
            and buff_temp.id in immune_dict[immune_buff.temp.id]
        ):
            prevent = True
    if not prevent:
        new_buff = Buff(buff_temp, duration, caster.id, level)
        action = context.get_last_action()
        if action.actor == caster and target == caster:
            new_buff.duration = duration + 1
        existing_buff = next(
            (buff for buff in target.buffs if buff.temp.id == new_buff.temp.id), None
        )
        if existing_buff is not None:
            # Replace the existing buff if the new buff has a higher level
            if new_buff.level > existing_buff.level:
                target.buffs.remove(existing_buff)
                target.buffs.append(new_buff)
            else:
                _increase_actor_certain_buff_stack(new_buff.temp.id, target, 1)
        else:
            target.buffs.append(new_buff)

        # remove the related buff if buff_temp.id is in the immune_dict
        if buff_temp.id in immune_dict:
            immune_list = immune_dict[buff_temp.id]
            for immune_buff_id in immune_list:
                for buff in target.buffs:
                    if buff_temp.id in immune_all_harm_list and buff.type == BuffTypes.Harm:
                        target.buffs.remove(buff)
                    elif (
                            buff_temp.id in immune_all_benefit_list
                            and buff.type == BuffTypes.Benefit
                    ):
                        target.buffs.remove(buff)
                    elif buff.temp.id == immune_buff_id:
                        target.buffs.remove(buff)
    event_listener_calculator(target, caster, EventTypes.get_buff_end, context)


def _increase_actor_certain_buff_stack(
    buff_temp_id: str, actor: Hero, increase_stack: int
):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            if buff.stack >= buff.temp.max_stack:
                return
            buff.stack += increase_stack
            break


def calculate_remove_buff(
    buff_instance, actor: Hero, context: Context
):
    from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
    from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
    event_listener_calculator(actor, None, EventTypes.lose_buff_start, context)
    if buff_instance in actor.buffs:
        actor.buffs.remove(buff_instance)
    event_listener_calculator(actor, None, EventTypes.lose_buff_end, context)


def calculate_additional_action(
    actor: Hero, context: Context, move_range=None,
):
    from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_buff_modifier
    action_disabled = get_buff_modifier("is_extra_action_disabled", actor, None, context)
    if action_disabled:
        return
    if move_range is None:
        move_range = actor.temp.profession.value[2] + get_a_modifier(actor, None, "move_range", context)
    action = context.get_last_action()
    action.update_additional_action(move_range)

def calculate_additional_move(
    actor: Hero, context: Context, move_range,
):
    from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_buff_modifier
    action_disabled = get_buff_modifier("is_extra_move_range_disable", actor, None, context)
    if action_disabled:
        return
    action = context.get_last_action()
    action.update_additional_move(move_range)
