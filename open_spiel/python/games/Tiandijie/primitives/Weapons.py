from enum import Enum
from typing import TYPE_CHECKING
from functools import partial

from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as Ma
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.TalentRequirementChecks import TalentRequirementChecks as TRs
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements

from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
# if TYPE_CHECKING:


class Weapon:
    def __init__(self, temp):
        self.temp = temp
        self.fabao_mark = False


class WeaponTemp:
    def __init__(self, weapon_id, name, modifier_effects, on_event, weapon_features):
        self.weapon_id = weapon_id
        self.name = name
        self.modifier_effects = modifier_effects
        self.on_event = on_event
        self.weapon_features = weapon_features


class WeaponFeature:
    def __init__(self, weaponfeatures_id, name, modifier_effects, on_event):
        self.weaponfeatures_id = weaponfeatures_id
        self.name = name
        self.modifier_effects = modifier_effects
        self.on_event = on_event


class WeaponFeatures(Enum):
    # ◈[鹤唳]暴击率提升5%
    # ◈[翎牙]暴击伤害提升5%
    # ◈[锁心]气血高于50%时，进入对战后伤害提升10%
    heli = WeaponFeature(
        "heli",
        "鹤唳",
        [
            ModifierEffect(Rs.always_true, {Ma.critical_percentage: 5}),
        ],
        [],
    )
    lingya = WeaponFeature(
        "lingya",
        "翎牙",
        [
            ModifierEffect(Rs.always_true, {Ma.critical_damage_percentage: 5}),
        ],
        [],
    )
    suoxin = WeaponFeature(
        "suoxin",
        "锁心",
        [
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_higher, 50),
                {Ma.battle_damage_percentage: 10},
            ),
        ],
        [],
    )

    # ◈[丹阳]治疗效果提升5%
    # ◈[真传]全伤害减免提升5%
    # ◈[贯清]气血高于50%时，治疗效果提升10%
    danyang = WeaponFeature(
        "danyang",
        "丹阳",
        [
            ModifierEffect(Rs.always_true, {Ma.heal_percentage: 5}),
        ],
        [],
    )
    zhenchuan = WeaponFeature(
        "zhenchuan",
        "真传",
        [
            ModifierEffect(
                Rs.always_true,
                {
                    Ma.physical_damage_reduction_percentage: 5,
                    Ma.magic_damage_reduction_percentage: 5,
                },
            ),
        ],
        [],
    )
    guanqing = WeaponFeature(
        "guanqing",
        "贯清",
        [
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_higher, 50),
                {Ma.heal_percentage: 10},
            )
        ],
        [],
    )

    # ◈[决明]伤害提升5%
    # ◈[天魁]法术伤害减免提升5%
    # ◈[锁心]气血高于50%时，进入对战后伤害提升10%
    jueming = WeaponFeature(
        "jueming",
        "决明",
        [
            ModifierEffect(
                Rs.always_true,
                {Ma.physical_damage_percentage: 5, Ma.magic_damage_percentage: 5},
            )
        ],
        [],
    )
    tiankui = WeaponFeature(
        "tiankui",
        "天魁",
        [
            ModifierEffect(
                Rs.always_true,
                {
                    Ma.physical_damage_reduction_percentage: 5,
                    Ma.magic_damage_reduction_percentage: 5,
                },
            )
        ],
        [],
    )
    # [破空]反击伤害提升5%
    # [通脉]受治疗效果提升5%
    # [锁心]气血高于50%时，进入对战后伤害提升10%
    pokong = WeaponFeature(
        "pokong",
        "破空",
        [
            ModifierEffect(Rs.always_true, {Ma.counterattack_damage_percentage: 5}),
        ],
        [],
    )
    tongmai = WeaponFeature(
        "tongmai",
        "通脉",
        [
            ModifierEffect(Rs.always_true, {Ma.be_healed_percentage: 5}),
        ],
        [],
    )

