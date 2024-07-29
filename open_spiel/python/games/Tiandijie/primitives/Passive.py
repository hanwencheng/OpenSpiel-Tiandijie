from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
# from open_spiel.python.games.Tiandijie.primitives.equipment.Equipment import Equipment
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as Ma


class Passive:
    def __init__(self, caster_id, temp):
        self.caster_id = caster_id
        self.temp = temp
        self.trigger = 0

class PassiveTemp:
    def __init__(self, id, chinese_name, modifier_effects, on_event, passive_from="Passives"):
        self.id = id
        self.chinese_name = chinese_name
        self.modifier_effects = modifier_effects
        self.on_event = on_event
        self.passive_from = passive_from


class Passives(Enum):
    #  三阙回生: 若目标处于2圈范围内，「对战前」恢复自身25%气血，且「对战中」使目标物攻、法攻降低20%。若自身携带「执戮」状态，则恢复量提升到50%。
    sanquehuisheng = PassiveTemp(
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
            ),
            EventListener(
                EventTypes.game_start,
                1,
                Rs.always_true,
                partial(Effects.add_self_field_buff, ["sanquehuisheng"], 200),
            )
        ],
    )

    #  变谋: 使用炎或冰属相绝学后，该绝学冷却时间-1。
    bianmou = PassiveTemp(
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

    # [被动]回合开始时，与气血百分比最低的1个其他友方平衡气血百分比，并恢复双方生命值（恢复量为施术者法攻的1倍）。
    tongmai = PassiveTemp(
        "tongmai",
        "同脉",
        [],
        [
            EventListener(
                EventTypes.turn_start,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_tongmai),
            )
        ],
    )

    #  [被动]行动结束时，为3格范围内3个气血百分比最低的友方角色恢复气血（恢复量为施术者法攻的0.5倍），并驱散1个「有害状态」。
    fengshaganlinshu = PassiveTemp(
        "fengshaganlinshu",
        "风砂甘霖术",
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_fengshaganlinshu),
            )
        ],
        "skill",
    )

    #  [被动]代替相邻1格内友方承受攻击。
    xiekujieyou = PassiveTemp(
        "xiekujieyou",
        "卸苦解忧",
        [ModifierEffect(Rs.always_true, {Ma.physical_protect_range: 1, Ma.magic_protect_range: 1})],
        [],
        "skill",
    )

    # 法术免伤提高10 %，使用绝学后，获得再移动（2格）。
    zuibuhuayin = PassiveTemp(
        "zuibuhuayin",
        "醉步花阴",
        [ModifierEffect(Rs.always_true, {Ma.magic_damage_reduction_percentage: 10})],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                Rs.always_true,
                partial(Effects.update_self_additional_move, 2),
            )
        ],
    )
