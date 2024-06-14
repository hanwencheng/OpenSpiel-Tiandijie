from typing import List, Any

from calculation.Modifier import Modifier
from primitives.effects.EventListener import EventListener
from primitives.effects.ModifierEffect import ModifierEffect


class FormationTemp:
    def __init__(
        self,
        formation_id: str,
        formation_hero_id: str,
        activation_hero_requirements: List[dict[str, Any]],
        effects: List[ModifierEffect] = None,
        event_listeners: List[EventListener] = None,
    ):
        if event_listeners is None:
            event_listeners = []
        if effects is None:
            effects = []
        self.id = formation_id
        self.activation_requirements = activation_hero_requirements
        self.hero_id = formation_hero_id
        self.modifier_effects = effects
        self.event_listeners = event_listeners
        self.basic_modifier = Modifier(
            {
                "attack_percentage": 15,
                "magic_attack_percentage": 15,
                "defense_percentage": 15,
                "magic_defense_percentage": 15,
            }
        )
