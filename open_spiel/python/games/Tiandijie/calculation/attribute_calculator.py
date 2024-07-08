from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives import Context
    from open_spiel.python.games.Tiandijie.primitives.hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill
    from open_spiel.python.games.Tiandijie.primitives.Action import Action
from open_spiel.python.games.Tiandijie.primitives.hero.Element import (
    get_elemental_relationship,
    get_elemental_multiplier,
)

from open_spiel.python.games.Tiandijie.helpers import is_normal_attack_magic
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.ActionTypes import ActionTypes
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_targe_in_diamond_range
from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Professions
from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import (
    accumulate_attribute,
    get_level1_modified_result,
    get_level2_modifier,
    get_heal_level2_modifier,
    get_skill_modifier,
    accumulate_stone_attribute,
    get_damage_and_reduction_level2_modifier,
    accumulate_suit_stone_attribute,
    get_sstone_perstone_talent_equip_formation_passive_buff_weapon_modifier,
    get_a_modifier
)
from math import ceil

XINGYAO_DAMAGE_REDUCTION = 4
XINGYAO_DAMAGE_INCREASE = 4
LIEXING_DAMAGE_INCREASE = 10
LIEXING_HEAL_INCREASE = 10
JIANREN = 40


def check_is_magic_action(skill: Skill or None, attacker_instance: Hero) -> bool:
    if skill is None:
        return is_normal_attack_magic(attacker_instance.temp.profession)
    else:
        return skill.temp.is_magic()


def normalize_value(v: float) -> float:
    return max(0, min(1, v))


# TODO Shenbin calculation is not included


def get_element_attacker_multiplier(
    attacker_instance: Hero, target_instance: Hero, action: Action, context: Context
) -> float:
    skill = action.skill
    attr_name = ma.element_attacker_multiplier
    if skill is not None:
        is_ignore_element = get_skill_modifier(
            "ignore_element_advantage", attacker_instance, target_instance, skill, context
        )
        if is_ignore_element:
            return 1

    damage_element = attacker_instance.temp.element
    if skill and skill.temp.element != Elements.NONE:
        damage_element = skill.temp.element

    basic_elemental_multiplier = get_elemental_multiplier(
        get_elemental_relationship(damage_element, target_instance.temp.element)
    )
    accumulated_skill_damage_modifier = 0
    if skill is not None:
        accumulated_skill_damage_modifier = get_skill_modifier(
            attr_name, attacker_instance, target_instance, skill, context
        )
    return (
            basic_elemental_multiplier
            + accumulated_skill_damage_modifier
            + get_level2_modifier(attacker_instance, target_instance, attr_name, context)
    )


def get_penetration_multiplier(
    hero_instance: Hero,
    counter_hero: Hero,
    skill: Skill or None,
    context: Context,
    is_basic: bool = False,
) -> float:
    is_magic = check_is_magic_action(skill, hero_instance)
    attr_name = (
        ma.magic_penetration_percentage
        if is_magic
        else ma.physical_penetration_percentage
    )
    accumulated_skill_damage_modifier = (
        0
        if skill is None
        else get_skill_modifier(attr_name, hero_instance, counter_hero, skill, context)
    )
    leve2_modifier = get_sstone_perstone_talent_equip_formation_passive_buff_weapon_modifier(
        hero_instance, counter_hero, attr_name, context
    )
    return normalize_value((leve2_modifier + accumulated_skill_damage_modifier)/100)


def get_defense_with_penetration(
    attacker_instance: Hero,
    defender_instance: Hero,
    context: Context,
    is_basic: bool = False,
) -> float:     # 防御穿透
    skill = context.get_last_action().skill
    is_magic = check_is_magic_action(skill, attacker_instance)
    penetration = get_penetration_multiplier(
        attacker_instance, True, skill, context, is_basic
    )
    # calculate buffs
    basic_defense = get_defense(defender_instance, attacker_instance, is_magic, context, is_basic)
    return basic_defense * (1 - normalize_value(penetration))


