from typing import List

from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect


class Talent:
    def __init__(
        self,
        hero_id: str,
        temp: "TalentTemp",
    ):
        self.caster_id = hero_id
        self.trigger: int = 0
        self.cooldown: int = 0
        self.temp = temp


class TalentTemp:
    def __init__(
        self,
        talent_id: str,
        effects: List[ModifierEffect] = None,
        event_listeners: List[EventListener] = None,
    ):
        if effects is None:
            effects = []
        if event_listeners is None:
            event_listeners = []
        self.id = talent_id
        self.modifier_effects = effects
        self.event_listeners = event_listeners
