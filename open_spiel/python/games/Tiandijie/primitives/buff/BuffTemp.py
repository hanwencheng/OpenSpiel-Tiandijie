from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from primitives.effects import EventListener
    from primitives.effects.ModifierEffect import ModifierEffect
import enum
import string
from typing import List


class BuffTypes(enum.IntEnum):
    Benefit = 0
    Harm = 1
    Others = 2


class BuffTemp:
    def __init__(
        self,
        buff_id: string,
        buff_type: BuffTypes,
        dispellable,
        expandable,
        stealable,
        modifier_effects: List[List[ModifierEffect]] or List[ModifierEffect] = None,
        on_event: List[List[ModifierEffect]] or List[EventListener] = None,
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
            on_event = [[]]
        elif all(isinstance(item, list) for item in on_event):
            pass
        else:
            on_event = [on_event]

        self.id = buff_id
        self.type: BuffTypes = buff_type
        self.dispellable: bool = dispellable
        self.stealable: bool = stealable
        self.expandable: bool = expandable
        self.modifier_effects: List[List[ModifierEffect]] or List[ModifierEffect] = modifier_effects
        self.event_listeners: List[EventListener] = on_event
        # self.field_buff: FieldBuffTemp = FieldBuffsTemps.get_buff_temp_by_id(buff_id)

    def __getitem__(self, key):
        return getattr(self, key)
