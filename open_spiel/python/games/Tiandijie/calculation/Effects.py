from __future__ import annotations

from random import random
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.calculation.damage_calculator import (
    calculate_fix_damage,
    calculate_magic_damage,
    calculate_physical_damage,
)
from open_spiel.python.games.Tiandijie.calculation.OtherlCalculation import (
    calculate_fix_heal,
    calculate_reset_hero_actionable,
    calculate_fix_shield,
    calculate_add_buff,
    calculate_additional_action,
    calculate_additional_move,
)
from open_spiel.python.games.Tiandijie.helpers import random_select

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.hero import Hero
    from open_spiel.python.games.Tiandijie.primitives import Context, Action
    from open_spiel.python.games.Tiandijie.primitives.buff import BuffTemp
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuffTemp import FieldBuffTemp
    from open_spiel.python.games.Tiandijie.primitives.equipment.Equipments import Equipment
    from open_spiel.python.games.Tiandijie.primitives.formation.Formation import Formation
from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuff import FieldBuff
from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill

from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from typing import List
from open_spiel.python.games.Tiandijie.basics import Position
from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import get_defense, get_attack
from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTypes
from open_spiel.python.games.Tiandijie.calculation.BuffStack import get_buff_max_stack
from open_spiel.python.games.Tiandijie.calculation.BuffTriggerLimit import get_buff_max_trigger_limit
from open_spiel.python.games.Tiandijie.state.apply_action import is_hero_live
from open_spiel.python.games.Tiandijie.primitives.talent.Talent import Talent


def get_current_action(context: Context) -> Action:
    return context.actions[-1]


def check_is_attacker(actor: Hero, context: Context) -> bool:
    return actor.id == get_current_action(context).actor.id


def _add_buffs(
    caster: Hero,
    target: Hero,
    buff_temp: List[BuffTemp],
    duration: int,
    context: Context,
    level: int = 1,
):
    for buff in buff_temp:
        calculate_add_buff(buff, duration, level, caster, target, context)


def _remove_actor_certain_buff(buff_temp_id: str, actor: Hero):
    actor.buffs = [buff for buff in actor.buffs if buff.temp.id != buff_temp_id]


def _reduce_actor_certain_buff_stack(
    buff_temp_id: str, actor: Hero, reduced_stack: int
):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            buff.stack -= reduced_stack
            if buff.temp.stack <= 0:
                actor.buffs.remove(buff)
            break


def _increase_actor_certain_buff_stack(
    buff_temp_id: str, actor: Hero, increase_stack: int
):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            if buff.stack >= buff.temp.max_stack:
                return
            buff.stack += increase_stack
            break


def _increase_actor_energy(actor: Hero, increase_stack: int):
    pass


def _reduce_actor_energy(actor: Hero, increase_stack: int):
    pass


def _increase_actor_certain_buff_max_stack(buff_temp_id: str, actor: Hero):
    for buff in actor.buffs:
        if buff.temp.id == buff_temp_id:
            buff.stack = get_buff_max_stack(buff.temp)
            break


def _reserve_buffs(
    actor: Hero, target: Hero, is_benefit: bool, buff_count: int, context: Context
):
    if is_benefit:
        target_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Benefit
        ]
    else:
        target_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm
        ]
    if not target_buffs:
        return
    selected_buffs = random_select(target_buffs, buff_count)
    new_opposite_buffs = random_select(context.harm_buffs_temps, buff_count)

    for i in range(min(buff_count, len(selected_buffs))):
        _remove_actor_certain_buff(selected_buffs[i].temp.id, target)
        _add_buffs(
            actor,
            target,
            [new_opposite_buffs[i]],
            selected_buffs[i].duration,
            context,
        )


# Field Buffs
def _add_field_buffs(
    caster: Hero,
    target: Hero,
    field_buff_temp: List[FieldBuffTemp],
    duration: int,
    context: Context,
):
    new_field_buffs = [FieldBuff(b, duration + 1, caster.id) for b in field_buff_temp]
    for new_field_buff in new_field_buffs:
        existing_field_buff = next(
            (
                field_buff
                for field_buff in target.field_buffs
                if field_buff.temp.id == new_field_buff.temp.id
            ),
            None,
        )
        if existing_field_buff is not None:
            # Replace the existing buff if the new buff has a higher level
            if new_field_buff.level > existing_field_buff.level:
                target.field_buffs.remove(existing_field_buff)
                target.field_buffs.append(new_field_buff)
            else:
                existing_field_buff.duration = duration
        else:
            target.field_buffs.append(new_field_buff)


def _remove_actor_certain_field_buff(field_buff_temp_id: str, actor: Hero):
    actor.field_buffs = [
        field_buff
        for field_buff in actor.field_buffs
        if field_buff.temp.id != field_buff_temp_id
    ]


