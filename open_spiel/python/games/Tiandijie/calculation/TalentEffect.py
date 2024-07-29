from __future__ import annotations

from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.calculation.damage_calculator import (
    calculate_fix_damage,
)
from open_spiel.python.games.Tiandijie.calculation.OtherlCalculation import (
    calculate_fix_heal,
)
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.helpers import random_select

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.hero import Hero
    from open_spiel.python.games.Tiandijie.primitives import Context
    from open_spiel.python.games.Tiandijie.primitives.talent.Talent import Talent
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuffTemp import FieldBuffTemp
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuff import FieldBuff
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from open_spiel.python.games.Tiandijie.primitives.skill.skills import Skills
from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill
from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType
from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTypes

from collections import Counter
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.BuffRequirementChecks import BuffRequirementChecks
from open_spiel.python.games.Tiandijie.calculation.attribute_calculator import get_defense, get_attack
from typing import List


# Talents


# Field Buffs
def _init_talent_field_buffs(
    caster: Hero,
    target: Hero,
    field_buff_temp: List[FieldBuffTemp],
    duration: int,
    context: Context,
):
    new_field_buffs = [FieldBuff(b, duration, caster.id) for b in field_buff_temp]
    for new_field_buff in new_field_buffs:
        existing_field_buff = next(
            (
                field_buff
                for field_buff in target.talents_field_buffs
                if field_buff.temp.id == new_field_buff.temp.id
            ),
            None,
        )
        if existing_field_buff is not None:
            if new_field_buff.level > existing_field_buff.level:
                target.talents_field_buffs.remove(existing_field_buff)
                target.talents_field_buffs.append(new_field_buff)
            else:
                existing_field_buff.duration = duration
        else:
            target.talents_field_buffs.append(new_field_buff)


