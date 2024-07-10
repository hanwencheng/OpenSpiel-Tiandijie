from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.effects import EventListener
    from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from typing import List
from open_spiel.python.games.Tiandijie.calculation.RangeType import RangeType

class FieldBuffTemp:
    def __init__(
        self,
        buff_id: str,
        caster_id: str,
        buff_range: int,
        modifier_effects: List[List[ModifierEffect]] or List[ModifierEffect] = None,
        on_event: List[EventListener] = None,
        range_type=RangeType.DIAMOND,
        field_from="talent"
    ):
        if modifier_effects is None:
            modifier_effects = [[]]
            self.upgradable = False
        elif all(isinstance(item, list) for item in modifier_effects):
            self.upgradable = True
        else:
            modifier_effects = [modifier_effects]
            self.upgradable = False
        if on_event is None:
            on_event = []
        self.id = buff_id
        self.caster_id = caster_id
        self.buff_range = buff_range
        self.modifier_effects: List[List[ModifierEffect]] or List[ModifierEffect] = modifier_effects
        self.event_listeners: List[EventListener] = on_event
        self.range_type = range_type
        self.field_from = field_from

    def __getitem__(self, key):
        return getattr(self, key)
