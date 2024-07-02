from typing import List, Any
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_targe_in_diamond_range
from random import random
from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType

skill_related_events = [
    EventTypes.skill_start,
    EventTypes.skill_end,
    EventTypes.damage_start,
    EventTypes.damage_end,
    EventTypes.skill_single_damage_start,
    EventTypes.skill_single_damage_end,
    EventTypes.skill_range_damage_start,
    EventTypes.skill_range_damage_end,
    EventTypes.under_damage_start,
    EventTypes.under_damage_end,
    EventTypes.under_skill_single_damage_start,
    EventTypes.under_skill_single_damage_end,
    EventTypes.under_skill_range_damage_start,
    EventTypes.under_skill_range_damage_end,
    EventTypes.action_end,
]


class EventListenerContainer:
    def __init__(self, event_listener: EventListener, instance_self: Any):
        self.event_listener = event_listener
        self.instance_self = instance_self


def event_listener_calculator(
    actor_instance: 'Hero',
    counter_instance: 'Hero' or None,
    event_type: EventTypes,
    context,
):
    if actor_instance.is_alive is False:
        return
    event_listener_containers: List[EventListenerContainer] = []
    current_action = context.get_last_action()
    if current_action is None and event_type != EventTypes.game_start and event_type != EventTypes.turn_start:
        return
    # 有额外技能的话不结算action_end，在额外技能处结算action_end, 且在释放技能的action无需计算before_action_end
    ignore_event_types = {EventTypes.action_end, EventTypes.before_action_end}
    if event_type in ignore_event_types:
        if current_action.additional_skill_list is not None:
            return
        if current_action.additional_move > 0:
            return
        if len(context.actions) >= 2 and context.actions[-2].additional_move > 0:
            current_action.skill = context.actions[-2].skill

    if event_type == EventTypes.before_action_end and len(context.actions) >= 2 and context.actions[-2].actor.id == actor_instance.id and context.actions[-2].additional_skill_list is not None:
        return

    # Calculated Buffs
    for buff in actor_instance.buffs:
        buff_event_levels_listeners = buff.temp.event_listeners
        if len(buff_event_levels_listeners) == 0:
            continue
        buff_event_listeners: List[EventListener] = buff_event_levels_listeners[
            buff.level - 1
            ]
        for event_listener in buff_event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(
                    EventListenerContainer(event_listener, buff)
                )

    if event_type == EventTypes.battle_start or event_type == EventTypes.battle_end:
        for buff in counter_instance.buffs:
            buff_event_levels_listeners = buff.temp.event_listeners
            if len(buff_event_levels_listeners) == 0:
                continue
            buff_event_listeners: List[EventListener] = buff_event_levels_listeners[
                buff.level - 1
            ]
            for event_listener in buff_event_listeners:
                if event_listener.event_type == event_type:
                    event_listener_containers.append(
                        EventListenerContainer(event_listener, buff)
                    )

    # Calculated FieldBuffs
    for field_temp_buff in context.fieldbuffs_temps.values():
        field_target_instances = context.get_hero_list_by_id(field_temp_buff.caster_id)
        for (
            field_target_instance
        ) in field_target_instances:  # 双方同时上阵相同hero的情况
            if (field_target_instance.get_field_buff_by_id(field_temp_buff.id)
                and calculate_if_targe_in_diamond_range(
                    actor_instance.position, field_target_instance.position, field_temp_buff.buff_range
                )
            ):
                field_buff_event_listeners: List[EventListener] = field_temp_buff.event_listeners
                for event_listener in field_buff_event_listeners:
                    field_buff = field_target_instance.get_field_buff_by_id(field_temp_buff.id)
                    if event_listener.event_type == event_type:
                        probability = event_listener.requirement(
                            actor_instance,
                            counter_instance,
                            context,
                            field_buff,
                        )
                        if probability > 0 and random() < probability:
                            event_listener.listener_effects(
                                actor_instance,
                                counter_instance,
                                context,
                                field_buff,
                            )

    # Calculated Skills
    if current_action:
        skill = current_action.skill
        if skill:
            for event_listener in skill.temp.event_listeners:
                if event_listener.event_type == event_type:
                    event_listener_containers.append(
                        EventListenerContainer(event_listener, skill)
                    )

    # Calculate Talents
    talent = actor_instance.temp.talent
    for event_listener in talent.event_listeners:
        if event_listener.event_type == event_type:
            event_listener_containers.append(
                EventListenerContainer(event_listener, talent)
            )

    # Calculate Formation
    formation = context.get_formation_by_player_id(actor_instance.player_id)
    if formation is not None:
        formation_event_listeners: List[EventListener] = formation.temp.event_listeners
        for event_listener in formation_event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(
                    EventListenerContainer(event_listener, formation)
                )

    # Calculate Passives
    passives = actor_instance.enabled_passives
    for passive in passives:
        passive_event_listeners: List[EventListener] = passive.on_event
        for event_listener in passive_event_listeners:
            if event_listener.event_type == event_type:
                event_listener_containers.append(
                    EventListenerContainer(event_listener, passive)
                )

    # re-order the event listeners by priority in accumulated_event_listeners
    event_listener_containers.sort(key=lambda x: x.event_listener.priority)

    for event_listener_container in event_listener_containers:
        probability = event_listener_container.event_listener.requirement(
            actor_instance,
            counter_instance,
            context,
            event_listener_container.instance_self,
        )
        if probability > 0 and random() < probability:
            event_listener_container.event_listener.listener_effects(
                actor_instance,
                counter_instance,
                context,
                event_listener_container.instance_self,
            )
    if event_type == EventTypes.skill_start:
        skill = current_action.skill
        skill.cool_down = skill.temp.max_cool_down+1
    if event_type == EventTypes.before_action_end:
        before_action_end_event(actor_instance, context)
    if event_type == EventTypes.action_end:
        action_end_event(actor_instance, context)
    if event_type == EventTypes.turn_start:
        new_turn_event(actor_instance, context)