class Weapons(Enum):
    # 执妄不破
    # 满级技能
    # 自身2圈范围内存在其他「雷」或「暗」属相的角色时，物理穿透提高20%。携带「执戮」状态时，反击伤害提高20%且反击射程+1。
    zhiwangbupo = WeaponTemp(
        "zhiwangbupo",
        "执妄不破",
        [
            ModifierEffect(
                partial(Rs.PositionChecks.element_hero_in_square, [Elements.DARK, Elements.THUNDER], 2),
                {Ma.physical_penetration_percentage: 20},
            ),
            ModifierEffect(
                partial(Rs.BuffChecks.self_has_certain_buff_in_list, ["zhilu"]),
                {Ma.counterattack_damage_percentage: 22, Ma.counterattack_range: 1},
            ),
        ],
        [],
        [
            WeaponFeatures.heli.value,
            WeaponFeatures.lingya.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 携带「清流」状态的友方受治疗效果增加15%。行动结束时，对3格范围内气血大于等于80%的其他友方施加「霜铠」状态。
    shenwuhanwei = WeaponTemp(
        "shenwuhanwei",
        "神武寒威",
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                Rs.always_true,
                partial(Effects.take_effect_of_shenwuhanwei)
            )
        ],
        [
            WeaponFeatures.danyang.value,
            WeaponFeatures.zhenchuan.value,
            WeaponFeatures.guanqing.value,
        ],
    )

    # 「寒岚」「焚狱」「玄幽」每种状态提升自身5%法术穿透和免伤（最高提升15%）。自身气血大于等于50%时，受到致命伤害免除死亡，气血恢复30%，并立即获得「寒岚」「焚狱」「玄幽」状态（每场战斗最多触发1次）。
    yourifusu = WeaponTemp(
        "yourifusu",
        "幽日复苏",
        [
            ModifierEffect(
                partial(Rs.BuffChecks.self_has_certain_buff_in_list, ["hanlan", "fanyu", "xuanyou"]),
                {Ma.physical_penetration_percentage: 5, Ma.magic_penetration_percentage: 5},
            ),
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_higher, 50),
                {Ma.prevent_death: 0.3},
            ),
        ],
        [
            EventListener(
                EventTypes.rebirth_start,
                1,
                Rs.always_true,
                partial(Effects.add_buffs, ["hanlan", "fanyu", "xuanyou"])
            )
        ],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.tiankui.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 自身周围3格范围内存在非「铁卫」、「祝由」职业的敌方时，法攻提高10%。处于「金乌旗」机关2格范围的敌人主动攻击前驱散其1个「有益状态」。
    qixiangdimi = WeaponTemp(
        "qixiangdimi",
        "旗向敌靡",
        [
            ModifierEffect(
                partial(TRs.linqiqiongyu_requires_check),
                {
                    Ma.magic_attack_percentage: 10,
                },
            ),],
        [],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.zhenchuan.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 「回灵界」范围内的友方物理免伤增加10%，「眩灭界」范围内的敌方受治疗效果降低30%。友方触发阵式时，反转真胤2个「有害状态」。
    budaoshensen = WeaponTemp(
        "budaoshensen",
        "不倒神僧",
        [],
        [],
        [
            WeaponFeatures.pokong.value,
            WeaponFeatures.tongmai.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 遭受攻击「对战前」100 % 概率获得1层「御敌」状态，持续1回合。若自身气血低于70 %，遭受攻击「对战前」恢复30 % 气血，且每多1层「御敌」状态额外回复5 % 气血，并驱散1个「有害状态」（每回合最多触发1次）。
    zhenjinbailian = WeaponTemp(
        "zhenjinbailian",
        "真金百炼",
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.is_battle_attack_target),
                partial(Effects.add_buffs, ["yudi"], 1)
            ),
            EventListener(
                EventTypes.battle_start,
                2,
                partial(Rs.zhenjinbailian_requires_check),
                partial(Effects.take_effect_of_zhenjinbailian)
            )
        ],
        [
            WeaponFeatures.pokong.value,
            WeaponFeatures.tongmai.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 目标每有1个「有害状态」，主动攻击伤害提高3%（最高15%）。使用伤害绝学后，行动结束时5格范围内每有1个携带「有害状态」的敌方，回复自身10%气血（最高50%）。
    juehensugu = WeaponTemp(
        "juehensugu",
        "绝恨苏骨",
        [
            ModifierEffect(
                partial(Rs.BuffChecks.target_harm_buff_count),
                {
                    Ma.single_target_skill_damage_percentage: 3,
                    Ma.range_skill_damage_percentage: 3,
                    Ma.normal_attack_damage_percentage: 3,
                }
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.skill_has_damage),
                partial(Effects.take_effect_of_juehensugu)
            )
        ],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.tiankui.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 2格内存在携带「有益状态」的其他友方时，法攻提高10 %。释放「关切」或「授业」后，对目标施加「冰清」状态，持续1回合。
    chunshichuandao = WeaponTemp(
        "chunshichuandao",
        "谆师传道",
        [
            ModifierEffect(
                partial(Rs.PositionChecks.has_benefit_buff_partner_in_range, 2),
                {
                    Ma.magic_attack_percentage: 10,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.self_use_certain_skill, "guanqie"),
                partial(Effects.add_buffs, ["bingqing"], 1)
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.self_use_certain_skill, "shouye"),
                partial(Effects.add_buffs, ["bingqing"], 1)
            )
        ],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.tiankui.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 霞云披帜: 自身不携带「有害状态」的情况下，治疗效果提高20%。自身处于女娲石状态时，免疫「有害状态」。
    xiayunpizhi = WeaponTemp(
        "xiayunpizhi",
        "霞云披帜",
        [
            ModifierEffect(
                partial(Rs.BuffChecks.self_has_no_harm_buff),
                {
                    Ma.heal_percentage: 20,
                },
            ),
        ],
        [],
        [
            WeaponFeatures.danyang.value,
            WeaponFeatures.zhenchuan.value,
            WeaponFeatures.guanqing.value,
        ],
    )

    # 利剑淬火: 处于友方「真炎」地形上，伤害和物理免伤提高10 %，且行动结束时恢复最大气血的25 %。
    lijiancuihuo = WeaponTemp(
        "lijiancuihuo",
        "利剑淬火",
        [
            ModifierEffect(
                partial(Rs.lijiancuihuo_requires_check),
                {
                    Ma.physical_damage_percentage: 10,
                    Ma.magic_damage_percentage: 10,
                    Ma.physical_damage_reduction_percentage: 10,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.lijiancuihuo_requires_check),
                partial(Effects.heal_self, 0.25)
            )
        ],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.heli.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 好醴慰时: 气血大于等于50 % 时，双防和暴击抗性提高15 %。携带「贮酿」状态时，受到治疗绝学后对3格内友方施加「披甲I」状态，持续1回合。
    haoliweishi = WeaponTemp(
        "haoliweishi",
        "好醴慰时",
        [
            ModifierEffect(
                partial(Rs.LifeChecks.self_life_is_higher, 50),
                {
                    Ma.defense_percentage: 15,
                    Ma.magic_defense_percentage: 15,
                    Ma.suffer_critical_damage_reduction_percentage: 15,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.under_heal_end,
                1,
                partial(Rs.haoliweishi_requires_check),
                partial(Effects.take_effect_of_haoliweishi)
            )
        ],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.heli.value,
            WeaponFeatures.suoxin.value,
        ],
    )