# TODO, calculate 先攻和反击上限，范围加成
def get_counter_attack_range(hero_instance: Hero, context: Context):
    counter_attack_range = hero_instance.temp.range
    return counter_attack_range


def check_in_battle(context: Context) -> bool:
    current_action = context.get_last_action()
    target = current_action.targets[0]
    if len(target) != 1:
        return False
    actor = current_action.actor
    if calculate_if_targe_in_diamond_range(
        actor, target, get_counter_attack_range(target, context)
    ):
        return True
    else:
        return False


def get_max_life(
    hero_instance: Hero, target_instance: Hero, context: Context, is_basic: bool = False
) -> float:
    life_attribute = hero_instance.initial_attributes.life
    basic_life = get_level1_modified_result(hero_instance, ma.life, life_attribute) + hero_instance.temp.strength_attributes.life + hero_instance.temp.xingzhijing.life
    if hero_instance.id == "mohuahuangfushen0":     # 这里是模拟小号的面板写死的
        basic_life = 6365 + 1059
        return basic_life * (
            1
            + (
                get_a_modifier(
                    ma.life_percentage, hero_instance, target_instance, context, is_basic
                )
                + JIANREN
            )/100
    )
    elif hero_instance.id == "zhujin0":
        basic_life = 2858 + 1690
    elif hero_instance.id == "huoyong0":
        basic_life = 3753 + 1808
    elif hero_instance.id == "fuyayu0":
        basic_life = 5541 + 944
    return basic_life * (
        1
        + (
            get_a_modifier(
                ma.life_percentage, hero_instance, target_instance, context, is_basic
            )
            + JIANREN
        )/100
    )


