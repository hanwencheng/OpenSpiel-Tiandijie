from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuff import FieldBuff
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from open_spiel.python.games.Tiandijie.primitives.talent.Talent import Talent
from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Professions
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_target_in_diamond_range


class TalentRequirementChecks:
    @staticmethod
    def talent_is_ready(
        actor_hero: Hero, target_hero: Hero, context: Context, talent: Talent
    ) -> int:
        if talent.cooldown == 0:
            return 1
        else:
            return 0

    @staticmethod
    def huangyuanlangshen_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        buff = actor_hero.get_buff_by_id("lieshang")
        if not buff:
            return 0
        if buff.trigger >= 1:
            return 0
        if Rs.BuffChecks.target_has_certain_buff(
            "lieshang", actor_hero, target_hero, context
        ):
            buff.trigger += 1
            return 1

    @staticmethod
    def yaochixianshou_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        enemies = context.get_enemies_in_diamond_range(actor_hero, 3)
        if not enemies:
            return 0
        for enemy in enemies:
            if Rs.BuffChecks.target_has_certain_buff(
                "xianzui", actor_hero, enemy, context
            ):
                return 1
        return 0

    @staticmethod
    def wenchangxingyun_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, talent: Talent
    ) -> int:
        if not TalentRequirementChecks.talent_is_ready(
            actor_hero, target_hero, context, talent
        ):
            return 0
        if Rs.BuffChecks.self_buff_stack_reach(
            2, "changming", actor_hero, target_hero, context
        ):
            talent.cooldown = 3
            return 1
        return 0

    @staticmethod
    def take_effect_of_yaocaolinghua(
        actor_hero: Hero, target_hero: Hero, context: Context, talent: Talent
    ):
        partners = context.get_partners_in_diamond_range(actor_hero, 3)
        for partner in partners:
            if Rs.LifeChecks.life_not_full(partner, target_hero, context):
                return 1
        return 0

    @staticmethod
    def linqiqiongyu_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        enemies = context.get_enemies_in_diamond_range(actor_hero, 3)
        if not enemies:
            return 0
        for enemy in enemies:
            if enemy.temp.profession in [
                Professions.SWORDSMAN,
                Professions.SORCERER,
                Professions.ARCHER,
                Professions.RIDER,
                Professions.WARRIOR,
            ]:
                return 1
        return 0

    @staticmethod
    def ruhaishuangsheng_requires_check(
        state: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        talent: Talent,
    ):
        if state == 1:
            if Rs.self_is_certain_element(
                Elements.THUNDER,
                actor_hero,
                target_hero,
                context,
            ):
                talent.cooldown = 3
                return 1
        elif state == 2:
            if Rs.self_is_certain_element(
                Elements.LIGHT,
                actor_hero,
                target_hero,
                context,
            ):
                talent.cooldown = 3
                return 1
        return 0

    @staticmethod
    def youmingcixin_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ):
        partners = context.get_partners_in_diamond_range(actor_hero, 3)
        if not partners:
            return 0
        for partner in partners:
            if partner.actionable:
                return 1
        return 0

    @staticmethod
    def heyururun_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ):
        if Rs.action_is_active_skill(actor_hero, target_hero, context) and Rs.BuffChecks.self_buff_stack_reach(
            2, "shengming", actor_hero, target_hero, context
        ):
            return 1

    @staticmethod
    def youfenghuashen_requires_check(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ):
        partners = context.get_partners_in_diamond_range(actor_hero, 4)
        element_values = {partner.temp.element for partner in partners}
        if Elements.WATER in element_values and Elements.FIRE in element_values:
            return 1
        return 0




    # Talent Field buffs


    @staticmethod
    def huzongqianli_requires_check(
        state: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        buff: FieldBuff,
    ) -> int:
        if state == 1:
            caster = context.get_hero_by_id(buff.caster_id)
            if (
                Rs.self_is_certain_profession(
                    [Professions.SORCERER, Professions.ARCHER, Professions.PRIEST],
                    actor_hero,
                    target_hero,
                    context,
                )
            ) and calculate_if_target_in_diamond_range(actor_hero, caster, 1):
                return 1
            return 0
        elif state == 2:
            if buff.trigger >= 2:
                return 0
