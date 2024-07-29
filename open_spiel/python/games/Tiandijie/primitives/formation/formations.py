from functools import partial

from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.formation.FormationTemp import FormationTemp
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Professions, Gender
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Check
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as ma


class Formations:
    # 飞燕惊鸿阵: 上阵韩千秀和「侠客」，「铁卫」英灵至少各一名时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，主动造成伤害后，额外附加1次「固定伤害」（目标当前气血*15%）。
    feiyanjinghong = FormationTemp(
        "feiyanjinghong",
        "hanqianxiu",
        [{"profession": Professions.GUARD}, {"profession": Professions.SWORDSMAN}],
        None,
        [
            EventListener(
                EventTypes.damage_end,
                1,
                Check.always_true,
                partial(Effects.add_fixed_damage_by_current_life, 0.15),
            )
        ],
    )

    # 万念轮回阵: 上阵铁手夏侯仪和「雷」，「冰」属性英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，3格范围内存在气血未满的角色，伤害提高10%。
    wannianlunhui = FormationTemp(
        "wannianlunhui",
        "tieshouxiahouyi",
        [{"element": Elements.THUNDER}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.life_not_full_in_range, 3),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 三身通智阵: 上阵真胤和至少2位「阵眼」英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，2格内有其他友方角色时，绝学伤害提升10%。
    sanshentongzhi = FormationTemp(
        "sanshentongzhi",
        "zhenyin",
        [{"has_formation": True}, {"has_formation": True}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.has_partner_in_range, 2),
                {ma.skill_damage_percentage: 10},
            )
        ],
    )

    # 义鼠夺风阵: 上阵白玉堂和「暗」，「炎」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，自身携带「有益状态」时，伤害提高10%。
    yishuduofeng = FormationTemp(
        "yishuduofeng",
        "baiyutang",
        [{"element": Elements.DARK}, {"element": Elements.FIRE}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.self_has_benefit_buff),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 乾坤流烨阵: 上阵武英仲和至少2位「光」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，若目标未携带「有益状态」，「对战中」伤害提高15%。
    qiankunliuye = FormationTemp(
        "qiankunliuye",
        "wuyingzhong",
        [{"element": Elements.LIGHT}, {"element": Elements.LIGHT}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_has_no_benefit_buff),
                {ma.battle_damage_percentage: 15},
            )
        ],
    )

    # 伦巴第协阵： 上阵古伦德和至少2位「男性」英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，自身气血未满时，伤害提高10%。
    lunbadixie = FormationTemp(
        "lunbadixie",
        "gulunde",
        [{"gender": Gender.MALE}, {"gender": Gender.MALE}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.life_not_full),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 佛口蛇心阵: 上阵青和「雷」，「光」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。目标每有1个「有害状态」，「对战中」伤害提高5%（最多提高15%）。
    fokoushexin = FormationTemp(
        "fokoushexin",
        "qing",
        [{"element": Elements.THUNDER}, {"element": Elements.LIGHT}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_harm_buff_count),
                {ma.battle_damage_percentage: 5},
            )
        ],
    )

    # 侠风洗刃阵: 上阵奚歌和「炎」，「雷」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，单体绝学伤害提高10%。
    xiafengxiren = FormationTemp(
        "xiafengxiren",
        "xige",
        [{"element": Elements.FIRE}, {"element": Elements.THUNDER}],
        [
            ModifierEffect(
                partial(Check.always_true),
                {ma.single_target_skill_damage_percentage: 10},
            )
        ],
    )

    # 元龙两仪阵： 上阵召祐和「炎」，「冰」属性英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，3格范围内存在「炎」或「冰」属性角色，伤害提高10%。
    yuanlongliangyi = FormationTemp(
        "yuanlongliangyi",
        "zhaoyou",
        [{"element": Elements.FIRE}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(
                    Check.PositionChecks.has_element_hero_in_range,
                    [Elements.FIRE, Elements.WATER],
                    3,
                ),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 冰火绝狱阵: 上阵罗渊女皇和「炎」，「冰」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，自身携带「有益状态」时伤害提高8%，自身未携带「有益状态」时免伤提高8%。
    binghuojueyu = FormationTemp(
        "binghuojueyu",
        "luoyuannvhuang",
        [{"element": Elements.FIRE}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.self_has_benefit_buff),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.BuffChecks.self_has_no_benefit_buff),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 凶星镇荒阵: 上阵殷千炀和「咒师」，「铁卫」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。「对战中」自身气血大于等于50%时免伤提高8%，目标气血大于等于50%时伤害提高8%。
    xiongxingzhenhuang = FormationTemp(
        "xiongxingzhenhuang",
        "yinqianyang",
        [{"profession": Professions.SORCERER}, {"profession": Professions.GUARD}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.self_life_is_higher, 50),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.LifeChecks.target_life_is_higher, 50),
                {ma.battle_damage_percentage: 8},
            ),
        ],
    )

    # 剑心凛蝉阵: 上阵冰蝉玉剑和「御风」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。主动攻击时，穿透提高10%，若3格范围内敌方数量大于等于2，穿透额外提高5%。
    jianxinlinchan = FormationTemp(
        "jianxinlinchan",
        "bingchuanyujian",
        [{"profession": Professions.RIDER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.is_attacker),
                {
                    ma.physical_penetration_percentage: 10,
                    ma.magic_penetration_percentage: 10,
                },
            ),
            ModifierEffect(
                partial(
                    Check.PositionChecks.attack_enemy_in_range_count_bigger_than_with_base_2,
                    3,
                    2,
                ),
                {
                    ma.physical_penetration_percentage: 5,
                    ma.magic_penetration_percentage: 5,
                },
            ),
        ],
    )

    # 剑灼焰染阵: 上阵安逸和「羽士」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，目标不满血时，「对战中」自身伤害提高10%
    jianzhuoyanran = FormationTemp(
        "jianzhuoyanran",
        "anyi",
        [{"profession": Professions.ARCHER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.target_life_is_below, 100),
                {ma.battle_damage_percentage: 10},
            )
        ],
    )

    # 剑胆星驰阵: 上阵燕赤霞和「咒师」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，3格内每多1个其他角色，伤害和暴击率提高2%（最多提高8%）。
    jiandanxingchi = FormationTemp(
        "jiandanxingchi",
        "yanchixia",
        [{"profession": Professions.SORCERER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.in_range_count_with_limit, 3, 4),
                {ma.physical_damage_percentage: 2, ma.critical_percentage: 2},
            )
        ],
    )

    # 千煌幻日阵: 上阵夏侯仪，冰璃和慕容璇玑时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，造成范围伤害额外提高10%。
    qianhuanghuanri = FormationTemp(
        "qianhuanghuanri",
        "xiahouyi",
        [{"id": "bingli"}, {"id": "murongxuanji"}],
        [
            ModifierEffect(
                partial(Check.always_true), {ma.range_skill_damage_percentage: 10}
            )
        ],
    )

    # 墨染冬月阵: 上阵白复归和「冰」，「暗」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，2格内存在携带「有害状态」的友方时免伤提高8%，2格内存在携带「有害状态」的敌方时伤害提高8%。
    morandongyue = FormationTemp(
        "morandongyue",
        "baifugui",
        [{"element": Elements.WATER}, {"element": Elements.DARK}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.has_harm_buff_partner_in_range, 2),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.PositionChecks.has_harm_buff_enemy_in_range, 2),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 天命玄烨阵: 上阵胧夜和「侠客」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。与无克制关系的目标「对战中」伤害提升8%，受到克制伤害降低8%。
    tianmingxuanuye = FormationTemp(
        "tianmingxuanuye",
        "longye",
        [{"profession": Professions.SWORDSMAN}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.battle_with_no_element_advantage),
                {
                    ma.physical_damage_percentage: 8,
                    ma.magic_damage_percentage: 8,
                },
            ),
            ModifierEffect(
                partial(Check.under_attack_by_advantage_elements),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 天师明光阵: 上阵双双和「暗」，「雷」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。2格内存在携带「有益状态」的其他友方时伤害提高10%
    tianshimingguang = FormationTemp(
        "tianshimingguang",
        "shuangshuang",
        [{"element": Elements.DARK}, {"element": Elements.THUNDER}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.has_benefit_buff_partner_in_range, 2),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 天恩妙雪阵: 上阵于小雪和「侠客」、「铁卫」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，自身携带「有害状态」小于3个，伤害提高10%。
    tianenmiaoxue = FormationTemp(
        "tianenmiaoxue",
        "yuxiaoxue",
        [{"profession": Professions.GUARD}, {"profession": Professions.SWORDSMAN}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.self_harm_buff_count_smaller_than, 3),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 天机阵: 上阵尉迟良和「铁卫」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，身周2格有友方角色时，提升10%伤害。
    tianji = FormationTemp(
        "tianji",
        "yuchiliang",
        [{"profession": Professions.GUARD}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.has_partner_in_range, 2),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 天烈炽炎阵: 上阵殷剑平和至少2位「炎」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，主动攻击「对战中」伤害提高10%。
    tianliechiyan = FormationTemp(
        "tianliechiyan",
        "yinjianping",
        [{"element": Elements.FIRE}, {"element": Elements.FIRE}],
        [ModifierEffect(partial(Check.is_attacker), {ma.battle_damage_percentage: 10})],
    )

    # 天魔万象阵: 上阵剑邪和「暗」，「冰」属性英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，周围2圈内每有1个敌人，造成伤害提高5%（最多15%）。
    tianmowanxiang = FormationTemp(
        "tianmowanxiang",
        "jianxie",
        [{"element": Elements.DARK}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.in_range_enemy_count_with_limit, 2, 3),
                {ma.physical_damage_percentage: 5, ma.magic_damage_percentage: 5},
            )
        ],
    )

    # 幽使驭天阵: 上阵双曜冰璃和「侠客」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。与非飞行角色「对战中」伤害和暴击抗性提高8%。
    youshiyutian = FormationTemp(
        "youshiyutian",
        "shuangyaobingli",
        [{"profession": Professions.SWORDSMAN}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.in_battle_with_non_flyable),
                {ma.battle_damage_percentage: 8, ma.suffer_critical_damage_reduction_percentage: 8},
            )
        ],
    )

    # 幽冥夜华阵: 上阵黎幽和至少2位「暗」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，攻击携带3个及以上「有害状态」的目标时，伤害提高15%。
    youminyehua = FormationTemp(
        "youminyehua",
        "liyou",
        [{"element": Elements.DARK}, {"element": Elements.DARK}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_harm_buff_count_bigger_than, 3),
                {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15},
            )
        ],
    )

    # 幽寰天契阵: 上阵霍雍和「炎」，「冰」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，若气血高于50%且未携带「有害状态」，伤害提高15%。
    youhuantianqi = FormationTemp(
        "youhuantianqi",
        "huoyong",
        [{"element": Elements.FIRE}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.self_life_is_higher_and_no_harm_buff, 50),
                {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15},
            )
        ],
    )

    # 弦月封霜阵: 上阵封寒月和至少2位「冰」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，自身满血时，物穿，法穿提高10%。
    xianyuefengshuang = FormationTemp(
        "xianyuefengshuang",
        "fenghanyue",
        [{"element": Elements.WATER}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.life_is_full),
                {
                    ma.physical_penetration_percentage: 10,
                    ma.magic_penetration_percentage: 10,
                },
            )
        ],
    )

    # 暗月斗灵阵: 上阵月孛和「斗将」，「铁卫」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。与携带「属性降低」类「有害状态」的敌方「对战中」伤害和免伤提高8%。#TODO not accurate
    anyuedouling = FormationTemp(
        "anyuedouling",
        "yuebo",
        [{"profession": Professions.GUARD}, {"profession": Professions.WARRIOR}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_has_harm_buff, "attribute_reduction"),
                {
                    ma.battle_damage_percentage: 8,
                    ma.battle_damage_reduction_percentage: 8,
                },
            )
        ],
    )

    # 朝花夕梦阵: 上阵九阴和「光」，「暗」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，3格范围内同时存在其他「光」和「暗」属相角色，伤害和暴击率提高8%。
    zhaohuaximeng = FormationTemp(
        "zhaohuaximeng",
        "jiuyin",
        [{"element": Elements.LIGHT}, {"element": Elements.DARK}],
        [
            ModifierEffect(
                partial(
                    Check.PositionChecks.element_hero_in_range,
                    [Elements.LIGHT, Elements.DARK],
                    3,
                ),
                {ma.physical_damage_percentage: 8, ma.critical_percentage: 8},
            )
        ],
    )

    # 流霭绝杀阵: 上阵巴艾迩和「咒师」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，伤害提升8%，暴击率提高8%，2格范围内每有1个其他友方，造成伤害降低4%（最多8%），造成暴击率降低4%（最多8%）。
    liuajuesha = FormationTemp(
        "liuajuesha",
        "baaini",
        [{"profession": Professions.SORCERER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.always_true),
                {
                    ma.physical_damage_percentage: 8,
                    ma.magic_damage_percentage: 8,
                    ma.critical_percentage: 8,
                },
            ),
            ModifierEffect(
                partial(Check.PositionChecks.in_range_partner_count_with_limit, 2, 2),
                {
                    ma.physical_damage_percentage: -4,
                    ma.magic_damage_percentage: -4,
                    ma.critical_percentage: -4,
                },
            ),
        ],
    )

    # 海潮升歌阵: 上阵露葵和「铁卫」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。自身满血时，伤害提高8%，气血未满时，免伤提高8%。
    haichaoshengge = FormationTemp(
        "haichaoshengge",
        "lukui",
        [{"profession": Professions.GUARD}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.life_is_full),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.LifeChecks.life_not_full),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 灼光雷鸣阵: 上阵阿秋和「炎」，「光」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，使用伤害绝学时，对处于自身直线位置的目标，暴击率和伤害提高8%。
    zhuoguangleiming = FormationTemp(
        "zhuoguangleiming",
        "aqiu",
        [{"element": Elements.FIRE}, {"element": Elements.LIGHT}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.in_the_same_line),
                {
                    ma.single_target_skill_damage_percentage: 8,
                    ma.range_skill_damage_percentage: 8,
                    ma.critical_percentage: 8,
                },
            )
        ],
    )

    # 玄雷淬火阵: 上阵赛特和「暗」，「雷」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，自身气血越高，伤害和暴击率越高（最高8%）。
    xuanleicuihuo = FormationTemp(
        "xuanleicuihuo",
        "saite",
        [{"element": Elements.DARK}, {"element": Elements.THUNDER}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.self_life_is_higher_percentage, 0),
                {
                    ma.physical_damage_percentage: 8,
                    ma.magic_damage_percentage: 8,
                    ma.critical_percentage: 8,
                },
            )
        ],
    )

    # 牵灵慑魂阵： 上阵妮可和「侠客」，「斗将」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，主动攻击时，伤害提高7%，技能范围内每多1个目标，伤害额外提高2%（最多额外提高8%）。
    qianlingshehun = FormationTemp(
        "qianlingshehun",
        "nike",
        [{"profession": Professions.WARRIOR}, {"profession": Professions.SWORDSMAN}],
        [
            ModifierEffect(
                partial(Check.is_attacker), {ma.battle_damage_percentage: 7}
            ),
            ModifierEffect(
                partial(Check.enemies_in_skill_range, 4),
                {
                    ma.range_skill_damage_percentage: 2,
                    ma.single_target_skill_damage_percentage: 2,
                },
            ),
        ],
    )

    # 焚香销魂阵: 上阵憛香和「侠客」，「铁卫」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，若自身未携带「有害状态」，范围伤害和暴击率提高8%。
    fenxiangxiaohun = FormationTemp(
        "fenxiangxiaohun",
        "tanxiang",
        [{"profession": Professions.GUARD}, {"profession": Professions.SWORDSMAN}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.self_has_no_harm_buff),
                {ma.range_skill_damage_percentage: 8, ma.critical_percentage: 8},
            )
        ],
    )

    # 狐灵神氛阵： 上阵太玄灵狐和「火」，「幽」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。目标气血低于90%时，「对战中」伤害提高8%；自身气血低于90%时，「对战中」免伤提高8%。
    hulingshenfen = FormationTemp(
        "hulingshenfen",
        "taixuanlinghu",
        [{"element": Elements.FIRE}, {"element": Elements.DARK}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.target_life_is_below, 90),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.LifeChecks.self_life_is_below, 90),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 琼华飞仙阵: 上阵紫枫和「羽士」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，携带移动力提高的状态时，使用绝学伤害提高10%。
    qionghuafeixian = FormationTemp(
        "qionghuafeixian",
        "zifeng",
        [{"profession": Professions.ARCHER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.self_has_move_buff),
                {ma.skill_damage_percentage: 10},
            )
        ],
    )

    # 璇光天映阵: 上阵星占贤者和至少2位「光」属相英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，2格范围内存在其他「光」属相角色，暴击伤害减免和伤害提高8%。
    xuanguangtianying = FormationTemp(
        "xuanguangtianying",
        "xingzhanxianzhe",
        [{"element": Elements.LIGHT}, {"element": Elements.LIGHT}],
        [
            ModifierEffect(
                partial(
                    Check.PositionChecks.element_hero_in_range, [Elements.LIGHT], 2
                ),
                {
                    ma.suffer_critical_damage_reduction_percentage: 8,
                    ma.physical_damage_percentage: 8,
                    ma.magic_damage_percentage: 8,
                },
            )
        ],
    )

    # 璇玑引雷阵: 上阵慕容璇玑和至少2位「雷」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升15%，主动攻击暴击率提升15%。
    xuanjiyinlei = FormationTemp(
        "xuanjiyinlei",
        "murongxuanji",
        [{"element": Elements.THUNDER}, {"element": Elements.THUNDER}],
        [ModifierEffect(partial(Check.is_attacker), {ma.critical_percentage: 15})],
    )

    # 祝法化生阵: 上阵九色鹿和「咒师」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。自身满血时伤害提高8%，自身未携带「有害状态」时免伤提高8%。
    zhufahuasheng = FormationTemp(
        "zhufahuasheng",
        "jiuselu",
        [{"profession": Professions.SORCERER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.life_is_full),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.BuffChecks.self_has_no_harm_buff),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 神武曦舒阵: 上阵傅雅鱼和「男性」、「女性」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，2格范围内存在其他男性角色时，伤害提高8%，2格范围内存在其他女性角色时，免伤提高8%。
    shenwuxishu = FormationTemp(
        "shenwuxishu",
        "fuyayu",
        [{"gender": Gender.MALE}, {"gender": Gender.FEMALE}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.has_male_in_range, 2),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            ),
            ModifierEffect(
                partial(Check.PositionChecks.has_female_in_range, 2),
                {
                    ma.physical_damage_reduction_percentage: 8,
                    ma.magic_damage_reduction_percentage: 8,
                },
            ),
        ],
    )

    # 神观天掣阵：上阵云衣宫主和「雷」，「光」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，自身有主动绝学处于冷却中时，伤害提高10%。
    shenguantianche = FormationTemp(
        "shenguantianche",
        "yunyigongzhu",
        [{"element": Elements.THUNDER}, {"element": Elements.LIGHT}],
        [
            ModifierEffect(
                partial(Check.self_all_active_skills_in_cooldown),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 神阙灵繁阵: 上阵白菀，紫蕴，朱缳和青萝时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升20%。
    shenquelingfan = FormationTemp(
        "shenquelingfan",
        "baiwan",
        [{"id": "ziyun"}, {"id": "zhuhuan"}, {"id": "qingluo"}],
        [
            ModifierEffect(
                partial(Check.always_true),
                {
                    ma.attack_percentage: 5,
                    ma.magic_attack_percentage: 5,
                    ma.defense_percentage: 5,
                    ma.magic_defense_percentage: 5,
                },
            )
        ],
    )

    # 紫电青霜阵: 上阵紫蕴和至少2位「雷」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升10%，攻击携带「电流」状态的目标时，伤害提高10%
    zidianqingshuang = FormationTemp(
        "zidianqingshuang",
        "ziyun",
        [{"element": Elements.THUNDER}, {"element": Elements.THUNDER}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_has_certain_buff, "dianliu"),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            ),
            ModifierEffect(
                partial(Check.always_true),
                {
                    ma.attack_percentage: -5,
                    ma.magic_attack_percentage: -5,
                    ma.defense_percentage: -5,
                    ma.magic_defense_percentage: -5,
                },
            ),
        ],
    )
    # 醉梦红尘阵: 上阵李逍遥和「咒师」，「御风」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，自身每有1个「有益状态」，伤害提高5%（最多提高15%）。
    zuimenghongchen = FormationTemp(
        "zuimenghongchen",
        "lixiaoyao",
        [{"profession": Professions.SORCERER}, {"profession": Professions.RIDER}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_benefit_buff_count),
                {ma.physical_damage_percentage: 5, ma.magic_damage_percentage: 5},
            )
        ],
    )

    # 问仙破御阵: 上阵雪芝和「咒师」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。攻击存在主动绝学处于冷却中的敌方时，伤害提高10%。
    wenxianduyu = FormationTemp(
        "wenxianduyu",
        "xuezhi",
        [{"profession": Professions.SORCERER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.target_has_active_skills_in_cooldown),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 附星擢升阵: 上阵允迦和「暗」，「雷」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，伤害提升15%，3格范围内每有1个敌方，造成伤害降低5%（最多15%）。
    fuxingzhuosheng = FormationTemp(
        "fuxingzhuosheng",
        "yunjia",
        [{"element": Elements.DARK}, {"element": Elements.THUNDER}],
        [
            ModifierEffect(
                partial(Check.always_true),
                {ma.physical_damage_percentage: 15, ma.magic_damage_percentage: 15},
            ),
            ModifierEffect(
                partial(Check.PositionChecks.in_range_enemy_count_with_limit, 3, 3),
                {ma.physical_damage_percentage: -5, ma.magic_damage_percentage: -5},
            ),
        ],
    )

    # 风花剑影阵: 上阵殷无邪和至少2位「女性」英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，2格范围内存在女性角色时，伤害提高10%。
    fenghuajianying = FormationTemp(
        "fenghuajian",
        "yinwuxie",
        [{"gender": Gender.FEMALE}, {"gender": Gender.FEMALE}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.has_female_in_range, 2),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            )
        ],
    )

    # 驱雷魔魄阵: 上阵剑魂·天尊和「雷」，「幽」属相英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，若自身未携带「有害状态」，「对战中」伤害提高15%。
    quleimopo = FormationTemp(
        "qule",
        "jianhuntianzun",
        [{"element": Elements.THUNDER}, {"element": Elements.ETHEREAL}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.self_has_no_harm_buff),
                {ma.battle_damage_percentage: 15},
            )
        ],
    )

    # 鬼冥炼狱阵: 上阵鲜于超和「羽士」，「咒师」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，气血高于70%时，伤害和免伤提高8%。
    guiminglianyu = FormationTemp(
        "guiminglianyu",
        "xianyuchao",
        [{"profession": Professions.ARCHER}, {"profession": Professions.SORCERER}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.self_life_is_higher, 70),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            )
        ],
    )

    # 光焰烛天阵: 上阵慕容筝和至少2位「炎」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升10%，攻击携带「燃烧」状态的目标时，伤害提高10%。
    guangyanzhutian = FormationTemp(
        "guangyanzhutian",
        "murongzheng",
        [{"element": Elements.FIRE}, {"element": Elements.FIRE}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_has_certain_buff, "burn"),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            ),
            ModifierEffect(
                partial(Check.always_true),
                {
                    ma.attack_percentage: -5,
                    ma.magic_attack_percentage: -5,
                    ma.defense_percentage: -5,
                    ma.magic_defense_percentage: -5,
                },
            ),
        ],
    )

    # 头狼寻猎阵: 上阵苍狼和「咒师」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%。3格范围内其他友方大于等于2名时，伤害和免伤提高8%。
    toulangxunlie = FormationTemp(
        "toulanxunlie",
        "canglang",
        [{"profession": Professions.SORCERER}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.PositionChecks.partner_in_range_count_bigger_than, 3, 2),
                {ma.physical_damage_percentage: 8, ma.magic_damage_percentage: 8},
            )
        ],
    )

    # 幻冰凝霜阵: 上阵胧妖和至少2位「冰」属性英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升10%，攻击携带「迟缓」类状态的目标时，伤害提高10%
    huanbingningshuang = FormationTemp(
        "huanbingningshuang",
        "longyao",
        [{"element": Elements.WATER}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(Check.BuffChecks.target_has_certain_buff, "slow"),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            ),
            ModifierEffect(
                partial(Check.always_true),
                {
                    ma.attack_percentage: -5,
                    ma.magic_attack_percentage: -5,
                    ma.defense_percentage: -5,
                    ma.magic_defense_percentage: -5,
                },
            ),
        ],
    )

    # 暗香迷情阵: 上阵韩无砂和至少2位「女性」英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提升10%，与非女性单位战斗时，伤害提升10%
    anxiangmiqing = FormationTemp(
        "anxiangmiqing",
        "hanwusha",
        [{"gender": Gender.FEMALE}, {"gender": Gender.FEMALE}],
        [
            ModifierEffect(
                partial(Check.in_battle_with_non_female),
                {ma.physical_damage_percentage: 10, ma.magic_damage_percentage: 10},
            ),
            ModifierEffect(
                partial(Check.always_true),
                {
                    ma.attack_percentage: -5,
                    ma.magic_attack_percentage: -5,
                    ma.defense_percentage: -5,
                    ma.magic_defense_percentage: -5,
                },
            ),
        ],
    )

    # 六天自在阵:  上阵波旬尉迟良和「铁卫」，「祝由」英灵至少各一位时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，若自身气血百分比大于等于目标，主动攻击「对战中」伤害提高15%。
    liutianzizai = FormationTemp(
        "liutianzizai",
        "boxun",
        [{"profession": Professions.GUARD}, {"profession": Professions.PRIEST}],
        [
            ModifierEffect(
                partial(Check.LifeChecks.self_life_is_higher_than_target),
                {ma.battle_damage_percentage: 15},
            )
        ],
    )

    # 冰天照雪阵:  上阵禄存高皇君和至少2位「冰」属相英灵时，激活战阵。所有我方上阵角色物攻，物防，法攻，法防提高15%，2格范围内存在其他「冰」属相角色，伤害、穿透提高8%。
    bingtianzhaoxue = FormationTemp(
        "bingtianzhaoxue",
        "lucong",
        [{"element": Elements.WATER}, {"element": Elements.WATER}],
        [
            ModifierEffect(
                partial(
                    Check.PositionChecks.element_hero_in_range, [Elements.WATER], 2
                ),
                {
                    ma.physical_damage_percentage: 8,
                    ma.magic_damage_percentage: 8,
                    ma.physical_penetration_percentage: 8,
                    ma.magic_penetration_percentage: 8,
                },
            )
        ],
    )
