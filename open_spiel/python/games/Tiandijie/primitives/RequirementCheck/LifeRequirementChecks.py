from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.Context import Context
    from primitives.hero.Hero import Hero
from primitives.buff.BuffTemp import BuffTypes


class LifeRequirementChecks:
    @staticmethod
    def life_not_full(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if actor_hero.current_life < actor_hero.max_life else 0

    @staticmethod
    def life_is_full(actor_hero: Hero, target_hero: Hero, context: Context) -> int:
        return 1 if actor_hero.current_life == actor_hero.max_life else 0

    @staticmethod
    def target_life_is_below(
        percentage: float, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        return (
            1
            if target_hero.current_life / target_hero.max_life < percentage / 100
            else 0
        )

    @staticmethod
    def target_life_is_higher(
        percentage: float, _actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        return (
            1
            if target_hero.current_life / target_hero.max_life > percentage / 100
            else 0
        )

    @staticmethod
    def self_life_is_higher(
        percentage: float, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        return (
            1 if actor_hero.current_life / actor_hero.max_life > percentage / 100 else 0
        )

    @staticmethod
    def self_life_is_below(
        percentage: float, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        return (
            1 if actor_hero.current_life / actor_hero.max_life < percentage / 100 else 0
        )

    @staticmethod
    def self_life_is_higher_percentage(
        percentage: float, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> float:
        offset_base = actor_hero.max_life * percentage / 100
        offset_range = actor_hero.max_life - offset_base
        if actor_hero.current_life > offset_base:
            current_offset_percentage = (
                actor_hero.current_life - offset_base
            ) / offset_range
            return current_offset_percentage
        return 0

    @staticmethod
    def self_life_is_lower_percentage(
        percentage: float, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> float:
        offset_base = actor_hero.max_life * percentage / 100
        offset_range = actor_hero.max_life - offset_base
        if actor_hero.current_life > offset_base:
            current_offset_percentage = (
                actor_hero.current_life - offset_base
            ) / offset_range
            return 1 - current_offset_percentage
        return 0

    @staticmethod
    def self_life_is_higher_and_no_harm_buff(
        percentage: float, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        if actor_hero.current_life / actor_hero.max_life > percentage / 100:
            for buff in actor_hero.buffs:
                if buff.temp.type == BuffTypes.Harm:
                    return 0
            return 1
        return 0

    @staticmethod
    def self_life_is_higher_than_target(
        _percentage: float, actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        return 1 if actor_hero.current_life < target_hero.current_life else 0

    @staticmethod
    def self_life_is_higher_than_target_in_range(
        actor_hero: Hero, target_hero: Hero, context: Context
    ) -> int:
        enemies = context.get_enemies_in_cross_range(actor_hero, 3)
        partner = context.get_partner_in_square_range(actor_hero, 3)
        target_list = enemies + partner
        if not target_list:
            return 0
        for target in target_list:
            if actor_hero.current_life > target.current_life:
                return 1
        return 0
