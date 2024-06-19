from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives import Context
    from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTemp, BuffTypes
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.FieldBuff import FieldBuff
    from open_spiel.python.games.Tiandijie.primitives.fieldbuff.fieldbuffs import FieldBuffsTemps


from open_spiel.python.games.Tiandijie.primitives.buff.BuffImmuneList import *


class Buff:
    def __init__(
        self,
        buff_temp: BuffTemp,
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
        self.cooldown: int = 0
        self.content = content


def cast_buff(
    buff_temp: BuffTemp,
    duration: int,
    caster_id: str,
    target_id: str,
    level: int = 1,
    stack: int = 1,
    context: Context = None,
):
    target_hero = context.get_hero_by_id(target_id)
    # prevent adding buff if the target hero is immune to the buff
    for immune_buff in target_hero.buffs:
        if (
            immune_buff.temp.id in prevent_all_harm_list
            and buff_temp.type == BuffTypes.Harm
        ):
            return

        if (
            immune_buff.temp.id in prevent_all_benefit_list
            and buff_temp.type == BuffTypes.Benefit
        ):
            return

        if (
            immune_buff.temp.id in immune_dict
            and buff_temp.id in immune_dict[immune_buff.temp.id]
        ):
            return

    # remove the related buff if buff_temp.id is in the immune_dict
    if buff_temp.id in immune_dict:
        immune_list = immune_dict[buff_temp.id]
        for immune_buff_id in immune_list:
            for buff in target_hero.buffs:
                if buff_temp.id in immune_all_harm_list and buff.type == BuffTypes.Harm:
                    target_hero.buffs.remove(buff)
                elif (
                    buff_temp.id in immune_all_benefit_list
                    and buff.type == BuffTypes.Benefit
                ):
                    target_hero.buffs.remove(buff)
                elif buff.temp.id == immune_buff_id:
                    target_hero.buffs.remove(buff)
    target_hero.buffs.append(Buff(buff_temp, duration, caster_id, level, stack, 0, 0))
