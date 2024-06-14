from enum import Enum
from typing import TYPE_CHECKING
from functools import partial

from calculation.ModifierAttributes import ModifierAttributes as Ma
from primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from primitives.RequirementCheck.TalentRequirementChecks import TalentRequirementChecks as TRs
from primitives.effects.Event import EventTypes
from calculation.Effects import Effects
from primitives.effects.ModifierEffect import ModifierEffect
from primitives.hero.Element import Elements

from primitives.effects.EventListener import EventListener
# if TYPE_CHECKING:


class Weapon:
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


class Weapons(Enum):
    # 执妄不破
    # 满级技能
    # 自身2圈范围内存在其他「雷」或「暗」属相的角色时，物理穿透提高20%。携带「执戮」状态时，反击伤害提高20%且反击射程+1。
    zhiwangbupo = Weapon(
        "zhiwangbupo",
        "执妄不破",
        [
            ModifierEffect(
                partial(Rs.PositionChecks.element_hero_in_range, [Elements.DARK, Elements.THUNDER]),
                {Ma.physical_penetration_percentage: 20},
            ),
            ModifierEffect(
                partial(Rs.BuffChecks.self_has_certain_buff_in_list, ["zhilu"]),
                {Ma.counterattack_damage_percentage: 20, Ma.counterattack_range: 1},
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
    shenwuhanwei = Weapon(
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
    yourifusu = Weapon(
        "yourifusu",
        "幽日复苏",
        [
            ModifierEffect(
                partial(Rs.BuffChecks.self_has_certain_buff_in_list, ["hanlan", "fenyu", "xuanyou"]),
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
                partial(Effects.add_buffs, ["hanlan", "fenyu", "xuanyou"])
            )
        ],
        [
            WeaponFeatures.jueming.value,
            WeaponFeatures.tiankui.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 自身周围3格范围内存在非「铁卫」、「祝由」职业的敌方时，法攻提高10%。处于「金乌旗」机关2格范围的敌人主动攻击前驱散其1个「有益状态」。
    qixiangdimi = Weapon(
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
            WeaponFeatures.heli.value,
            WeaponFeatures.lingya.value,
            WeaponFeatures.suoxin.value,
        ],
    )

    # 「回灵界」范围内的友方物理免伤增加10%，「眩灭界」范围内的敌方受治疗效果降低30%。友方触发阵式时，反转真胤2个「有害状态」。
    budaoshensen = Weapon(
        "budaoshensen",
        "不倒神僧",
        [],
        [],
        [
            WeaponFeatures.danyang.value,
            WeaponFeatures.zhenchuan.value,
            WeaponFeatures.guanqing.value,
        ],
    )