class TalentEffects:
    @staticmethod
    def add_fixed_damage_by_talent_owner_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        talent_owner = talent.caster_id
        damage = get_attack(talent_owner, actor_instance, context, True) * multiplier
        calculate_fix_damage(damage, talent_owner, actor_instance, context)

    @staticmethod
    def add_fixed_damage_by_talent_owner_physical_and_magic_attack(
        multiplier: float,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        talent_owner = talent.caster_id
        damage = get_attack(talent_owner, actor_instance, context, True) * multiplier
        calculate_fix_damage(damage, talent_owner, actor_instance, context)

    @staticmethod
    def init_talent_field_buff(
        field_buff_value: str,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        field_buff_temp = context.get_field_buff_by_id(field_buff_value)
        _init_talent_field_buffs(
            actor_instance, actor_instance, field_buff_temp, 1, context
        )

    @staticmethod
    def reset_random_damage_skill_cooldown(
        actor: Hero, target: Hero, context: Context, talent: Talent
    ):
        skill_list = [
            skill
            for skill in actor.enabled_skills
            if skill.is_damage_skill and skill.cool_down > 0
        ]
        if not skill_list:
            return
        skill = random_select(skill_list, 1)
        skill.cool_down = 0

    @staticmethod
    def take_effect_of_lv(
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        targets = context.get_enemies_in_cross_range(actor_instance, 7)
        selected_harm_buff_temps = random_select(context.harm_buffs_temps, 1)
        additional_buff_temp = context.get_buff_by_id("youjin")
        if additional_buff_temp is not None:
            selected_harm_buff_temps.append(context.get_buff_by_id("youjin"))
        selected_heroes = random_select(targets, 2)
        for enemy_hero in selected_heroes:
            Effects.add_buffs(
                selected_harm_buff_temps, 2, actor_instance, enemy_hero, context, talent
            )

    @staticmethod
    def take_effect_zhifatianjiang(
        actor_instance: Hero,
        target_instance: Hero,
        partner: Hero,
        context: Context,
        talent: Talent or FieldBuff,
    ):
        if talent.trigger > 2:
            return
        talent.trigger += 1
        TalentEffects.add_fixed_damage_by_talent_owner_magic_attack(
            0.3, talent.caster, actor_instance, context, talent
        )
        Effects.add_self_buffs(["zhanyin"], 1, actor_instance, target_instance, context, talent)

    @staticmethod
    def take_effect_of_wenchangxingyun(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        action = context.get_last_action()
        Effects.reduce_actor_certain_buff_stack(
            "changming", 2, actor_instance, target_instance, context, talent
        )
        talent.cooldown = 3

    @staticmethod
    def take_effect_of_youhuangminhua(
        stage: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        if stage == 1:
            Effects.add_self_buffs(
                ["youshuang"], 3, actor_instance, actor_instance, context, talent
            )
            talent.cooldown = 4
        else:
            if talent.trigger >= 1:
                return
            talent.trigger += 1
            actor_instance.current_life = (
                actor_instance.get_max_life(context) * 0.5
            )
            if actor_instance.buff["youshuang"]:
                enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
                for enemy in enemies:
                    calculate_fix_damage(
                        (
                            get_attack(actor_instance, target_instance, context, False)
                            + get_defense(
                                actor_instance, target_instance, False, context
                            )
                        )
                        * 0.5,
                        actor_instance,
                        enemy,
                        context,
                    )
                    Effects.add_buffs(
                        ["wucuichihuan"], 2, actor_instance, enemy, context, talent
                    )

    @staticmethod
    def take_effect_of_yaocaolinghua(
        state: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            talent.cooldown = 2
            action = context.get_last_action()
        else:
            partners = context.get_all_partners(actor_hero)
            for partner in partners:
                for buff in partner.buffs:
                    if buff.temp.id == "shengxi":
                        Effects.remove_actor_harm_buffs(
                            1, partner, target_hero, context, talent
                        )
                        calculate_fix_heal(
                            get_attack(actor_hero, target_hero, context, True) * 0.3,
                            actor_hero,
                            partner,
                            context,
                        )
                    if buff.temp.id == "mingsha":
                        skill_list = []
                        for skill in partner.enabled_skills:
                            if skill.cool_down > 0:
                                skill_list.append(skill)
                        if len(skill_list) > 0:
                            random_select(skill_list, 1).cool_down -= 1

    @staticmethod
    def take_effect_of_qilinquanyu(
        state: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            Effects.add_extra_skill(["buqi"], actor_instance, target_instance, context, talent)
        elif state == 2:
            position = context.battlemap.get_terrain_position_by_type(TerrainType.JINWUQI)
            if position is not None:
                terrain = context.battlemap.get_terrain(position)
                caster_id = terrain.caster_id
                if caster_id == actor_instance.id:
                    Effects.remove_jinwuqi(context)
        else:
            position = context.battlemap.get_terrain_position_by_type(TerrainType.JINWUQI)
            if position is not None:
                terrain = context.battlemap.get_terrain(position)
                caster_id = terrain.caster_id
                if caster_id == actor_instance.id:
                    context.battlemap.init_terrain(position)
                    Effects.clear_terrain_by_buff_name("jinwuqi", context)

    # 行动结束前，可额外使用绝学「光·自在」/「雷·自在」（间隔2回合触发，使用后将切换所有专属绝学并刷新冷却时间且保留当前气力）
    @staticmethod
    def take_effect_of_ruhaishuangsheng(
        state: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        ruhaishuangsheng_skill_dic = {
            "chaodufanyin": "fanyinchaodu",
            "lizanwangsheng": "wangshenglizan",
            "pusaxing": "luochadao",
            "tiangujialan": "miaotanjialan",
        }
        if state == 1:  # 光
            for i in range(len(actor_instance.enabled_skills)):
                if (
                    actor_instance.enabled_skills[i].temp.skill_temp_id
                    in ruhaishuangsheng_skill_dic
                ):
                    new_skill = Skills.get_skill_by_id(
                        ruhaishuangsheng_skill_dic[
                            actor_instance.enabled_skills[i].temp.skill_temp_id
                        ]
                    )
                    actor_instance.enabled_skills[i] = Skill(0, new_skill)
        elif state == 2:
            for i in range(len(actor_instance.enabled_skills)):
                for (
                    thunder_skill_name,
                    light_skill_name,
                ) in ruhaishuangsheng_skill_dic.items():
                    if (
                        actor_instance.enabled_skills[i].temp.skill_temp_id
                        == light_skill_name
                    ):
                        new_skill = Skills.get_skill_by_id(thunder_skill_name)
                        actor_instance.enabled_skills[i] = Skill(0, new_skill)

    # 使用绝学后使气血全满的友方目标「有益状态」等级提升1级。3格内友方「对战后」若气血小于等于50%，恢复该角色气血（恢复量为施术者法攻的0.5倍）（每回合发动2次）。
    @staticmethod
    def take_effect_of_youmingcixin(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        if talent.trigger >= 2:
            return
        talent.trigger += 1
        Effects.add_buffs(["youming"], 2, actor_instance, target_instance, context, talent)

    @staticmethod
    def take_effect_of_shangshandaoxin(
        state: int, actor_instance: Hero, target_instance: Hero, context: Context, talent
    ):
        if state == 1:
            if talent.cooldown > 0:
                return
            talent.cooldown = 2
            Effects.add_extra_skill(["guanqie", "shouye"], actor_instance, target_instance, context, talent)
        else:
            # 并复制身上的3个「有益状态」给目标。
            buff_list = random_select([buff for buff in actor_instance.buffs if buff.temp.type == BuffTypes.Benefit], 3)
            for buff in buff_list:
                Effects.add_buffs([buff.temp.id], buff.duration, actor_instance, target_instance, context, talent)

    @staticmethod
    def take_effect_of_nuxiongzhiwei(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
        selected_harm_buff_temps = random_select(context.harm_buffs, 1)
        for enemy_hero in enemies:
            Effects.add_buffs(
                selected_harm_buff_temps, 1, actor_instance, enemy_hero, context, talent
            )
        Effects.add_self_buffs(["ankai"], 1, actor_instance, actor_instance, context, talent)

    @staticmethod
    def take_effect_of_zhanfengwangxiang(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        action = context.get_last_action()
        enemies = context.get_enemy_list_by_id(actor_instance.player_id)
        move_count = action.get_moves(context.battlemap, enemies)
        move_range = actor_instance.move_range - move_count
        if move_range >= 1:
            Effects.add_certain_buff_with_level(
                "shenxing",
                1,
                min(move_range, 3),
                actor_instance,
                actor_instance,
                context,
                talent,
            )

    @staticmethod
    def take_effects_of_hongyanmeigu(
        state: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            action = context.get_last_action()
            count = len(action.targets)
            if count > 0:
                Effects.add_self_buffs(
                    ["yingwei"], 15, actor_instance, actor_instance, context, talent
                )
                if count > 1:
                    for i in range(count - 1):
                        Effects.increase_actor_certain_buff_stack(
                            "yingwei", actor_instance, actor_instance, context, talent
                        )
        elif state == 2:
            buff = actor_instance.get_buff_by_id("yingwei")
            enemies = context.get_enemies_in_diamond_range(actor_instance, 2)
            mark = []
            for i in range(buff.stack):
                enemy = random_select(enemies, 1)
                mark.append(enemies.index(enemy))
                Effects.add_fixed_damage_by_caster_magic_attack(
                    0.1, actor_instance, enemy, context, buff
                )
                Effects.remove_target_benefit_buffs(1, actor_instance, enemy, context, talent)

            counts = Counter(mark)
            duplicates = [element for element, count in counts.items() if count >= 2]
            for index in duplicates:
                Effects.add_buffs(
                    ["meihuo"], 1, actor_instance, enemies[index], context, talent
                )

    @staticmethod
    def take_effect_of_linghaishutao(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        enemies = context.get_enemies_in_diamond_range(target_instance, 1)
        if enemies:
            for enemy in enemies:
                Effects.add_fixed_damage_by_caster_physical_attack(
                    0.3, actor_instance, enemy, context, talent
                )
        Effects.add_terrain_buff_by_target_position(
            "ice", 2, 1, actor_instance, target_instance.position, context
        )

    @staticmethod
    def take_effect_of_huangshenxiongpo(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        enemies = context.get_enemies_in_cross_range(actor_instance, 5)
        if not enemies:
            return
        elif len(enemies) > 2:
            def compare(target):
                return max(
                    get_attack(target, actor_instance, context, False),
                    get_attack(target, actor_instance, context, True),
                )

            enemies = sorted(enemies, key=compare, reverse=True)[:2]
        for enemy in enemies:
            Effects.add_buffs(["shefu"], 2, actor_instance, enemy, context, talent)

    @staticmethod
    def take_effect_of_pohuishenfu(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        if talent.trigger > 3:
            return
        talent.trigger += 1
        selected_harm_buff_temps = random_select(context.harm_buffs_temps, 1)
        selected_harm_buff_temps.append(context.get_buff_by_id("youjin"))
        Effects.add_buffs(
            selected_harm_buff_temps, 2, actor_instance, target_instance, context, talent
        )

    @staticmethod
    def take_effect_of_tianxuanyaowei(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        Effects.remove_actor_certain_buff(
            "tianxuan", actor_instance, target_instance, context, talent
        )
        Effects.add_fixed_damage_in_range_by_caster_physical_attack(
            0.3, 3, actor_instance, target_instance, context, talent
        )
        Talent.cooldown = 4

    @staticmethod
    def take_effect_of_pudujiaoyu(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
        if not enemies:
            return
        for enemy in enemies:
            for buff in enemy.buffs:
                if buff.temp.type == "benefit":
                    enemies.remove(enemy)
        if not enemies:
            return
        enemy = random_select(enemies, 1)
        Effects.add_buffs(["yunxuan"], 1, actor_instance, enemy, context, talent)
        talent.cooldown = 3

    @staticmethod
    def take_effect_of_anxingnixing(
        state: int,
        actor_instance: Hero,
        target_instance: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            Effects.add_self_buffs(
                ["juexin"], 200, actor_instance, actor_instance, context, talent
            )
            targets = context.get_partner_in_square_range(actor_instance, 2) + context.get_enemies_in_square_range(actor_instance, 2)
            element_values = [target.temp.element for target in targets]
            if Elements.DARK in element_values and Elements.THUNDER in element_values:
                Effects.add_buffs(
                    ["juexin"], 200, actor_instance, actor_instance, context, talent
                )

            if BuffRequirementChecks.self_buff_stack_reach(
                5, "juexin", actor_instance, actor_instance, context, talent
            ):
                Effects.remove_actor_certain_buff(
                    "juexin", actor_instance, actor_instance, context, talent
                )
                Effects.add_self_buffs(
                    ["zhilu"], 3, actor_instance, actor_instance, context, talent
                )
        else:
            enemies = context.get_enemies_in_diamond_range(actor_instance, 2)
            if enemies:
                target_enemy = enemies[0]
                for enemy in enemies:
                    if enemy.get_current_life_percentage(context, None) < target_enemy.get_current_life_percentage(context, None):
                        target_enemy = enemy
                Effects.add_fixed_damage_by_caster_physical_attack(
                    0.9, actor_instance, target_enemy, context, talent
                )

    @staticmethod
    def take_effect_of_youmengminqi(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        enemies = context.get_enemies_in_diamond_range(actor_instance, 3)
        if not enemies:
            return
        elif len(enemies) > 4:
            enemies = random_select(enemies, 4)
        for enemy in enemies:
            Effects.add_target_random_harm_buff(2, actor_instance, enemy, context, talent)

    @staticmethod
    def take_effect_of_hanlinhuachou(
        actor_instance: Hero, target_instance: Hero, context: Context, talent: Talent
    ):
        partners = random_select(context.get_partners_in_diamond_range(actor_instance, 3), 4)
        partners.append(actor_instance)
        for partner in partners:
            Effects.add_buffs(["shenrui"], 2, actor_instance, partner, context, talent)
