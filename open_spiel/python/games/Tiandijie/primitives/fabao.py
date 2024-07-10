from enum import Enum
from functools import partial
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as Ma
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects


class Fabao:
    def __init__(self, weapon_id, modifier_effects, on_event):
        self.weapon_id = weapon_id
        self.modifier_effects = modifier_effects
        self.on_event = on_event
        self.cooldown = 0


class Fabaos(Enum):
    # 气血大于等于50 % 时，治疗效果提升15 %。    气血大于等于50 % 时，免伤提升10 %。    使用绝学后，若自身气血不满为自己恢复气血（法攻 * 0.5）并驱散1个「有害状态」（触发间隔1回合）。
    shierpinliantai = Fabao(
        "shierpinliantai",
        [
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_higher, 50),
                {Ma.heal_percentage: 15, Ma.physical_damage_reduction_percentage: 10, Ma.magic_damage_reduction_percentage: 10},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.LifeChecks.life_not_full),
                partial(Effects.take_effect_of_shierpinliantai)
            ),
        ],
    )

    # 气血大于等于50 % 时，主动攻击「对战中」伤害提升10 %。    气血大于等于50 % 时，主动攻击「对战中」暴击率提升10 %。    每场战斗首次遭受攻击免伤提升30 %。
    zijinhulu = Fabao(
        "zijinhulu",
        [
            ModifierEffect(
                partial(Rs.zijinhulu_requires_check, 1),
                {Ma.battle_damage_percentage: 10, Ma.critical_percentage: 10},
            ),
            ModifierEffect(
                partial(Rs.zijinhulu_requires_check, 2),
                {Ma.physical_damage_reduction_percentage: 30, Ma.magic_damage_reduction_percentage: 30},
            ),
        ],
        [],
    )