def get_defense(
    hero_instance: Hero,
    counter_instance: Hero,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:
    # calculate buffs
    attr_name = ma.magic_defense if is_magic else ma.defense
    defense_attribute = (
        hero_instance.initial_attributes.magic_defense if is_magic else hero_instance.initial_attributes.defense
    )

    basic_defense = (
            get_level1_modified_result(hero_instance, attr_name, defense_attribute)
            + (hero_instance.temp.strength_attributes.magic_defense if is_magic else hero_instance.temp.strength_attributes.defense)
            + (hero_instance.temp.xingzhijing.magic_defense if is_magic else hero_instance.temp.xingzhijing.defense))

    if hero_instance.id == "mohuahuangfushen0":
        basic_defense = 1245 + 648 if is_magic else 1197 + 530
    elif hero_instance.id == "zhujin0":
        basic_defense = 501 + 353 if is_magic else 566 + 242
    elif hero_instance.id == "huoyong0":
        basic_defense = 766 + 323 if is_magic else 625 + 299
    elif hero_instance.id == "fuyayu0":
        basic_defense = 1423 + 324 if is_magic else 1128 + 208

    return basic_defense * (1 + get_level2_modifier(
        hero_instance, counter_instance, attr_name+"_percentage", context, is_basic
    )/100)


def get_attack(
    actor_instance: Hero,
    target_instance: Hero,
    context: Context,
    is_magic_input=None,
    is_basic: bool = False,
) -> float:
    action = context.get_last_action()
    if is_magic_input is not None:
        is_magic = is_magic_input
    else:
        is_magic = action.is_magic
    # calculate buffs
    attr_name = "magic_attack" if is_magic else "attack"
    attack_attribute = (
        actor_instance.initial_attributes.attack
        if not is_magic
        else actor_instance.initial_attributes.magic_attack
    )
    basic_attack = (
            get_level1_modified_result(
                actor_instance, attr_name, attack_attribute
            )
            + (actor_instance.temp.strength_attributes.magic_attack if is_magic else actor_instance.temp.strength_attributes.attack)
            + (actor_instance.temp.xingzhijing.magic_attack if is_magic else actor_instance.temp.xingzhijing.attack))

    if actor_instance.id == "mohuahuangfushen0":
        basic_attack = 454 if is_magic else 3193 + 1895
    elif actor_instance.id == "zhujin0":
        basic_attack = 1848 + 1099 if is_magic else 232
    elif actor_instance.id == "huoyong0":
        basic_attack = 2134 + 1194 if is_magic else 256
    elif actor_instance.id == "fuyayu0":
        basic_attack = 2150 + 437 if is_magic else 325

    return basic_attack * (1 + get_level2_modifier(
        actor_instance, target_instance, attr_name+"_percentage", context, is_basic
        )/100)


def get_damage_modifier(
    attacker_instance: Hero,
    counter_instance: Hero,
    skill: Skill or None,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:
    attr_name = (
        ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage
    )
    accumulated_stones_percentage_damage_modifier = accumulate_stone_attribute(
        attacker_instance.stones, attr_name
    )

    level2_damage_modifier = 1 + (
        get_damage_and_reduction_level2_modifier(
            attacker_instance, counter_instance, attr_name, context, skill
        )
        + get_action_type_damage_modifier(attacker_instance, counter_instance, context, skill)
    ) / 100

    # B-type damage increase (Additive)
    level1_damage_modifier = (
        1
        + (
            accumulated_stones_percentage_damage_modifier + XINGYAO_DAMAGE_INCREASE
        ) / 100
    )
    return level1_damage_modifier * level2_damage_modifier


def get_a_damage_modifier(
    attacker_instance: Hero,
    counter_instance: Hero,
    skill: Skill or None,
    is_magic: bool,
    context: Context,
) -> float:
    modifier = (
            get_a_modifier(
                ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage,
                attacker_instance,
                counter_instance,
                context
            )
            + get_action_type_damage_modifier(attacker_instance, counter_instance, context, skill)
            - get_a_modifier(
                ma.magic_damage_reduction_percentage if is_magic else ma.physical_damage_reduction_percentage,
                counter_instance,
                attacker_instance,
                context
            )
            - get_action_type_damage_reduction_modifier(counter_instance, attacker_instance, context)
    )
    from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, accumulate_xinghun_attribute, accumulate_equipments_modifier, get_weapon_modifier, get_buff_modifier, get_formation_modifier, accumulate_jishen_attribute
    print("-------------------------A类增减伤-------------------------------", "attacker:", attacker_instance.id)
    print("A类增伤", get_a_modifier(ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage, attacker_instance, counter_instance, context) + get_action_type_damage_modifier(attacker_instance, counter_instance, context, skill), "\n",
          "其中"
          "talents",  accumulate_talents_modifier(ma.magic_damage_percentage, attacker_instance, counter_instance, context), "\n",
          "skill",  get_skill_modifier(ma.magic_damage_percentage, attacker_instance, counter_instance, skill, context), "\n",
          "xinghun",  accumulate_xinghun_attribute(attacker_instance.temp.xinghun, ma.magic_damage_percentage), "\n",
          "weapon",  get_weapon_modifier(ma.magic_damage_percentage, attacker_instance, counter_instance, context), "\n",
          "equipments",  accumulate_equipments_modifier(ma.magic_damage_percentage, attacker_instance, counter_instance, context), "\n",
          "suit_stone",  accumulate_suit_stone_attribute(attacker_instance, counter_instance, ma.magic_damage_percentage, context), "\n",
          "buff",  get_buff_modifier(ma.magic_damage_percentage, attacker_instance, counter_instance, context), "\n",
          "formation",  get_formation_modifier(ma.magic_damage_percentage, attacker_instance, counter_instance, context), "\n",
          "jishen",  accumulate_jishen_attribute(ma.magic_damage_percentage, attacker_instance, counter_instance, context), "\n",
          "action", get_action_type_damage_modifier(attacker_instance, counter_instance, context, skill), "\n",
          "----------------------------------------------------", "\n",
          "A类减伤", get_a_modifier(ma.magic_damage_reduction_percentage if is_magic else ma.physical_damage_reduction_percentage, counter_instance, attacker_instance, context) - get_action_type_damage_reduction_modifier(counter_instance, attacker_instance, context), "\n",
          "其中"
          "talents", accumulate_talents_modifier(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, context), "\n",
          "skill", get_skill_modifier(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, skill, context), "\n",
          "xinghun", accumulate_xinghun_attribute(attacker_instance.temp.xinghun, ma.magic_damage_reduction_percentage), "\n",
          "weapon", get_weapon_modifier(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, context), "\n",
          "equipments", accumulate_equipments_modifier(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, context),
          "\n",
          "suit_stone", accumulate_suit_stone_attribute(counter_instance, attacker_instance, ma.magic_damage_reduction_percentage, context),
          "\n",
          "buff", get_buff_modifier(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, context), "\n",
          "formation", get_formation_modifier(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, context), "\n",
          "jishen", accumulate_jishen_attribute(ma.magic_damage_reduction_percentage, counter_instance, attacker_instance, context), "\n",
          "action", get_action_type_damage_reduction_modifier(counter_instance, attacker_instance, context), "\n",
    )

    return 1 + modifier / 100


def get_b_damage_modifier(  # 魂石百分比词条加这里
    attacker_instance: Hero,
    counter_instance: Hero,
    skill: Skill or None,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:

    accumulated_liexing_modifier = 0
    if attacker_instance.temp.profession != Professions.PRIEST:     # 除了奶，所有角色列星都是加伤
        accumulated_liexing_modifier = 10

    modifier = (
            accumulate_stone_attribute(attacker_instance.stones, ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage)
            + XINGYAO_DAMAGE_INCREASE
            + accumulated_liexing_modifier
            - accumulate_stone_attribute(counter_instance.stones, ma.magic_damage_reduction_percentage if is_magic else ma.physical_damage_reduction_percentage)
            - XINGYAO_DAMAGE_REDUCTION
    )
    print("-------------------------B类增减伤-------------------------------", modifier, "attacker:", attacker_instance.id)
    print("stone增伤词条", accumulate_stone_attribute(attacker_instance.stones, ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage), "\n",
          "XINGYAO_DAMAGE_INCREASE", XINGYAO_DAMAGE_INCREASE, "\n",
          "stone减伤词条", accumulate_stone_attribute(counter_instance.stones, ma.magic_damage_reduction_percentage if is_magic else ma.physical_damage_reduction_percentage), "\n",
          "XINGYAO_DAMAGE_REDUCTION", XINGYAO_DAMAGE_REDUCTION, "\n",
          )
    return 1 + modifier / 100


def get_action_type_damage_modifier(
    actor: Hero, target: Hero, context: Context, skill
) -> float:
    current_action = context.get_last_action()
    action_type = current_action.type
    action_type_modifier = 0
    if action_type == ActionTypes.SKILL_ATTACK:
        action_type_modifier += get_a_modifier(
            ma.skill_damage_percentage, actor, target, context, skill
        )
        skill = context.get_last_action().skill
        from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillType, SkillTargetTypes
        from open_spiel.python.games.Tiandijie.calculation.Range import RangeType
        if skill.temp.target_type == SkillTargetTypes.ENEMY and skill.temp.range_instance.range_type == RangeType.POINT and (skill.temp.skill_type in {SkillType.Physical, SkillType.Magical}):
            action_type_modifier += get_a_modifier(
                ma.single_target_skill_damage_percentage, actor, target, context, skill
            )
        else:
            action_type_modifier += get_a_modifier(
                ma.range_skill_damage_percentage, actor, target, context, skill
            )
    elif action_type == ActionTypes.NORMAL_ATTACK:
        action_type_modifier += get_a_modifier(
            ma.normal_attack_damage_percentage, actor, target, context, skill
        )

    if current_action.is_in_battle:
        action_type_modifier += get_a_modifier(
            ma.battle_damage_percentage, actor, target, context, skill
        )

    return action_type_modifier


def get_action_type_damage_reduction_modifier(
    defender: Hero, attacker: Hero, context: Context
) -> float:
    current_action = context.get_last_action()
    action_type = current_action.type
    action_type_modifier = 0
    if action_type == ActionTypes.SKILL_ATTACK:
        skill_target_type = context.get_last_action().skill.temp.range_instance.range_value
        if skill_target_type == 0:
            action_type_modifier += get_a_modifier(
                ma.single_target_skill_damage_reduction_percentage,
                defender,
                attacker,
                context,
            )
        elif skill_target_type > 0:
            action_type_modifier += get_a_modifier(
                ma.range_skill_damage_reduction_percentage, defender, attacker, context
            )
    elif action_type == ActionTypes.NORMAL_ATTACK:
        action_type_modifier += get_a_modifier(
            ma.normal_attack_damage_reduction_percentage, defender, attacker, context
        )

    if current_action.is_in_battle:
        action_type_modifier += get_a_modifier(
            ma.battle_damage_reduction_percentage, defender, attacker, context
        )

    return action_type_modifier


def get_damage_reduction_modifier(
    defense_instance: Hero,
    counter_instance: Hero,
    is_magic: bool,
    context: Context,
    is_basic: bool = False,
) -> float:
    attr_name = (
        ma.magic_damage_reduction_percentage
        if is_magic
        else ma.physical_damage_reduction_percentage
    )

    # A-type damage increase (Additive)
    a_type_damage_reduction = (
        1
        - (
            get_damage_and_reduction_level2_modifier(
                defense_instance, counter_instance, attr_name, context
            )
            + get_action_type_damage_reduction_modifier(
                defense_instance, counter_instance, context
            )
        )
        / 100
    )

    accumulated_stones_damage_reduction_percentage_modifier = accumulate_stone_attribute(
        defense_instance.stones, attr_name
    )
    # B-type damage increase (Additive)
    b_type_damage_reduction = (
        1
        - (
            XINGYAO_DAMAGE_REDUCTION
            + accumulated_stones_damage_reduction_percentage_modifier
        )
        / 100
    )
    return a_type_damage_reduction * b_type_damage_reduction


def get_critical_hit_probability(
    actor_hero: Hero, counter_instance: Hero, context: Context, is_basic: bool = False, skill=None
) -> float:
    critical_stones_percentage_modifier = accumulate_stone_attribute(
        actor_hero.stones, ma.critical_percentage
    )

    total_luck = get_luck(actor_hero, counter_instance, context, is_basic)
    level2_critical_modifier = get_a_modifier(
        ma.critical_percentage, actor_hero, counter_instance, context, skill
    )
    total_critical = (
        total_luck / 10 + level2_critical_modifier + critical_stones_percentage_modifier
    )
    return total_critical / 100


def get_luck(actor_hero: Hero, counter_instance: Hero, context: Context, is_basic: bool = False) -> float:
    luck_attribute = actor_hero.initial_attributes.luck + actor_hero.temp.xingzhijing.luck
    total_luck = luck_attribute * (
        1
        + get_a_modifier(ma.luck_percentage, actor_hero, counter_instance, context, False)/100
    )

    if actor_hero.id == "mohuahuangfushen0":
        total_luck = 350 + 10
    elif actor_hero.id == "zhujin0":
        total_luck = 69
    elif actor_hero.id == "huoyong0":
        total_luck = 130
    elif actor_hero.id == "fuyayu0":
        total_luck = 132

    return total_luck


def get_critical_hit_suffer(
    actor_hero: Hero, counter_instance: Hero, context: Context, is_basic: bool = False
) -> float:
    # Calculate buffs
    level_2_hit_suffer = get_a_modifier(
        ma.suffer_critical_percentage,
        actor_hero,
        counter_instance,
        context,
    )
    suffer_critical_stones_percentage_modifier = accumulate_stone_attribute(
        actor_hero.stones, ma.suffer_critical_percentage
    )

    return (level_2_hit_suffer + suffer_critical_stones_percentage_modifier) / 100


def get_critical_damage_modifier(
    actor_hero: Hero, counter_instance: Hero, context: Context
) -> float:
    critical_stones_damage_percentage_modifier = accumulate_stone_attribute(actor_hero.stones, ma.critical_damage_percentage)
    return (
        1
        + (
            get_a_modifier(
                ma.critical_damage_percentage, actor_hero, counter_instance, context
            )
            + critical_stones_damage_percentage_modifier
            - get_a_modifier(
                ma.critical_damage_reduction_percentage,
                actor_hero,
                counter_instance,
                context,
            )   # 攻击者的暴击伤害降低
            - get_a_modifier(
                ma.suffer_critical_damage_reduction_percentage,
                counter_instance,
                actor_hero,
                context,
            )  # 被攻击者的暴击抗性
        )
        / 100
    )


def get_fixed_damage_reduction_modifier(
    hero_instance: Hero, counter_instance: Hero, context: Context
) -> float:
    return (
        1
        + (
            get_a_modifier(
                ma.fixed_damage_percentage,
                hero_instance,
                counter_instance,
                context,
            )
            - get_a_modifier(
                ma.fixed_damage_reduction_percentage,
                hero_instance,
                counter_instance,
                context,
            )
        )
        / 100
    )


def get_fixed_heal_modifier(
    hero_instance: Hero, target_instance: Hero, context: Context
) -> float:
    return (
        1
        + (
            get_heal_level2_modifier(
                hero_instance,
                target_instance,
                ma.heal_percentage,
                context,
            )
            + get_heal_level2_modifier(
                target_instance,
                hero_instance,
                ma.be_healed_percentage,
                context,
            )
        )
        / 100
    )


def get_counterattack_damage_modifier(
    attacker_instance: Hero,
    counter_instance: Hero,
    is_magic: bool,
    context: Context,
) -> float:
    attr_name = (
        ma.magic_damage_percentage if is_magic else ma.physical_damage_percentage
    )
    accumulated_passive_damage_modifier = accumulate_attribute(
        attacker_instance.temp.passives, attr_name
    )
    accumulated_stones_percentage_damage_modifier = accumulate_stone_attribute(
        attacker_instance.stones, attr_name
    )

    level2_damage_modifier = 1 + (
        get_damage_and_reduction_level2_modifier(
            attacker_instance, counter_instance, attr_name, context
        )
        + accumulated_passive_damage_modifier
        + get_a_modifier(
            ma.counterattack_damage_percentage, attacker_instance, counter_instance, context
        )
    ) / 100

    # B-type damage increase (Additive)
    level1_damage_modifier = (
        1
        + (
            XINGYAO_DAMAGE_INCREASE + accumulated_stones_percentage_damage_modifier + XINGYAO_DAMAGE_INCREASE
        ) / 100
    )
    return level1_damage_modifier * level2_damage_modifier


def get_counterattack_damage_reduction_modifier(
    defense_instance: Hero,
    counter_instance: Hero,
    is_magic: bool,
    context: Context,
) -> float:
    attr_name = (
        ma.magic_damage_reduction_percentage
        if is_magic
        else ma.physical_damage_reduction_percentage
    )
    accumulated_passives_damage_reduction_modifier = accumulate_attribute(
        defense_instance.temp.passives, attr_name
    )

    # A-type damage increase (Additive)
    a_type_damage_reduction = (
        1
        - (
            get_damage_and_reduction_level2_modifier(
                defense_instance, counter_instance, attr_name, context
            )
            + accumulated_passives_damage_reduction_modifier
        )
        / 100
    )

    accumulated_stones_damage_reduction_percentage_modifier = accumulate_stone_attribute(
        defense_instance.stones, attr_name
    )
    # B-type damage increase (Additive)
    b_type_damage_reduction = (
        1
        - (
            XINGYAO_DAMAGE_REDUCTION
            + accumulated_stones_damage_reduction_percentage_modifier
        )
        / 100
    )
    return a_type_damage_reduction * b_type_damage_reduction
