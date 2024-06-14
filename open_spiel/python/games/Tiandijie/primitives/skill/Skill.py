from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List
from basics import Position
from primitives.skill.SkillTemp import SkillTemp

if TYPE_CHECKING:
    from primitives.hero.Element import Elements
    from primitives.skill.Distance import Distance
    from calculation.Range import Range
    from primitives.effects.EventListener import EventListener
    from primitives.effects.SkillListener import SkillListener
    from primitives.effects.ModifierEffect import ModifierEffect


class Skill:
    def __init__(
        self, current_cool_down: int, skill_temp: SkillTemp
    ):
        self.cool_down = current_cool_down
        self.temp = skill_temp
