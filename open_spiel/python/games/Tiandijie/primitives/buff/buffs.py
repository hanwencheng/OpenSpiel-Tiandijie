from enum import Enum
from functools import partial

from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from open_spiel.python.games.Tiandijie.primitives.buff.BuffTemp import BuffTemp, BuffTypes
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as RS
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements


class BuffTemps(Enum):
    @classmethod
    def get_buff_temp_by_id(cls, buff_id):
        """Return the BuffTemp with the specified ID, or None if not found."""
        for buff_temp in cls:
            if buff_temp.value["id"] == buff_id:
                return buff_temp.value
        return None

    # 无摧·封脉	有害	不可驱散	不可扩散	不可偷取	所有被动「绝学」失效（不可驱散）
    wucui_fengmai = BuffTemp(
        "wucui_fengmai",
        BuffTypes.Harm,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_passives_skill_disabled: True})],
    )

    # 迟缓I	有害	可驱散	可扩散	不可偷取	移动力-1，无法护卫
    chihuan = BuffTemp(
        "chihuan",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 0,
                        ma.magic_protect_range: 0,
                        ma.move_range: -1,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 0,
                        ma.magic_protect_range: 0,
                        ma.move_range: -2,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_protect_range: 0,
                        ma.magic_protect_range: 0,
                        ma.move_range: -3,
                    },
                )
            ],
        ],
    )

    # 封劲	有害	可驱散	可扩散	可偷取	主动绝学射程-1
    fengjing = BuffTemp(
        "fengjing",
        BuffTypes.Harm,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.active_skill_range: -1})],
    )

    # 幽霜	其他	不可驱散	不可扩散	不可偷取	免伤+20%，主动造成伤害后，对目标造成1次「固定伤害」（（物攻+物防）的30%），并施加「迟缓I」状态，持续2回合
    youshuang = BuffTemp(
        "youshuang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.magic_damage_reduction_percentage: 20,
                    ma.physical_damage_reduction_percentage: 20,
                },
            )
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_fixed_damage_with_attack_and_defense,
                    0.3,
                    False,
                ),
            ),
            EventListener(
                EventTypes.damage_end,
                2,
                RS.always_true,
                partial(
                    Effects.add_target_harm_buffs, ["chihuan"], 2
                ),
            ),
        ],
    )

    # 禁闭 其他 不可驱散	不可扩散	不可偷取	无法行动，且在对战中无法进行反击。行动结束时，对周围2格内所有友方施加1个随机「有害状态」（不可驱散，队友行动结束若处于自身1格范围移除）
    jinbi = BuffTemp(
        "jinbi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_action_disabled: True, ma.is_counterattack_disabled: True},
            )
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_partner_harm_buffs, 1, 2, 2
                ),
            ),
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.has_partner_in_range, 1),
                partial(Effects.remove_target_certain_buff, "jinbi"),
            ),
        ],
    )

    # 幽禁 其他 不可驱散  不可扩散	不可偷取  若自身1格内无其他友方，行动力-1。与律「对战中」攻击、免伤降低15%
    youjin = BuffTemp(
        "youjin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.no_partners_in_range, 1), {ma.move_range: -1}
            ),
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "lv"),
                {
                    ma.battle_damage_percentage: -15,
                    ma.battle_damage_reduction_percentage: -15,
                },
            ),
        ],
    )

    # 三昧真火	有害	可驱散	不可扩散	不可偷取	法防-15%，行动结束时，遭受1次法术伤害（施加者法攻的50%）
    sanmei_zhenhuo = BuffTemp(
        "sanmei_zhenhuo",
        BuffTypes.Harm,
        True,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: -15})],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_magic_damage_by_caster_magic_attack,
                    0.5,
                ),
            )
        ],
    )

    # 中毒	有害	可驱散	可扩散	可偷取	行动结束时，损失10%气血，若每多格，则额外损失5%气血（最多15%）
    zhongdu = BuffTemp(
        "zhongdu",
        BuffTypes.Harm,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_max_life_percentage, 0.1
                ),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.take_fixed_damage_by_percentage_per_each_move,
                    0.05,
                    0.15,
                ),
            ),
        ],
    )

    # 乱神I	有害	可驱散	可扩散	不可偷取	伤害-10%, 乱神II	有害	可驱散	可扩散	不可偷取	伤害-20%
    luanshen = BuffTemp(
        "luanshen",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_percentage: -10,
                        ma.magic_damage_percentage: -10,
                    },
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_percentage: -20,
                        ma.magic_damage_percentage: -20,
                    },
                )
            ],
        ],
        [],
    )

    # 云隐	其他	不可驱散	不可扩散	不可偷取	无法作为目标被选中，主动造成伤害或者承受1次范围伤害后状态消失
    yunyin = BuffTemp(
        "yunyin",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_non_selectable: True})],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "yunyin"),
            ),
            EventListener(
                EventTypes.under_skill_end,
                1,
                partial(RS.skill_is_range_target_damage),
                partial(Effects.remove_actor_certain_buff, "yunyin"),
            ),
        ],
    )

    # 仙灵	其他	不可驱散	不可扩散	不可偷取	移动力+1，气血大于等于80%时，无法被敌方选中（主动攻击「对战后」移除）。
    xianling = BuffTemp(
        "xianling",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.move_range: 1}),
            ModifierEffect(
                partial(RS.LifeChecks.self_life_is_higher, 80),
                {ma.is_non_selectable: True},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "xianling"),
            ),
        ],
    )

    # 仙罪	其他	不可驱散	不可扩散	不可偷取	与「雪芝」「对战中」伤害、免伤-10%（上限3层）。主动绝学都在冷却中时，移动力-1。
    xianzui = BuffTemp(
        "xianzui",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "xuezhi"),
                {
                    ma.battle_damage_reduction_percentage: -10,
                    ma.battle_damage_percentage: -10,
                },
            ),
            ModifierEffect(
                partial(RS.self_all_active_skills_in_cooldown), {ma.move_range: -1}
            ),
        ],
        [],
        3,
    )

    # 仙躯	其他	不可驱散	不可扩散	不可偷取	法术免伤提高20%，代替2格内友方承受法术攻击（遭受攻击「对战后」消失并回复50%气血）
    xianqu = BuffTemp(
        "xianqu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 20, ma.magic_protect_range: 2},
            )
        ],
        [
            EventListener(
                EventTypes.battle_end,
                3,
                partial(RS.is_battle_attack_target),
                partial(Effects.remove_actor_certain_buff, "xianqu"),
            ),
            EventListener(
                EventTypes.battle_end,
                3,
                partial(RS.is_battle_attack_target),
                partial(Effects.heal_self, 0.5),
            ),
        ],
    )

    #  余蕴幽香	其他	不可驱散	不可扩散	不可偷取	若自身气血低于100%，则对友方使用绝学后同时为自己恢复气血（恢复量为施术者法攻的1倍）
    yuyunyouxiang = BuffTemp(
        "yuyunyouxiang",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_for_partner_end,
                1,
                partial(RS.LifeChecks.life_not_full),
                partial(Effects.heal_self_by_caster_magic_attack, 1),
            )
        ],
    )

    #  侠义	其他	不可驱散	不可扩散	不可偷取	行动结束前，若携带3层「侠义」状态，则获得再移动4格，并消耗2层。（上限3层，无法驱散）
    xiayi = BuffTemp(
        "xiayi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.BuffChecks.self_buff_stack_reach, 3, "xiayi"),
                partial(Effects.take_effect_of_xiayi),
            ),
        ],
        3,
    )

    #  信步	有益	可驱散	可扩散	可偷取	免疫「移动力降低」
    xinbu = BuffTemp("xinbu", BuffTypes.Benefit, True, True, True, [], [])

    # 光铠	有益	可驱散	可扩散	可偷取	遭受范围绝学攻击时，受到伤害降低20%，并为自身驱散1个「有害状态」（遭受范围绝学攻击后消失）
    guangkai = BuffTemp(
        "guangkai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            ModifierEffect(
                partial(RS.self_is_target_and_skill_is_range_target_damage), {ma.physical_damage_reduction_percentage: 20, ma.magic_damage_reduction_percentage: 20}
            )
        ],
        [
            EventListener(
                EventTypes.under_skill_start,
                1,
                partial(RS.self_is_target_and_skill_is_range_target_damage),
                partial(Effects.remove_self_harm_buffs, 1),
            ),
            EventListener(
                EventTypes.under_skill_end,
                1,
                partial(RS.skill_is_range_target_damage),
                partial(Effects.remove_target_certain_buff, "guangkai"),
            ),
        ],
    )

    # 冰之力	其他	不可驱散	不可扩散	不可偷取	攻击携带「迟缓」类状态的目标时，战斗中伤害额外提高20%。
    bingzhili = BuffTemp(
        "bingzhili",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.BuffChecks.target_has_certain_buff, "chihuan"),
                {ma.battle_damage_percentage: 20},
            )
        ],
        [],
    )

    # 冰劫	其他	不可驱散	不可扩散	不可偷取	主动移动时，若移动距离小于等于1格，行动结束时，将「冰劫」替换为「晕眩」，持续1回合。
    bingjie = BuffTemp(
        "bingjie",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.move_end,
                1,
                partial(RS.move_less_or_equal_than, 1),
                partial(Effects.replace_self_buff, "bingjie", "yunxuan", 1),
            )
        ],
    )

    # 冰清	有益	可驱散	可扩散	可偷取	免疫所有有害效果
    bingqing = BuffTemp("bingqing", BuffTypes.Benefit, True, True, True, [], [])

    # 刺骨I	有益	可驱散	可扩散	可偷取	暴击率+20%
    cigu = BuffTemp(
        "cigu",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.critical_percentage: 20})],
            [ModifierEffect(RS.always_true, {ma.critical_percentage: 25})],
        ],
        [],
    )

    # 固元I	有益	可驱散	可扩散	可偷取	法术免伤+10%
    guyuan = BuffTemp(
        "guyuan",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: 10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: 20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: 25}
                )
            ],
        ],
        [],
    )

    # 失智I	有害	可驱散	可扩散	可偷取	法术免伤-10%
    shizhi = BuffTemp(
        "shizhi",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: -10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: -20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.magic_damage_reduction_percentage: -25}
                )
            ],
        ],
        [],
    )

    # 御魔I	有益	可驱散	可扩散	可偷取	法防+30%
    yumou = BuffTemp(
        "yumou",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: 30})],
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: 35})],
        ],
        [],
    )

    # 披甲I	有益	可驱散	可扩散	可偷取	物防+20%
    pijia = BuffTemp(
        "pijia",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.defense_percentage: 20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.defense_percentage: 25}
                )
            ],
        ],
        [],
    )

    # 断刺I	有害	可驱散	可扩散	不可偷取	暴击率-20%
    duanci = BuffTemp(
        "duanci",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.critical_percentage: -20})],
            [ModifierEffect(RS.always_true, {ma.critical_percentage: -25})],
        ],
        [],
    )

    # 极意I	有益	可驱散	可扩散	可偷取	伤害+10%
    jiyi = BuffTemp(
        "jiyi",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 10})],
            [ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 20})],
            [ModifierEffect(RS.always_true, {ma.physical_damage_percentage: 25})],
        ],
        [],
    )

    # 疲弱I	有害	可驱散	可扩散	不可偷取	物攻，法攻-20%
    piruo = BuffTemp(
        "piruo",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: -20, ma.magic_attack_percentage: -20},
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: -25, ma.magic_attack_percentage: -25},
                )
            ],
        ],
        [],
    )

    # 神护I	有益	可驱散	可扩散	可偷取	物理免伤+10%
    shenhu = BuffTemp(
        "shenhu",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: 25}
                )
            ],
        ],
        [],
    )

    # 神睿I	有益	可驱散	可扩散	可偷取	物攻、法攻+20%
    shenrui = BuffTemp(
        "shenrui",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: 20, ma.magic_attack_percentage: 20},
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: 25, ma.magic_attack_percentage: 25},
                )
            ],
        ],
        [],
    )

    # 神行I	其他	不可驱散	不可扩散	不可偷取	移动力+1，使用伤害绝学造成暴击，该绝学冷却时间-1
    shenxing = BuffTemp(
        "shenxing",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.move_range: 1})],
            [ModifierEffect(RS.always_true, {ma.move_range: 2})],
            [ModifierEffect(RS.always_true, {ma.move_range: 3})],
        ],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                partial(RS.action_is_active_skill),
                partial(Effects.reduce_skill_cooldown, 1),
            )
        ],
    )

    # 芬芳I	有益	可驱散	可扩散	可偷取	治疗效果提高20%
    fenfang = BuffTemp(
        "fenfang",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.heal_percentage: 20})],
            [ModifierEffect(RS.always_true, {ma.heal_percentage: 30})],
        ],
        [],
    )

    # 虚损I	有害	可驱散	可扩散	不可偷取	物理免伤-10%
    xusun = BuffTemp(
        "xusun",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -10}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -20}
                )
            ],
            [
                ModifierEffect(
                    RS.always_true, {ma.physical_damage_reduction_percentage: -25}
                )
            ],
        ],
        [],
    )

    # 蚀御I	有害	可驱散	可扩散	不可偷取	物防-20%
    shiyu = BuffTemp(
        "shiyu",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.defense_percentage: -20})],
            [ModifierEffect(RS.always_true, {ma.defense_percentage: -25})],
        ],
        [],
    )

    # 蚀魔I	有害	可驱散	可扩散	不可偷取	法防-30%
    shimo = BuffTemp(
        "shimo",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: -30})],
            [ModifierEffect(RS.always_true, {ma.magic_defense_percentage: -35})],
        ],
        [],
    )

    # 迅捷I	有益	可驱散	可扩散	可偷取	移动力+1
    xunjie = BuffTemp(
        "xunjie",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.move_range: 1})],
            [ModifierEffect(RS.always_true, {ma.move_range: 2})],
            [ModifierEffect(RS.always_true, {ma.move_range: 3})],
        ],
        [],
    )

    # 迅目I	有益	可驱散	可扩散	可偷取	会心+30%
    xunmu = BuffTemp(
        "xunmu",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [ModifierEffect(RS.always_true, {ma.luck_percentage: 30})],
            [ModifierEffect(RS.always_true, {ma.luck_percentage: 40})],
        ],
        [],
    )

    #  圣耀	其他	不可驱散	不可扩散	不可偷取	3格内的敌人行动结束时获得「魂创」状态，并恢复施加者30%最大气血。(领域)
    # 圣耀·贰	其他	不可驱散	不可扩散	不可偷取	自身免伤+15%，3格内的敌人行动结束时获得「魂创」状态，驱散施加者1个「有害状态」并恢复施加者30%最大气血。
    shengyao = BuffTemp(
        "shengyao",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_reduction_percentage: 15,
                        ma.magic_damage_reduction_percentage: 15,
                    },
                )
            ],
        ],
        [],
    )

    #   地火焚狱	其他	不可驱散	不可扩散	不可偷取	若敌人行动结束时，位于施加者3格范围内，驱散2个「有益状态」，并受到1次「固定伤害」（施术者物攻的15%）
    dihuofanyu = BuffTemp(
        "dihuofanyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 堕罪	有害	不可驱散	不可扩散	不可偷取	无法获得「有益状态」，遭受施加者攻击时，法术免伤-10%。
    duozui = BuffTemp(
        "duozui",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.attacked_by_caster),
                {ma.magic_damage_reduction_percentage: -10},
            )
        ],
        [],
    )

    # 处刑    其他 不可驱散   不可扩散   不可偷取   射程和移动力+1，主动攻击后使目标携带的「有害状态」等级提升1级。
    chuxing = BuffTemp(
        "chuxing",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.attack_range: 1, ma.move_range: 1})],
        [
            EventListener(
                EventTypes.normal_attack_end,
                1,
                RS.always_true,
                partial(Effects.increase_target_harm_buff_level, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.target_is_enemy),
                partial(Effects.increase_target_harm_buff_level, 1),
            ),
        ],
    )

    # 复仇	有益	可驱散	可扩散	可偷取	反击伤害提高30%
    fuchou = BuffTemp(
        "fuchou",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.counterattack_damage_percentage: 30})],
        [],
    )

    # 天玑印	有益	可驱散	不可扩散	不可偷取	免疫所有「有害状态」，获得来自施加者触发的天赋效果（不可复制，不可偷取）
    # 自身3格范围内每多1个其他友方，法攻提高6%（最多提高18%）。若本回合主动造成伤害，则行动结束时，为3格范围内其他友方恢复气血（恢复量为施术者法攻的0.5倍）；反之为自身3格范围内4个其他友方施加1个随机「有益状态」。
    tianjiyin = BuffTemp(
        "tianjiyin",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 3, 3),
                {ma.magic_attack_percentage: 6},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.take_effect_of_tianjiyin),
            )
        ],
    )

    # 天魔护铠	其他	不可驱散	不可扩散	不可偷取	免伤提高50%（受到伤害后消失）
    tianmohukai = BuffTemp(
        "tianmohukai",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_reduction_percentage: 50,
                    ma.magic_damage_reduction_percentage: 50,
                },
            )
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "tianmohukai"),
            )
        ],
    )

    # 如燕	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战中」暴击率提高20%，移动力+1，可跨越障碍（不可驱散）
    ruyan = BuffTemp(
        "ruyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacker),
                {
                    ma.critical_percentage: 20,
                },
            ),
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: 1,
                    ma.is_ignore_obstacle: True,
                },
            ),
        ],
        [],
    )

    # 威慑	其他	不可驱散	不可扩散	不可偷取	自身反击射程+1，3格范围内所有敌人除气血外全属性降低10%，且具有轻功能力的角色翻越障碍能力失效
    weishe = BuffTemp(
        "weishe",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.counterattack_range: 1},
            ),
        ],
        [],
    )

    # 定身	有害	不可驱散	不可扩散	不可偷取	无法移动，无法护卫
    dingshen = BuffTemp(
        "dingshen",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.max_move_range: 0,
                    ma.physical_protect_range: 0,
                    ma.magic_protect_range: 0,
                },
            )
        ],
        [],
    )

    # 冲阵	其他	不可驱散	不可扩散	不可偷取	移动力+1，伤害和免伤提高12%（上限2层）
    chongzhen = BuffTemp(
        "chongzhen",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: 1,
                    ma.physical_damage_percentage: 12,
                    ma.magic_damage_percentage: 12,
                    ma.physical_damage_reduction_percentage: 12,
                    ma.magic_damage_reduction_percentage: 12,
                },
            )
        ],
        [],
        2,
    )

    # 凝冰	有益	不可驱散	不可扩散	不可偷取	伤害提高1%，物理穿透提高1%（上限4层）
    ningbing = BuffTemp(
        "ningbing",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 1,
                    ma.magic_damage_percentage: 1,
                    ma.physical_penetration_percentage: 1,
                },
            )
        ],
        [],
        4,
    )

    # 剑意激荡	其他	不可驱散	不可扩散	不可偷取	普攻附带0.5目标（物攻+法攻）的伤害（无法被减免）。魔天凛意附带0.75目标（物攻+法攻）的伤害（无法被减免）；若会心大于对方，则附带1目标（物攻+法攻）的伤害（无法被减免）
    jianyijidang = BuffTemp(
        "jianyijidang",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.normal_attack_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_fixed_damage_with_physical_and_magic_attack,
                    0.5,
                ),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.self_use_certain_skill, "motianlingyi"),
                partial(
                    Effects.take_effect_of_jianyi_jidang,
                ),
            ),
        ],
    )

    # 剑气	其他	不可驱散	不可扩散	不可偷取	造成伤害提升24%，遭受伤害降低24%
    jianqi = BuffTemp(
        "jianqi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 24,
                    ma.magic_damage_percentage: 24,
                    ma.physical_damage_reduction_percentage: 24,
                    ma.magic_damage_reduction_percentage: 24,
                },
            )
        ],
        [],
    )

    # 剑绝	其他	不可驱散	不可扩散	不可偷取	「对战中」物理穿透提升20%，遭受攻击「对战中」发动「先攻」，且「先攻」射程提高1格。受到伤害后获得1层「剑绝」状态（最多叠加3层，达到3层时，主动使用单体伤害绝学造成伤害后降低2层）
    jianjue = BuffTemp(
        "jianjue",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_in_battle),
                {ma.physical_penetration_percentage: 20},
            ),
            ModifierEffect(
                partial(RS.is_attack_target),
                {ma.is_counterattack_first: True, ma.counterattack_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(Effects.increase_actor_certain_buff_stack, "jianjue"),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.jianjue_requires_check),
                partial(
                    Effects.reduce_actor_certain_buff_stack,
                    "jianjue",
                    2,
                ),
            ),
        ],
    )

    # 剑绝霜狱	其他	不可驱散	不可扩散	不可偷取	周围2格内所有敌人移动力-3，且无法护卫（无法驱散）
    jianjueshuangyu = BuffTemp(
        "jianjueshuangyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_of_enemy, "yinwuxie", 2),
                {
                    ma.move_range: -3,
                    ma.is_ignore_protector: True,
                },
            ),
        ],
        [],
    )

    # 劫烬	其他	不可驱散	不可扩散	不可偷取	全属性提升20%
    jiejin = BuffTemp(
        "jiejin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.life_percentage: 20,
                    ma.attack_percentage: 20,
                    ma.magic_attack_percentage: 20,
                    ma.defense_percentage: 20,
                    ma.magic_defense_percentage: 20,
                    ma.luck_percentage: 20,
                },
            )
        ],
        [],
    )

    # 化形·反啄I	有益	不可驱散	不可扩散	不可偷取	反击射程+1，与远程作战「对战中」物防、法防提升20%
    huaxing_fanzhuo = BuffTemp(
        "huaxing_fanzhuo",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.counterattack_range: 1},
            ),
            ModifierEffect(
                partial(RS.is_battle_with_remote),
                {
                    ma.defense_percentage: 20,
                    ma.magic_defense_percentage: 20,
                },
            ),
        ],
        [],
    )

    # 压制	其他	不可驱散	不可扩散	不可偷取	无法进行反击或先攻（不可驱散，遭受攻击「对战后」消失）
    yazhi = BuffTemp(
        "yazhi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_counterattack_disabled: True, ma.is_counterattack_first: False},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_battle_attack_target),
                partial(Effects.remove_actor_certain_buff, "yazhi"),
            )
        ],
    )

    # 同归	其他	不可驱散	不可扩散	不可偷取	暴击率提高100%，行动结束死亡
    tonggui = BuffTemp(
        "tonggui",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.critical_percentage: 100}),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.kill_self),
            )
        ],
    )

    # 启智	其他	不可驱散	不可扩散	不可偷取	遭受单体伤害绝学攻击时气血越高免伤和暴击抗性越高（最高提升20%）（遭受单体伤害绝学后移除）
    qizhi = BuffTemp(
        "qizhi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.skill_is_single_target_damage_and_life_is_higher_percentage),
                {
                    ma.battle_damage_reduction_percentage: 20,
                    ma.suffer_critical_damage_reduction_percentage: 20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.under_skill_end,
                1,
                partial(RS.skill_is_single_target_damage),
                partial(Effects.remove_actor_certain_buff, "qizhi"),
            )
        ],
    )

    # 命蕴	有益	可驱散	可扩散	可偷取	行动结束时，恢复20%气血
    mingyun = BuffTemp(
        "mingyun",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, 0.2),
            )
        ],
    )

    # 宿魂	其他	不可驱散	不可扩散	不可偷取	携带「执戮」状态时，若受到致命伤害时免除死亡，自身恢复30%气血（每场战斗触发1次）
    suhun = BuffTemp(
        "suhun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.prevent_death: 0.3}),
        ],
        [],
    )

    # 寄形	其他	不可驱散	不可扩散	不可偷取	与施加者作战，「对战前」被施加者偷取3个随机「有益状态」（不可驱散，触发后消失）
    jixing_renduanli = BuffTemp(
        "jixing",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.battle_with_caster),
                partial(Effects.stolen_self_benefit_buff_by_caster, 3),
            )
        ],
    )

    # 寒岚	其他	不可驱散	不可扩散	不可偷取	使用冰属相绝学攻击时提高10%法穿（使用冰属相绝学后移除）。
    hanlan = BuffTemp(
        "hanlan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.skill_is_certain_element, "WATER"),
                {ma.magic_penetration_percentage: 10},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.skill_is_certain_element, "WATER"),
                partial(Effects.remove_actor_certain_buff, "hanlan"),
            )
        ],
    )

    # 封劲	有害	可驱散	可扩散	可偷取	主动绝学射程-1
    fengjin = BuffTemp(
        "fengjin",
        BuffTypes.Harm,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.active_skill_range: -1})],
        [],
    )

    # 封咒	有害	可驱散	可扩散	不可偷取	无法使用主动「绝学」
    fengzhou = BuffTemp(
        "fengzhou",
        BuffTypes.Harm,
        True,
        True,
        False,
        [ModifierEffect(RS.always_true, {ma.is_active_skill_disabled: True})],
        [],
    )

    # 封穴	有害	可驱散	可扩散	不可偷取	无法发动「连击」「追击」和「闪避」
    fengxue = BuffTemp(
        "fengxue",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.is_double_attack_disabled: True,
                    ma.is_chase_attack_disabled: True,
                    ma.is_dodge_disabled: True,
                },
            )
        ],
        [],
    )

    # 封缄	有害	可驱散	可扩散	可偷取	范围绝学的范围-1
    fengjian = BuffTemp(
        "fengjian",
        BuffTypes.Harm,
        True,
        True,
        True,
        [ModifierEffect(RS.always_true, {ma.range_skill_range: -1})],
        [],
    )

    # 封脉	有害	可驱散	可扩散	不可偷取	所有被动「绝学」失效
    fengmai = BuffTemp(
        "fengmai",
        BuffTypes.Harm,
        True,
        True,
        False,
        [ModifierEffect(RS.always_true, {ma.is_passives_skill_disabled: True})],
    )

    # 屠戮	其他	不可驱散	不可扩散	不可偷取	无法护卫队友，主动攻击「对战后」造成1次「固定伤害」（物攻的50%）若目标气血低于50%，则本次「固定伤害」翻倍（下一次主动攻击「对战后」触发消耗）
    tulu = BuffTemp(
        "tulu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_protect_range: 0, ma.magic_protect_range: 0},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.add_fixed_damage_with_physical_attack, 0.5),
            ),
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.LifeChecks.target_life_is_below, 50),
                partial(Effects.add_fixed_damage_with_physical_attack, 0.5),
            ),
        ],
    )

    # 巨影	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战中」免伤提高15%，且「对战后」恢复自身气血（恢复量为本次伤害的50%）（不可驱散）
    juying = BuffTemp(
        "juying",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacker),
                {ma.battle_damage_reduction_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.heal_self, 0.5),
            )
        ],
    )

    # 幽煌邪焰	其他	不可驱散	不可扩散	不可偷取	除气血外所有属性提高10%
    youhuangxieyan = BuffTemp(
        "youhuangxieyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 10,
                    ma.magic_attack_percentage: 10,
                    ma.defense_percentage: 10,
                    ma.magic_defense_percentage: 10,
                    ma.luck_percentage: 10,
                },
            )
        ],
        [],
    )

    # 幽阙	有害	不可驱散	不可扩散	不可偷取	无法获得治疗（无法驱散）
    youque = BuffTemp(
        "youque",
        BuffTypes.Harm,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_heal_disabled: True})],
        [],
    )

    # 幽魂	其他	不可驱散	不可扩散	不可偷取	移动力+1，行动时无视敌方角色阻挡（不可驱散
    youhun = BuffTemp(
        "youhun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: 1, ma.is_ignore_block: True},
            )
        ],
        [],
    )

    # 异心	其他	不可驱散	不可扩散	不可偷取	3格内每有1名其他友方行动结束时携带者受到1次「固定伤害」（当前气血的30%）并获得1个随机「有害状态」（不可驱散）
    yixin = BuffTemp(
        "yixin",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(
                    Effects.receive_fixed_damage_by_current_life_percentage,
                    0.3,
                ),
            ),
            EventListener(
                EventTypes.partner_action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.add_self_random_harm_buff, 1),
            ),
        ],
    )

    # 归依	其他	不可驱散	不可扩散	不可偷取	行动结束时，使施加者恢复3格内所有施加者友方的气血（恢复量为施加者法攻的0.5倍）并施加1个随机「有益状态」（不可驱散）
    guiyi = BuffTemp(
        "guiyi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(
                    Effects.heal_partner_and_add_benefit_buff_by_caster, 0.5
                ),
            ),
        ],
    )

    # 影遁	其他	不可驱散	不可扩散	不可偷取	伤害和暴击率提高12%，无法被敌人普通攻击及绝学锁定为目标（遭受1次范围伤害或造成伤害后，或行动结束时，自身2格范围内存在敌人时，该状态消失）
    yingdun = BuffTemp(
        "yingdun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 12,
                    ma.magic_damage_percentage: 12,
                    ma.critical_percentage: 12,
                    ma.is_non_selectable: True,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.under_skill_end,
                1,
                partial(RS.skill_is_range_target_damage),
                partial(Effects.remove_actor_certain_buff, "yingdun"),
            ),
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "yingdun"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.enemy_in_range_count_bigger_than, 2, 1),
                partial(Effects.remove_actor_certain_buff, "yingdun"),
            ),
        ],
    )

    # 御敌	其他	不可驱散	不可扩散	不可偷取	每层伤害、免伤+15%（上限4层）, 「御敌」状态消失时，以3格范围内物攻/法攻最高的敌人为中心，对其2格范围内所有敌方造成1次「固定伤害」伤害（最大气血的12%），并施加1层「燃烧」状态，持续2回合。。
    yudi = BuffTemp(
        "yudi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 15,
                    ma.magic_damage_percentage: 15,
                    ma.physical_damage_reduction_percentage: 15,
                    ma.magic_damage_reduction_percentage: 15,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.lose_buff_end,
                1,
                RS.always_true,
                partial(Effects.take_effect_of_yudi),
            ),
        ],
        3,
    )

    # 御火	其他	不可驱散	不可扩散	不可偷取	火属相免伤80%，受到攻击后消失。
    yuhuo = BuffTemp(
        "yuhuo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacked_by_fire_element),
                {
                    ma.magic_damage_reduction_percentage: 80,
                    ma.physical_damage_reduction_percentage: 80,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "yuhuo"),
            )
        ],
    )

    # 心莲	其他	不可驱散	不可扩散	不可偷取	免伤+30%，状态消失时恢复自身气血（恢复量为施术者法攻的0.7倍）受到伤害后消失。
    xinlian = BuffTemp(
        "xinlian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.magic_damage_reduction_percentage: 30,
                    ma.physical_damage_reduction_percentage: 30,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "xinlian"),
            ),
            EventListener(
                EventTypes.lose_buff_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_caster_magic_attack, 0.7),
            ),
        ],
    )

    # 忘时	有害	不可驱散	不可扩散	不可偷取	行动结束时，自身1个初始冷却时间最长地伤害绝学冷却时间+1（不可驱散）
    wangshi = BuffTemp(
        "wangshi",
        BuffTypes.Harm,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.increase_self_loongest_skill_cooldown, 1),
            )
        ],
    )

    # 怒意	其他	不可驱散	不可扩散	不可偷取	除气血外全属性提高10%
    nuyi = BuffTemp(
        "nuyi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 10,
                    ma.magic_attack_percentage: 10,
                    ma.defense_percentage: 10,
                    ma.magic_defense_percentage: 10,
                    ma.luck_percentage: 10,
                },
            )
        ],
        [],
    )

    # 怒火	有益	不可驱散	不可扩散	不可偷取	物攻提高30%，主动攻击「对战后」自身所有主动绝学冷却时间-1
    nuhuo = BuffTemp(
        "nuhuo",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 30,
                },
            )
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.reduce_self_all_skill_cooldown, 1),
            )
        ],
    )

    # 怯懦	其他	不可驱散	不可扩散	不可偷取	除气血外全属性降低20%，遭受鲜于超主动攻击「对战中」受到伤害提升20%，且无法反击
    qienou = BuffTemp(
        "qienou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: -20,
                    ma.magic_attack_percentage: -20,
                    ma.defense_percentage: -20,
                    ma.magic_defense_percentage: -20,
                    ma.luck_percentage: -20,
                },
            ),
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "xianyuchao"),
                {
                    ma.physical_damage_reduction_percentage: -20,
                    ma.magic_damage_reduction_percentage: -20,
                    ma.is_counterattack_disabled: True,
                },
            ),
        ],
        [],
    )

    # 怵惕	其他	不可驱散	不可扩散	不可偷取	每层物理伤害、暴击率-20%，携带者主动攻击后，叠加1层（上限3层，不可驱散）。
    chuti = BuffTemp(
        "chuti",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: -20,
                    ma.critical_percentage: -20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.increase_actor_certain_buff_stack, "chuti"),
            )
        ],
        3,
    )

    # 恩念	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战后」自身受到1次「固定伤害」（当前气血的50%）（不可驱散）
    ennian = BuffTemp(
        "ennian",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(
                    Effects.receive_fixed_damage_by_current_life_percentage,
                    0.5,
                ),
            )
        ],
    )

    # 惶乱	有害	不可驱散	不可扩散	不可偷取	遭受攻击受到暴击后，获得1个随机「有害状态」，并对施加者施加1个随机「有益状态」（不可驱散）
    huangluan = BuffTemp(
        "huangluan",
        BuffTypes.Harm,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.under_critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.add_self_random_harm_buff, 1),
            ),
            EventListener(
                EventTypes.under_critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.add_self_random_harm_buff, 1),
            ),
        ],
    )

    # 愈合	有益	可驱散	可扩散	可偷取	「对战后」恢复15%气血
    yuhe = BuffTemp(
        "yuhe",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, 0.15),
            )
        ],
    )

    # 愤怒	其他	不可驱散	不可扩散	不可偷取	射程+2，除气血外全属性提升20%
    fennv = BuffTemp(
        "fennv",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.life_percentage: 20,
                    ma.attack_percentage: 20,
                    ma.magic_attack_percentage: 20,
                    ma.defense_percentage: 20,
                    ma.magic_defense_percentage: 20,
                    ma.luck_percentage: 20,
                    ma.attack_range: 2,
                },
            )
        ],
        [],
    )

    # 执剑	其他	不可驱散	不可扩散	不可偷取	遭受非飞行角色攻击时，「对战前」夺取敌方1个「有益状态」，「对战中」免伤和暴击抗性提高15%
    zhijian = BuffTemp(
        "zhijian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attacked_by_non_flyer),
                {
                    ma.battle_damage_reduction_percentage: 15,
                    ma.suffer_critical_damage_reduction_percentage: 15,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacked_by_non_flyer),
                partial(Effects.steal_target_benefit_buff, 1),
            )
        ],
    )

    # 执念	其他	不可驱散	不可扩散	不可偷取	伤害+4%，暴击率+4%（上限4层）
    zhinian = BuffTemp(
        "zhinian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 4,
                    ma.magic_damage_percentage: 4,
                    ma.critical_percentage: 4,
                },
            ),
        ],
        [],
        4,
    )

    # 护佑	其他	不可驱散	不可扩散	不可偷取	双防+20%，遭受暴击后恢复30%气血
    huyou = BuffTemp(
        "huyou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.defense_percentage: 20, ma.magic_defense_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.under_critical_damage_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, 0.3),
            )
        ],
    )

    # 护卫	其他	不可驱散	不可扩散	不可偷取	代替相邻2格距离的队友承受攻击（不可驱散）
    huwei = BuffTemp(
        "huwei",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_protect_range: 2, ma.magic_protect_range: 2},
            ),
        ],
        [],
    )

    # 护法	其他	不可驱散	不可扩散	不可偷取	法术免伤提高20%，代替2格内友方承受法术攻击（「对战后」消失）
    hufa = BuffTemp(
        "hufa",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 20, ma.magic_protect_range: 2},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "hufa"),
            )
        ],
    )

    # 报怒	其他	不可驱散	不可扩散	不可偷取	移除「空性」状态，伤害+20%，克制攻击加成+15%，移动力+1（不可驱散）
    baonu = BuffTemp(
        "baonu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 20,
                    ma.magic_damage_percentage: 20,
                    ma.move_range: 1,
                },
            ),
            ModifierEffect(
                partial(RS.attack_to_advantage_elements),
                {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15},
            ),
        ],
        [
            EventListener(
                EventTypes.action_start,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "kongxing"),
            )
        ],
    )

    # 担因	其他	不可驱散	不可扩散	不可偷取	物理免伤+20%，代替2格内友方承受1次物攻（「对战后」消失）
    danyin = BuffTemp(
        "danyin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_reduction_percentage: 20,
                    ma.physical_protect_range: 2,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.remove_actor_certain_buff, "danyin"),
            )
        ],
    )

    # 持旗	其它	不可偷取	不可偷取	不可偷取	相邻1格内开启「限制区域」：敌方移动 力消耗+1。主动攻击前驱散敌方1个「有益状态」，并施加「燃烧」状态，持续2 回合。
    chiqi = BuffTemp(
        "chiqi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 障眼I	有害	可驱散	可扩散	不可偷取	会心-30%
    zhangyan = BuffTemp(
        "zhangyan",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.luck_percentage: -30},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.luck_percentage: -35},
                ),
            ],
        ],
        [],
    )

    # 雷劫	其他	不可驱散	不可扩散	不可偷取	行动结束时，如果自身菱形2格内有其它友方单位，则将「雷劫」替换为「晕眩」，持续1回合。
    leijie = BuffTemp(
        "leijie",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.replace_self_buff, "leijie", "yunxuan", 1),
            ),
        ],
    )

    # 雷场	其他	不可驱散	不可扩散	不可偷取	遭受暴击概率+20%
    leichang = BuffTemp(
        "leichang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.suffer_critical_percentage: 20},
            ),
        ],
        [],
    )

    # 挽弓	其他	不可驱散	不可扩散	不可偷取	伤害提高20%，射程+1（不可驱散，主动使用伤害绝学后消耗）
    wangong = BuffTemp(
        "wangong",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 20, ma.attack_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_attack_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "wangong"),
            )
        ],
    )

    # 探敌	其他	不可驱散	不可扩散	不可偷取	移动力+1，主动攻击造成伤害时为施加者增加1层「御敌」状态，持续1回合，且施加者立刻触发1次天赋的「御敌」效果（每回合最多触发1次）
    tandi = BuffTemp(
        "tandi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_tandi),
            ),
        ],
    )

    # 撕裂	有害	可驱散	不可扩散	不可偷取	行动结束时，遭受1次伤害（施加者物攻的70%，上限7层，期间受到施加者的攻击伤害，可叠加1层，无法扩散）
    silie = BuffTemp(
        "silie",
        BuffTypes.Harm,
        True,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_caster_physical_attack, 0.7
                ),
            ),
            EventListener(
                EventTypes.under_damage_end,
                1,
                partial(RS.attacked_by_caster),
                partial(Effects.increase_actor_certain_buff_stack, "silie"),
            ),
        ],
        7,
    )

    # 断步I	有害	不可驱散	不可扩散	不可偷取	移动力上限变为4（不可驱散）
    # 断步II	有害	不可驱散	不可扩散	不可偷取	移动力上限变为3（不可驱散）
    duanbu = BuffTemp(
        "duanbu",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.max_move_range: 4},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.max_move_range: 3},
                ),
            ],
        ],
        [],
    )

    # 断筋	有害	不可驱散	不可扩散	不可偷取	受治疗效果降低30%，无法触发再移动和自身赋予的再行动（不可驱散）
    duanjin = BuffTemp(
        "duanjin",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.be_healed_percentage: -30,
                    ma.is_extra_move_disabled: True,
                    ma.is_extra_action_disabled: True,
                },
            ),
        ],
        [],
    )

    # 断骨	有害	不可驱散	不可扩散	不可偷取	无法护卫，无法使用主动「绝学」
    duangu = BuffTemp(
        "duangu",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.is_active_skill_disabled: True,
                    ma.physical_protect_range: 0,
                    ma.magic_protect_range: 0,
                },
            ),
        ],
        [],
    )

    # 施咒	其他	不可驱散	不可扩散	不可偷取	其他友方在自身2格范围内发起对战，且优先攻击时，则为其施加「神睿」「御魔」状态，持续1回合（每回合只能触发1次）(领域)
    shizhou = BuffTemp(
        "shizhou",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 旖梦香	其他	不可驱散	不可扩散	不可偷取	伤害提升8%，达到3层时，绝学射程+1（上限3层）
    yimengxiang = BuffTemp(
        "yimengxiang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(RS.BuffChecks.buff_stack_bigger_than, 3),
                {ma.range_skill_range: 1},
            ),
        ],
        [],
    )

    # 无忧域	其他	不可驱散	不可扩散	不可偷取	免疫「晕眩」，且施术者自身反击射程+1（不可驱散）
    wuyouyu = BuffTemp(
        "wuyouyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.counterattack_range: 1},
            ),
        ],
        [],
    )

    # 无摧·天玑印	有益	不可驱散	不可扩散	不可偷取	免疫所有「有害状态」，获得来自施加者触发的天赋效果（不可复制，不可偷取，不可驱散）
    wucui_tianjiyin = BuffTemp(
        "wucui_tianjiyin",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 3, 3),
                {ma.magic_attack_percentage: 6},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.take_effect_of_tianjiyin),
            )
        ],
    )

    # 无摧·封劲	有害	不可驱散	不可扩散	不可偷取	主动绝学射程-1（不可驱散）
    wucui_fengjin = BuffTemp(
        "wucui_fengjin",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.range_skill_range: -1},
            ),
        ],
        [],
    )

    # 无摧·迟缓III	有害	不可驱散	不可扩散	不可偷取	移动力-3，无法护卫（无法驱散）
    wucui_chihuan = BuffTemp(
        "wucui_chihuan",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: -3,
                    ma.physical_protect_range: 0,
                    ma.magic_protect_range: 0,
                },
            ),
        ],
        [],
    )

    # 无法反击	其他	不可驱散	不可扩散	不可偷取	无法反击类状态包含：「压制」「麻痹」「晕眩」「禁闭」
    wufafanji = BuffTemp(
        "wufafanji",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_counterattack_disabled: True},
            ),
        ],
        [],
    )

    # 无瑕I	有益	可驱散	可扩散	可偷取	遭受暴击-20%
    wuxia = BuffTemp(
        "wuxia",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.suffer_critical_percentage: -20},
                ),
                [
                    ModifierEffect(
                        RS.always_true,
                        {ma.suffer_critical_percentage: -25},
                    ),
                ],
            ],
        ],
        [],
    )

    # 无觉	有益	可驱散	不可扩散	不可偷取	携带的「有害状态」（仅限满足可驱散）无效。遭受3格内敌人的攻击后，将自身1个「有害状态」转移给攻击者。
    wujue = BuffTemp(
        "wujue",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.transfer_self_harm_buff_to_attacker),
            )
        ],
    )

    # 无摧·无觉	有益	不可驱散	不可扩散	不可偷取	携带的「有害状态」（仅限满足可驱散的）无效。遭受3格内敌人的攻击后，将自身1个「有害状态」转移给攻击者。
    wucui_wujue = BuffTemp(
        "wucui_wujue",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.PositionChecks.in_range, 3),
                partial(Effects.transfer_self_harm_buff_to_attacker),
            )
        ],
    )

    # 昌明	其他	不可驱散	不可扩散	不可偷取	每层法攻提高5%，携带2层及以上时，免疫「封咒」状态且绝学射程+1（上限4层）
    changming = BuffTemp(
        "changming",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_attack_percentage: 5},
            ),
            ModifierEffect(
                partial(RS.BuffChecks.buff_stack_bigger_than, 2),
                {ma.range_skill_range: 1, ma.single_skill_range: 1},
            ),
        ],
        [],
        4,
    )

    # 星狩	其他	不可驱散	不可扩散	不可偷取	射程和绝学范围+2，无法移动，使用绝学后为2格范围气血最低的1个友方恢复气血（恢复量为施术者物攻的0.7倍）。
    xingshou = BuffTemp(
        "xingshou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.range_skill_range: 2,
                    ma.single_skill_range: 2,
                    ma.attack_range: 2,
                    ma.max_move_range: 0,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(
                    Effects.heal_least_partner_health_by_physical_attack_in_range,
                    0.7,
                    2,
                ),
            ),
        ],
    )

    # 星蚀	其他	不可驱散	不可扩散	不可偷取	无法使用「星垂平野」
    xingshi = BuffTemp(
        "xingshi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_certain_skill_disabled: ["xingchuipingye"]},
            ),
        ],
        [],
    )

    # 晕眩	有害	可驱散	可扩散	不可偷取	无法行动，且在对战中无法进行反击。
    yunxuan = BuffTemp(
        "yunxuan",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_action_disabled: True, ma.is_counterattack_disabled: True},
            ),
        ],
        [],
    )

    # 暗引	其他	不可驱散	不可扩散	不可偷取	遭受攻击受到伤害后立刻恢复施加者和攻击者该次伤害数值30%的气血。
    anyin = BuffTemp(
        "anyin",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_and_caster_damage, 0.3),
            ),
        ],
    )

    # 暗流	有益	不可驱散	不可扩散	不可偷取	主动攻击后，恢复自身气血（恢复量为施术者法攻的0.4倍）并将自身1个「有害状态」转移给白复归。
    anliu = BuffTemp(
        "anliu",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_and_transfer_self_harm_buff, 0.4),
            ),
        ],
    )

    # 暗铠	有益	可驱散	可扩散	可偷取	受到克制伤害降低20%，受到伤害后，40%概率对攻击者施加1个随机「有害状态」（受到伤害后消耗）
    ankai = BuffTemp(
        "ankai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(Effects.add_attacker_random_harm_buff_with_probability, 1, 0.4),
            ),
        ],
    )

    # 暴风眼	其他	不可驱散	不可扩散	不可偷取	伤害和暴击率+5%（最多叠加3层）本回合若释放过绝学，行动结束时对1圈内所有敌人造成0.15倍范围伤害（触发后移除1层）。
    baofengyan = BuffTemp(
        "baofengyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 5,
                    ma.magic_damage_percentage: 5,
                    ma.critical_percentage: 5,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.reduce_actor_certain_buff_stack, "baofengyan", 1),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.self_is_used_active_skill),
                partial(
                    Effects.add_fixed_damage_in_range_by_caster_physical_attack,
                    0.15,
                ),
            ),
        ],
        5,
    )

    # 杳影	其他	不可驱散	不可扩散	不可偷取	「对战中」闪避一次攻击，且只可使用「逐星破日」或普通攻击（触发后移除，无法驱散）
    yaoying = BuffTemp(
        "yaoying",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_dodge_attack: True})],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "yaoying"),
            )
        ],
    )

    # 梦海	其他	不可驱散	不可扩散	不可偷取	自身气血大于等于80%，则遭受范围绝学伤害降低50%（不可驱散，触发后移除）
    menghai = BuffTemp(
        "menghai",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.menghai_requires_check),
                {ma.physical_damage_reduction_percentage: 50, ma.magic_damage_reduction_percentage: 50},
            ),
        ],
        [
            EventListener(
                EventTypes.under_skill_end,
                1,
                partial(RS.menghai_requires_check),
                partial(Effects.remove_actor_certain_buff, "menghai"),
            ),
        ],
    )

    # 梵天	其他	不可驱散	不可扩散	不可偷取	免伤提高50%，免疫「有害状态」（不可驱散，「对战后」消失，状态消失时驱散2格内所有敌方2个「有益状态」）
    # 梵天·贰	其他	不可驱散	不可扩散	不可偷取	免伤提高50%，免疫「有害状态」（「对战后」消失，状态消失时反转3格内所有敌方2个「有益状态」并降低2点气力）
    fantian = BuffTemp(
        "fantian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_reduction_percentage: 50,
                        ma.magic_damage_reduction_percentage: 50,
                    },
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {
                        ma.physical_damage_reduction_percentage: 50,
                        ma.magic_damage_reduction_percentage: 50,
                    },
                ),
            ],
        ],
        [
            [
                EventListener(
                    EventTypes.battle_end,
                    1,
                    RS.always_true,
                    partial(Effects.remove_actor_certain_buff, "fantian"),
                ),
                EventListener(
                    EventTypes.battle_end,
                    1,
                    RS.always_true,
                    partial(Effects.remove_target_harm_buffs_in_range, 2, 2),
                ),
            ],
            [
                EventListener(
                    EventTypes.battle_end,
                    1,
                    RS.always_true,
                    partial(Effects.remove_actor_certain_buff, "fantian"),
                ),
                EventListener(
                    EventTypes.battle_end,
                    1,
                    RS.always_true,
                    partial(Effects.reverse_target_benefit_buffs_in_range, 3, 2),
                ),
                EventListener(
                    EventTypes.battle_end,
                    1,
                    RS.always_true,
                    partial(Effects.reduce_target_energy_in_range, 2, 2),
                ),
            ],
        ],
    )

    # 止歌	其他	不可驱散	不可扩散	不可偷取	法术免伤+10%，代替2格内友方承受法术攻击（「对战后」消失）
    zhige = BuffTemp(
        "zhige",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 10, ma.magic_protect_range: 2},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.PositionChecks.in_range, 2),
                partial(Effects.remove_actor_certain_buff, "zhige"),
            )
        ],
    )

    # 死灭印记	其他	不可驱散	不可扩散	不可偷取	受到治疗效果减少50%。行动结束时，遭受1次「固定伤害」（自身最大气血*8%+已损失气血*20%）（不可驱散）
    simieyinji = BuffTemp(
        "simieyinji",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.be_healed_percentage: -50},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_with_maxlife_and_losslife,
                    0.08,
                    0.2,
                ),
            ),
        ],
    )

    # 残蛊	其他	不可驱散	不可扩散	不可偷取	对友方使用绝学后施加「逆阙」状态，持续1回合，触发后移除。
    cangu = BuffTemp(
        "cangu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_for_partner_end,
                1,
                RS.always_true,
                partial(Effects.add_buffs, ["nique"], 1),
            ),
            EventListener(
                EventTypes.skill_for_partner_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "cangu"),
            ),
        ],
    )

    # 气劲	其他	不可驱散	不可扩散	不可偷取	回合结束时，如果携带4层「气劲」，则消耗所有「气劲」对自身2格范围内1个敌人施加「晕眩」状态，持续1回合。
    qijin = BuffTemp(
        "qijin",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.BuffChecks.buff_stack_bigger_than, 4),
                partial(Effects.take_effect_of_qijin),
            ),
        ],
    )

    # 污秽	有害	可驱散	可扩散	不可偷取	无法获得任何有益状态
    wuhui = BuffTemp(
        "wuhui",
        BuffTypes.Harm,
        True,
        True,
        False,
        [],
        [],
    )

    # 沐春风	其他	不可驱散	不可扩散	不可偷取	免疫所有「有害状态」，且行动结束时，位于施加者2格范围内，驱散2个「有害状态」，并恢复自身50%最大气血
    # 沐春风·壹	其他	不可驱散	不可扩散	不可偷取	免疫所有「有害状态」，且行动结束时，位于施加者3格范围内，驱散2个「有害状态」，并恢复自身50%最大气血
    # 沐春风·贰	其他	不可驱散	不可扩散	不可偷取	免疫所有「有害状态」，且行动结束时，位于施加者3格范围内，驱散2个「有害状态」，获得2个随机「有益状态」，并恢复自身50%最大气血
    muchunfeng = BuffTemp(
        "muchunfeng",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            [
                EventListener(
                    EventTypes.action_end,
                    1,
                    partial(RS.PositionChecks.in_range, 2),
                    partial(Effects.heal_self_and_remove_harm_buffs, 0.5),
                )
            ],
            [
                EventListener(
                    EventTypes.action_end,
                    1,
                    partial(RS.PositionChecks.in_range, 3),
                    partial(Effects.heal_self_and_remove_harm_buffs, 0.5),
                )
            ],
            [
                EventListener(
                    EventTypes.action_end,
                    1,
                    partial(RS.PositionChecks.in_range, 3),
                    partial(Effects.heal_self_and_remove_harm_buffs, 0.5),
                ),
                EventListener(
                    EventTypes.action_end,
                    1,
                    partial(RS.PositionChecks.in_range, 3),
                    partial(Effects.add_partner_benefit_buffs, 2, 2),
                ),
            ],
        ],
    )

    # 沐音	其他	不可驱散	不可扩散	不可偷取	法术免伤+20%，遭受法术攻击后恢复30％气血
    muyin = BuffTemp(
        "muyin",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.under_magic_damage_end,
                1,
                RS.always_true,
                partial(Effects.heal_self, 0.3),
            ),
        ],
    )

    # 法力	其他	不可驱散	不可扩散	不可偷取	每层法攻提升4%，携带3层及以上时，移动力+1（上限5层，不可驱散）
    fali = BuffTemp(
        "fali",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_attack_percentage: 4},
            ),
            ModifierEffect(
                partial(RS.BuffChecks.buff_stack_bigger_than, 3),
                {ma.move_range: 1},
            ),
        ],
        [],
    )

    # 活血	有益	可驱散	可扩散	可偷取	物攻，物防额外+20%
    huoxue = BuffTemp(
        "huoxue",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 20, ma.defense_percentage: 20},
            ),
        ],
        [],
    )

    # 流火	其他	不可驱散	不可扩散	不可偷取	物攻和暴击率+20%
    liuhuo = BuffTemp(
        "liuhuo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 20, ma.critical_percentage: 20},
            ),
        ],
        [],
    )

    # 流血	有害	可驱散	可扩散	不可偷取	行动结束时，遭受1次「固定伤害」（施加者物攻的30%）
    liuxue = BuffTemp(
        "liuxue",
        BuffTypes.Harm,
        True,
        True,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_caster_physical_attack,
                    0.3,
                ),
            ),
        ],
    )

    # 浊尘	其他	不可驱散	不可扩散	不可偷取	2格内的敌人主动释放技能前，使其2个「有益状态」变为随机「有害状态」，获得或刷新「遁地」状态时该状态持续回合数刷新至2回合。
    zhuochen = BuffTemp(
        "zhuochen",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 涅槃	有益	可驱散	可偷取	可扩散	「对战前」恢复自身气血（恢复量为施术者法攻*0.5）
    niepan = BuffTemp(
        "niepan",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_caster_magic_attack, 0.5),
            ),
        ],
    )

    # 清流	有益	可驱散	不可扩散	不可偷取	受到来自敌方的主动攻击伤害后消失，驱散1个「有害状态]，并恢复气血（恢复量为施术者法攻的0.4倍），生效后立刻为2格范围内1个气血百分比最低的其他友方驱散1个「有害状态」，并恢复气血(恢复量为施术者法攻的0.4倍)
    # 携带「清流」状态的友方受治疗效果增加15%
    qingliu = BuffTemp(
        "qingliu",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.be_healed_percentage: 15})
        ],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(Effects.take_effect_of_qingliu),
            ),
        ],
    )

    # 激怒	其他	不可驱散	不可扩散	不可偷取	除气血外全属性提升10%，移动力+1，攻击「殷千炀」触发其免死者死亡后移除。
    jinu = BuffTemp(
        "jinu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 10,
                    ma.defense_percentage: 10,
                    ma.magic_attack_percentage: 10,
                    ma.magic_defense_percentage: 10,
                    ma.luck_percentage: 10,
                    ma.move_range: 1,
                },
            ),
        ],
        [],
    )

    # 激荡	其他	不可驱散	不可扩散	不可偷取	克制攻击加成额外提升20%
    jidang = BuffTemp(
        "jidang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.element_attacker_multiplier: 0.2},
            ),
        ],
        [],
    )

    # 火佑	其他	不可驱散	不可扩散	不可偷取	炎属相免伤提升30%，遭受炎属相攻击后消失。
    huoyou = BuffTemp(
        "huoyou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_target_by_fire_element),
                {
                    ma.magic_damage_reduction_percentage: 30,
                    ma.physical_damage_reduction_percentage: 30,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                partial(RS.is_target_by_fire_element),
                partial(Effects.remove_actor_certain_buff, "huoyou"),
            ),
        ],
    )

    # 灭道	其他	不可驱散	不可扩散	不可偷取	免伤提高20%，受到攻击时，自身无视「克制」伤害（不可驱散，遭受攻击后消耗）
    miedao = BuffTemp(
        "miedao",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.magic_damage_reduction_percentage: 20,
                    ma.physical_damage_reduction_percentage: 20,
                },
            ),
            ModifierEffect(
                partial(RS.is_attack_target),
                {
                    ma.ignore_element_advantage: True,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "miedao"),
            ),
        ],
    )

    # 灵动	其他	不可驱散	不可扩散	不可偷取	造成伤害提升24%
    lingdong = BuffTemp(
        "lingdong",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 24, ma.magic_damage_percentage: 24},
            ),
        ],
        [],
    )

    # 灵风	有益	可驱散	不可扩散	不可偷取	移动力+1，可跨越障碍，免疫「移动力降低」。
    lingfeng = BuffTemp(
        "lingfeng",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: 1, ma.is_ignore_obstacle: True},
            ),
        ],
        [],
    )

    # 炎浴	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战后」，恢复伤害数值50%的气血，驱散自身2个「有害状态」。
    yanyu = BuffTemp(
        "yanyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.heal_self_by_damage, 0.5),
            ),
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_self_harm_buffs, 2),
            ),
        ],
    )

    # 炎狱	其他	不可驱散	不可扩散	不可偷取	3格范围内所有敌方主动攻击「对战前」驱散其1个「有益状态」，并施加「燃烧」状态，持续2回合。
    yanyu1 = BuffTemp(
        "yanyu1",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 炎铠	有益	可驱散	可扩散	可偷取	被攻击「对战前」自身恢复20%气血，并对目标驱散1个「有益状态」（对战后消耗）
    yankai = BuffTemp(
        "yankai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_battle_attack_target),
                partial(Effects.heal_self, 0.2),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_battle_attack_target),
                partial(Effects.remove_target_benefit_buffs, 1),
            ),
        ],
    )

    # 焚炎	有益	可驱散	可扩散	可偷取	受到来自敌方的主动攻击伤害后消失，恢复自身气血（恢复量为施术者0.5倍法攻）并对菱形2格敌人造成1次「固定伤害」（施术者法攻*0.4）
    fanyan = BuffTemp(
        "fanyan",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.under_damage_end,
                1,
                partial(RS.is_attack_target),
                partial(Effects.heal_self_by_caster_magic_attack, 0.5),
            ),
            EventListener(
                EventTypes.under_damage_end,
                1,
                RS.always_true,
                partial(
                    Effects.add_fixed_damage_in_diamond_range_by_caster_magic_attack,
                    2,
                    0.4,
                ),
            ),
        ],
    )

    # 焚狱	其他	不可驱散	不可扩散	不可偷取	使用炎属相绝学攻击后驱散目标1个「有益状态」（使用炎属相绝学后移除）。
    fanyu = BuffTemp(
        "fanyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_certain_element, "Fire"),
                partial(Effects.remove_target_benefit_buffs, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_certain_element, "Fire"),
                partial(Effects.remove_actor_certain_buff, "funyu"),
            ),
        ],
    )

    # 煌烨	其他	不可驱散	不可扩散	不可偷取	伤害提升15%，绝学范围+1（主动使用绝学攻击后移除）
    huangye = BuffTemp(
        "huangye",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 15,
                    ma.magic_damage_percentage: 15,
                    ma.range_skill_range: 1,
                    ma.single_skill_range: 1,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "huangye"),
            ),
        ],
    )

    # 煽动	其他	不可驱散	不可扩散	不可偷取	主动攻击「对战前」对自身2格范围内其他角色施加1个随机「有害状态」，并造成1次法术伤害（施术者法攻30%）（无法驱散）
    shandong = BuffTemp(
        "shandong",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(Effects.add_all_harm_buff_in_range, 1, 2),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(
                    Effects.add_fixed_damage_in_range_by_caster_magic_attack,
                    2,
                    0.3,
                ),
            ),
        ],
    )

    # 燃烧	有害	可驱散	可扩散	不可偷取	行动结束时，损失12%最大气血的固定伤害。（上限2层）
    ranshao = BuffTemp(
        "ranshao",
        BuffTypes.Harm,
        True,
        True,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
               RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_max_life_percentage, 0.12
                ),
            ),
        ],
    )

    # 燃焰	其它	不可驱散	不可扩散	不可偷取	无法获得再行动，护盾获得加成提高50%，行动结束时移除。
    ranyan = BuffTemp(
        "ranyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.shield_percentage: 0.5, ma.is_extra_action_disabled: True},
            ),
        ],
        [],
    )

    # 狂乱	有益	可驱散	不可扩散	不可偷取	物攻提高12%，伤害提高12%
    kuangluan = BuffTemp(
        "kuanglun",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 12,
                    ma.attack_percentage: 12,
                    ma.magic_attack_percentage: 12,
                },
            ),
        ],
        [],
    )

    # 狂意	其他	不可驱散	不可扩散	不可偷取	主动攻击发动「追击」（首击的0.4倍伤害）（主动攻击「对战后」移除）
    kuangyi = BuffTemp(
        "kuangyi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.chase_attack_percentage: 0.4},
            )
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "kuangyi"),
            ),
        ],
    )

    # 狂魔	其他	不可驱散	不可扩散	不可偷取	范围绝学范围提升1，法攻增加10%
    kuangmo = BuffTemp(
        "kuangmo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.range_skill_range: 1, ma.magic_attack_percentage: 10},
            ),
        ],
        [],
    )

    # 玄幽	其他	不可驱散	不可扩散	不可偷取	使用暗属相绝学攻击后对目标施加1个随机「有害状态」（使用暗属相绝学后移除）。
    xuanyou = BuffTemp(
        "xuanyou",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_certain_element, "Dark"),
                partial(Effects.add_target_harm_buffs, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_certain_element, "Dark"),
                partial(Effects.remove_actor_certain_buff, "xuanyou"),
            ),
        ],
    )

    # 王者姿态	其他	不可驱散	不可扩散	不可偷取	反击伤害提高30%且反击射程+1，若攻击者为携带「战引」状态的敌方遭受攻击前获得护盾（最大气血的100%）。自身相邻1格开启「限制区域」：敌方移动力消耗+1。
    wangzhezitai = BuffTemp(
        "wangzhezitai",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.counterattack_damage_percentage: 30,
                    ma.counterattack_range: 1,
                    ma.restrict_area: 1,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.wangzhezitai_requires_check),
                partial(Effects.add_shield, 1),
            )
        ],
    )

    # 生息	其他	不可驱散	不可扩散	不可偷取	免疫敌方造成的「传送」效果，「对战后」恢复气血（恢复量为施术者0.5倍法攻）并驱散1个「有害状态」。
    shengxi = BuffTemp(
        "shengxi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_caster_magic_attack, 0.5),
            ),
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.remove_self_harm_buffs, 1),
            ),
        ],
    )

    # 电流	有害	可驱散	可扩散	不可偷取	遭受暴击率+20%
    dianliu = BuffTemp(
        "dianliu",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.suffer_critical_percentage: 20},
            ),
        ],
        [],
    )

    # 瞬击	其他	不可驱散	不可扩散	不可偷取	近战攻击「对战前」对目标造成1次「固定伤害」（物攻的30%），并反转目标2个「有益状态」为「乱神II」和「断刺I」状态，持续2回合（不可驱散）
    shunji = BuffTemp(
        "shunji",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(
                    Effects.add_fixed_damage_by_caster_physical_attack, 0.3
                ),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(Effects.add_target_harm_buffs, 2),
            ),
        ],
    )

    # 磐石	其他	不可驱散	不可扩散	不可偷取	免疫击退和拉拽，遭受攻击「对战中」免伤提高15%，且反击射程+1（不可驱散）
    panshi = BuffTemp(
        "panshi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_attack_target),
                {
                    ma.is_repelled_disabled: True,
                    ma.physical_damage_reduction_percentage: 15,
                    ma.magic_damage_reduction_percentage: 15,
                    ma.counterattack_range: 1,
                },
            ),
        ],
        [],
    )

    # 祛星	有益	可驱散	可扩散	可偷取	主动攻击「对战后」，若目标存活，消耗状态，对目标及周围菱形2格敌人造成1次「固定伤害」（施术者法攻*0.5）
    quxing = BuffTemp(
        "quxing",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_quxing),
            ),
        ],
    )

    # 祝安	有益	可驱散	可扩散	可偷取	行动结束时，恢复自身气血。（恢复量=施术者法攻*0.3）
    zhuan = BuffTemp(
        "zhuan",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_caster_magic_attack, 0.3),
            ),
        ],
    )

    # 神恩天泽	其他	不可驱散	不可扩散	不可偷取	法攻、暴击率提升6%（上限3层）
    shenentianze = BuffTemp(
        "shenentianze",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_attack_percentage: 6, ma.critical_percentage: 6},
            ),
        ],
        [],
    )

    # 神意	其他	不可驱散	不可扩散	不可偷取	物攻物防提升9%（上限2层）
    shenyi = BuffTemp(
        "shenyi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.attack_percentage: 9, ma.defense_percentage: 9},
            ),
        ],
        [],
    )

    # 神算	其他	不可驱散	不可扩散	不可偷取	其他友方在自身2格范围内对友方目标使用非伤害绝学时，在绝学释放前对其所选目标的2格范围内所有友方驱散1个「有害状态」（每回合只能触发1次）
    shensuan = BuffTemp(
        "shensuan",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_start,
                1,
                partial(RS.skill_is_no_damage_and_target_is_partner),
                partial(Effects.remove_partner_harm_buffs_in_range, 1, 2),
            ),
        ],
    )

    # 禁疗	有害	可驱散	可扩散	不可偷取	无法被治疗。
    jinliao = BuffTemp(
        "jinliao",
        BuffTypes.Harm,
        True,
        True,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_heal_disabled: True},
            ),
        ],
        [],
    )

    # 离间	其他	不可驱散	不可扩散	不可偷取	无法获得「有益状态」，2格范围内每多1个其他友方，伤害降低10%（最多降低30%）（无法驱散）
    lijian = BuffTemp(
        "lijian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 2, 3),
                {
                    ma.physical_damage_reduction_percentage: 10,
                    ma.magic_damage_reduction_percentage: 10,
                },
            ),
        ],
        [],
    )

    # 精准	有益	不可驱散	不可扩散	不可偷取	物理，法术穿透+20%
    jingzhun = BuffTemp(
        "jingzhun",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_penetration_percentage: 20,
                    ma.magic_penetration_percentage: 20,
                },
            ),
        ],
        [],
    )

    # 结党	其他	不可驱散	不可扩散	不可偷取	免疫「有害状态」，遭受攻击时，2格范围内每多1个其他友方时，伤害和免伤提高10%(最多提高30%)（无法驱散）
    jiedang = BuffTemp(
        "jiedang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_partner_count_with_limit, 2, 3),
                {
                    ma.physical_damage_percentage: 10,
                    ma.magic_damage_percentage: 10,
                    ma.physical_penetration_percentage: 10,
                    ma.magic_penetration_percentage: 10,
                },
            ),
        ],
        [],
    )

    # 缀甲·壹	其他	不可驱散	不可扩散	不可偷取	代替2格内友方承受攻击。
    # 缀甲·贰	其他	不可驱散	不可扩散	不可偷取	代替2格内友方承受攻击，遭受攻击「对战前」恢复自身25%气血，驱散1个「有害状态」（每回合触发1次）
    zhuijia = BuffTemp(
        "zhuijia",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.physical_protect_range: 2, ma.magic_protect_range: 2},
                )
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.physical_protect_range: 2, ma.magic_protect_range: 2},
                )
            ],
        ],
        [
            [],
            [
                EventListener(
                    EventTypes.battle_end,
                    1,
                    partial(RS.is_attack_target),
                    partial(Effects.take_effect_of_zhuijia),
                )
            ],
        ],
    )

    # 罔效I	有害	可驱散	可扩散	可偷取	受治疗效果降低20%
    wangxiao = BuffTemp(
        "wangxiao",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.be_healed_percentage: -20},
            ),
        ],
        [],
    )

    # 罡震	其他	不可驱散	不可扩散	不可偷取	遭受攻击「对战前」对自身1圈内所有敌人造成1次「固定伤害」（物防的100%），并对攻击目标施加「封劲」状态，持续1回合。
    gangzhen = BuffTemp(
        "gangzhen",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attack_target),
                partial(
                    Effects.add_fixed_damage_in_range_by_physical_defense,
                    1,
                    1,
                ),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attack_target),
                partial(Effects.add_buffs, ["fengjin"], 1),
            ),
        ],
    )

    # 花火	其他	不可驱散	不可扩散	不可偷取	「花火」：每层提高3%/4%/5%/6%法攻。主动释放绝学后，减少一层「花火」。行动结束时，如果未释放绝学，增加一层「花火」。每当有敌方角色死亡后，刷新至最大层数。（上限4层）
    huahuo = BuffTemp(
        "huahuo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.BuffChecks.huahuo_stack_count),
                {ma.magic_attack_percentage: 3},
            )
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "huahuo"),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.increase_actor_certain_buff_stack, "huahuo"),
            ),
            EventListener(
                EventTypes.hero_death,
                1,
                RS.always_true,
                partial(Effects.increase_actor_certain_buff_max_stack, "huahuo"),
            ),
        ],
    )

    # 苦咒	其他	不可驱散	不可扩散	不可偷取	法术穿透提高20%，造成伤害后，对目标施加1个随机「有害状态」（不可驱散）
    kuzhou = BuffTemp(
        "kuzhou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_penetration_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.add_target_harm_buffs, 1),
            ),
        ],
    )

    # 蓄劲	其他	不可驱散	不可扩散	不可偷取	暴击率提升20%（可叠加，主动攻击触发暴击后移除）
    xujin = BuffTemp(
        "xujin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.critical_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "xujin"),
            ),
        ],
    )

    # 蓄电	有益	可驱散	可扩散	可偷取	暴击率+30%（暴击后消耗）
    xudian = BuffTemp(
        "xudian",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.critical_percentage: 30},
            ),
        ],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "xudian"),
            ),
        ],
    )

    # 虚弱	其他	不可驱散	不可扩散	不可偷取	无法使用主动绝学
    xuruo = BuffTemp(
        "xuruo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_active_skill_disabled: True},
            ),
        ],
        [],
    )

    # 虚梦之境	其他	不可驱散	不可扩散	不可偷取	敌方无法触发再移动和自身赋予的再行动，且使用伤害绝学后若处于范围内，获得「幻梦」状态，持续1回合。
    xumengzhijing = BuffTemp(
        "xumengzhijing",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 蛇毒	其他	可驱散	可扩散	可偷取	行动结束时，损失20%气血
    shedu = BuffTemp(
        "shedu",
        BuffTypes.Others,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_max_life_percentage, 0.2
                ),
            ),
        ],
    )

    # 蜕皮	其他	不可驱散	不可扩散	不可偷取	全属性提高5%（上限4层）
    tuipi = BuffTemp(
        "tuipi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.life_percentage: 5,
                    ma.attack_percentage: 5,
                    ma.defense_percentage: 5,
                    ma.magic_attack_percentage: 5,
                    ma.magic_defense_percentage: 5,
                    ma.luck_percentage: 5,
                },
            ),
        ],
        [],
        4,
    )

    # 血咒	其他	不可驱散	不可扩散	不可偷取	伤害和免伤提高20%，「对战后」恢复伤害数值50%的气血。行动结束时，损失自身当前气血25%。
    xuezhou = BuffTemp(
        "xuezhou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: 20,
                    ma.magic_damage_percentage: 20,
                    ma.physical_damage_reduction_percentage: 20,
                    ma.magic_damage_reduction_percentage: 20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_damage, 0.5),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_current_life_percentage,
                    0.25,
                ),
            ),
        ],
    )

    # 血契	其他	不可驱散	不可扩散	不可偷取	胧夜遭受攻击后未死亡则对其造成损失气血同等伤害（无法免疫，不可驱散）
    xueqi = BuffTemp(
        "xueqi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.attack_certain_hero, "longye"),
                partial(Effects.take_effect_of_xueqi),
            ),
        ],
    )

    # 血魂	其他	不可驱散	不可扩散	不可偷取	胧夜主动攻击「对战前」对所有携带「血魂」状态的敌方造成1次法术伤害（施术者法攻的40%）
    xuehun = BuffTemp(
        "xuehun",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(
                    Effects.add_fixed_damage_in_range_by_caster_magic_attack,
                    2,
                    0.4,
                ),
            ),
        ],
    )

    # 血魂之系	其他	不可驱散	不可扩散	不可偷取	回合开始时，损失自身15%当前气血，攻击「殷千炀」触发其免死者死亡后移除。
    xuehunzhixi = BuffTemp(
        "xuehunzhixi",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_start,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_current_life_percentage,
                    0.15,
                ),
            ),
            EventListener(
                EventTypes.kill_enemy_start,
                1,
                partial(RS.attack_certain_hero, "yinqianyang"),
                partial(Effects.remove_actor_certain_buff, "xuehunzhixi"),
            ),
        ],
    )

    # 血龙壁	其他	不可驱散	不可扩散	不可偷取	无法使用主动绝学，受治疗效果降低50%，无法发动「抵挡致命伤害」的效果。
    xuelongbi = BuffTemp(
        "xuelongbi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.is_active_skill_disabled: True,
                    ma.be_healed_percentage: -50,
                    ma.is_block_fatal_damage_disabled: True,
                },
            ),
        ],
        [],
    )

    # 裂伤	有害	可驱散	可扩散	可偷取	受治疗效果-10%；行动结束时，遭受1次「固定伤害」（施加者物防+法防的20%）。（可驱散、最多共存4个）
    lieshang = BuffTemp(
        "lieshang",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.be_healed_percentage: -10},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(
                    Effects.receive_fixed_damage_by_physical_defense_and_magic_defense,
                    0.2,
                ),
            ),
        ],
    )

    # 警觉	其他	不可驱散	不可扩散	不可偷取	护盾获得加成+50%，暴击率+15%，移动力+1（上限2层）
    jingjue = BuffTemp(
        "jingjue",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.shield_percentage: 0.5,
                    ma.critical_percentage: 15,
                    ma.move_range: 1,
                },
            ),
        ],
        [],
    )

    # 讹心	其他	不可驱散	不可扩散	不可偷取	若携带者行动结束时的「有益状态」大于2个，则携带者至少保留2个「有益状态」并将其余「有益状态」转移至施加者（最多转移6个），且施加者获得1层「心念」状态。
    exin = BuffTemp(
        "exin",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_exin),
            ),
        ],
    )

    # 论道	其他	不可驱散	不可扩散	不可偷取	携带者主动使用绝学后，恢复施加者30%气血并使其获得1个随机「有益状态」。
    lundao = BuffTemp(
        "lundao",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.heal_caster, 0.3),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.add_caster_benefit_buffs, 1),
            ),
        ],
    )

    # 识破	其他	不可驱散	不可扩散	不可偷取	若攻击前移动距离大于1格，则伤害、暴击率降低20%。
    shipo = BuffTemp(
        "shipo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.move_more_than, 1),
                {ma.physical_damage_percentage: -20, ma.critical_percentage: -20},
            ),
        ],
        [],
    )

    # 豪侠	其他	不可驱散	不可扩散	不可偷取	「对战中」伤害提高15%，遭受近战攻击「对战前」发动「先攻」（每回合发动1次）（不可驱散）
    haoxia = BuffTemp(
        "haoxia",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.is_in_battle),
                {
                    ma.physical_damage_percentage: 15,
                    ma.magic_damage_percentage: 15,
                    ma.is_counterattack_first: True,
                },
            ),
            ModifierEffect(
                partial(RS.attacked_by_melee_attack),
                {
                    ma.is_counterattack_first: True,
                },
            ),
        ],
        [],
    )

    # 起势	有益	可驱散	不可扩散	不可偷取	移动力+1，可跨越障碍
    qishi = BuffTemp(
        "qishi",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: 1, ma.is_ignore_obstacle: True},
            ),
        ],
        [],
    )

    # 超载	其他	不可驱散	不可扩散	不可偷取	法攻、物理免伤+20%，主动攻击造成伤害时，50%概率施加「禁闭」状态，持续1回合。（不可驱散，无法获得「魂魄之力」）
    chaozhai = BuffTemp(
        "chaozhai",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.magic_defense_percentage: 20,
                    ma.defense_percentage: 20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_chaozai),
            ),
            EventListener(
                EventTypes.lose_buff_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, ["xuruo"], 1),
            ),
            EventListener(
                EventTypes.lose_buff_end,
                1,
                RS.always_true,
                partial(Effects.reduce_actor_certain_buff_stack, ["hunpozhili"], 3),
            ),
        ],
    )

    # 蹈火	其他	不可驱散	不可扩散	不可偷取	伤害提升10%，自身在友方「真炎」地形上移动时不消耗移动力。
    daohuo = BuffTemp(
        "daohuo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            ),
            ModifierEffect(
                partial(RS.is_in_terrain, "zhenyan"),
                {ma.is_unconsume_move_range: True},
            ),
        ],
        [],
    )

    # 转厄生天	其他	不可驱散	不可扩散	不可偷取	受到法术伤害降低25%，遭受法术攻击时，使1个有害状态变为随机「有益状态」（不可驱散，遭受法术攻击后移除）
    zhuaneshengtian = BuffTemp(
        "zhuaneshengtian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_damage_reduction_percentage: 25},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_magic_attack),
                partial(Effects.reverse_self_harm_buffs, 1),
            ),
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_magic_attack),
                partial(Effects.remove_actor_certain_buff, "zhuaneshengtian"),
            ),
        ],
    )

    # 辟厄	有益	可驱散	可扩散	可偷取	免疫「封脉」
    pie = BuffTemp(
        "pie",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [],
    )

    # 辟攻	有益	可驱散	可扩散	可偷取	免疫物攻、法攻降低
    pigong = BuffTemp(
        "pigong",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [],
    )

    # 辟秽	有益	可驱散	可扩散	可偷取	免疫「污秽」
    pihui = BuffTemp(
        "pihui",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [],
    )

    # 辟防	有益	可驱散	可扩散	可偷取	免疫物防、法防降低
    pifang = BuffTemp(
        "pifang",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [],
    )

    # 辟险	有益	可驱散	可扩散	可偷取	免疫敌方造成的位移效果（位移效果包含：「击退」「拉拽」）
    bixian = BuffTemp(
        "bixian",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [],
    )

    # 达摩	其他	不可驱散	不可扩散	不可偷取	遭受「固定伤害」提升30%，遭受攻击「对战后」额外受到1次「固定伤害」（施术者法攻的30%）
    damo = BuffTemp(
        "damo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.fixed_damage_percentage: 30},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_battle_attack_target),
                partial(
                    Effects.receive_fixed_damage_by_caster_magic_attack,
                    0.3,
                ),
            ),
        ],
    )

    # 连潮	其他	不可驱散	不可扩散	不可偷取	下一次普攻必定发动连击（0.3倍伤害，主动普攻后移除）。
    # 连潮·贰	其他	不可驱散	不可扩散	不可偷取	下一次普攻必定发动连击（0.3倍伤害，主动普攻后移除），若攻击前目标处于友方「霜冻」地形上，连击倍率提高0.2倍，且战后随机1个绝学冷却-1。
    lianchao = BuffTemp(
        "lianchao",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.chase_attack_percentage: 0.3},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.chase_attack_percentage: 0.3},
                ),
                ModifierEffect(
                    partial(RS.is_in_terrain, "shuangdong"),
                    {ma.chase_attack_percentage: 0.2},
                ),
            ],
        ],
        [],
    )

    # 迷心	有害	不可驱散	不可扩散	不可偷取	行动结束对自身以及周围1圈友方造成「固定伤害」（目标最大气血*25%）（不可驱散）
    # 迷心II	有害	不可驱散	不可扩散	不可偷取	行动结束对自身以及周围1圈友方造成「固定伤害」（目标最大气血*25%）与方芸「对战中」除气血外全属性降低20%（不可驱散）
    mixin = BuffTemp(
        "mixin",
        BuffTypes.Harm,
        True,
        False,
        False,
        [
            [],
            [
                ModifierEffect(
                    partial(RS.battle_with_certain_hero, "fangyun"),
                    {
                        ma.attack_percentage: -20,
                        ma.magic_attack_percentage: -20,
                        ma.defense_percentage: -20,
                        ma.magic_defense_percentage: -20,
                        ma.luck_percentage: -20,
                    },
                )
            ],
        ],
        [
            [
                EventListener(
                    EventTypes.action_end,
                    1,
                    RS.always_true,
                    partial(
                        Effects.add_fixed_damage_in_range_by_max_life,
                        0.25,
                        1,
                    ),
                ),
            ],
            [
                EventListener(
                    EventTypes.action_end,
                    1,
                    RS.always_true,
                    partial(
                        Effects.add_fixed_damage_in_range_by_max_life,
                        0.25,
                        1,
                    ),
                ),
            ],
        ],
    )

    # 追命	有害	不可驱散	不可扩散	不可偷取	无法使用主动「绝学」，与青「对战中」除气血外全属性降低20%，死亡后随机传递给3格范围1名其他友方（死亡传递只触发1次）。
    zhuiming = BuffTemp(
        "zhuiming",
        BuffTypes.Harm,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.is_active_skill_disabled: True,
                },
            ),
            ModifierEffect(
                partial(RS.battle_with_certain_hero, "qing"),
                {
                    ma.attack_percentage: -20,
                    ma.magic_attack_percentage: -20,
                    ma.defense_percentage: -20,
                    ma.magic_defense_percentage: -20,
                    ma.luck_percentage: -20,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.hero_death,
                1,
                partial(RS.PositionChecks.has_partner_in_range, 3),
                partial(Effects.transfer_certain_buff_to_random_partner, "zhuiming", 3),
            )
        ],
    )

    # 逆阙	有害	可驱散	可扩散	可偷取	被施加的治疗直接转变为治疗量的50%伤害
    nique = BuffTemp(
        "nique",
        BuffTypes.Harm,
        True,
        True,
        True,
        [],
        [
            # EventListener(
            #     EventTypes.heal_end,
            #     1,
            #     RS.always_true,
            #     partial(Effects.heal_to_damage, 0.5),
            # ),
        ],
    )

    # 遁地	其他	不可驱散	不可扩散	不可偷取	移动力和绝学范围+1，不可被敌方选中，受到的物理伤害减少60%。主动攻击进入对战提前结束「遁地」状态。
    dundi = BuffTemp(
        "dundi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: 1,
                    ma.single_skill_range: 1,
                    ma.range_skill_range: 1,
                    ma.is_non_selectable: True,
                    ma.physical_damage_reduction_percentage: 60,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "dundi"),
            ),
        ],
    )

    # 遮天蔽日	其他	不可驱散	不可扩散	不可偷取	免疫「封脉」「晕眩」「禁闭」「位移」「传送」「封 劲」「封缄」「颤栗」「魅惑」「嘲讽」「疫瘴」「逆阙」「麻痹」「断骨」「异心」「怵惕」「移动限制」「 气血交换」「冷却增加/无法减少」「禁止再移动/再行动」「主动「绝学」禁用」效果且减免大部分「百分比伤害」无视「烟雾」地形、「 禁咒烨域」效果
    zhetianbiri = BuffTemp(
        "zhetianbiri",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 酒困	其他	不可驱散	不可扩散	不可偷取	伤害-30%，免伤和治疗效果+30%，无法食用「美味的紫霜云芝」
    jiukun = BuffTemp(
        "jiukun",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_percentage: -30,
                    ma.magic_damage_percentage: -30,
                    ma.physical_damage_reduction_percentage: 30,
                    ma.magic_damage_reduction_percentage: 30,
                    ma.heal_percentage: 30,
                },
            ),
        ],
        [],
    )

    # 酷吏	有益	不可驱散	不可扩散	不可偷取	物攻+4%，物穿+2%（上限4层，不可驱散）
    # 酷吏II	有益	不可驱散	不可扩散	不可偷取	物攻、物穿+4%，大于等于4层时绝学射程+1，获得6层时随机伤害绝学冷却时间-2（上限6层）
    kuli = BuffTemp(
        "kuli",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: 4, ma.physical_penetration_percentage: 2},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.attack_percentage: 4, ma.physical_penetration_percentage: 2},
                ),
                ModifierEffect(
                    partial(RS.BuffChecks.self_buff_stack_reach, 4, "kuli"),
                    {ma.single_skill_range: 1, ma.range_skill_range: 1},
                ),
            ],
        ],
        [
            [],
            [
                EventListener(
                    EventTypes.get_buff_end,
                    1,
                    partial(RS.BuffChecks.get_certain_buff_and_stack_reach, 6, "kuli"),
                    partial(Effects.reduce_self_ramdon_damage_skill_cooldown, 2),
                )
            ],
        ],
    )

    # 醉仙望月步	其他	不可驱散	不可扩散	不可偷取	移动力+1，可跨越障碍，主动普攻触发「连击」，造成0.4倍伤害
    zuixianwangyuebu = BuffTemp(
        "zuixianwangyuebu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: 1,
                    ma.is_ignore_obstacle: True,
                    ma.chase_attack_percentage: 0.4,
                },
            ),
        ],
        [],
    )

    # 重击·崩山	其他	不可驱散	不可扩散	不可偷取	暴击率提升20%，发动「追击」（首击的0.3倍伤害）
    zhongjibengshan = BuffTemp(
        "zhongjibengshan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.critical_percentage: 20, ma.chase_attack_percentage: 0.3},
            ),
        ],
        [],
    )

    # 重击·散魂	其他	不可驱散	不可扩散	不可偷取	对选取的目标施加「逆阙」状态，持续1回合，对其2格范围内所有敌方造成1次物理伤害（0.2倍物攻）。
    zhongjisanhun = BuffTemp(
        "zhongjisanhun",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(Effects.add_buffs, ["nique"], 1),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(
                    Effects.add_fixed_damage_in_range_by_caster_physical_attack,
                    0.2,
                    2,
                ),
            ),
        ],
    )

    # 重击·神威	其他	不可驱散	不可扩散	不可偷取	伤害提高20%，造成伤害后施加「电流」状态，持续2回合。
    zhongjishenwei = BuffTemp(
        "zhongjishenwei",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_damage_percentage: 20, ma.magic_damage_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.add_buffs, ["dianliu"], 2),
            ),
        ],
    )

    # 锢步	有害	可驱散	可扩散	可偷取	无法触发再移动和自身赋予的再行动
    gubu = BuffTemp(
        "gubu",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_extra_action_disabled: True, ma.is_extra_move_disabled: True},
            ),
        ],
        [],
    )

    # 闪避	其他	不可驱散	不可扩散	不可偷取	躲闪对战中的1次攻击（不可驱散，触发后消失）
    shanbi = BuffTemp(
        "shanbi",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {ma.is_dodge_attack: True})],
        [],
    )

    # 防卫	其他	不可驱散	不可扩散	不可偷取	免伤提高20%，代替2格内友方承受攻击（「对战后」消失）
    fangwei = BuffTemp(
        "fangwei",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.physical_protect_range: 20, ma.magic_protect_range: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "fangwei"),
            )
        ],
    )

    # 降疗I	有害	可驱散	可扩散	可偷取	治疗效果降低20%
    jiangliao = BuffTemp(
        "jiangliao",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.heal_percentage: -20},
            ),
        ],
        [],
    )

    # 雷电空间	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战时，「对战中」伤害提高10%，对冰属相敌人额外提升10%。（1回合限定发动2次）
    # 雷电空间·壹	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战时，「对战中」伤害、暴击率提高10%，对冰属相敌人额外提升10%。（1回合限定发动3次）
    # 雷电空间·贰	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战时，「对战中」伤害、暴击率提高10%，对冰属相敌人额外提升15%。（1回合限定发动3次）
    leidiankongjian = BuffTemp(
        "leidiankongjian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.physical_damage_percentage: 10},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.physical_damage_percentage: 10, ma.critical_percentage: 10},
                ),
            ],
            [
                ModifierEffect(
                    RS.always_true,
                    {ma.physical_damage_percentage: 10, ma.critical_percentage: 10},
                ),
            ],
        ],
        [],
    )

    # 雷铠	有益	可驱散	可扩散	可偷取	遭受暴击伤害降低20%（受到暴击后消耗）
    leikai = BuffTemp(
        "leikai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.suffer_critical_damage_reduction_percentage: 20},
            ),
        ],
        [
            EventListener(
                EventTypes.under_critical_damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "leikai"),
            ),
        ],
    )

    # 霜冻	其他	不可驱散	不可扩散	不可偷取	移动力-1
    shuangdong = BuffTemp(
        "shuangdong",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.move_range: -1},
            ),
        ],
        [],
    )

    # 霜铠	有益	可驱散	可扩散	可偷取	主动攻击「对战中」遭受伤害降低30%。（主动攻击「对战中」受到伤害后消耗）
    shuangkai = BuffTemp(
        "shuangkai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.suffer_physical_damage_reduction_percentage: 30,
                    ma.suffer_magic_damage_reduction_percentage: 30,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "shuangkai"),
            ),
        ],
    )

    # 颂祝	其他	不可驱散	不可扩散	不可偷取	受治疗效果提升30%，且行动结束时，驱散自身2格范围内所有友方1个「有害状态」（不可驱散））
    songzhu = BuffTemp(
        "songzhu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.be_healed_percentage: 30},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.remove_partner_harm_buffs, 1, 2),
            ),
        ],
    )

    # 颤栗	有害	可驱散	不可扩散	不可偷取	无法选中施加者，状态消失时替换为「虚损I」，持续1回合
    chanli = BuffTemp(
        "chanli",
        BuffTypes.Harm,
        True,
        False,
        True,
        [],
        [
            EventListener(
                EventTypes.lose_buff_end,
                1,
                RS.always_true,
                partial(Effects.add_self_buffs, ["xusun"], 1),
            ),
        ],
    )

    # 飞灰	其他	不可驱散	不可扩散	不可偷取	2格内的敌人，若不携带「有益状态」则暴击率和治疗效果降低20%，主动释放技能前，使其2个「有益状态」变为随机「有害状态」，获得或刷新「遁地」状态时该状态持续回合数刷新至2回合。
    feihui = BuffTemp(
        "feihui",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 餍足	其他	不可驱散	不可扩散	不可偷取	获得时立刻恢复15%气血
    yanzu = BuffTemp(
        "yanzu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.get_buff_end,
                1,
                partial(RS.BuffChecks.get_certain_buff, "yanzu"),
                partial(Effects.heal_self, 0.15),
            ),
        ],
    )

    # 魁兽	其他	不可驱散	不可扩散	不可偷取	3格范围内每有1个敌方单位，双防提升10%（最高30%）
    kuishou = BuffTemp(
        "kuishou",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.PositionChecks.in_range_enemy_count_with_limit, 3, 3),
                {ma.defense_percentage: 10, ma.magic_defense_percentage: 10},
            )
        ],
        [],
    )

    # 魂创	其他	不可驱散	不可扩散	不可偷取	物攻-5%（最多叠加3层，不可免疫）
    hunchuang = BuffTemp(
        "hunchuang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.attack_percentage: -5},
            ),
        ],
        [],
    )

    # 魂魄之力	其他	不可驱散	不可扩散	不可偷取	法术穿透+3%，使用绝学后恢复自身气血（恢复量为施术者法攻的0.2倍）（上限5层，不可驱散）
    hunpozhili = BuffTemp(
        "hunpozhili",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_penetration_percentage: 3},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                RS.always_true,
                partial(Effects.heal_self_by_caster_magic_attack, 0.2),
            ),
        ],
        5,
    )

    # 魉生	其他	不可驱散	不可扩散	不可偷取	法攻+4%/5%/6%/7%、免伤+1%/2%/3%/4%，（上限5层，若本回合未主动攻击或释放绝学，行动结束时，减少1层）
    liangsheng = BuffTemp(
        "liangsheng",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.magic_attack_percentage: 4, ma.magic_defense_percentage: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "liangsheng"),
            ),
        ],
    )

    # 鲛力	其他	不可驱散	不可扩散	不可偷取	射程+1，免伤提高20%，遭受暴击率降低20%，天赋造成的追加伤害倍率提高0.2倍
    jiaoli = BuffTemp(
        "jiaoli",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_range: 1,
                    ma.physical_damage_reduction_percentage: 20,
                    ma.magic_damage_reduction_percentage: -20,
                    ma.suffer_critical_percentage: -20,
                },
            ),
        ],
        [],
    )

    # 鹿王	其他	不可驱散	不可扩散	不可偷取	不可被敌方选中，3格范围内敌方无法获得气力且主动远程攻击「对战中」伤害和暴击率降低20%（不可驱散）
    luwang = BuffTemp(
        "luwang",
        BuffTypes.Others,
        False,
        False,
        False,
        [ModifierEffect(RS.always_true, {})],
        [],
    )

    # 麻痹	有害	可驱散	可扩散	可偷取	无法进行反击
    mabi = BuffTemp(
        "mabi",
        BuffTypes.Harm,
        True,
        True,
        True,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_counterattack_disabled: True},
            )
        ],
        [],
    )

    # 龙骧	其他	不可驱散	不可扩散	不可偷取	遭受近战攻击「对战前」自身恢复20%气血，且「对战中」发动「先攻」（触发后消耗，触发时若处于己方「真炎」地形额外恢复20%气血，不可驱散）
    longxiang = BuffTemp(
        "longxiang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.attacked_by_melee_attack),
                {ma.is_counterattack_first: True},
            )
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.attacked_by_melee_attack),
                partial(Effects.heal_self, 0.2),
            ),
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_in_terrain, "zhenyan"),
                partial(Effects.add_buffs, ["xiangong"], 1),
            ),
        ],
    )

    # 遏心	其他	不可驱散	不可扩散	不可偷取	移除「空性」和「报怒」状态，存在时无法获得「报怒」和「空性」状态，自身无法移动，无法攻击，无法反击（不可驱散，每场战斗仅触发1次）
    exin1 = BuffTemp(
        "exin1",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.max_move_range: 0,
                    ma.is_attack_disabled: True,
                    ma.is_counterattack_disabled: True,
                },
            )
        ],
        [
            EventListener(
                EventTypes.get_buff_end,
                1,
                partial(RS.BuffChecks.get_certain_buff, "yanzu"),
                partial(Effects.remove_actor_certain_buff, "kongxing"),
            ),
            EventListener(
                EventTypes.get_buff_end,
                1,
                partial(RS.BuffChecks.get_certain_buff, "yanzu"),
                partial(Effects.remove_actor_certain_buff, "baonu"),
            ),
        ],
    )

    # 降曜	其他	不可驱散	不可扩散	不可偷取	无法再通过「浑天推星·贰式」展开结界「无方幻界」。
    jiangyao = BuffTemp(
        "jiangyao",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_wufangjiejie_disabled: True},
            ),
        ],
        [],
    )

    # 觉醒之力	其他	不可驱散	不可扩散	不可偷取	累积6层将激活「圣枪之力」状态，持续2回合，激活后无法获得「觉醒之力」
    juexingzhili = BuffTemp(
        "juexingzhili",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.get_buff_end,
                1,
                partial(RS.BuffChecks.get_certain_buff_and_stack_reach, 6, "juexingzhili"),
                partial(Effects.add_buffs, ["shengqiangzhili"], 2),
            ),
        ],
    )

    # 执戮	其他	不可驱散	不可扩散	不可偷取	全属性提高20%，雷伤减免和暗伤减免额外提高30%，主动攻击「对战后」随机对1圈范围内的敌人造成3次「固定伤害」（物攻的30%）。「执戮」存在期间无法获得「绝心」（不可驱散）
    zhilu = BuffTemp(
        "zhilu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.life_percentage: 20,
                    ma.attack_percentage: 20,
                    ma.magic_attack_percentage: 20,
                    ma.defense_percentage: 20,
                    ma.magic_defense_percentage: 20,
                    ma.luck_percentage: 20,
                    ma.thunder_damage_reduction_percentage: 30,
                    ma.dark_damage_reduction_percentage: 30,
                },
            ),
        ],
        [],
    )

    # 绝心	其他	不可驱散	不可扩散	不可偷取	每层「绝心」状态，全属性提高4% （不可驱散）。若达到5层，则转化为「执戮」状态。
    juexin = BuffTemp(
        "juexin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.life_percentage: 4,
                    ma.attack_percentage: 4,
                    ma.magic_attack_percentage: 4,
                    ma.defense_percentage: 4,
                    ma.magic_defense_percentage: 4,
                    ma.luck_percentage: 4,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.get_buff_end,
                1,
                partial(RS.BuffChecks.get_certain_buff_and_stack_reach, 5, "juexin"),
                partial(Effects.transfer_buff_to_other_buff, "juexin", "zhilu")
            ),
        ],
        5,
    )

    # 心念	其他	不可驱散	不可扩散	不可偷取	达到2层后消耗并获得「波旬降临」状态，处于「波旬降临」状态时无法获得（上限2层）
    xinnian = BuffTemp(
        "xinnian",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.get_buff_end,
                1,
                partial(RS.BuffChecks.self_buff_stack_reach, 2, "xinnian"),
                partial(Effects.add_buffs, ["boxunjianglin"]),
            ),
        ],
    )

    # 链锁	其他	不可驱散	不可扩散	不可偷取	只可朝施加者移动，行动结束时若处于施加者3格外则将「链锁」替换为「禁闭」，持续1回合。
    suolian = BuffTemp(
        "suolian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.is_only_move_to_caster: True},
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.in_range_of_enemy_caster, 3),
                partial(Effects.transfer_buff_to_other_buff, "suolian", "jinbi"),
            ),
        ],
    )

    # 注能	其他	不可驱散	不可扩散	不可偷取	物攻和免伤提高15%，免疫「固定伤害」，主动攻击「对战前」对目标造成一次「固定伤害」（目标最大气血的10%），消失后获得「温度冷却」，持续1回合（无法驱散）
    zhuneng = BuffTemp(
        "zhuneng",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.attack_percentage: 15,
                    ma.physical_damage_reduction_percentage: 15,
                    ma.magic_damage_reduction_percentage: 15,
                    ma.is_immunity_fix_damage: True,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attacker),
                partial(Effects.add_fixed_damage_by_target_max_life, 0.1),
            ),
        ],
    )

    # 温度冷却	其他	不可驱散	不可扩散	不可偷取	无法获得「注能」状态（无法驱散）
    wendulengque = BuffTemp(
        "wendulengque",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 对决	其他	不可驱散	不可扩散	不可偷取	选择敌方作为目标时只能选中施加者，且与施加者对战时，暴击率、暴击抗性降低20%，行动结束时，若不处于施加者3格范围内，给施加者施加「迅捷I」持续1回合。
    duijue = BuffTemp(
        "duijue",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.critical_percentage: -20,
                    ma.suffer_critical_damage_reduction_percentage: -20,
                    ma.is_only_attack_to_caster: True,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.PositionChecks.not_in_range_of_enemy_caster, 3),
                partial(Effects.add_caster_buffs, ["xunjie"], 1),
            ),
        ],
    )

    # 寒袭	其他	不可驱散	不可扩散	不可偷取	遭受近战攻击「对战中」物攻提高20%，并发动「先攻」。（「先攻」每回合触发1次）
    # 寒袭·壹	其他	不可驱散	不可扩散	不可偷取	遭受近战攻击「对战中」物攻提高20%，并发动「先攻」
    # 寒袭·贰	其他	不可驱散	不可扩散	不可偷取	遭受攻击「对战后」对目标施加「迟缓I」状态，持续1回合。遭受近战攻击「对战中」物攻提高20%，并发动「先攻」
    hanxi = BuffTemp(
        "hanxi",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            [
                ModifierEffect(
                    partial(RS.attacked_by_melee_attack),
                    {
                        ma.physical_damage_percentage: 20,
                        ma.is_counterattack_first: True,
                    },
                ),
            ],
            [
                ModifierEffect(
                    partial(RS.attacked_by_melee_attack),
                    {
                        ma.physical_damage_percentage: 20,
                        ma.is_counterattack_first: True,
                    },
                ),
            ],
            [
                ModifierEffect(
                    partial(RS.attacked_by_melee_attack),
                    {
                        ma.physical_damage_percentage: 20,
                        ma.is_counterattack_first: True,
                    },
                ),
            ],
        ],
        [
            [],
            [],
            [
                EventListener(
                    EventTypes.battle_end,
                    1,
                    partial(RS.is_battle_attack_target),
                    partial(Effects.add_buffs, ["chihuan"], 1),
                ),
            ],
        ],
    )

    # 意乱	其他	不可驱散	不可扩散	不可偷取	选择敌方作为目标时只能选中施加者，且与施加者对战时，暴击率降低100%
    yiluan = BuffTemp(
        "yiluan",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.critical_percentage: -100, ma.is_only_attack_to_caster: True},
            ),
        ],
        [],
    )

    # 战引	其他	不可驱散	不可扩散	不可偷取	选择敌方作为目标时只能选中施加者，主动攻击施加者时伤害降低20%。
    zhanyin = BuffTemp(
        "zhanyin",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.suffer_physical_damage_reduction_percentage: 20,
                    ma.is_only_attack_to_caster: True,
                },
            ),
        ],
        [],
    )

    # 浑天	其他	不可驱散	不可扩散	不可偷取	用所有主动绝学攻击时都可触发「寒岚」「焚狱」和「玄幽」状态的攻击效果，使用主动绝学攻击后消耗「寒岚」「焚狱」「玄幽」状态。
    huntian = BuffTemp(
        "huntian",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.skill_is_certain_element, "WATER"),
                {ma.magic_penetration_percentage: 10},
            ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_certain_element, "Fire"),
                partial(Effects.remove_target_benefit_buffs, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_certain_element, "Dark"),
                partial(Effects.add_target_harm_buffs, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_in_element_list, [Elements.DARK.value, Elements.FIRE.value, Elements.WATER.value]),
                partial(Effects.remove_actor_certain_buff, "hanlan"),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_in_element_list, [Elements.DARK.value, Elements.FIRE.value, Elements.WATER.value]),
                partial(Effects.remove_actor_certain_buff, "fanyu"),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(RS.skill_is_in_element_list, [Elements.DARK.value, Elements.FIRE.value, Elements.WATER.value]),
                partial(Effects.remove_actor_certain_buff, "xuanyou"),
            ),
        ],
    )

    # 瑞奏	其他	不可驱散	不可扩散	不可偷取	主动攻击造成暴击后，自身和施加者获得1点气力（暴击后消失）
    ruizou = BuffTemp(
        "ruizou",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.critical_damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_ruizou),
            ),
            EventListener(
                EventTypes.critical_damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.remove_actor_certain_buff, "ruizou"),
            ),
        ],
    )

    # 星云	有益	可驱散	不可扩散	不可偷取	遭受攻击时，敌方「对战前」每移动1格则伤害降低10%（最多降低30%，状态触发后消失，并使施加者获得2点「星屑」）
    xingyun = BuffTemp(
        "xingyun",
        BuffTypes.Benefit,
        True,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.xingyun_requires_check),
                {ma.battle_damage_reduction_percentage: 10},
            ),
        ],
        [
            EventListener(
                EventTypes.damage_start,
                1,
                partial(RS.xingyun_requires_check),
                partial(Effects.remove_actor_certain_buff, "xingyun"),
            ),
            EventListener(
                EventTypes.damage_start,
                1,
                partial(RS.xingyun_requires_check),
                partial(Effects.increase_actor_certain_buff_stack, "xingxue", 2),
            ),
        ],
    )

    # 星屑	其他	不可驱散	不可扩散	不可偷取	愿我如星君如月，夜夜流光相皎洁。消耗「星屑」，以强化或开启「摇光破军界」（上限10点）。
    xingxue = BuffTemp(
        "xingxue",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 飞羽	其他	不可驱散	不可扩散	不可偷取	攻击射程+1，主动攻击「对战后」获得再移动（2格）（不可驱散）
    feiyu = BuffTemp(
        "feiyu",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {ma.attack_range: 1},
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_feiyu, 2),
            ),
        ],
    )

    # 拢烟	其他	不可驱散	不可扩散	不可偷取	主动攻击每命中1个敌人给施加者回复1点气力（最多3点，不可驱散）
    longyan = BuffTemp(
        "longyan",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.damage_end,
                1,
                partial(RS.is_attacker),
                partial(Effects.take_effect_of_longyan),
            )
        ],
    )

    # 既行	其他	不可驱散	不可扩散	不可偷取	无法被再次激活（不可驱散，下回合开始时移除）
    jixing_yuqin = BuffTemp(
        "jixing",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(RS.always_true, {ma.is_jixing_disabled: True}),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                RS.always_true,
                partial(Effects.remove_actor_certain_buff, "jixing"),
            )
        ],
    )

    # # 极乐	其他	不可驱散	不可扩散	不可偷取	全属性提升15%，敌方行动结束若处于自身3格范围内则被夺取1个「有益状态」，若为召唤物且气血值低于自身则被吞蚀（受到最大气血100%固定伤害）并恢复自身50%气血（「极乐」状态下，无法获得餍足」状态）
    # jile = BuffTemp(
    #     "jile",
    #     BuffTypes.Others,
    #     False,
    #     False,
    #     False,
    #     [
    #         ModifierEffect(
    #             RS.always_true,
    #             {
    #                 ma.life_percentage: 15,
    #                 ma.attack_percentage: 15,
    #                 ma.magic_attack_percentage: 15,
    #                 ma.defense_percentage: 15,
    #                 ma.magic_defense_percentage: 15,
    #                 ma.luck_percentage: 15,
    #             },
    #         ),
    #     ],
    #     [
    #         EventListener(
    #             EventTypes.action_end,
    #             1,
    #             partial(RS.PositionChecks.in_range, 3),
    #             partial(Effects.take_buff_from_enemy),
    #         ),
    #     ],
    # )

    # 福灵	其他	不可驱散	不可扩散	不可偷取	移动力+2，可跨越障碍，物攻的15%附加至物防、法防上
    fuling = BuffTemp(
        "fuling",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.move_range: 2,
                    ma.is_ignore_obstacle: True,
                    ma.defense_percentage: "attack_15",
                    ma.magic_defense_percentage: "attack_15",
                },
            ),
        ],
        [],
    )

    # 灵辉	其他	不可驱散	不可扩散	不可偷取	行动结束时，如果携带不少于7层「灵辉」，消耗7层「灵辉」，再激活自身十字7格内1名法攻/物攻最高已结束行动的其他友方。（间隔2回合触发）
    linghui = BuffTemp(
        "linghui",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                partial(RS.BuffChecks.self_buff_stack_reach, 7, "linghui"),
                partial(Effects.take_effect_of_linghui),
            ),
        ],
        14,
    )

    # 疫瘴	其他	不可驱散	不可扩散	不可偷取	携带者受到驱散「有害状态」的效果作用时，每层本状态防止1个「有害状态」（仅限满足可驱散）被驱散，并消耗对应层数（最多叠加3层，不可驱散）
    # 禁咒烨域	其他	不可驱散	不可扩散	不可偷取	3格范围内敌方释放法术伤害绝学时法攻降低50%。(已入「遮天蔽日」套餐)
    # 循血	其他	不可驱散	不可扩散	不可偷取	自身每携带1个「有益状态」状态，伤害、物理免伤提升5%（最多提升15%）；「对战后」反转自身2个「有害状态」，恢复自身气血（最大气血的30%），并将自身最多2个「有益状态」复制给3格内的其他友方。（每回合只能触发1次）
    xunxue = BuffTemp(
        "xunxue",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                partial(RS.BuffChecks.self_benefit_buff_count, 3),
                {
                    ma.attack_percentage: 5,
                    ma.magic_attack_percentage: 5,
                    ma.physical_damage_reduction_percentage: 5,
                },
            ),
        ],
        [
            EventListener(
                EventTypes.battle_end,
                1,
                RS.always_true,
                partial(Effects.take_effect_of_xunxue),
            ),
        ],
    )

    # 幽铠	有益	可驱散	可扩散	可偷取	遭受攻击「对战前」夺取目标2个「有益状态」，若夺取数达上限则造成1次「固定伤害」（目标最大气血的10%）（触发后移除）。
    youkai = BuffTemp(
        "youkai",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(RS.is_attack_target),
                partial(Effects.take_effect_of_youkai),
            ),
        ],
    )

    # 优先攻击
    # 慑服	其他	不可驱散	不可扩散	不可偷取	行动结束时若处于施加者3格内，反转自身1个「有益状态」并发生1格内「扰动」效果（不可驱散，触发后移除）。
    shefu = BuffTemp(
        "shefu",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 送清明	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方主动发起对战，且优先攻击时，则在「对战前」为其施加「命蕴」效果，持续2回合（每回合只能触发2次）[若协攻对象为聂小倩，则「对战前」为其施加「极意II」「神护II」效果，持续1回合，且聂小倩所有主动绝学冷却时间减少1回合]
    songqingming = BuffTemp(
        "songqingming",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 寻猎	其他	不可驱散	不可扩散	不可偷取	若队友主动攻击自身2格范围内的敌人，且优先攻击时，则在「对战中」双方交战后，立刻对敌方造成额外一次0.3倍物攻伤害（每回合只能触发1次）
    xunlie = BuffTemp(
        "xunlie",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 灭破空间	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方主动发起对战，且优先攻击时，「对战中」伤害提高10%，若攻击者气血不满额外提升15%。（1回合限定发动2次）
    miepokongjian = BuffTemp(
        "miepokongjian",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )
    # 号令	其他	不可驱散	不可扩散	不可偷取	自身两格范围内，若有友方主动发起对战，且优先攻击时，伤害提高10%，
    haoling = BuffTemp(
        "haoling",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 焕焱烈阵	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，若有友方主动发起对战，且优先攻击时，使其本次战斗中伤害提高15%，若目标携带「燃烧」状态，伤害额外提高15%（每回合发动3次）
    huanyanliezhen = BuffTemp(
        "huanyanliezhen",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 炎狱空间	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战，且优先攻击时，「对战中」伤害提高10%，对雷属相敌人额外提升10%。（1回合限定发动2次）
    # 炎狱空间·壹	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战，且优先攻击时，「对战中」暴击率、伤害提高10%，对雷属相敌人额外提升10%。（1回合限定发动2次）
    # 炎狱空间·贰	其他	不可驱散	不可扩散	不可偷取	自身2格范围内，友方角色主动发起对战，且优先攻击时，「对战中」暴击率、伤害提高10%，对雷属相敌人额外提升15%。（1回合限定发动3次）
    yanyukongjian = BuffTemp(
        "yanyukongjian",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 护象	其他	不可驱散	不可扩散	不可偷取	范围内所有友方遭受「固定伤害」减免50% ，且施术者自身免伤额外提高10%（无法驱散）
    huxiang = BuffTemp(
        "huxiang",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.physical_damage_reduction_percentage: 10,
                    ma.magic_damage_reduction_percentage: 10,
                },
            ),
        ],
        [],
    )

    # 空性	其他	不可驱散	不可扩散	不可偷取	物攻的15%附加至物防、法防上，自身3格范围内友方受到攻击后，对攻击者造成1次物理伤害（受击人数（上限5人）*（物攻的0.4倍）），并进入「报怒」状态，持续2回合（不可驱散）
    kongxing = BuffTemp(
        "kongxing",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.defense_percentage: "attack_15",
                    ma.magic_defense_percentage: "attack_15",
                },
            ),
        ],
        [],
    )

    # 储存
    # 贮酿	其他	不可驱散	不可扩散	不可偷取	最多储存自身最大气血的50%，行动结束时，自身受到1次伤害（储存总量的50%）（不可驱散，不可免疫，必定在2回合内消化储存总量）
    chuliang = BuffTemp(
        "chuliang",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.take_effect_of_chuliang),
            ),
        ],
    )

    # 匿鞘	其他	不可驱散	不可扩散	不可偷取	最多储存自身最大气血的100%（不可驱散，必定在2回合内消化储存总量）
    niqiao = BuffTemp(
        "niqiao",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
    )

    # 盈尾	其他	不可驱散	不可扩散	不可偷取	盈盈佳人笑，百媚倾城欢（无法驱散，上限6层）。
    yingwei = BuffTemp(
        "yingwei",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
        6,
    )

    # 魅惑	其他	不可驱散	不可扩散	不可偷取	受到暴击概率+30%，无法选中施加者（无法驱散）。
    meihuo = BuffTemp(
        "meihuo",
        BuffTypes.Others,
        False,
        False,
        False,
        [
            ModifierEffect(
                RS.always_true,
                {
                    ma.suffer_critical_percentage: 30,
                    ma.is_attack_to_caster_disable: True,
                },
            ),
        ],
        [],
    )

    # 剑威   其他 不可驱散  不可扩散  不可偷取
    jianwei = BuffTemp(
        "jianwei",
        BuffTypes.Others,
        False,
        False,
        False,
        [],
        [],
        3,
    )
    
    # 微澜   其他 不可驱散  不可扩散  不可偷取 行动结束时,为3格范围内所有友方驱散1个「有害状态」, 并恢复气血（恢复量为施术者法攻的0.4倍）
    weilan = BuffTemp(
        "weilan",
        BuffTypes.Benefit,
        False,
        False,
        False,
        [],
        [
            EventListener(
                EventTypes.action_end,
                1,
                RS.always_true,
                partial(Effects.take_effect_of_weilan),
            )
        ],
    )

    # 辟险	有益	可驱散	可扩散	可偷取	 免疫敌方造成的位移效果（位移效果包含：「击退」「拉拽」）
    pixian = BuffTemp(
        "pixian",
        BuffTypes.Benefit,
        True,
        True,
        True,
        [],
        [],
    )


    # 火源	其他	不可驱散	不可扩散	不可偷取	最多储存「梦种灯」最大气血的100%，行动结束时消化50%储存总量为3格内其他友方恢复气血（必定在2回合内消化储存总量）

    # 传送	其他	不可驱散	不可扩散	不可偷取	传送效果包含：「传送」、「扰动」、「牵引」
    # 位移	其他	不可驱散	不可扩散	不可偷取	位移效果包含：「击退」、「拉拽」
    # 命杀	其他	不可驱散	不可扩散	不可偷取	免疫「属性类降低」有害状态，主动攻击「对战后」，使目标发生1圈内「扰动」效果。

    # 地形(领域)
    # 审判	其他	不可驱散	不可扩散	不可偷取	当敌方行动结束时，如果在警戒范围内，则立刻对其1圈范围内所有敌人造成0.4倍物攻伤害，驱散1个「有益状态」（累积触发3次后消失）
    # 审判·贰	其他	不可驱散	不可扩散	不可偷取	当敌方行动结束时，如果在警戒范围内，则立刻对其1圈范围内所有敌人造成0.5倍物攻伤害，反转1个「有益状态」（累积触发3次后消失，每触发1次降低「弥伽诫喻」1回合冷却）
    # 回灵界	其他	不可驱散	不可扩散	不可偷取	法阵内友方免疫「属性降低」类「有害状态」（不可驱散）
    # 回灵阵式	其他	不可驱散	不可扩散	不可偷取	友方落位时触发，对「回灵界」内的所有友方施加1个随机「有益状态」，并恢复最大气血的30%。
    # 眩灭阵式	其他	不可驱散	不可扩散	不可偷取	友方落位时触发，对「眩灭界」内的阵眼外其他敌方造成1次固定伤害（最大气血的20%），且发生「眩灭界」内的「扰动」
    # 眩灭界	其他	不可驱散	不可扩散	不可偷取	法阵内敌方无法获得「有益状态」（不可驱散）
    # 控潮	其他	不可驱散	不可扩散	不可偷取	若自身处于我方「霜冻」地形上，敌方行动结束时，若处于露葵3格范围内，对其目标位置触发1次天赋伤害和地形（每回合触发1次）
    # 冰霜	其他	不可驱散	不可扩散	不可偷取	受治疗效果、护盾获得加成降低10%，达到3层时立刻受到1次「固定伤害」（当前气血的20%），并在所在格制造敌方阵营的「霜冻」地形，持续2回合。（触发后移除）
    # 机巧·坚壳	其他	不可驱散	不可扩散	不可偷取	友方「阿秋」行动结束时拾取，恢复自身气血50%，获得「甲力」状态。
    # 机巧·械躯	其他	不可驱散	不可扩散	不可偷取	友方「阿秋」行动结束时拾取，主动绝学冷却时间-1，若本回合未使用气力技，获得3气力。
    # 机巧·独角	其他	不可驱散	不可扩散	不可偷取	友方「阿秋」行动结束时拾取，获得「蓄电」状态、「神睿I」状态，持续2回合。

    # 结界
    # 真法·无方幻界	其他	不可驱散	不可扩散	不可偷取	立即使气血低于50%的敌方所有不在冷却中的主动绝学获得1回合冷却。暗属相友方全属性+10%，且使用主动伤害或治疗绝学后，该绝学冷却时间-1。敌方每携带1个「有害状态」治疗和受治疗效果降低10%（最多降低30%）。
