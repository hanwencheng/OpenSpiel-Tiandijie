from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.buff.Buff import Buff
from typing import List
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma


class BuffTriggerLimit:
    def __init__(self, max_triggerlimit: int):
        self.max_triggerlimit = max_triggerlimit


buff_trigger_limit = {
    "tandi": BuffTriggerLimit(3),
    "shizhou": BuffTriggerLimit(1),
    "zhuijia": BuffTriggerLimit(1),
    "zhuiming": BuffTriggerLimit(1),
    "xunlie": BuffTriggerLimit(1),
}


def get_buff_max_trigger_limit(buff_id: str):
    return buff_trigger_limit[buff_id].max_triggerlimit if buff_id in buff_trigger_limit else 1
