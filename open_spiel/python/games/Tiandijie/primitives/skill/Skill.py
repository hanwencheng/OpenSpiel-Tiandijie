from __future__ import annotations

import enum
from typing import TYPE_CHECKING, List
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTemp import SkillTemp


class Skill:
    def __init__(
        self, current_cool_down: int, skill_temp: SkillTemp
    ):
        self.cool_down = current_cool_down
        self.temp = skill_temp
