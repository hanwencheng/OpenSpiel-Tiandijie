from __future__ import annotations
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.CheckHelpers import check_buff_on_target

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTypes


class BuffRequirementChecks:
    @staticmethod
    def target_buff_stack_reach(
        reach_number: int,
        buff_id: str,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        for buff in target_hero.buffs:
            if buff.temp.id == buff_id:
                if buff.stack >= reach_number:
                    return 1
        return 0

    @staticmethod
    def self_buff_stack_reach(
        reach_number: int,
        buff_id: str,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        for buff in actor_hero.buffs:
            if buff.temp.id == buff_id:
                if buff.stack >= reach_number:
                    return 1
        return 0

    @staticmethod
    def target_has_no_benefit_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Benefit:
                return 0
        return 1

    @staticmethod
    def target_has_no_harm_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                return 0
        return 1

    @staticmethod
    def self_has_no_benefit_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                return 0
        return 1

    @staticmethod
    def self_has_no_harm_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Benefit:
                return 0
        return 1

    @staticmethod
    def self_has_benefit_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Benefit, True)

    @staticmethod
    def target_has_benefit_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Benefit, False)

    @staticmethod
    def self_has_harm_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Harm, True)

    @staticmethod
    def target_has_harm_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        return check_buff_on_target(actor_hero, target_hero, BuffTypes.Harm, False)

    @staticmethod
    def target_harm_buff_count(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        harm_buff_count = 0
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                harm_buff_count += 1
        return min(3, harm_buff_count)

    @staticmethod
    def target_benefit_buff_count(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        benefit_buff_count = 0
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Benefit:
                benefit_buff_count += 1
        return min(3, benefit_buff_count)

    @staticmethod
    def self_benefit_buff_count(
        max_count: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        benefit_buff_count = 0
        for buff in actor_hero.buffs:
            if buff.temp.type == BuffTypes.Benefit:
                benefit_buff_count += 1
        return min(max_count, benefit_buff_count)

    @staticmethod
    def self_harm_buff_count_smaller_than(
        count: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        harm_buff_count = 0
        for buff in actor_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                harm_buff_count += 1
        return 1 if harm_buff_count < count else 0

    @staticmethod
    def target_harm_buff_count_bigger_than(
        count: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        harm_buff_count = 0
        for buff in target_hero.buffs:
            if buff.temp.type == BuffTypes.Harm:
                harm_buff_count += 1
        return 1 if harm_buff_count > count else 0

    @staticmethod
    def huahuo_stack_count(
        actor_hero: Hero, target_hero: Hero, context: Context, buff: Buff
    ) -> float:
        return (buff.stack + 3) / 3

    @staticmethod
    def target_has_certain_buff(
        buff_id: str, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in target_hero.buffs:
            if buff.temp.id == buff_id:
                return 1
        return 0

    @staticmethod
    def self_has_certain_buff_in_list(
        buff_list: [str], actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        self_buffs = [buff.temp.id for buff in actor_hero.buffs]
        count = 0
        for buff in buff_list:
            if buff in self_buffs:
                count += 1
        return count

    @staticmethod
    def self_has_no_certain_buff(
        buff_id: str, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in actor_hero.buffs:
            if buff.temp.id == buff_id:
                return 0
        return 1

    @staticmethod
    def self_has_move_buff(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        for buff in actor_hero.buffs:
            for k, v in buff.temp.modifier_effects.modifiers.items():
                if k == "move_range" and v > 0:
                    return 1
        return 0

    @staticmethod
    def buff_stack_bigger_than(
        stack_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
        buff: Buff,
    ) -> int:
        return 0 if buff.stack >= stack_value else 1

    @staticmethod
    def get_certain_buff(buff_id: str, actor_hero: Hero, target_hero: Hero, context: Context, primitive) -> int:
        if primitive.temp.id == buff_id:
            return 1
        return 0

    @staticmethod
    def get_certain_buff_and_stack_reach(reach_number: int, buff_id: str, actor_hero: Hero, target_hero: Hero, context: Context, primitive) -> int:
        if primitive.temp.id == buff_id:
            if primitive.stack >= reach_number:
                return 1
        return 0

    @staticmethod
    def wanghuan_stack_count(
        actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> float:
        return primitive.stack