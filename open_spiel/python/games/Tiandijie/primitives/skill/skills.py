from enum import Enum
from functools import partial

from open_spiel.python.games.Tiandijie.calculation.Range import RangeType, Range
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.skill.Distance import Distance, DistanceType
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillType, SkillTargetTypes
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as Ma
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTemp import SkillTemp


class Skills(Enum):
    @classmethod
    def get_skill_by_id(cls, skill_id):
        for skill in cls:
            if skill.value.id == skill_id:
                return skill.value
        return None
    #  疾风快刃	 消耗： 2
    #  类别：物攻伤害	 冷却：2回合
    #  射程：1格	 范围：单体
    #  无视护卫攻击单个敌人，造成1.3倍伤害，若目标满血则「对战前」造成1次0.3倍物攻伤害。
    jifengkuairen = SkillTemp(
        "jifengkuairen",
        "疾风快刃",
        2,
        Elements.NONE,
        SkillType.Physical,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [ModifierEffect(partial(Rs.always_true), {Ma.is_ignore_protector: True})],
        [],
    )

    #  纵命格杀	 消耗： 2
    #  类别：物攻伤害	 冷却：2回合
    #  射程：1格	 范围：单体
    #  攻击单个敌人，造成1.3倍伤害，「对战前」施加「幽阙」状态，持续2回合。若目标周围1格没有友方则本次攻击无视护卫且物理穿透提高30%。
    zongmingesha = SkillTemp(
        "zongmingesha",
        "纵命格杀",
        2,
        Elements.ETHEREAL,
        SkillType.Physical,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [
            ModifierEffect(
                partial(
                    Rs.PositionChecks.no_partners_in_target_range,
                    1,
                ),
                {Ma.is_ignore_protector: True, Ma.physical_penetration_percentage: 30},
            )
        ],
        [],
    )

    # 律隙万变	 消耗： 1
    #  类别：再动	 冷却：3回合
    #  射程：4格	 范围：单体
    #  主动使用，传送到1个目标身周的指定空格，使自身2格范围友方/敌方的「有益状态」/「有害状态」持续时间增加1回合。自身获得再行动（2格）。
    lvxiwanbian = SkillTemp(
        "lvxiwanbian",
        "律隙万变",
        1,
        Elements.ETHEREAL,
        SkillType.Move,
        SkillTargetTypes.TERRAIN,
        3,
        Distance(DistanceType.NORMAL, 4),
        Range(RangeType.POINT, 0, 1, 1),
        0,
        [],
        [
            EventListener(
                EventTypes.move_end,
                1,
                partial(Rs.always_true),
                partial(
                    Effects.extend_enemy_harm_buffs,
                    2,
                    2,
                    1,
                ),
            ),
            EventListener(
                EventTypes.move_end,
                1,
                partial(Rs.always_true),
                partial(
                    Effects.extend_partner_benefit_buffs,
                    2,
                    2,
                    1,
                ),
            ),
        ],
    )

    # 雷引万宇	 消耗： 2
    # 类别：物攻伤害	 冷却：3回合
    # 射程：自身	 范围：2圈
    # 对范围内所有敌人造成0.3倍伤害，吸引范围内敌人到身边，若2格内存在3个及以上敌人，触发原地再行动。使用后切换为「天闪乱魂」。
    leiyinwanyu = SkillTemp(
        "leiyinwanyu",
        "雷引万宇",
        2,
        Elements.DARK,
        SkillType.Physical,
        SkillTargetTypes.SELF,
        3,
        Distance(DistanceType.NORMAL, 0),
        Range(RangeType.SQUARE, 2, 2, 2),
        0.3,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_leiyinwanyu),
            )
        ],
    )

    # 天闪乱魂	 消耗： -
    # 类别：物攻伤害	 冷却：-
    # 射程：2格	 范围：单体
    # 攻击单个敌人，造成1.3倍伤害，战后使目标身周1圈内所有敌人发生1圈内「扰动」状态，使用后切换为「雷引万宇」
    tianshanluanhun = SkillTemp(
        "tianshanluanhun",
        "天闪乱魂",
        0,
        Elements.DARK,
        SkillType.Physical,
        SkillTargetTypes.ENEMY,
        0,
        Distance(DistanceType.NORMAL, 2),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [
            # ModifierEffect(
            #     partial(Rs.always_true),
            #     {Ma.is_attract: True},
            # ),
        ],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_tianshanluanhun),
            )
        ],
    )

    # 暗霎幽琰	 消耗： 2
    # 类别：物攻伤害	 冷却：2回合
    # 射程：1格	 范围：单体
    # 攻击单个敌人，造成1.5倍伤害，「对战前」自身获得3层「绝心」状态，「对战前」施加「禁疗」状态，持续2回合。
    anshayouyan = SkillTemp(
        "anshayouyan",
        "暗霎幽琰",
        2,
        Elements.DARK,
        SkillType.Physical,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 0, 1, 1),
        1.5,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_anshayouyan),
            )
        ],
    )

    # 神气流转	 消耗： 2
    # 类别：治疗	 冷却：1回合
    # 射程：3格	 范围：菱形2格
    # 主动使用，恢复范围内所有友方气血（恢复量为施术者法攻的0.75倍），驱散1个「有害状态」。
    shenqiliuzhuan = SkillTemp(
        "shenqiliuzhuan",
        "神气流转",
        2,
        Elements.NONE,
        SkillType.Heal,
        SkillTargetTypes.PARTNER,
        1,
        Distance(DistanceType.NORMAL, 3),
        Range(RangeType.DIAMOND, 2, 5, 5),
        0.75,
        [],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.always_true),
                partial(Effects.remove_partner_harm_buffs_in_range, 1, 2),
            )
        ],
    )
    # 载舟号令	 消耗： 2
    # 类别：支援	 冷却：3回合
    # 射程：自身	 范围：菱形3格
    # 主动使用，对范围内的所有友方施加「神护I」「固元I」状态，持续3回合。
    zaizhouhaoling = SkillTemp(
        "zaizhouhaoling",
        "载舟号令",
        2,
        Elements.NONE,
        SkillType.Support,
        SkillTargetTypes.SELF,
        3,
        Distance(DistanceType.NORMAL, 0),
        Range(RangeType.DIAMOND, 3, 7, 7),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_start,
                1,
                partial(Rs.always_true),
                partial(Effects.add_buffs, ["shenhu", "guyuan"], 3),
            )
        ],
    )

    # 力挽狂澜	 消耗： 2
    # 类别：治疗	 冷却：3回合
    # 射程：3格	 范围：菱形4格
    # 主动使用，驱散范围内所有友方身上2个「有害状态」，并恢复气血（恢复量为施术者法攻的1倍），自身获得「微澜」「芬芳I」状态，持续2回合。
    liwankuanglan = SkillTemp(
        "liwankuanglan",
        "力挽狂澜",
        2,
        Elements.NONE,
        SkillType.Heal,
        SkillTargetTypes.PARTNER,
        3,
        Distance(DistanceType.NORMAL, 3),
        Range(RangeType.DIAMOND, 4, 5, 5),
        1,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.add_self_buffs, ["weilan", "fenfang"], 2),
            ),
            EventListener(
                EventTypes.skill_start,
                1,
                partial(Rs.always_true),
                partial(Effects.remove_target_harm_buffs_in_range, 2, 4),
            ),
        ],
    )

    # 浑天推星	 消耗： 1
    # 类别：支援	 冷却：3回合
    # 射程：自身	 范围：单体
    # 主动使用，获得「浑天」状态，持续1回合。获得「寒岚」「焚狱」「玄幽」状态和再行动（2格）。
    huntiantuixing = SkillTemp(
        "huntiantuixing",
        "浑天推星",
        1,
        Elements.DARK,
        SkillType.Support,
        SkillTargetTypes.SELF,
        3,
        Distance(DistanceType.NORMAL, 0),
        Range(RangeType.POINT, 0, 1, 1),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_start,
                1,
                partial(Rs.always_true),
                partial(Effects.add_self_buffs, ["hanlan", "fanyu", "xuanyou"], 15),
            ),
            EventListener(
                EventTypes.skill_start,
                2,
                partial(Rs.always_true),
                partial(Effects.add_self_buffs, ["huntian"], 2),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.update_self_additional_action, 2),
            )
        ],
    )

    # 决战无双	 消耗： 2
    # 类别：主动	 冷却：2回合
    # 射程：5格	 范围：单体
    # 主动使用，对目标施加「对决」状态，持续2回合，自身获得护盾（最大气血的50%）。使用后切换为「炎烬裂凶」。
    juezhanwushuang = SkillTemp(
        "juezhanwushuang",
        "决战无双",
        2,
        Elements.NONE,
        SkillType.EFFECT_ENEMY,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 5),
        Range(RangeType.POINT, 0, 1, 1),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_start,
                1,
                partial(Rs.always_true),
                partial(Effects.add_buffs, ["duijue"], 2),
            ),
            EventListener(
                EventTypes.skill_start,
                2,
                partial(Rs.always_true),
                partial(Effects.add_shield_by_self_max_life, 0.5),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_juezhanwushuang),
            )
        ],
    )

    # 炎烬裂凶	 消耗： 2
    # 类别：法攻伤害	 冷却：-
    # 射程：1格	 范围：单体
    # 攻击单个敌人，造成1.3倍伤害，「对战前」施加「蚀魔I」状态，持续2回合。目标携带自身施加的「对决」状态时，则本次攻击无视护卫，「对战后」对目标造成1次法术伤害（法攻的0.3倍）。使用后切换为「决战无双」。
    yanjinliexiong = SkillTemp(
        "yanjinliexiong",
        "炎烬裂凶",
        2,
        Elements.FIRE,
        SkillType.Magical,
        SkillTargetTypes.ENEMY,
        0,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.POINT, 1, 1, 1),
        1.3,
        [
            ModifierEffect(partial(Rs.BuffChecks.target_has_certain_buff, "duijue"), {Ma.is_ignore_protector: True}),
        ],
        [
            EventListener(
                EventTypes.battle_start,
                1,
                partial(Rs.always_true),
                partial(Effects.add_buffs, ["shimo"], 2),
            ),
            EventListener(
                EventTypes.battle_end,
                1,
                partial(Rs.always_true),
                partial(Effects.add_fixed_damage_by_caster_magic_attack, 0.3),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_yanjinliexiong),
            )
        ],
    )

    # 赤旗凌曜	 消耗： 2
    # 类别：法攻伤害	 冷却：3回合
    # 射程：3格	 范围：菱形2格
    # 选择1个格子释放，对范围内所有敌人造成0.5倍伤害，对范围内的目标施加「燃烧」状态，持续2回合，若目标处于「金乌旗」2格范围内，则额外施加「罔效I」状态，持续2回合。使用绝学后召回「金乌旗」。    chiqilingyao
    chiqilingyao = SkillTemp(
        "chiqilingyao",
        "赤旗凌曜",
        2,
        Elements.FIRE,
        SkillType.Magical,
        SkillTargetTypes.ENEMY,
        3,
        Distance(DistanceType.NORMAL, 3),
        Range(RangeType.DIAMOND, 2, 5, 5),
        0.5,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                3,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_chiqilingyao),
            ),
        ],
    )
    # 布旗	 消耗： -
    # 类别：法攻伤害	 冷却：-
    # 射程：5格	 范围：单体
    # 主动使用，在指定格子布置「金乌旗」，并对2格范围内所有敌人造成1次法术伤害（施术者法攻的20%），自身立刻获得护盾（最大气血的25%）。
    # 「金乌旗」：相邻1格开启「限制区域」：敌方移动力消耗+1。（无法再生成其他地形，不可停留）
    buqi = SkillTemp(
        "buqi",
        "布旗",
        0,
        Elements.FIRE,
        SkillType.Magical,
        SkillTargetTypes.TERRAIN,
        0,
        Distance(DistanceType.NORMAL, 5),
        Range(RangeType.DIAMOND, 2, 1, 1),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                2,
                partial(Rs.always_true),
                partial(Effects.add_shield_by_self_max_life, 0.25),
            ),

            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_buqi, 1),
            ),
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_buqi, 2),
            )
        ],
    )

    # 焰染穿云	 消耗： 2
    # 类别：法攻伤害	 冷却：3回合
    # 射程：自身	 范围：直线5格
    # 对范围内所有敌人造成0.3倍伤害，自身获得再移动（3格），移动后若自身处于「金乌旗」2格范围内，获得再行动。发动再行动时获得「燃焰」状态。
    yanranchuanyun = SkillTemp(
        "yanranchuanyun",
        "焰染穿云",
        2,
        Elements.FIRE,
        SkillType.Magical,
        SkillTargetTypes.DIRECTION,
        3,
        Distance(DistanceType.NORMAL, 1),
        Range(RangeType.DIRECTIONAL, 5, 5, 1),
        0.3,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_yanranchuanyun, 1),
            ),
            EventListener(
                EventTypes.before_action_end,
                1,
                partial(Rs.PositionChecks.self_in_certain_terrianbuff, "jinwuqi"),
                partial(Effects.take_effect_of_yanranchuanyun, 2),
            )
        ],
    )

    # 式鬼召唤	 消耗： 2
    # 类别：召唤	 冷却：4回合
    # 射程：2格	 范围：单体
    # 召唤1个「式鬼」进行作战（继承自身140%物攻属性，其他属性继承80%，「式鬼」最多同时存在1个）。
    shiguizhaohuan = SkillTemp(
        "shiguizhaohuan",
        "式鬼召唤",
        2,
        Elements.NONE,
        SkillType.Support,
        SkillTargetTypes.TERRAIN,
        4,
        Distance(DistanceType.NORMAL, 2),
        Range(RangeType.POINT, 0, 1, 1),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_shiguizhaohuan),
            )
        ],
    )

    # 地御之阵	 消耗： 2
    # 类别：支援	 冷却：3回合
    # 射程：3格	 范围：菱形2格
    # 主动使用，对范围内的所有友方施加「披甲I」状态，持续3回合。
    diyuzhizhen = SkillTemp(
        "diyuzhizhen",
        "地御之阵",
        2,
        Elements.NONE,
        SkillType.Support,
        SkillTargetTypes.PARTNER,
        3,
        Distance(DistanceType.NORMAL, 3),
        Range(RangeType.DIAMOND, 2, 5, 5),
        0,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_diyuzhizhen),
            )
        ],
    )

    # 金刚法轮	 消耗： 2
    # 类别：物攻伤害	 冷却：3回合
    # 射程：4格	 范围：1圈
    # 对范围内所有敌人共造成1倍伤害，并施加「乱神II」状态，持续2回合。对暗系或冰系额外施加「压制」状态。
    jingangfalun = SkillTemp(
        "jingangfalun",
        "金刚法轮",
        2,
        Elements.NONE,
        SkillType.Physical,
        SkillTargetTypes.ENEMY,
        3,
        Distance(DistanceType.NORMAL, 4),
        Range(RangeType.SQUARE, 1, 1, 1),
        1,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.take_effect_of_jingangfalun),
            )
        ],
    )

    # 天霜雪舞	 消耗： 2
    # 类别：法攻伤害	 冷却：2回合
    # 射程：2格	 范围：单体
    # 攻击单个敌人，造成1.5倍伤害，「对战前」对敌方施加「蚀魔I」状态，持续2回合。
    tianshuangxuewu = SkillTemp(
        "tianshuangxuewu",
        "天霜雪舞",
        2,
        Elements.WATER,
        SkillType.Magical,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 2),
        Range(RangeType.POINT, 0, 1, 1),
        1.5,
        [],
        [
            EventListener(
                EventTypes.skill_start,
                1,
                partial(Rs.always_true),
                partial(Effects.add_buffs, ["shimo"], 2),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.skill_is_used_by_certain_hero, "huoyong"),
                partial(Effects.take_effect_of_luohouzhenfa),
            )
        ],
    )

    # 无天黑炎	 消耗： 2
    # 类别：法攻伤害	 冷却：2回合
    # 射程：2格	 范围：单体
    # 攻击单个敌人，造成1.3倍伤害，施加2个随机「有害状态」。
    wutianheiyan = SkillTemp(
        "wutianheiyan",
        "无天黑炎",
        2,
        Elements.DARK,
        SkillType.Magical,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 2),
        Range(RangeType.POINT, 0, 1, 1),
        1.3,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.add_target_random_harm_buff, 2),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.skill_is_used_by_certain_hero, "huoyong"),
                partial(Effects.take_effect_of_luohouzhenfa),
            )
        ],
    )

    # 离火神诀	 消耗： 2
    # 类别：法攻伤害	 冷却：2回合
    # 射程：2格	 范围：单体
    # 攻击单个敌人，造成1.5倍伤害，施加「燃烧」状态，持续2回合。
    lihuoshenjue = SkillTemp(
        "lihuoshenjue",
        "离火神诀",
        2,
        Elements.FIRE,
        SkillType.Magical,
        SkillTargetTypes.ENEMY,
        2,
        Distance(DistanceType.NORMAL, 2),
        Range(RangeType.POINT, 0, 1, 1),
        1.5,
        [],
        [
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.always_true),
                partial(Effects.add_buffs, ["ranshao"], 2),
            ),
            EventListener(
                EventTypes.action_end,
                1,
                partial(Rs.skill_is_used_by_certain_hero, "huoyong"),
                partial(Effects.take_effect_of_luohouzhenfa),
            )
        ],
    )
