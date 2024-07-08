from __future__ import annotations

from enum import Enum
from functools import partial
from typing import List

from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as Ma
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect as ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs


class TerrainBuffTemp:
    def __init__(self, buff_id: str, dispellable: bool, modifier_list, on_event=None):
        if on_event is None:
            on_event = []
        self.modifier = modifier_list
        self.id = buff_id
        self.dispellable = dispellable
        self.on_event: List[EventListener] = on_event


class TerrainBuff:
    def __init__(self, temp: TerrainBuffTemp, duration: int, side: int):
        self.temp = temp
        self.duration = duration
        self.side = side


class TerrainBuffTemps(Enum):
    @classmethod
    def get_buff_temp_by_id(cls, buff_id):
        for buff_temp in cls:
            if buff_temp.value.id == buff_id:
                return buff_temp.value
        return None

    fire = TerrainBuffTemp(
        "fire",
        True,
        {},
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_fixed_damage_by_percentage, percentange=0.1),
            )
        ],
    )
    # 移动力 - 1
    ice = TerrainBuffTemp("ice", True, [ModifierEffect(partial(Rs.always_true), {Ma.move_range: -1})])
    # 「剑牢」：敌人无法触发再移动和自身赋予的再行动，暴击率-20%
    jianlao = TerrainBuffTemp("jianlao", True, [ModifierEffect(partial(Rs.always_true), {Ma.critical_percentage: -30})])
    # 相邻1格内开启「限制区域」：敌方移动力消耗 + 1。主动攻击前驱散敌方1个「有益状态」，并施加「燃烧」状态，持续2回合。
    jinwuqi = TerrainBuffTemp(
        "jinwuqi",
        False,
        [
            ModifierEffect(
                partial(Rs.always_true),
                {Ma.move_range: -1})
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                Rs.always_true,
                partial(Effects.reverse_self_benefit_buffs, 1)
            ),
            EventListener(
                EventTypes.battle_start,
                2,
                Rs.always_true,
                partial(Effects.add_self_buffs, ["ranshao"], 2)
            )
        ]
    )

