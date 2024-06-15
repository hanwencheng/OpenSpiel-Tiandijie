from __future__ import annotations
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.BuffRequirementChecks import BuffRequirementChecks
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.CheckHelpers import _is_attacker
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.LifeRequirementChecks import LifeRequirementChecks
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.PositionRequirementChecks import (
    PositionRequirementChecks,
)

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
    from open_spiel.python.games.Tiandijie.primitives.skill.skills import Skill
    from open_spiel.python.games.Tiandijie.primitives.formation.Formation import Formation
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuff import FieldBuff
    from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillTargetTypes
    from open_spiel.python.games.Tiandijie.primitives.Action import Action

from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillType
from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_modifier
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma

from typing import List
from open_spiel.python.games.Tiandijie.primitives.hero.Element import get_elemental_relationship, ElementRelationships
from open_spiel.python.games.Tiandijie.primitives.Action import ActionTypes

from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Professions, Gender


class RequirementCheck:
    # TODO  should not include any function related to level2 modifier

    @staticmethod
    def enemies_in_skill_range(
        maximum_count: int, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        counted_enemies = 0
        action = context.get_last_action()
        skill = action.skill
        for hero in context.heroes:
            if hero.player_id != actor_hero.player_id:
                if skill.temp.range_value.check_if_target_in_range(
                    actor_hero.position, skill.target_point, hero.position
                ):
                    counted_enemies += 1
        return min(maximum_count, counted_enemies)

    @staticmethod
    def battle_with_certain_hero(
        hero_temp_id: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if (
                target_hero.temp.id == hero_temp_id
                or actor_hero.temp.id == hero_temp_id
            ):
                return 1
        return 0

    @staticmethod
    def attack_certain_hero(
        hero_temp_id: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if target_hero.temp.id == hero_temp_id:
                return 1
        return 0

    @staticmethod
    def battle_with_caster(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster_id = buff.caster_id
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.id == caster_id:
                return 1
        return 0

    @staticmethod
    def attacked_by_caster(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> int:
        caster_id = buff.caster_id
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if target_hero.id == caster_id:
                return 1
        return 0

    @staticmethod
    def move_less_or_equal_than(
        max_move: int, actor_hero: Hero, target_hero: Hero, context: Context
    ):
        action = context.get_last_action()
        if actor_hero == action.actor:
            if action.moves <= max_move:
                return True
        return False

    @staticmethod
    def move_more_than(
        max_move: int, actor_hero: Hero, target_hero: Hero, context: Context
    ):
        action = context.get_last_action()
        if actor_hero == action.actor:
            if action.moves > max_move:
                return True
        return False

    @staticmethod
    def self_all_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in actor_hero.enabled_skills:
            if skill not in actor_hero.temp.passives and skill.cool_down <= 0:
                return 0
        return 1

    @staticmethod
    def self_has_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in actor_hero.enabled_skills:
            if skill not in actor_hero.temp.passives and skill.cool_down > 0:
                return 1
        return 0

    @staticmethod
    def target_has_active_skills_in_cooldown(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        for skill in target_hero.enabled_skills:
            if skill not in target_hero.temp.passives and skill.cool_down > 0:
                return 1
        return 0

    @staticmethod
    def in_battle_with_non_flyable(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.temp.flyable:
                return 0
            else:
                return 1
        return 0

    @staticmethod
    def in_battle_with_non_female(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            if target_hero.temp.gender != Gender.FEMALE:
                return 1
        return 0

    @staticmethod
    def always_true(actor_hero: Hero, target_hero: Hero, context: Context, primitives) -> int:
        return 1

    @staticmethod
    def battle_with_no_element_advantage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.is_in_battle:
            actor_element = actor_hero.temp.element
            target_element = target_hero.temp.element
            if (
                get_elemental_relationship(actor_element, target_element)
                == ElementRelationships.NEUTRAL
            ):
                return 1
            else:
                return 0
        return 0

    @staticmethod
    def is_attacker(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return _is_attacker(actor_hero, context)

    @staticmethod
    def is_in_battle(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        return action.is_in_battle

    @staticmethod
    def is_attack_target(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return _is_attacker(target_hero, context)

    @staticmethod
    def is_battle_attack_target(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        action = context.get_last_action()
        return _is_attacker(target_hero, context) and action.is_in_battle

    @staticmethod
    def is_battle_with_remote(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if (
            target_hero.temp.profession
            in [
                Professions.SORCERER,
                Professions.PRIEST,
                Professions.ARCHER,
            ]
            and action.is_in_battle
        ):
            return 1
        return 0

    @staticmethod
    def attacked_by_melee_attack(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if (
            target_hero.temp.profession
            in [
                Professions.GUARD,
                Professions.SWORDSMAN,
                Professions.RIDER,
                Professions.WARRIOR,
            ]
            and action.is_in_battle
            and _is_attacker(target_hero, context)
        ):
            return 1
        return 0

    @staticmethod
    def self_is_certain_profession(
        professions: List[Professions],
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
    ) -> int:
        if actor_hero.temp.profession in professions:
            return 1
        return 0

    @staticmethod
    def skill_is_certain_element(
        element_value: Elements, actor_hero: Hero, target_hero: Hero, context: Context, primitives: Buff or Skill or Formation or FieldBuff
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill and action.skill.temp.element == element_value:
                return 1
        return 0

    @staticmethod
    def self_use_certain_skill(
        skill_id: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.id == skill_id:
                return 1
        return 0

    @staticmethod
    def skill_is_in_element_list(
        element_list: List[Elements],
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitives
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.element in element_list:
                return 1
        return 0

    @staticmethod
    def action_is_active_skill(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if context.get_last_action().type == ActionTypes.SKILL_ATTACK:
            return 1
        return 0

    @staticmethod
    def action_is_not_active_skill(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if context.get_last_action().type != ActionTypes.SKILL_ATTACK:
            return 1
        return 0

    @staticmethod
    def is_attacked_by_fire_element(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if action.skill.temp.element == Elements.FIRE:
                return 1
        return 0

    @staticmethod
    def is_attacked_by_non_flyer(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if not target_hero.temp.flyable and action.is_in_battle:
                return 1
        return 0

    @staticmethod
    def attack_to_advantage_elements(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if (
                get_elemental_relationship(
                    actor_hero.temp.element, target_hero.temp.element
                )
                == ElementRelationships.ADVANTAGE
            ):
                return 1
        return 0

    @staticmethod
    def under_attack_by_advantage_elements(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(target_hero, context):
            if (
                get_elemental_relationship(
                    actor_hero.temp.element, target_hero.temp.element
                )
                == ElementRelationships.ADVANTAGE
            ):
                return 1
        return 0

    @staticmethod
    def self_is_used_active_skill(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp in actor_hero.enabled_skills:
                return 1
        return 0

    @staticmethod
    def is_target_by_fire_element(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(target_hero, context):
            if action.skill.temp.element == Elements.FIRE:
                return 1
        return 0

    @staticmethod
    def target_is_certain_element(
        element_value: Elements, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if actor_hero.temp.element == element_value:
                return 1
        return 0

    @staticmethod
    def self_is_certain_element(
        element_value: Elements, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(actor_hero, context):
            if actor_hero.temp.element == element_value:
                return 1
        return 0

    @staticmethod
    def action_has_no_damage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.total_damage == 0:
            return 1
        return 0

    @staticmethod
    def skill_is_damage_type(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        skill = context.get_last_action().skill
        if skill and (skill.temp.skill_type == SkillType.Magical or skill.temp.skill_type == SkillType.Physical):
            return 1
        return 0

    @staticmethod
    def skill_has_no_damage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.skill and action.total_damage == 0:
            return 1
        return 0

    @staticmethod
    def skill_has_damage(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        if action.skill and action.total_damage == 0:
            return 1
        return 0

    @staticmethod
    def target_is_enemy(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return target_hero.player_id != actor_hero.player_id

    @staticmethod
    def target_is_partner(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return target_hero.player_id == actor_hero.player_id

    @staticmethod
    def target_is_single(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        return len(action.targets) == 1

    @staticmethod
    def skill_is_single_target_damage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.skill.temp.range_instance.range_value == 0:
            return 1
        return 0

    @staticmethod
    def skill_is_range_target_damage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if action.skill.temp.range_instance.range_value > 0:
            return 1
        return 0

    @staticmethod
    def skill_is_no_damage_and_target_is_partner(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if RequirementCheck.skill_has_no_damage(
            actor_hero, target_hero, context
        ) and RequirementCheck.target_is_partner(actor_hero, target_hero, context):
            return 1
        return 0

    @staticmethod
    def self_is_target_and_skill_is_range_target_damage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if RequirementCheck.is_attack_target(
            target_hero, actor_hero, context
        ) and RequirementCheck.skill_is_range_target_damage(
            actor_hero, target_hero, context
        ):
            return 1
        return 0

    @staticmethod
    def skill_is_single_target_damage_and_life_is_higher_percentage(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> float:
        if RequirementCheck.skill_is_single_target_damage:
            return actor_hero.current_life / actor_hero.max_life
        return 0

    @staticmethod
    def all_partners_live_count(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        count = 0
        for hero in context.get_all_partners(actor_hero):
            if hero.is_alive:
                count += 1
        return min(count, 4)

    @staticmethod
    def yurenjinpei_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(
            target_hero, context
        ) and LifeRequirementChecks.self_life_is_higher(
            0.8, actor_hero, target_hero, context
        ) and RequirementCheck.is_in_battle(actor_hero, target_hero, context):
            return 1
        return 0

    @staticmethod
    def wangzhezitai_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if _is_attacker(
            target_hero, context
        ) and BuffRequirementChecks.target_has_certain_buff(
            "zhanyin", actor_hero, target_hero, context
        ):
            return 1
        return 0

    @staticmethod
    def is_magic_attack(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        action = context.get_last_action()
        if action.skill.temp.is_magic():
            return 1
        return 0

    @staticmethod
    def is_in_terrain(
        terrain_value: str, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        positon = actor_hero.position
        terrain_buff = context.battlemap.get_terrain(positon).buff
        if terrain_value == terrain_buff.temp.id:
            return 1
        return 0

    @staticmethod
    def jianjue_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if (
            action.skill
            and len(action.skill.target_point) == 1
            and action.total_damage > 0
            and BuffRequirementChecks.self_buff_stack_reach(
                3, "jianjue", actor_hero, target_hero, context
            )
        ):
            return 1
        return 0

    @staticmethod
    def menghai_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if (
            action.skill
            and RequirementCheck.skill_is_range_target_damage(
                actor_hero, target_hero, context
            )
            and action.total_damage > 0
            and LifeRequirementChecks.self_life_is_higher(
                0.8, actor_hero, target_hero, context
            )
        ):
            return 1
        return 0

    @staticmethod
    def xingyun_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if actor_hero in action.targets:
            return min(action.moves, 3)
        return 0

    @staticmethod
    def get_moves_before_battle(
        min_value: int, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context) and action.is_in_battle:
            return min(action.moves, min_value)
        return 0

    @staticmethod
    def self_is_first_attack(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context) and action.is_in_battle():
            if RequirementCheck.target_has_counterattack_first(action, context):
                return 1
        return 0

    @staticmethod
    def target_has_counterattack_first(action: Action, context: Context):
        target = action.get_defender_hero_in_battle()
        actor = action.actor
        is_counterattack_first = get_modifier(
            Ma.is_counterattack_first, target, actor, context
        )
        counterattack_first_limit = get_modifier(
            Ma.counterattack_first_limit, target, actor, context
        )
        return (
            is_counterattack_first
            and counterattack_first_limit > target.counterattack_count
        )

    # Field Buffs

    @staticmethod
    def self_and_caster_is_partner_and_first_attack(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: FieldBuff
    ) -> int:
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        if (
            _is_attacker(actor_hero, context)
            and action.is_in_battle()
            and actor_hero.player_id == caster.player_id
        ):
            if RequirementCheck.target_has_counterattack_first(action, context):
                return 1
        return 0

    @staticmethod
    def miepokongjian_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: FieldBuff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.player_id != actor_hero.player_id:
            return 0
        if LifeRequirementChecks.life_not_full(
            actor_hero, target_hero, context
        ) and RequirementCheck.self_is_first_attack(actor_hero, target_hero, context):
            if buff.trigger < 2:
                buff.trigger += 1
                return 1
        return 0

    @staticmethod
    def huanyanliezhen_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: FieldBuff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.player_id != actor_hero.player_id:
            return 0
        if BuffRequirementChecks.target_has_certain_buff(
            "ranshao", actor_hero, target_hero, context
        ) and RequirementCheck.self_is_first_attack(actor_hero, target_hero, context):
            if buff.trigger < 3:
                buff.trigger += 1
                return 1
        return 0

    @staticmethod
    def self_and_caster_is_enemy(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: FieldBuff
    ) -> int:
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        return caster.player_id != actor_hero.player_id

    @staticmethod
    def yanyukongjian_requires_check(
        level_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        buff: FieldBuff,
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if caster.player_id != actor_hero.player_id:
            return 0
        if RequirementCheck.target_is_certain_element(
            Elements.THUNDER, actor_hero, target_hero, context
        ) and RequirementCheck.self_is_first_attack(actor_hero, target_hero, context):
            if (level_value == 1 or level_value == 2) and buff.trigger <= 2:
                buff.trigger += 1
                return 1
            elif level_value == 3 and buff.trigger <= 3:
                buff.trigger += 1
                return 1
        return 0

    @staticmethod
    def self_and_caster_is_partner(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: FieldBuff
    ) -> int:
        action = context.get_last_action()
        caster = context.get_hero_by_id(buff.caster_id)
        return caster.player_id == actor_hero.player_id

    @staticmethod
    def self_and_caster_is_partner_and_is_attacked_target(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: FieldBuff
    ) -> int:
        caster = context.get_hero_by_id(buff.caster_id)
        if (
            _is_attacker(target_hero, context)
            and caster.player_id == actor_hero.player_id
        ):
            return 1
        return 0


    # Stone Check


    @staticmethod
    def self_is_batter_attacker_and_luck_is_higher(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context) and action.is_in_battle and actor_hero.initial_attributes.luck > target_hero.initial_attributes.luck:
            return 1
        return 0


    # Passive


    @staticmethod
    def sanquehuisheng_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, passive
    ) -> int:
        if PositionRequirementChecks.battle_member_in_range(2, actor_hero, target_hero, context, passive) and(
            passive in actor_hero.enabled_passives or passive in target_hero.enabled_passives
        ):
            return 1
        return 0

    @staticmethod
    def bianmou_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, passive
    ) -> int:
        skill = context.get_last_action().skill
        if skill and skill.temp.element in [Elements.FIRE.value, Elements.WATER.value]:
            return 1
        return 0


    # Stone Check


    @staticmethod
    def skill_is_used_by_certain_hero(
        hero_temp_id: str, actor_hero: Hero, target_hero: Hero, context: Context, skill
    ) -> int:
        action = context.get_last_action()
        if _is_attacker(actor_hero, context):
            if action.skill.temp.id == hero_temp_id:
                return 1
        return 0

    LifeChecks = LifeRequirementChecks
    PositionChecks = PositionRequirementChecks
    BuffChecks = BuffRequirementChecks
