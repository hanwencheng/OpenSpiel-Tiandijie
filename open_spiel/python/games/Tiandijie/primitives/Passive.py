from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from calculation.Effects import Effects
# from primitives.equipment.Equipment import Equipment
from primitives.effects.EventListener import EventListener
from primitives.effects.Event import EventTypes
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from calculation.ModifierAttributes import ModifierAttributes as Ma


class Passive:
    def __init__(self, passive_id, chinese_name, modifier_effects, on_event):
        self.passive_id = passive_id
        self.chinese_name = chinese_name
        self.modifier_effects = modifier_effects
        self.on_event = on_event



class Passives(Enum):
    #  三阙回生: 若目标处于2圈范围内，「对战前」恢复自身25%气血，且「对战中」使目标物攻、法攻降低20%。若自身携带「执戮」状态，则恢复量提升到50%。
    sanquehuisheng = Passive(
        "sanquehuisheng",
        "三阙回生",
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.PositionChecks.battle_member_in_range, 2),
                partial(Effects.heal_self, 0.25),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.sanquehuisheng_requires_check),
                partial(Effects.heal_self, 0.25),
            )
        ],
    )

    #  变谋: 使用炎或冰属相绝学后，该绝学冷却时间-1。
    bianmou = Passive(
        "bianmou",
        "变谋",
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.bianmou_requires_check),
                partial(Effects.reduce_skill_cooldown, 1),
            )
        ],
    )
