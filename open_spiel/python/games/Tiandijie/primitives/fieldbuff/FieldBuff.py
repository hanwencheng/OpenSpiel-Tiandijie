from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuffTemp import FieldBuffTemp


class FieldBuff:
    def __init__(
        self,
        buff_temp: FieldBuffTemp,
        duration: int,
        caster_id: str,
        level: int = 1,
        stack: int = 1,
        trigger: int = 0,
        content: int = 0,
    ):
        # Copying attributes from BuffTemp
        self.__dict__.update(buff_temp.__dict__)
        # Setting duration
        self.duration: int = duration
        self.temp = buff_temp
        self.caster_id = caster_id
        self.level = level
        self.stack = stack
        self.trigger = trigger
        self.content = content
