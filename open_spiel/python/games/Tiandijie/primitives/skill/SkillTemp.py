from __future__ import annotations
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.calculation.RangeType import RangeType
from open_spiel.python.games.Tiandijie.helpers import is_magic_profession_dict
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillTargetTypes, SkillType

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
    from open_spiel.python.games.Tiandijie.primitives.effects.SkillListener import SkillListener
    from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
    from open_spiel.python.games.Tiandijie.primitives.skill.Distance import (
        Distance,
        DistanceType,
    )
    from typing import List
    from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Professions
    from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener

from open_spiel.python.games.Tiandijie.calculation.Range import Range
from open_spiel.python.games.Tiandijie.primitives.skill.Distance import distance_profession_dict


class SkillTemp:
    def __init__(
        self,
        skill_temp_id: str,
        chinese_name: str,
        cost: int,
        skill_element: Elements,
        skill_type: SkillType,
        target_type: SkillTargetTypes,
        max_cool_down: int,
        distance: Distance,
        range_instance: Range,
        multiplier: float,
        effects: List[ModifierEffect] = None,
        event_listeners: List[EventListener] = None,
        is_battle_skill: bool = False,
        rush=0,
    ):
        if effects is None:
            effects = []
        if event_listeners is None:
            event_listeners = []
        self.id = skill_temp_id
        self.chinese_name = chinese_name
        self.max_cool_down = max_cool_down
        self.cost = cost
        self.element = skill_element
        self.skill_type = skill_type
        self.target_type = target_type
        self.distance = distance
        self.range_instance = range_instance
        self.multiplier = multiplier
        self.modifier_effects = effects
        self.event_listeners = event_listeners
        self.is_battle_skill = is_battle_skill
        self.rush = rush

    def is_magic(self):
        return self.skill_type == SkillType.Magical


class NormalAttackTemp(SkillTemp):
    def __init__(
            self,
            skill_temp_id: str,
            cost: int,
            skill_element: Elements,
            skill_type: SkillType,
            skill_target_type: SkillTargetTypes,
            max_cool_down: int,
            distance: Distance,
            range_value: Range,
            multiplier: float,
            effects: List[ModifierEffect] = None,
            event_listeners: List[SkillListener] = None,
    ):
        super().__init__(
            skill_temp_id,
            "a",
            cost,
            skill_element,
            skill_type,
            skill_target_type,
            max_cool_down,
            distance,
            range_value,
            multiplier,
            effects,
            event_listeners,
        )
        if effects is None:
            effects = []
        if event_listeners is None:
            event_listeners = []
        self.id = skill_temp_id
        self.cost = cost
        self.element = skill_element
        self.skill_type = skill_type
        self.target_type = skill_target_type
        self.max_cool_down = 0
        self.distance = distance
        self.range_value = range_value
        self.multiplier = multiplier
        self.modifier_effects = effects
        self.event_listeners = event_listeners


def is_normal_attack(skill: SkillTemp) -> bool:
    return isinstance(skill, NormalAttackTemp)


def create_normal_attack_skill(
        element: Elements, profession: Professions, is_magic
) -> NormalAttackTemp:
    if is_magic is None:
        is_magic = is_magic_profession_dict[profession]
    skill_type = SkillType.Magical if is_magic else SkillType.Physical
    return NormalAttackTemp(
        "normal",
        0,
        element,
        skill_type,
        SkillTargetTypes.ENEMY,
        0,
        distance_profession_dict[profession],
        Range(RangeType.POINT, 1),
        1.0,
        [],
        [],
    )
