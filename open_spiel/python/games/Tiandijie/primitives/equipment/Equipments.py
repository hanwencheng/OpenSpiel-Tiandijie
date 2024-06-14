from enum import Enum
from functools import partial
from typing import TYPE_CHECKING

#
# if TYPE_CHECKING:
from calculation.Effects import Effects
# from primitives.equipment.Equipment import Equipment
from primitives.effects.EventListener import EventListener
from primitives.effects.Event import EventTypes
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from calculation.ModifierAttributes import ModifierAttributes as Ma


class Equipment:
    def __init__(self, equipment_id, modifier_effects, on_event):
        self.equipment_id = equipment_id
        self.modifier_effects = modifier_effects
        self.on_event = on_event
        self.cool_down = 0



class Equipments(Enum):
    # 物攻+10%，主动攻击「对战前」施加「封穴」效果，持续1回合。
    bingchanchuanzhu_chen = Equipment(
        "bingchanchuanzhu_chen",
        [ModifierEffect(Rs.always_true, {Ma.attack_percentage: 10})],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.is_attacker),
                partial(Effects.add_buffs, buff_list=["fengxue"], duration=1),
            )
        ],
    )

    # 物攻+10%，主动攻击「对战前」施加「封脉」效果，持续1回合。
    bingchanchuanzhu_yan = Equipment(
        "bingchanchuanzhu_yan",
        [ModifierEffect(Rs.always_true, {Ma.attack_percentage: 10})],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.is_attacker),
                partial(Effects.add_buffs, buff_list=["fengmai"], duration=1),
            )
        ],
    )

    # 物防，气血+5%，气血大于等于80%时，遭受攻击时，物理免伤和暴击减伤提升15%
    yurenjinpei = Equipment(
        "yurenjinpei",
        [
            ModifierEffect(
                Rs.always_true, {Ma.defense_percentage: 5, Ma.life_percentage: 5}
            ),
            ModifierEffect(
                partial(Rs.yurenjinpei_requires_check),
                {
                    Ma.physical_damage_reduction_percentage: 15,
                    Ma.critical_damage_reduction_percentage: 15,
                },
            ),
        ],
        [],
    )

    # 法防+5%，气血+5%，在行动结束时，若自身气血低于50%，则恢复35%气血，并驱散1个「有害状态」（间隔1回合触发）
    xuanqueyaodai = Equipment(
        "xuanqueyaodai",
        [
            ModifierEffect(
                Rs.always_true,
                {Ma.magic_defense_percentage: 5, Ma.life_percentage: 5},
            )
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.LifeChecks.self_life_is_below, 0.5),
                partial(Effects.take_effect_of_xuanqueyaodai),
            )
        ],
    )

    # 全属性+5%，与无克制关系的目标「对战中」伤害额外提升15%
    zanghaijie = Equipment(
        "zanghaijie",
        [
            ModifierEffect(
                Rs.always_true,
                {
                    Ma.life_percentage: 5,
                    Ma.attack_percentage: 5,
                    Ma.magic_attack_percentage: 5,
                    Ma.defense_percentage: 5,
                    Ma.magic_defense_percentage: 5,
                    Ma.luck_percentage: 5,
                },
            ),
            ModifierEffect(
                partial(Rs.battle_with_no_element_advantage),
                {Ma.battle_damage_percentage: 15},
            ),
        ],
        [],
    )

    # 治疗效果+15%，对友方使用单体绝学时，附加「披甲」效果，持续1回合。
    longguxianglian_chen = Equipment(
        "longguxianglian_chen",
        [ModifierEffect(Rs.always_true, {Ma.heal_percentage: 15})],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.target_is_partner),
                partial(Effects.add_buffs, buff_list=["piajia"], duration=1),
            )
        ],
    )

    # 治疗效果+15%，对友方使用单体绝学时，附加「御魔」效果，持续1回合。
    longguxianglian_yan = Equipment(
        "longguxianglian_yan",
        [ModifierEffect(Rs.always_true, {Ma.heal_percentage: 15})],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.target_is_partner),
                partial(Effects.add_buffs, buff_list=["yumo"], duration=1),
            )
        ],
    )

    # 气血+5%，气血高于50%时，物防+15%
    pixieyupei_yan = Equipment(
        "pixieyupei_yan",
        [
            ModifierEffect(Rs.always_true, {Ma.life_percentage: 5}),
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_higher, 0.5),
                {Ma.defense_percentage: 15},
            ),
        ],
        [],
    )

    # 物防+5%，气血低于50%时，物防+20%
    pixieyupei_chen = Equipment(
        "pixieyupei_chen",
        [
            ModifierEffect(Rs.always_true, {Ma.defense_percentage: 5}),
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_below, 0.5),
                {Ma.defense_percentage: 20},
            ),
        ],
        [],
    )

    # 气血+5%，行动结束时，对自己2格范围内法防属性最高的1个友方施加「御魔」状态，持续1回合。
    jiaorenbeige_wu = Equipment(
        "jiaorenbeige_wu",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_jiaorenbeige, state="wu"),
            )
        ],
    )

    # 气血+5%，行动结束时，对自己2格范围内物攻/法攻属性最高的1个友方施加「神睿」状态，持续1回合。
    jiaorenbeige_yan = Equipment(
        "jiaorenbeige_yan",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_jiaorenbeige, state="yan"),
            )
        ],
    )

    # 气血+5%，行动结束时，对自己2格范围内物防属性最高的1个友方施加「披甲」状态，持续1回合。
    jiaorenbeige_chen = Equipment(
        "jiaorenbeige_chen",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_jiaorenbeige, state="chen"),
            )
        ],
    )

    # 气血+5%，行动结束时，对自己2格范围内会心属性最高的1个友方施加「刺骨」状态，持续1回合。
    jiaorenbeige_ying = Equipment(
        "jiaorenbeige_ying",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_jiaorenbeige, state="ying"),
            )
        ],
    )

    # 攻防属性+5%，免疫「固定伤害」「封咒」
    youyaoxiuhuan = Equipment(
        "youyaoxiuhuan",
        [
            ModifierEffect(
                Rs.always_true,
                {
                    Ma.attack_percentage: 5,
                    Ma.magic_attack_percentage: 5,
                    Ma.defense_percentage: 5,
                    Ma.magic_defense_percentage: 5,
                    Ma.is_immunity_fix_damage: True,
                },
            )
        ],
        [],
    )

    # 法攻+10%，使用单体绝学时，伤害额外提升15%。
    tianhezhusha = Equipment(
        "tianhezhusha",
        [
            ModifierEffect(
                Rs.always_true,
                {Ma.magic_attack_percentage: 10},
            ),
            ModifierEffect(
                partial(Rs.skill_is_single_target_damage),
                {Ma.battle_damage_percentage: 15},
            ),
        ],
        [],
    )

    # 气血+5%，主动攻击「对战中」物防、法防提升15%
    qingshenjingyu = Equipment(
        "qingshenjingyu",
        [
            {
                ModifierEffect(
                    Rs.always_true,
                    {Ma.life_percentage: 5},
                ),
                ModifierEffect(
                    partial(Rs.is_attacker),
                    {Ma.defense_percentage: 15, Ma.magic_defense_percentage: 15},
                ),
            }
        ],
        [],
    )

    # 法防+7%，气血+7%，行动结束时，若本回合未造成过伤害，则获得「复仇」和「极意I」状态，持续1回合。
    tianjingfuhun = Equipment(
        "tianjingfuhun",
        [
            ModifierEffect(
                Rs.always_true, {Ma.magic_defense_percentage: 7, Ma.life_percentage: 7}
            )
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.action_has_no_damage),
                partial(Effects.add_self_buffs, ["fuchou", "jiyi"], 1),
            )
        ],
    )

    # 法攻+8%，使用伤害绝学时，暴击率+20%，暴击伤害+10%
    zhongyaoyuzhuo = Equipment(
        "zhongyaoyuzhuo",
        [
            ModifierEffect(
                Rs.always_true, {Ma.magic_attack_percentage: 8}
            ),
            ModifierEffect(
                partial(Rs.skill_is_damage_type),
                {Ma.critical_percentage: 20, Ma.critical_damage_percentage: 10},
            ),
        ],
        [],
    )

    # 物攻+5%，气血+5%，遭受攻击「对战后」，对目标造成一次「固定伤害」（已损失生命的30%）
    feiquanmingyu = Equipment(
        "feiquanmingyu",
        [
            ModifierEffect(
                Rs.always_true, {Ma.attack_percentage: 5, Ma.life_percentage: 5}
            )
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(Rs.is_attack_target),
                partial(Effects.add_fixed_damage_by_target_lose_life, 0.3),
            )
        ],
    )

    # 气血+5%，行动结束时，对自己直线7格内的一个敌人施加「疲弱」状态，持续1回合。
    lingyuepeihuan_yan = Equipment(
        "lingyuepeihuan_yan",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_lingyuepeihuan, "yan"),
            )
        ],
    )

    # 气血+5%，行动结束时，对自己直线7格内的一个敌人施加「蚀御」状态，持续1回合。
    lingyuepeihuan_chen = Equipment(
        "lingyuepeihuan_chen",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_lingyuepeihuan, "chen"),
            )
        ],
    )

    # 气血+5%，行动结束时，对自己直线7格内的一个敌人施加「蚀魔」状态，持续1回合。
    lingyuepeihuan_wu = Equipment(
        "lingyuepeihuan_wu",
        [ModifierEffect(Rs.always_true, {Ma.life_percentage: 5})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_lingyuepeihuan, "wu"),
            )
        ],
    )

    # 气血+10%，免疫「禁疗」「固定伤害」
    huanniaojie = Equipment(
        "huanniaojie",
        [
            ModifierEffect(
                Rs.always_true, {Ma.life_percentage: 10, Ma.is_immunity_fix_damage: True}
            )
        ],
        [],
    )

    # 气血+5%，自身1格范围内存在其他友方时，法术免伤+10%，遭受暴击率降低10%
    yanshanpei = Equipment(
        "yanshanpei",
        [
            ModifierEffect(
                Rs.always_true, {Ma.life_percentage: 5}
            ),
            ModifierEffect(
                partial(Rs.PositionChecks.partner_in_range_count_bigger_than, 1, 1),
                {Ma.magic_damage_reduction_percentage: 10, Ma.suffer_critical_percentage: -10},
            ),
        ],
        [],
    )

    # 全属性+5%，使用单体绝学时，伤害提高12%，使用群体绝学时，暴击率提高12%
    shuangzhijie = Equipment(
        "shuangzhijie",
        [
            ModifierEffect(
                Rs.always_true,
                {
                    Ma.life_percentage: 5,
                    Ma.attack_percentage: 5,
                    Ma.magic_attack_percentage: 5,
                    Ma.defense_percentage: 5,
                    Ma.magic_defense_percentage: 5,
                    Ma.luck_percentage: 5,
                },
            ),
            ModifierEffect(
                partial(Rs.skill_is_single_target_damage),
                {Ma.battle_damage_percentage: 12},
            ),
            ModifierEffect(
                partial(Rs.skill_is_range_target_damage),
                {Ma.critical_percentage: 12},
            ),
        ],
        [],
    )