class Effects:

    @staticmethod
    def remove_caster_harm_buff(
        buff_count: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        caster = context.get_hero_by_id(primary.caster_id)
        selected_buffs = random_select(caster.buffs, buff_count)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, caster)

    @staticmethod
    def add_enemies_harm_buff(
        enemy_number: int,
        buff_number: int,
        square_range: int,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        targets = context.get_enemies_in_square_range(actor_instance, square_range)
        selected_harm_buff_temps = random_select(context.harm_buffs_temps, buff_number)
        selected_heroes = random_select(targets, enemy_number)
        for enemy_hero in selected_heroes:
            _add_buffs(
                actor_instance, enemy_hero, selected_harm_buff_temps, duration, context
            )

    @staticmethod
    def add_all_harm_buff_in_range(
        buff_number: int,
        square_range: int,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        targets = context.get_enemies_in_square_range(actor_instance, square_range)
        selected_harm_buff_temps = random_select(context.harm_buffs_temps, buff_number)
        for enemy_hero in targets:
            _add_buffs(
                actor_instance, enemy_hero, selected_harm_buff_temps, duration, context
            )

    @staticmethod
    def reduce_skill_cooldown(
        cooldown_reduction: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        skill_id = context.get_last_action().skill.temp.id
        for skills in actor_instance.enabled_skills:
            if skills.temp.id == skill_id:
                skills.cool_down -= cooldown_reduction
                if skills.cool_down < 0:
                    skills.cool_down = 0

    @staticmethod
    def replace_buff(
        existed_buff_id: str,
        new_buff_id: str,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
    ):
        _remove_actor_certain_buff(existed_buff_id, target_instance)
        _add_buffs(
            actor_instance,
            target_instance,
            [context.get_buff_temp_by_id(new_buff_id)],
            2,
            context,
        )

    @staticmethod
    def replace_self_buff(
        existed_buff_id: str,
        new_buff_id: str,
        duration: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        _remove_actor_certain_buff(existed_buff_id, actor_instance)
        _add_buffs(
            caster,
            actor_instance,
            [context.get_buff_temp_by_id(new_buff_id)],
            duration,
            context,
        )

    @staticmethod
    def update_self_additional_action(
        additional_move: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary,
    ):
        calculate_additional_action(actor, context, additional_move)

    @staticmethod
    def update_self_additional_move(
        additional_move: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary,
    ):
        calculate_additional_move(actor, context, additional_move)

    @staticmethod
    def take_effect_of_xiayi(
        actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        context.get_last_action().update_additional_move(actor_instance, 4, context)
        _reduce_actor_certain_buff_stack("xiayi", actor_instance, 2)

    @staticmethod
    def increase_actor_certain_buff_stack(
        buff_id: str, actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        _increase_actor_certain_buff_stack(buff_id, actor_instance, 1)

    @staticmethod
    def increase_actor_certain_buff_max_stack(
        buff_id: str, actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        _increase_actor_certain_buff_max_stack(buff_id, actor_instance)

    @staticmethod
    def reduce_actor_certain_buff_stack(
        buff_id: str,
        stack_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary
    ):
        _reduce_actor_certain_buff_stack(buff_id, actor_instance, stack_value)

    @staticmethod
    def heal_self(
        multiplier: float, actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        actor_max_life = actor_instance.get_max_life(context)
        calculate_fix_heal(
            actor_max_life * multiplier, actor_instance, actor_instance, context, primary.temp.id
        )

    @staticmethod
    def heal_target_by_magic_attack(
        multiplier: float, actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        actor_magic_attack = get_attack(actor_instance, target_instance, context, True, True)
        calculate_fix_heal(
            actor_magic_attack * multiplier, actor_instance, target_instance, context, primary.temp.id
        )

    @staticmethod
    def heal_caster(
        multiplier: float,
        actor_instance: Hero,
        caster_hero: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        caster_max_life = actor_instance.get_max_life(context)
        calculate_fix_heal(
            caster_max_life * multiplier, actor_instance, caster_hero, context, buff.temp.id
        )

    @staticmethod
    def heal_self_by_caster_physical_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_magic_attack = get_attack(
            actor_instance, None, context, False, True
        )
        calculate_fix_heal(
            caster_magic_attack * multiplier, actor_instance, target_instance, context, buff.temp.id
        )

    @staticmethod
    def heal_self_by_caster_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        caster_magic_attack = get_attack(
            caster_hero, target_instance, context, True, True
        )
        calculate_fix_heal(
            caster_magic_attack * multiplier, actor_instance, target_instance, context, buff.temp.id
        )

    @staticmethod
    def remove_partner_harm_buffs(
        buff_count: int,
        range_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        partners = context.get_partners_in_diamond_range(actor_instance, range_value)
        for partner in partners:
            selected_harm_buffs = random_select(context.harm_buffs_temps, buff_count)
            for selected_harm_buff in selected_harm_buffs:
                partner.buffs = [
                    buff
                    for buff in partner.buffs
                    if buff.temp.id != selected_harm_buff.id
                ]

    @staticmethod
    def add_buffs(
        buff_list: List[str],
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary,
    ):
        _add_buffs(
            actor,
            target,
            [context.get_buff_by_id(buff_temp_id) for buff_temp_id in buff_list],
            duration,
            context,
        )

    @staticmethod
    def add_self_buffs(
        buff_list: List[str],
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary: Buff or Skill or Formation,
    ):
        _add_buffs(
            actor,
            actor,
            [context.get_buff_by_id(buff_temp_id) for buff_temp_id in buff_list],
            duration,
            context,
        )

    @staticmethod
    def add_certain_buff_with_level(
        buff_name: str,
        duration: int,
        level: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary,
    ):
        _add_buffs(
            actor,
            target,
            [context.get_buff_by_id(buff_name)],
            duration,
            context,
            level,
        )

    @staticmethod
    def add_caster_buffs(
        buff_list: List[str],
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        _add_buffs(
            actor,
            caster,
            [context.get_buff_by_id(buff_temp_id) for buff_temp_id in buff_list],
            duration,
            context,
        )

    @staticmethod
    def add_caster_benefit_buffs(
        count: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary
    ):
        caster = context.get_hero_by_id(primary.caster_id)
        benefit_buffs = random_select(context.benefit_buffs, count)
        actor = context.actor
        _add_buffs(
            caster,
            caster,
            benefit_buffs,
            2,
            context,
        )

    @staticmethod
    def add_fixed_damage_by_current_life(
        percentage: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        if check_is_attacker(actor_instance, context):
            current_life = target_instance.get_current_life(context)
            calculate_fix_damage(current_life * percentage, actor_instance, target_instance, context, primary.temp.id)

    @staticmethod
    def add_fixed_damage_with_attack_and_defense(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, is_magic, context)
                + get_defense(actor_instance, target_instance, is_magic, context)
            ) * multiplier
            calculate_fix_damage(damage, actor_instance, target_instance, context, primary.temp.id)

    @staticmethod
    def add_fixed_damage_with_physical_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, context, False) * multiplier
            )
            calculate_fix_damage(damage, actor_instance, target_instance, context, primary.temp.id)

    @staticmethod
    def add_fixed_damage_with_physical_and_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        if check_is_attacker(actor_instance, context):
            damage = (
                get_attack(actor_instance, target_instance, context, False)
                + get_attack(actor_instance, target_instance, context, True)
            ) * multiplier
            calculate_fix_damage(damage, actor_instance, target_instance, context, primary.temp.id)

    @staticmethod
    def add_fixed_damage_in_range_by_physical_defense(
        multiplier: float,
        range_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        enemies = context.get_enemies_in_square_range(actor_instance, range_value)
        for enemy in enemies:
            damage = get_defense(enemy, actor_instance, False, context) * multiplier
            calculate_fix_damage(damage, actor_instance, enemy, context, primary.temp.id)

    @staticmethod
    def add_fixed_damage_in_range_by_max_life(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_partners_in_diamond_range(actor, range_value)
        for target in targets:
            damage = target.get_max_life(context) * multiplier
            calculate_fix_damage(damage, caster, target, context, buff.temp.id)
        damage = actor.get_max_life(context) * multiplier
        calculate_fix_damage(damage, caster, actor, context, buff.temp.id)

    @staticmethod
    def add_fixed_damage_in_diamond_range_by_caster_magic_attack(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_enemies_in_diamond_range(caster, range_value)
        for target in targets:
            damage = get_attack(caster, target, context, True, True) * multiplier
            calculate_fix_damage(damage, caster, target, context, buff.temp.id)

    @staticmethod
    def add_fixed_damage_in_range_by_caster_magic_attack(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_enemies_in_square_range(caster, range_value)
        for target in targets:
            damage = get_attack(caster, target, context, True, True) * multiplier
            calculate_fix_damage(damage, caster, target, context, buff.temp.id)

    @staticmethod
    def add_fixed_damage_in_range_by_caster_physical_attack(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff or Talent,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        targets = context.get_enemies_in_square_range(caster, range_value)
        for target in targets:
            damage = get_attack(caster, target, context, False, True) * multiplier
            calculate_fix_damage(damage, caster, target, context, buff.temp.id)

    @staticmethod
    def add_fixed_damage_by_caster_physical_attack(
        multiplier: float,
        actor: Hero,
        target: Hero,
        context: Context,
        primitive: Buff or Talent,
    ):
        caster = context.get_hero_by_id(primitive.caster_id)
        damage = get_attack(caster, actor, context, False) * multiplier
        calculate_fix_damage(damage, caster, target, context, primitive.temp.id)

    @staticmethod
    def add_fixed_damage_by_caster_magic_attack(
        multiplier: float,
        actor: Hero,
        target: Hero,
        context: Context,
        primitive,
    ):
        caster = actor if type(primitive) == Skill else context.get_hero_by_id(primitive.caster_id)
        damage = get_attack(caster, actor, context, True) * multiplier
        calculate_fix_damage(damage, caster, target, context, primitive.temp.id)

    @staticmethod
    def add_fixed_damage_by_target_max_life(
        multiplier: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        damage = target.get_max_life(context) * multiplier
        calculate_fix_damage(damage, caster, target, context, buff.temp.id)

    @staticmethod
    def add_fixed_damage_by_target_lose_life(
        multiplier: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        damage = (
            target.get_max_life(context) - target.get_current_life(context)
        ) * multiplier
        calculate_fix_damage(damage, caster, actor, context, buff.temp.id)

    @staticmethod
    def receive_fixed_damage_by_current_life_percentage(
        multiplier: float,
        is_magic: bool,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = actor_instance.get_current_life(context) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context, buff.temp.id)

    @staticmethod
    def receive_fixed_damage_by_max_life_percentage(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        actor_max_life = actor_instance.get_max_life(context)
        damage = actor_max_life * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context, buff.temp.id)

    @staticmethod
    def receive_fixed_damage_by_caster_physical_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = get_attack(caster_hero, actor_instance, context, False) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context, buff.temp.id)

    @staticmethod
    def receive_fixed_damage_by_caster_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = get_attack(caster_hero, actor_instance, context, True) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context, buff.temp.id)

    @staticmethod
    def receive_fixed_damage_by_physical_defense_and_magic_defense(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        damage = (
            get_defense(actor_instance, target_instance, False, context)
            + get_defense(actor_instance, target_instance, True, context)
        ) * multiplier
        calculate_fix_damage(damage, caster_hero, actor_instance, context, buff.temp.id)

    @staticmethod
    def add_target_harm_buffs(
        buff_temp_ids: List[str],
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        buff_temps = [
            context.get_harm_buff_temp_by_id(buff_temp_id)
            for buff_temp_id in buff_temp_ids
        ]
        add_buffs = map(lambda b: Buff(b, 2, actor_instance.id), buff_temps)
        target_instance.buffs.extend(add_buffs)

    @staticmethod
    def reduce_target_benefit_buff_duration(
        duration_reduction: int, is_attacker: bool, context: Context, primary
    ):
        action = context.get_action_by_side(is_attacker)
        for target in action.targets:
            for buff in target.buffs:
                if (
                    buff.type == BuffTypes.Benefit
                ):  # Assuming each buff has an 'is_advantage' attribute
                    buff.duration -= duration_reduction
                    if buff.duration < 0:
                        buff.duration = 0  # Prevent negative duration

    @staticmethod
    def check_buff_conditional_add_target_buff(
        check_buff: BuffTemp,
        add_buff: BuffTemp,
        duration: int,
        is_attacker: bool,
        context: Context,
        primary,
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        action = context.get_action_by_side(is_attacker)
        if any(buff.temp == check_buff for buff in actor.buffs):
            for target in action.targets:
                _add_buffs(actor, target, [add_buff], duration, context)

    @staticmethod
    def add_partner_harm_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        is_attacker: bool,
        context: Context,
        primary,
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        selected_harm_buff_temps = random_select(context.harm_buffs_temps, buff_number)
        for partner in partners:
            _add_buffs(actor, partner, selected_harm_buff_temps, duration, context)

    @staticmethod
    def add_partner_benefit_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        is_attacker: bool,
        context: Context,
        primary,
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        selected_benefit_buff_temps = random_select(context.benefit_buffs, buff_number)
        for partner in partners:
            _add_buffs(actor, partner, selected_benefit_buff_temps, duration, context)

    @staticmethod
    def remove_partner_selected_buffs(
        buff_temp: BuffTemp, range_value: int, is_attacker: bool, context: Context, primary
    ):
        actor = context.get_actor_by_side_in_battle(is_attacker)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        for partner in partners:
            partner.buffs = [
                buff for buff in partner.buffs if buff.temp.id != buff_temp.id
            ]

    @staticmethod
    def clear_terrain_by_buff_name(buff_id: str, context: Context):
        battlemap = context.battlemap
        battlemap.remove_terrain_buff_by_name(buff_id)

    @staticmethod
    def add_terrain_by_self_position(
        terrain_buff: str,
        duration: int,
        range_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        from open_spiel.python.games.Tiandijie.calculation.Range import Range, RangeType
        from open_spiel.python.games.Tiandijie.primitives.map.TerrainBuff import TerrainBuffTemps

        buff_range = Range(RangeType.DIAMOND, range_value)
        for position in buff_range.get_area(
            actor_instance.position, actor_instance.position, context.battlemap
        ):
            context.battlemap.add_terrain_buff(
                position, TerrainBuffTemps.get_buff_temp_by_id(terrain_buff), duration, actor_instance.id
            )

    @staticmethod
    def add_terrain_buff_by_target_position(
        terrain_buff: str,
        duration: int,
        range_value: int,
        actor_instance: Hero,
        target_position: Position,
        context: Context,
    ):
        from open_spiel.python.games.Tiandijie.calculation.Range import Range, RangeType
        from open_spiel.python.games.Tiandijie.primitives.map.TerrainBuff import TerrainBuffTemps

        buff_range = Range(RangeType.DIAMOND, range_value)
        for position in buff_range.get_area(target_position, target_position, context.battlemap):
            context.battlemap.add_terrain_buff(
                position, TerrainBuffTemps.get_buff_temp_by_id(terrain_buff), duration, actor_instance.id
            )

    @staticmethod
    def receive_fixed_magic_damage_by_caster_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        if caster_hero.is_alive:
            caster_magic_attack = get_attack(
                actor_instance, target_instance, context, True, True
            )
            calculate_magic_damage(
                caster_magic_attack * multiplier, caster_hero, actor_instance, context, buff.temp.id
            )

    @staticmethod
    def take_physical_damage(
        multiplier: float, is_attacker: bool, context: Context, caster_id: str
    ):
        actor = context.getlast_action().actor
        caster_hero = context.get_hero_by_id(caster_id)
        if caster_hero.alive:
            caster_attack = get_attack(caster_hero, actor, context, False, True)
            calculate_physical_damage(
                caster_attack * multiplier, is_attacker, actor, context
            )

    @staticmethod
    def take_fixed_damage_by_percentage(
        percentage: float,
        actor_instance: Hero,
        target_instance: Hero or None,
        context: Context,
        primary,
    ):
        actor_max_life = actor_instance.get_max_life(context)
        caster = context.get_hero_by_id(primary.caster_id)
        calculate_fix_damage(
            actor_max_life * percentage, actor_instance, caster, context, primary.temp.id
        )

    @staticmethod
    def take_fixed_damage_by_percentage_per_each_move(
        percentage: float, max_percentage: int, actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        caster = context.get_hero_by_id(primary.caster_id)
        action = context.get_last_action()
        enemies = context.get_enemy_list_by_id(actor_instance.player_id)
        move_count = action.get_moves(context.battlemap, enemies)
        actor_max_life = actor_instance.get_max_life(context)
        multiplier = min(percentage * move_count, max_percentage)
        calculate_fix_damage(actor_max_life * multiplier, caster, actor_instance, context, primary.temp.id)

    @staticmethod
    def remove_actor_certain_buff(
        buff_temp_id: str, actor: Hero, target: Hero, context: Context, primary
    ):
        _remove_actor_certain_buff(buff_temp_id, actor)

    @staticmethod
    def remove_target_certain_buff(
        buff_temp_id: str, actor: Hero, target: Hero, context: Context, primary
    ):
        _remove_actor_certain_buff(buff_temp_id, target)

    @staticmethod
    def remove_actor_harm_buffs(
        count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        # collect all harm buffs in target.buffs and remove count number of them
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, actor)

    @staticmethod
    def remove_self_harm_buffs(count: int, actor: Hero, target: Hero, context: Context, primary):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, actor)

    @staticmethod
    def remove_target_harm_buffs_in_range(
        count: int, range_value: int, actor: Hero, target: Hero, context: Context, primary
    ):

        enemies = context.get_enemies_in_diamond_range(actor, range_value)
        for enemy in enemies:
            harm_buffs = [
                buff for buff in enemy.buffs if buff.temp.type == BuffTypes.Harm
            ]
            for harm_buff in harm_buffs[:count]:
                _remove_actor_certain_buff(harm_buff.temp.id, enemy)

    @staticmethod
    def remove_partner_harm_buffs_in_range(
        count: int, range_value: int, actor: Hero, target: Hero, context: Context, primary
    ):

        partners = context.get_enemies_in_diamond_range(actor, range_value)
        for partner in partners:
            harm_buffs = [
                buff for buff in partner.buffs if buff.temp.type == BuffTypes.Harm
            ]
            for harm_buff in harm_buffs[:count]:
                _remove_actor_certain_buff(harm_buff.temp.id, partner)

    @staticmethod
    def remove_actor_benefit_buffs(
        count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        harm_buffs = [
            buff for buff in actor.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        for harm_buff in harm_buffs[:count]:
            _remove_actor_certain_buff(harm_buff.temp.id, actor)

    @staticmethod
    def remove_target_benefit_buffs(
        count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        # collect all benefit buffs in target.buffs and remove count number of them
        benefit_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        for benefit_buff in benefit_buffs[:count]:
            _remove_actor_certain_buff(benefit_buff.temp.id, target)

    @staticmethod
    def increase_target_harm_buff_level(
        buff_level: int, actor: Hero, target: Hero, context: Context, primary
    ):
        harm_buffs = [buff for buff in target.buffs if buff.temp.type == BuffTypes.Harm]
        for buff in harm_buffs:
            if buff.temp.upgradable:
                buff.level += buff_level
                _add_buffs(actor, target, buff, buff.duration, context)

    @staticmethod
    def take_effect_of_tianjiyin(
        actor: Hero, target: Hero, is_attacker: bool, context: Context, buff: Buff
    ):
        partners = context.get_partners_in_diamond_range(actor, 3)
        damage = get_current_action(context).total_damage
        if damage > 0:  # 为3格范围内其他友方恢复气血（恢复量为施术者法攻的0.5倍）
            for partner in partners:
                Effects.heal_self_by_caster_magic_attack(
                    multiplier=0.5,
                    actor_instance=actor,
                    target_instance=partner,
                    context=context,
                    buff=buff,
                )
        else:  # 反之为自身3格范围内4个其他友方施加1个随机「有益状态」
            Effects.add_partner_benefit_buffs(
                buff_number=1,
                range_value=3,
                duration=2,
                is_attacker=is_attacker,
                context=Context,
                primary=buff,
            )

    @staticmethod
    def take_effect_of_weilan(
        actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        partners = context.get_partners_in_diamond_range(actor, 3)
        for partner in partners:
            Effects.heal_self_by_caster_magic_attack(
                multiplier=0.4,
                actor_instance=actor,
                target_instance=partner,
                context=context,
                buff=buff,
            )
        Effects.remove_partner_harm_buffs(1, 3, actor, target, context, buff)

    @staticmethod
    def reverse_target_harm_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _reserve_buffs(actor, target, False, buff_count, context)

    @staticmethod
    def reverse_target_benefit_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _reserve_buffs(actor, target, True, buff_count, context)

    @staticmethod
    def reverse_target_benefit_buffs_in_range(
        buff_count: int, range_value: int, actor: Hero, target: Hero, context: Context, primary
    ):
        enemies = context.get_enemies_in_square_range(actor, range_value)
        for enemy in enemies:
            _reserve_buffs(actor, enemy, True, buff_count, context)

    @staticmethod
    def reverse_self_harm_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _reserve_buffs(actor, actor, False, buff_count, context)

    @staticmethod
    def reverse_self_benefit_buffs(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _reserve_buffs(actor, actor, True, buff_count, context)

    @staticmethod
    def add_self_random_harm_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        harm_buffs = random_select(context.harm_buffs_temps, buff_count)
        _add_buffs(actor, actor, harm_buffs, 2, context)

    @staticmethod
    def add_self_random_benefit_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        benefit_buffs = random_select(context.benefit_buffs, buff_count)
        _add_buffs(actor, actor, benefit_buffs, 2, context)

    @staticmethod
    def add_target_random_harm_buff(
        buff_count: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff or Skill
    ):
        harm_buffs = random_select(context.harm_buffs_temps, buff_count)
        _add_buffs(actor, target, harm_buffs, 2, context)

    @staticmethod
    def add_attacker_random_harm_buff_with_probability(
        buff_count: int,
        probability: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        if random() < probability:
            harm_buffs = random_select(context.harm_buffs_temps, buff_count)
            _add_buffs(actor, target, harm_buffs, 2, context)

    @staticmethod
    def add_partner_random_benefit_buff(
        buff_count: int, range_value: int, actor: Hero, target: Hero, context: Context, primary
    ):
        benefit_buffs = random_select(context.benefit_buffs, buff_count)
        partners = context.get_partners_in_diamond_range(actor, range_value)
        for partner in partners:
            _add_buffs(actor, partner, benefit_buffs, 2, context)

    @staticmethod
    def kill_self(actor: Hero, target: Hero, context: Context, buff: Buff):
        actor.current_life = 0
        is_hero_live(actor, actor, context)

    @staticmethod
    def heal_partner_and_add_benefit_buff_by_caster(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster_hero = context.get_hero_by_id(buff.caster_id)
        if caster_hero.alive:
            partners = context.get_partners_in_diamond_range(caster_hero, range_value)
            for partner in partners:
                Effects.heal_self_by_caster_magic_attack(
                    multiplier, actor, partner, context, buff
                )
                benefit_buffs = random_select(context.benefit_buffs, 1)
                _add_buffs(actor, partner, benefit_buffs, 2, context)

    @staticmethod
    def increase_self_loongest_skill_cooldown(
        cooldown_reduction: int, actor: Hero, target: Hero, context: Context, primary
    ):
        longest_skill = max(actor.enabled_skills, key=lambda x: x.cool_down)
        longest_skill.cool_down += cooldown_reduction

    @staticmethod
    def reduce_self_all_skill_cooldown(
        cooldown_reduction: int, actor: Hero, target: Hero, context: Context, primary
    ):
        for skill in actor.enabled_skills:
            skill.cool_down -= cooldown_reduction
            if skill.cool_down < 0:
                skill.cool_down = 0

    @staticmethod
    def reduce_self_ramdon_damage_skill_cooldown(
        cooldown_reduction: int, actor: Hero, target: Hero, context: Context, primary
    ):
        pass
        # for skill in actor.enabled_skills:
        #     skill.cool_down -= cooldown_reduction
        #     if skill.cool_down < 0:
        #         skill.cool_down = 0

    @staticmethod
    def steal_target_benefit_buff(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        benefit_buffs = [
            buff for buff in target.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        selected_buffs = random_select(benefit_buffs, buff_count)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buffs.temp.id, target)
            _add_buffs(
                actor, actor, selected_buff.temp, selected_buff.duration, context
            )

    @staticmethod
    def stolen_self_benefit_buff_by_caster(
        buff_count: int, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        benefit_buffs = [
            buff for buff in actor.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        selected_buffs = random_select(benefit_buffs, buff_count)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, actor)
            selected_buff_caster = context.get_hero_by_id(selected_buff.caster_id)
            _add_buffs(
                selected_buff_caster,
                caster,
                selected_buff.temp,
                selected_buff.duration,
                context,
            )

    @staticmethod
    def extend_enemy_harm_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary,
    ):
        targets = context.get_enemies_in_diamond_range(actor, range_value)
        for enemy in targets:
            for buff in enemy.buffs:
                if buff.temp.type == BuffTypes.Harm:
                    buff.duration += duration

    @staticmethod
    def extend_partner_benefit_buffs(
        buff_number: int,
        range_value: int,
        duration: int,
        actor: Hero,
        target: Hero,
        context: Context,
        primary,
    ):
        partners = context.get_partners_in_diamond_range(actor, range_value)
        for partner in partners:
            for buff in partner.buffs:
                if buff.temp.type == BuffTypes.Benefit:
                    buff.duration += duration

    @staticmethod
    def transfer_self_harm_buff_to_attacker(
        buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        selected_buffs = random_select(harm_buffs, buff_count)
        caster = context.get_hero_by_id(target.caster_id)
        for selected_buff in selected_buffs:
            _remove_actor_certain_buff(selected_buff.temp.id, actor)
            _add_buffs(
                caster, target, selected_buff.temp, selected_buff.duration, context
            )

    @staticmethod
    def heal_least_partner_health_by_physical_attack_in_range(
        multiplier: float,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        partners = context.get_partners_in_diamond_range(actor, range_value)
        min_heal_actor = partners[0]
        for partner in partners:
            if partner.get_current_life(context) < min_heal_actor.get_current_life(context):
                min_heal_actor = partner
        Effects.heal_self_by_caster_physical_attack(
            multiplier, actor, min_heal_actor, context, buff
        )

    @staticmethod
    def heal_self_and_caster_damage(
        multiplier: float, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        damage = get_current_action(context).total_damage
        calculate_fix_heal(damage * multiplier, actor, caster, context, buff.temp.id)
        calculate_fix_heal(damage * multiplier, actor, actor, context, buff.temp.id)

    @staticmethod
    def heal_self_and_transfer_self_harm_buff(
        multiplier: float, actor: Hero, target: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for harm_buff in harm_buffs:
            harm_buff_caster = context.get_hero_by_id(harm_buff.caster_id)
            _remove_actor_certain_buff(harm_buff.temp.id, actor)
            _add_buffs(
                caster, harm_buff_caster, harm_buff.temp, harm_buff.duration, context
            )
        Effects.heal_self_by_caster_magic_attack(
            multiplier, caster, actor, context, buff
        )

    @staticmethod
    def heal_self_and_remove_harm_buffs(
        multiplier: float, buff_count: int, actor: Hero, target: Hero, context: Context, primary
    ):
        harm_buffs = [buff for buff in actor.buffs if buff.temp.type == BuffTypes.Harm]
        for i in range(buff_count):
            harm_buff = random_select(harm_buffs, 1)
            _remove_actor_certain_buff(harm_buff.temp.id, actor)
            harm_buffs.remove(harm_buff)
        Effects.heal_self(multiplier, actor, actor, context, primary)

    @staticmethod
    def receive_fixed_damage_with_maxlife_and_losslife(
        multiplier: float,
        multiplier2: float,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        actor_max_life = actor.get_max_life(context)
        damage = (
            actor_max_life * multiplier
            + (actor_max_life - actor.get_current_life(context)) * multiplier2
        )
        caster = context.get_hero_by_id(buff.caster_id)
        calculate_fix_damage(damage, caster, actor, context, buff.temp.id)

    @staticmethod
    def take_effect_of_qingliu(actor: Hero, target: Hero, context: Context, buff: Buff):
        Effects.heal_self_by_caster_magic_attack(0.4, actor, target, context, buff)
        partners = context.get_partners_in_diamond_range(actor, 2)
        min_life_percentage = 1
        min_life_percentage_partner = partners[0]
        for partner in partners:
            if partner.get_current_life(context) / partner.max_life < min_life_percentage:
                min_life_percentage = partner.get_current_life(context) / partner.max_life
                min_life_percentage_partner = partner
        harm_buffs = [
            buff
            for buff in min_life_percentage_partner.buffs
            if buff.temp.type == BuffTypes.Harm
        ]
        selected_harm_buffs = random_select(harm_buffs, 1)
        _remove_actor_certain_buff(
            selected_harm_buffs[0].temp.id, min_life_percentage_partner
        )

    @staticmethod
    def heal_self_by_damage(
        multiplier: float, actor: Hero, target: Hero, context: Context, primary
    ):
        damage = get_current_action(context).total_damage
        calculate_fix_heal(damage * multiplier, actor, actor, context, primary.temp.id)

    # energy
    @staticmethod
    def increase_self_energy(
        energy_value: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _increase_actor_energy(actor, energy_value)

    @staticmethod
    def increase_target_energy(
        energy_value: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _increase_actor_energy(target, energy_value)

    @staticmethod
    def reduce_target_energy(
        energy_value: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _reduce_actor_energy(target, energy_value)

    @staticmethod
    def reduce_target_energy_in_range(
        range_value: int, energy_value: int, actor: Hero, target: Hero, context: Context, primary
    ):
        enemies = context.get_enemies_in_diamond_range(actor, range_value)
        for enemy in enemies:
            _reduce_actor_energy(enemy, energy_value)

    @staticmethod
    def take_effect_of_quxing(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        if not target.is_alive:
            return
        caster = context.get_hero_by_id(buff.caster_id)
        Effects.add_fixed_damage_in_diamond_range_by_caster_magic_attack(
            0.5, 2, actor, target, context, buff
        )
        _remove_actor_certain_buff("quxing", actor)

    @staticmethod
    def take_effect_of_zhuijia(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        max_trigger = get_buff_max_trigger_limit("zhuijia")
        if buff.trigger >= max_trigger:
            return
        buff.trigger += 1
        Effects.heal_self(0.25, actor, actor, context, buff)
        Effects.remove_actor_harm_buffs(1, actor, actor, context, buff)

    # 以3格范围内物攻/法攻最高的敌人为中心，对其2格范围内所有敌方造成1次「固定伤害」伤害（最大气血的12%），并施加1层「燃烧」状态，持续2回合。
    @staticmethod
    def take_effect_of_tandi(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        max_trigger_limit = get_buff_max_trigger_limit("tandi")
        if buff.trigger >= max_trigger_limit:
            return
        buff.trigger += 1
        caster = context.get_hero_by_id(buff.caster_id)
        _add_buffs(actor, caster, [context.get_buff_by_id("yudi")], 1, context)
        Effects.take_effect_of_yudi(caster, target, context, buff)

    @staticmethod
    def take_effect_of_yudi(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        enemies = context.get_enemies_in_diamond_range(actor, 3)
        if not enemies:
            return
        target_enemy = enemies[0]
        for enemy in enemies:
            if max(
                get_attack(actor, enemy, context, False),
                get_attack(actor, enemy, context, True),
            ) > max(
                get_attack(actor, target_enemy, context, False),
                get_attack(actor, target_enemy, context, True),
            ):
                target_enemy = enemies
        target_enemies = context.get_enemies_in_diamond_range(target_enemy, 2)
        for enemy in target_enemies:
            damage = enemy.get_max_life(context) * 0.12
            calculate_fix_damage(damage, actor, enemy, context, buff.temp.id)
            _add_buffs(actor, enemy, [context.get_buff_by_id("ranshao")], 2, context)

    @staticmethod
    def take_effect_of_xueqi(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        if not target.is_alive:
            return
        damage = get_current_action(context).total_damage
        calculate_fix_damage(damage, target, actor, context, buff.temp.id)

    @staticmethod
    def take_effect_of_exin(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        benefit_buffs = [
            buff for buff in actor.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        if len(benefit_buffs) <= 2:
            return
        transfer_buffs_count = min(6, len(benefit_buffs) - 2)
        transfer_buffs = random_select(benefit_buffs, transfer_buffs_count)
        for transfer_buff in transfer_buffs:
            _remove_actor_certain_buff(transfer_buff.temp.id, actor)
            _add_buffs(
                caster, actor, transfer_buff.temp, transfer_buff.duration, context
            )
        _add_buffs(actor, caster, [context.get_buff_by_id("xinnian")], 2, context)

    @staticmethod
    def take_effect_of_chaozai(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        damage = get_current_action(context).total_damage
        if damage <= 0:
            return
        if random() < 0.5:
            _add_buffs(actor, actor, [context.get_buff_by_id("jinbi")], 1, context)

    @staticmethod
    def take_effect_of_jianyi_jidang(
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        actor_luck = actor.initial_attribute.luck
        target_luck = target.initial_attribute.luck
        damage = get_attack(actor, target, context, False) + get_attack(
            actor, target, context, True
        )
        if actor_luck > target_luck:
            calculate_fix_damage(damage, actor, target, context, buff.temp.id)
        else:
            calculate_fix_damage(damage * 0.75, actor, target, context, buff.temp.id)

    @staticmethod
    def take_effect_of_longyan(actor: Hero, target: Hero, context: Context, buff: Buff):
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        Effects.increase_target_energy(action.targets, actor, caster, context, buff)

    @staticmethod
    def take_effect_of_ruizou(actor: Hero, target: Hero, context: Context, buff: Buff):
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        Effects.increase_self_energy(1, actor, actor, context, buff)
        Effects.increase_target_energy(1, actor, caster, context, buff)

    @staticmethod
    def take_effect_of_feiyu(
        actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        context.get_last_action().update_additional_move(2)

    # 反转自身2个「有害状态」，恢复自身气血（最大气血的30%），并将自身最多2个「有益状态」复制给3格内的其他友方。（每回合只能触发1次）
    @staticmethod
    def take_effect_of_xunxue(
        actor_instance: Hero, target_instance: Hero, context: Context, buff
    ):
        if buff.trigger >= 1:
            return
        Effects.reverse_self_harm_buffs(2, actor_instance, actor_instance, context, buff)
        Effects.heal_self(0.3, actor_instance, target_instance, context, buff)

        benefit_buffs = [
            buff for buff in actor_instance.buffs if buff.temp.type == BuffTypes.Benefit
        ]
        benefit_buffs = random_select(benefit_buffs, 2)
        partners = context.get_partners_in_diamond_range(actor_instance, 3)
        for partner in partners:
            for benefit_buff in benefit_buffs:
                _add_buffs(
                    actor_instance,
                    partner,
                    benefit_buff.temp,
                    benefit_buff.duration,
                    context,
                )

    @staticmethod
    def take_effect_of_youkai(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        benefit_buffs = [
            buff
            for buff in target_instance.buffs
            if buff.temp.type == BuffTypes.Benefit
        ]
        buff_count = len(benefit_buffs)
        Effects.steal_target_benefit_buff(2, actor_instance, target_instance, context, buff)
        benefit_buffs = [
            buff
            for buff in target_instance.buffs
            if buff.temp.type == BuffTypes.Benefit
        ]
        if buff_count - len(benefit_buffs) == 2:
            Effects.add_fixed_damage_by_target_max_life(
                0.1, actor_instance, target_instance, context, buff
            )
            Effects.remove_actor_certain_buff(
                "youkai", actor_instance, target_instance, context, buff
            )

    @staticmethod
    def take_effect_of_chuliang(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        calculate_fix_damage(
            buff.content * 0.5, actor_instance, actor_instance, context, buff.temp.id
        )

    @staticmethod
    def take_effect_of_xunlie(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        max_trigger_limit = get_buff_max_trigger_limit("xunlie")
        if buff.trigger >= max_trigger_limit:
            return
        caster = context.get_hero_by_id(buff.caster_id)
        damage = get_attack(caster, target_instance, context, False, True)
        calculate_fix_damage(damage * 0.5, caster, target_instance, context, buff.temp.id)

    @staticmethod
    def take_effect_of_shizhou(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        if buff.trigger >= 1:
            return
        buff.trigger += 1
        Effects.add_buffs(
            ["shenrui", "yumo"], 1, actor_instance, target_instance, context, buff
        )

    @staticmethod
    def transfer_certain_buff_to_random_partner(
        buff_id: str,
        range_value: int,
        actor: Hero,
        target: Hero,
        context: Context,
        buff: Buff,
    ):
        max_trigger_limit = get_buff_max_trigger_limit(buff_id)
        if buff.trigger >= max_trigger_limit:
            return
        partners = context.get_partners_in_diamond_range(actor, range_value)
        partner = random_select(partners, 1)[0]
        _remove_actor_certain_buff(buff_id, actor)
        _add_buffs(actor, partner, [context.get_buff_by_id(buff_id)], 2, context)

    @staticmethod
    def transfer_buff_to_other_buff(
        buff_id: str, target_buff_id: str, duration: int, actor: Hero, target: Hero, context: Context, primary
    ):
        _remove_actor_certain_buff(buff_id, actor)
        _add_buffs(actor, target, [context.get_buff_by_id(target_buff_id)], duration, context)

    @staticmethod
    def add_extra_skill(
        skill_value: List[str], actor_hero: Hero, target_hero: Hero, context: Context, primary
    ):
        action = context.get_last_action()
        action.update_additional_skill(skill_value)

    @staticmethod
    def take_effect_of_linghui(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        partners = [
            partner
            for partner in context.get_enemies_in_cross_range(actor_instance, 7)
            if not partner.actionable
        ]
        if not partners:
            return
        target_hero = partners[0]
        for partner in partners:
            if get_attack(target_hero, target_instance, context, True) / get_attack(
                target_hero, target_instance, context, False
            ) > get_attack(partner, target_instance, context, True) / get_attack(
                partner, target_instance, context, False
            ):
                target_hero = partner
        calculate_reset_hero_actionable(actor_instance, target_hero, context)
        Effects.reduce_actor_certain_buff_stack(
            "lingxi", 7, actor_instance, target_instance, context, buff
        )
        buff.cooldown = 3

    @staticmethod
    def take_effect_of_qijin(actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 2)
        if enemies:
            enemy = random_select(enemies, 1)[0]
            Effects.add_buffs(["yunxuan"], 1, actor_instance, enemy, context, buff)

    # Field buffs

    @staticmethod
    def add_self_field_buff(
        buff_list: List[str],
        duration: int,
        actor: Hero,
        target_instance: Hero,
        context: Context,
        field_buff,
    ):
        _add_field_buffs(
            actor,
            actor,
            [context.get_field_buff_temp_by_id(buff_id) for buff_id in buff_list],
            duration,
            context,
        )

    @staticmethod
    def remove_self_field_buff(
        buff_list: List[str], actor: Hero, target_instance: Hero, context: Context, primary
    ):
        for buff_id in buff_list:
            _remove_actor_certain_field_buff(buff_id, actor)

    @staticmethod
    def take_effect_of_songqingming(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        if actor_instance.id == "niexiaoqian":
            _add_buffs(
                actor_instance,
                actor_instance,
                [context.get_buff_by_id(buff_name) for buff_name in ["jiyi", "shenhu"]],
                1,
                context,
            )
            Effects.reduce_self_all_skill_cooldown(
                1, actor_instance, actor_instance, context, buff
            )
        max_trigger_limit = get_buff_max_trigger_limit("songqingming")
        if buff.trigger >= max_trigger_limit:
            return
        caster = context.get_hero_by_id(buff.caster_id)
        _add_buffs(
            actor_instance,
            caster,
            [context.get_field_buff_temp_by_id("mingyun")],
            1,
            context,
        )

    @staticmethod
    def take_effect_of_kongxing(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: Buff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        action = context.get_last_action()
        hero_count = len(action.targets)
        caster_physical_attack = get_attack(caster, actor_instance, context, True, True)
        calculate_fix_damage(
            min(hero_count, 5) * 0.1 * caster_physical_attack,
            caster,
            actor_instance,
            context,
            buff.temp.id
        )
        _add_buffs(
            caster, caster, [context.get_field_buff_temp_by_id("baonu")], 1, context
        )

    @staticmethod
    def take_effect_of_shengyao(
        level_value: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        buff: Buff,
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        if actor_instance.player_id == caster.player_id:
            _add_buffs(
                caster,
                actor_instance,
                [context.get_field_buff_temp_by_id("hunchuang")],
                1,
                context,
            )
            caster.get_max_life(context)
            calculate_fix_heal(0.3 * caster.max_life, actor_instance, caster, context, buff.temp.id)
            if level_value == 2:
                Effects.remove_caster_harm_buff(
                    1, actor_instance, caster, context, buff
                )

    # Talent Field Buffs

    @staticmethod
    def take_effect_of_huzongqianli(
        actor_instance: Hero, target_instance: Hero, context: Context, buff: FieldBuff
    ):
        caster = context.get_hero_by_id(buff.caster_id)
        _add_buffs(
            caster, caster, [context.get_field_buff_temp_by_id("jingjue")], 1, context
        )
        buff.trigger += 1

    @staticmethod
    def take_effect_of_huilingjie(
        state, actor_instance: Hero, target_instance: Hero, context: Context, buff: FieldBuff
    ):
        if state == 1:
            actor_instance.buffs.append(Buff(context.get_buff_by_id("bingqing"), 1, actor_instance))
        else:
            actor_instance.buffs = [buff for buff in actor_instance.buffs if buff.temp.id != "bingqing"]

    @staticmethod
    def take_effect_of_xuanmiejie(
        state, actor_instance: Hero, target_instance: Hero, context: Context, buff: FieldBuff
    ):
        if state == 1:
            actor_instance.buffs.append(Buff(context.get_buff_by_id("wuhui"), 1, actor_instance))
        else:
            actor_instance.buffs = [buff for buff in actor_instance.buffs if buff.temp.id != "wuhui"]

    # Equipment Effects

    @staticmethod
    def take_effect_of_xuanqueyaodai(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        equipment: Equipment,
    ):
        equipment.cooldown = 2
        Effects.heal_self(0.35, actor_instance, actor_instance, context, equipment)
        Effects.remove_actor_harm_buffs(1, actor_instance, actor_instance, context, equipment)

    @staticmethod
    def take_effect_of_jiaorenbeige(
        state: str,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        equipment: Equipment,
    ):
        partners = context.get_partners_in_diamond_range(actor_instance, 2)
        target_partner = partners[0]
        temp_buff = []
        if state == "wu":
            for partner in partners:
                if (
                    partner.initial_attributes.magic_defense
                    > target_partner.initial_attributes.magic_defense
                ):
                    target_partner = partner
            temp_buff = ["yumo"]
        elif state == "yan":
            for partner in partners:
                if max(
                    partner.initial_attributes.attack,
                    partner.initial_attributes.magic_attack,
                ) > max(
                    target_partner.initial_attributes.attack,
                    target_partner.initial_attributes.magic_attack,
                ):
                    target_partner = partner
            temp_buff = ["shenrui"]
        elif state == "chen":
            for partner in partners:
                if (
                    partner.initial_attributes.defense
                    > target_partner.initial_attributes.defense
                ):
                    target_partner = partner
            temp_buff = ["pijia"]
        elif state == "ying":
            for partner in partners:
                if (
                    partner.initial_attributes.luck
                    > target_partner.initial_attributes.luck
                ):
                    target_partner = partner
            temp_buff = ["cigu"]
        Effects.add_buffs(temp_buff, 1, actor_instance, target_partner, context, equipment)

    @staticmethod
    def take_effect_of_lingyuepeihuan(
        state: str,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        equipment: Equipment,
    ):
        enemies = context.get_enemies_in_cross_range(actor_instance, 7)
        if not enemies:
            return
        target_enemy = random_select(enemies, 1)[0]
        if state == "yan":
            buff_name = "piruo"
        elif state == "chen":
            buff_name = "shiyu"
        else:
            buff_name = "shimo"
        Effects.add_buffs([buff_name], 1, actor_instance, target_enemy, context, equipment)

    @staticmethod
    def take_effect_of_dingbizan(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        equipment: Equipment
    ):
        if random() < 0.5:
            Effects.add_certain_buff_with_level(
                "luanshen",
                2,
                1,
                actor_instance,
                target_instance,
                context,
                equipment
            )

    @staticmethod
    def take_effect_of_yuanyujinling(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        equipment: Equipment
    ):
        if random() < 0.3:
            Effects.add_buffs(["piruo"], 2, actor_instance, target_instance, context, equipment)

    @staticmethod
    def take_effect_of_xuanwuyu(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        equipment: Equipment
    ):
        partners = context.get_partners_in_diamond_range(actor_instance, 1)
        partner = random_select(partners, 1)[0]
        for hero in [actor_instance, partner]:
            Effects.add_buffs(["shenhu"], 1, actor_instance, hero, context, equipment)
            Effects.add_buffs(["pixian"], 1, actor_instance, hero, context, equipment)

    # skill effects

    @staticmethod
    def move_point_by_skill(start_point, end_point, steps, map):
        def is_occupied(position, map):
            if not map.get_terrain(position).terrain_type.value[1]:
                return True
        start_x, start_y = start_point
        end_x, end_y = end_point

        direction_x = end_x - start_x
        direction_y = end_y - start_y

        if direction_x != 0:
            direction_x = direction_x / abs(direction_x)
        if direction_y != 0:
            direction_y = direction_y / abs(direction_y)

        # 移动点
        new_x = int(start_x + direction_x * steps)
        new_y = int(start_y + direction_y * steps)

        while new_x < 0 or new_y < 0 or new_x >= map.width or new_y >= map.height or is_occupied((int(new_x), int(new_y)), map):
            new_x -= direction_x
            new_y -= direction_y
        return int(new_x), int(new_y)

    @staticmethod
    def take_effect_of_tabuyanzhan(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        move_point = context.get_last_action().move_point
        action_point = context.get_last_action().action_point
        ending_point = Effects.move_point_by_skill(move_point, action_point, 5, context.battlemap)
        actor_instance.position = ending_point
        actor_instance.transfor_enable_skill("tabuyanzhan", "chuanyanglianzhan", 0)
        enemies = context.get_enemies_in_diamond_range(actor_instance, 2)
        if len(enemies) <= 3:
            Effects.update_self_additional_action(2, actor_instance, target_instance, context, skill)

    @staticmethod
    def take_effect_of_chuanyanglianzhan(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        actor_instance.transfor_enable_skill("chuanyanglianzhan", "tabuyanzhan", 3)

    @staticmethod
    def take_effect_of_huiyanjianjue(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        targets = context.get_last_action().targets
        if len(targets) >= 3:
            for buff in  actor_instance.buffs:
                if buff.temp.id == "zhuneng":
                    buff.duration += 2
        for target in targets:
            Effects.add_buffs(["liuxue"], 2, actor_instance, target, context, skill)

    @staticmethod
    def add_shield_by_self_max_life(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        actor_max_life = actor_instance.get_max_life(context)
        shield_value = actor_max_life * multiplier
        calculate_fix_shield(shield_value, actor_instance, actor_instance, context)

    @staticmethod
    def take_effect_of_leiyinwanyu(actor_instance: Hero, target_instance: Hero, context: Context, skill: Skill):
        actor_instance.transfor_enable_skill("leiyinwanyu", "tianshanluanhun")
        action = context.get_last_action()
        enemies = context.get_enemies_in_square_range(actor_instance, 2)
        partner_positions = set(context.get_all_partners_position(actor_instance))

        map_rule = [
            [5, 10, 15, 20, 25],
            [4, 9, 14, 19, 24],
            [3, 8, "*", 18, 23],
            [2, 7, 12, 17, 22],
            [13, 6, 11, 16, 21],
        ]

        def get_priority(enemy):
            dx = enemy.position[0] - action.action_point[0] + 2
            dy = enemy.position[1] - action.action_point[1] + 2
            return map_rule[dx][dy]

        sorted_enemies = sorted(enemies, key=get_priority)

        teleport_rules = [
            (1, 0), (0, -1), (0, 1), (-1, 0),
            (1, -1), (1, 1), (1, -1), (-1, 1),
            (2, 0), (0, -2), (0, 2), (-2, 0),
            (2, -1), (2, 1), (1, -2), (1, 2),
            (-1, -2), (-1, 2), (-2, -1), (-2, 1)
        ]

        used_positions = set()

        def is_valid_position(new_position):
            if new_position in used_positions:
                return False
            terrain = context.battlemap.get_terrain(new_position)
            if not terrain:
                return False
            if new_position in partner_positions:
                return False
            if terrain.terrain_type in {TerrainType.IMPASSABLE_OBSTACLE, TerrainType.ZHUOWU}:
                return False
            if not enemy.temp.flyable and terrain.terrain_type == TerrainType.FLYABLE_OBSTACLE:
                return False
            return True

        for enemy in sorted_enemies:
            for dx, dy in teleport_rules:
                new_position = (actor_instance.position[0] + dx, actor_instance.position[1] + dy)
                if is_valid_position(new_position):
                    context.teleport_hero(enemy, new_position)
                    used_positions.add(new_position)
                    break  # Exit inner loop once a valid position is found

        now_enemies = context.get_enemies_in_square_range(actor_instance, 2)
        if len(now_enemies) >= 3:
            Effects.update_self_additional_action(0, actor_instance, target_instance, context, skill)

    @staticmethod
    def take_effect_of_tianshanluanhun(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        actor_instance.transfor_enable_skill("tianshanluanhun", "leiyinwanyu", 3)

    @staticmethod
    def take_effect_of_anshayouyan(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        for i in range(3):
            Effects.add_self_buffs(
                ["juexin"], 200, actor_instance, actor_instance, context, skill
            )
        Effects.add_buffs(
            ["jinliao"], 2, actor_instance, target_instance, context, skill
        )
        from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.BuffRequirementChecks import BuffRequirementChecks
        if BuffRequirementChecks.self_buff_stack_reach(
            5, "juexin", actor_instance, actor_instance, context, skill
        ):
            Effects.remove_actor_certain_buff(
                "juexin", actor_instance, actor_instance, context, skill
            )
            Effects.add_self_buffs(
                ["zhilu"], 3, actor_instance, actor_instance, context, skill
            )

    @staticmethod
    def take_effect_of_juezhanwushuang(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        actor_instance.transfor_enable_skill("juezhanwushuang", "yanjinliexiong", 0)

    @staticmethod
    def take_effect_of_yanjinliexiong(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        actor_instance.transfor_enable_skill("yanjinliexiong", "juezhanwushuang", 2)

    @staticmethod
    def take_effect_of_chiqilingyao(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        action = context.get_last_action()
        # 先查看是不是自己的金乌旗
        terrain_position = context.battlemap.get_terrain_position_by_type(TerrainType.JINWUQI)
        if terrain_position:
            terrain = context.battlemap.get_terrain(terrain_position)
            caster = terrain.caster_id
            if actor_instance.id == caster:
                buff_list = ["ranshao"]
                for target in action.targets:
                    position = target.position
                    terrain_buff = context.battlemap.get_terrain(position).buff
                    if terrain_buff and "jinwuqi" == terrain_buff.temp.id:
                        buff_list.append("wangxiao")
                    Effects.add_buffs(buff_list, 2, actor_instance, target, context, skill)
                Effects.remove_jinwuqi(context)

    @staticmethod
    def remove_jinwuqi(context: Context):
        position = context.battlemap.get_terrain_position_by_type(TerrainType.JINWUQI)
        if position is not None:
            terrain = context.battlemap.get_terrain(position)
            caster_id = terrain.caster_id
            Effects.add_buffs(["chiqi"], 15, context.get_hero_by_id(caster_id), context.get_hero_by_id(caster_id), context, None)
            context.battlemap.init_terrain(position)
            Effects.clear_terrain_by_buff_name("jinwuqi", context)

    @staticmethod
    def set_jinwuqi(actor_instance, target_position, context: Context):
        context.battlemap.set_terrain(target_position, TerrainType.JINWUQI, actor_instance.id)
        Effects.add_terrain_buff_by_target_position(
            "jinwuqi", 15, 2, actor_instance, target_position, context
        )

    @staticmethod
    def take_effect_of_buqi(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        Effects.add_shield_by_self_max_life(0.25, actor_instance, None, context, skill)
        target_position = context.get_last_action().action_point
        Effects.remove_jinwuqi(context)
        Effects.remove_actor_certain_buff("chiqi", actor_instance, target_instance, context, skill)
        Effects.set_jinwuqi(actor_instance, target_position, context)
        if actor_instance.special_mark:
            actor_instance.special_mark = False
            calculate_additional_action(actor_instance, context, 3)
            Effects.add_self_buffs(["ranyan"], 2, actor_instance, None, context, skill)

    @staticmethod
    def take_effect_of_yanranchuanyun(
        state,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        if state == 1:
            action = context.get_last_action()
            action.update_additional_move(actor_instance, 3, context)
        elif state == 2:
            position = context.battlemap.get_terrain_position_by_type(TerrainType.JINWUQI)
            if position is not None:
                terrain = context.battlemap.get_terrain(position)
                caster_id = terrain.caster_id
                if caster_id == actor_instance.id:
                    actor_instance.special_mark = True

    @staticmethod
    def take_effect_of_diyuzhizhen(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        action = context.get_last_action()
        for target in action.targets:
            Effects.add_buffs(["pijia"], 3, actor_instance, target, context, skill)

    @staticmethod
    def take_effect_of_shiguizhaohuan(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        pass

    @staticmethod
    def take_effect_of_jingangfalun(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        action = context.get_last_action()
        for target in action.targets:
            Effects.add_certain_buff_with_level("luanshen", 2, 2, actor_instance, target,  context, skill)
            if target.temp.element in {Elements.DARK, Elements.WATER}:
                Effects.add_buffs(["yazhi"], 1, actor_instance, target, context, skill)

    @staticmethod
    def take_effect_of_luohouzhenfa(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        for other_skill in actor_instance.enabled_skills:
            if other_skill.temp.id in {"tianshuangxuewu", "wutianheiyan", "lihuoshenjue"}:
                other_skill.cool_down = skill.cool_down

    @staticmethod
    def heal_targets_by_max_life(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        target_max_life = target_instance.get_max_life(context)
        heal_value = target_max_life * multiplier
        calculate_fix_heal(heal_value, actor_instance, target_instance, context, skill.temp.id)

    @staticmethod
    def take_effect_of_niyuanguixin(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        targets = context.get_last_action().targets
        for target in targets:
            Effects.reverse_target_harm_buffs(2, actor_instance, target, context, skill)
            Effects.add_buffs(["guyuan"], 2, actor_instance, target, context, skill)
            Effects.heal_targets_by_max_life(0.5, actor_instance, target, context, skill)

    @staticmethod
    def take_effect_of_xiekujiayou(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        Effects.add_self_field_buff(["wuyouyu"], 2, actor_instance, target_instance, context, skill)
        Effects.add_self_buffs(["huwei"], 2, actor_instance, target_instance, context, skill)
        partners = context.get_partners_in_diamond_range(actor_instance, 2)
        partners.append(actor_instance)
        for partner in partners:
            Effects.add_buffs(["yumo"], 2, actor_instance, partner, context, skill)

    @staticmethod
    def take_effect_of_luoshuangjingshen(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        skill: Skill,
    ):
        Effects.add_terrain_by_self_position("shuangdong", 2, 2, actor_instance, target_instance, context, skill)
        if context.get_last_action().total_damage > 0:
            actor_instance.damage_container = 0.0

    # weapon Effects

    @staticmethod
    def take_effect_of_haoliweishi(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        weapon
    ):
        partners = context.get_partners_in_diamond_range(actor_instance, 3)
        partners.append(actor_instance)
        for hero in partners:
            Effects.add_buffs(["pijia"], 2, actor_instance, hero, context, weapon)

    @staticmethod
    def take_effect_of_shenwuhanwei(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        weapon
    ):
        partners = context.get_partners_in_diamond_range(actor_instance, 3)
        for partner in partners:
            if partner.get_current_life_percentage(context, target_instance) > 0.8:
                Effects.add_buffs(["shuangkai"], 200, actor_instance, partner, context, weapon)

    @staticmethod
    def take_effect_of_zhenjinbailian(
            actor_instance: Hero, target_instance: Hero, context: Context, weapon
    ):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
        if not enemies:
            return
        for enemy in enemies:
            Effects.add_fixed_damage_by_caster_physical_attack(
                0.3, actor_instance, enemy, context, weapon
            )
        weapon.cooldown = 2

    @staticmethod
    def take_effect_of_juehensugu(
        actor_instance: Hero, target_instance: Hero, context: Context, weapon
    ):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 5)
        count = 0
        for enemy in enemies:
            for buff in enemy.buffs:
                if buff.temp.type == BuffTypes.Harm:
                    count += 1
                    break
            if count >= 5:
                break
        Effects.heal_self(count*0.1, actor_instance, actor_instance, context, weapon)

    # stone Effects

    @staticmethod
    def add_stone_stack(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        stone,
    ):
        if stone.stack < stone.max_stack:
            stone.stack += 1

    @staticmethod
    def take_effect_of_minkui(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        stone,
    ):
        if random() < 0.4:
            benfit_buff = random_select(context.benefit_buffs, 1)[0]
            Effects.add_buffs([benfit_buff], 2, actor_instance, target_instance, context, stone)

    @staticmethod
    def take_effect_of_shierpinliantai(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        primary,
    ):
        pass

    # Passive Effects

    @staticmethod
    def take_effect_of_tongmai(
        actor_instance: Hero, target_instance: Hero, context: Context, passive
    ):
        partners = context.get_all_partners(actor_instance)
        partner = partners[0]
        for p in partners:
            if p.get_current_life_percentage(context) < partner.get_current_life_percentage(context):
                partner = p
        temp_percentage = (actor_instance.get_current_life_percentage(context, target_instance) + partner.get_current_life_percentage(context, target_instance))/2
        actor_instance.current_life_percentage = temp_percentage
        partner.current_life_percentage = temp_percentage
        for target in [actor_instance, partner]:
            Effects.heal_target_by_magic_attack(1, actor_instance, target, context, passive)

    @staticmethod
    def take_effect_of_fengshaganlinshu(
        actor_instance: Hero, target_instance: Hero, context: Context, primary
    ):
        pass