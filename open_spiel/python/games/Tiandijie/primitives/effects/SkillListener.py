from functools import partial

from primitives import Context
from primitives.effects.Event import EventTypes
from primitives.hero.Hero import Hero


class SkillListener:
    def __init__(
        self,
        priority: int,
        requirement: partial[[Hero, Hero, Context], int] or None,
        listener_effects: partial[[Hero, Hero, Context], None],
    ):
        if requirement is None:
            requirement = lambda x, y, z: 1
        self.priority = priority
        self.listener_effects = listener_effects
        self.requirement = requirement
