from __future__ import annotations
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.helpers import compose_hero_id
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.CheckHelpers import check_buff_in_range, _is_attacker

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.Context import Context
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
    from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
    from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
    from open_spiel.python.games.Tiandijie.primitives.Passive import Passive
from typing import List
from open_spiel.python.games.Tiandijie.calculation.Range import calculate_if_target_in_diamond_range, calculate_if_target_in_square_range
from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Gender
from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTypes


class PositionRequirementChecks:
    @staticmethod
    def in_range_of_enemy(
        enemy_hero_temp_id: str,
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        buff: Buff,
    ) -> int:
        enemy_hero_player_id = context.get_counter_player_id()
        base_hero_id = compose_hero_id(enemy_hero_temp_id, enemy_hero_player_id)
        enemy_base_hero = context.get_hero_by_id(base_hero_id)
        if enemy_base_hero.player_id != actor_hero.player_id:
            actor_position = actor_hero.position
            caster_position = enemy_base_hero.position
            if calculate_if_target_in_diamond_range(
                actor_position, caster_position, range_value
            ):
                return 1
        return 0

    @staticmethod
    def in_range_of_enemy_caster(
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        buff: Buff,
    ) -> int:
        caster_hero_id = buff.caster_id
        caster = context.get_hero_by_id(caster_hero_id)
        if caster.player_id != actor_hero.player_id:
            actor_position = actor_hero.position
            caster_position = caster.position
            if calculate_if_target_in_diamond_range(
                actor_position, caster_position, range_value
            ):
                return 1
        return 0

    @staticmethod
    def not_in_range_of_enemy_caster(
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        buff: Buff,
    ) -> int:
        caster_hero_id = buff.caster_id
        caster = context.get_hero_by_id(caster_hero_id)
        if caster.player_id != actor_hero.player_id:
            actor_position = actor_hero.position
            caster_position = caster.position
            if calculate_if_target_in_diamond_range(
                actor_position, caster_position, range_value
            ):
                return 0
        return 1

    @staticmethod
    def no_partners_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id == actor_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    return 0
        return 1

    @staticmethod
    def no_partners_in_target_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        actor_position = target_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id == target_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    return 0
        return 1

    @staticmethod
    def in_the_same_line(actor_hero: Hero, target_hero: Hero, context: Context, primitive) -> int:
        actor_position = actor_hero.position
        target_position = target_hero.position
        if (
            actor_position[0] == target_position[0]
            or actor_position[1] == target_position[1]
        ):
            return 1
        else:
            return 0

    @staticmethod
    def element_hero_in_range(
        elements: List[Elements],
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        actor_position = actor_hero.position
        count = 0
        for element in elements:
            for hero in context.heroes:
                if hero.id == actor_hero.id:
                    continue
                if hero.player_id == actor_hero.player_id:
                    if hero.temp.element == element:
                        if calculate_if_target_in_diamond_range(
                            actor_position, hero.position, range_value
                        ):
                            count += 1
                            break

        return 1 if count == len(elements) else 0

    @staticmethod
    def element_hero_in_square(     # 存在一个就生效， 对象是所有角色
        elements: List[Elements],
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        targets = context.get_enemies_in_square_range(actor_hero, 2) + context.get_partner_in_square_range(actor_hero, 2)
        for target in targets:
            if target.temp.element in elements:
                return 1
        return 0

    @staticmethod
    def has_element_hero_in_range(
        elements: List[Elements],
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        actor_position = actor_hero.position
        for element in elements:
            for hero in context.heroes:
                if hero.id == actor_hero.id:
                    continue
                if hero.player_id == actor_hero.player_id:
                    if hero.temp.element == element:
                        if calculate_if_target_in_diamond_range(
                            actor_position, hero.position, range_value
                        ):
                            return 1

        return 0

    @staticmethod
    def in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if calculate_if_target_in_diamond_range(
                actor_position, hero.position, range_value
            ):
                return 1
        return 0

    @staticmethod
    def has_partner_in_range(
        range_value, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id == actor_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    return 1
        return 0

    @staticmethod
    def has_male_in_range(
        range_value, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if calculate_if_target_in_diamond_range(
                actor_position, hero.position, range_value
            ):
                if hero.temp.gender == Gender.MALE:
                    return 1
        return 0

    @staticmethod
    def has_female_in_range(
        range_value, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if calculate_if_target_in_diamond_range(
                actor_position, hero.position, range_value
            ):
                if hero.temp.gender == Gender.FEMALE:
                    return 1
        return 0

    @staticmethod
    def in_range_count_with_limit(
        range_value,
        maximum_count: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        actor_position = actor_hero.position
        count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if calculate_if_target_in_diamond_range(
                actor_position, hero.position, range_value
            ):
                count += 1
        return min(count, maximum_count)

    @staticmethod
    def in_range_partner_count_with_limit(
        range_value,
        maximum_count: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive
    ) -> int:
        actor_position = actor_hero.position
        count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id == actor_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    count += 1
        return min(count, maximum_count)

    @staticmethod
    def in_range_enemy_count_with_limit(
        range_value,
        maximum_count: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        actor_position = actor_hero.position
        count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id != actor_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    count += 1
        return min(count, maximum_count)

    @staticmethod
    def enemy_in_range_count_bigger_than(
        range_value: int,
        count_requirement: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        actor_position = actor_hero.position
        enemy_count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id != actor_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    enemy_count += 1
        return 1 if enemy_count >= count_requirement else 0

    @staticmethod
    def partner_in_range_count_bigger_than(
        range_value: int,
        count_requirement: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive
    ) -> int:
        actor_position = actor_hero.position
        partner_count = 0
        for hero in context.heroes:
            if hero.id == actor_hero.id:
                continue
            if hero.player_id == actor_hero.player_id:
                if calculate_if_target_in_diamond_range(
                    actor_position, hero.position, range_value
                ):
                    partner_count += 1
        return 1 if partner_count >= count_requirement else 0

    def attack_enemy_in_range_count_bigger_than_with_base_2(
        self,
        range_value: int,
        count_requirement: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        primitive,
    ) -> int:
        is_attacker = _is_attacker(actor_hero, context)
        if is_attacker:
            return 2 + self.enemy_in_range_count_bigger_than(
                range_value, count_requirement, actor_hero, target_hero, context
            )
        else:
            return 2

    @staticmethod
    def has_harm_buff_partner_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context, primitive
    ) -> int:
        return check_buff_in_range(
            range_value, actor_hero, context, BuffTypes.Harm, True
        )

    @staticmethod
    def has_harm_buff_enemy_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context,  primitive
    ) -> int:
        return check_buff_in_range(
            range_value, actor_hero, context, BuffTypes.Harm, False
        )

    @staticmethod
    def has_benefit_buff_partner_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context,  primitive
    ) -> int:
        return check_buff_in_range(
            range_value, actor_hero, context, BuffTypes.Benefit, True
        )

    @staticmethod
    def has_benefit_buff_enemy_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context,  primitive
    ) -> int:
        return check_buff_in_range(
            range_value, actor_hero, context, BuffTypes.Benefit, False
        )

    @staticmethod
    def life_not_full_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context,  primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if calculate_if_target_in_diamond_range(
                actor_position, hero.position, range_value
            ):
                if hero.current_life < hero.max_life:
                    return 1
        return 0

    @staticmethod
    def is_actionable_in_range(
        range_value: int, actor_hero: Hero, target_hero: Hero, context: Context,  primitive
    ) -> int:
        actor_position = actor_hero.position
        for hero in context.heroes:
            if calculate_if_target_in_diamond_range(
                actor_position, hero.position, range_value
            ):
                if hero.actionable:
                    return 1
        return 0

    @staticmethod
    def self_in_certain_terrianbuff(
        terrain_buff: str, actor_hero: Hero, target_hero: Hero, context: Context,  primitive
    ) -> int:
        position = actor_hero.position
        if context.battlemap.get_terrain(position).buff and context.battlemap.get_terrain(position).buff.temp.id == terrain_buff:
            return 1
        return 0

    @staticmethod
    def battle_member_in_range(
        range_value: int,
        actor_hero: Hero,
        target_hero: Hero,
        context: Context,
        passive
    ) -> int:
        action = context.get_last_action()
        actor_position = action.move_point
        target_position = action.targets[0].position
        if calculate_if_target_in_diamond_range(actor_position, target_position, range_value):
            return 1
        return 0