def before_death_event_listener(
    actor_instance: 'Hero',
    counter_instance: 'Hero' or None,
    event_type: EventTypes,
    context,
):
    # TODO 统计自身是否带禁止复生buff，以及target.died_once是否为False，再统计自己是否有复生modifier：int 根据modifier的值来判断复活后的血量， died_once = True
    pass


def death_event_listener(
    actor_instance: 'Hero',
    counter_instance: 'Hero' or None,
    event_type: EventTypes,
    context,
):
    event_listener_calculator(actor_instance, counter_instance, EventTypes.hero_death, context)


def action_end_event(actor_instance: 'Hero', context):
    if context.battlemap.get_terrain(actor_instance.position).terrain_type == TerrainType.ZHUOWU:
        context.set_hero_died(actor_instance)
    # 所有的buff的duration-1, 技能, 天赋cd-1
    for buff in actor_instance.buffs:
        buff.duration -= 1
        if buff.duration == 0:
            from open_spiel.python.games.Tiandijie.calculation.OtherlCalculation import calculate_remove_buff

            calculate_remove_buff(buff, actor_instance, context)
    for buff in actor_instance.field_buffs:
        buff.duration -= 1
        if buff.duration == 0:
            actor_instance.field_buffs.remove(buff)

    actor_instance.temp.talent.cooldown -= 1
    if actor_instance.temp.talent.cooldown < 0:
        actor_instance.temp.talent.cooldown = 0

    action = context.get_last_action()
    if not action.has_additional_action:
        actor_instance.actionable = False


def before_action_end_event(actor_instance: 'Hero', context):
    for skill in actor_instance.enabled_skills:
        skill.cool_down -= 1
        if skill.cool_down < 0:
            skill.cool_down = 0


def new_turn_event(actor_instance: 'Hero', context):
    actor_instance.reset_actionable(context=context)
    actor_instance.temp.talent.trigger = 0
    for buff in actor_instance.buffs:
        buff.temp.trigger = 0
    for buff in actor_instance.field_buffs:
        buff.temp.trigger = 0
