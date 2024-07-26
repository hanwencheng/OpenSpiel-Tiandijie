from enum import Enum
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Gender, Professions, HideProfessions
from open_spiel.python.games.Tiandijie.primitives.hero.HeroTemp import HeroTemp
from open_spiel.python.games.Tiandijie.primitives.formation.formations import Formations
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.hero.Attributes import Attributes
from open_spiel.python.games.Tiandijie.primitives.talent.talents import Talents
from open_spiel.python.games.Tiandijie.primitives.talent.Talent import Talent
from open_spiel.python.games.Tiandijie.primitives.Weapons import Weapons, Weapon
from open_spiel.python.games.Tiandijie.primitives.fabao import Fabaos

#   大号是1 小号是0

class HeroeTemps(Enum):
    mohuahuangfushen0 = HeroTemp(
        name="魔化皇甫申",
        temp_id="mohuahuangfushen",
        basicInfo=None,
        flyable=True,
        has_formation=False,
        formation_temp=None,
        gender=Gender.MALE,
        element=Elements.DARK,
        profession=Professions.RIDER,
        hide_professions=HideProfessions.RIDER_BALANCE,
        level0_attributes=Attributes(188, 93, 31, 23, 30, 56),
        growth_coefficients=(28.18, 13.96, 4.7, 3.49, 4.43, 0.56),
        talent=Talent("mohuahuangfushen", Talents.anxingnixing.value),
        weapon=Weapon(Weapons.zhiwangbupo.value),
        xingzhijing=Attributes(242, 102, 36, 0, 36, 10),
        xinghun={"critical_damage_percentage": 5},
        # fabao=Fabaos.zijinhulu.value
    )

    mohuahuangfushen1 = HeroTemp(
        name="魔化皇甫申",
        temp_id="mohuahuangfushen",
        basicInfo=None,
        flyable=True,
        has_formation=False,
        formation_temp=None,
        gender=Gender.MALE,
        element=Elements.DARK,
        profession=Professions.RIDER,
        hide_professions=HideProfessions.RIDER_BALANCE,
        level0_attributes=Attributes(188, 93, 31, 23, 30, 56),
        growth_coefficients=(28.18, 13.96, 4.7, 3.49, 4.43, 0.56),
        talent=Talent("mohuahuangfushen", Talents.anxingnixing.value),
        weapon=Weapon(Weapons.zhiwangbupo.value),
        xingzhijing=Attributes(194, 56, 61, 0, 59, 22),
        xinghun={"life_percentage": 5},
        # fabao=Fabaos.zijinhulu.value
    )

    fuyayu = HeroTemp(
        name="傅雅鱼",
        temp_id="fuyayu",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.shenwuxishu,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.PRIEST,
        hide_professions=HideProfessions.PRIEST,
        level0_attributes=Attributes(149, 19, 28, 77, 38, 25),
        growth_coefficients=(22.28, 2.89, 4.16, 11.54, 5.64, 0.25),
        talent=Talent("fuyayu", Talents.shenwuqimou.value),
        weapon=Weapon(Weapons.shenwuhanwei.value),
        xingzhijing=Attributes(188, 0, 25, 92, 36, 14),
        xinghun={"heal_percentage": 10},
        # fabao=Fabaos.shierpinliantai.value

    )

    huoyong = HeroTemp(
        name="霍雍",
        temp_id="huoyong",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.MALE,
        element=Elements.DARK,
        profession=Professions.SORCERER,
        hide_professions=HideProfessions.SORCERER_DAMAGE,
        level0_attributes=Attributes(163, 22, 29, 88, 32, 44),
        growth_coefficients=(24.43, 3.29, 4.38, 13.15, 4.75, 0.44),
        talent=Talent("huoyong", Talents.youfenhuashen.value),
        weapon=Weapon(Weapons.yourifusu.value),
        xingzhijing=Attributes(195, 0, 15, 112, 50, 0),
        xinghun={"range_skill_damage_percentage": 5}
    )

    zhujin = HeroTemp(
        name="朱槿",
        temp_id="zhujin",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.FEMALE,
        element=Elements.FIRE,
        profession=Professions.WARRIOR,
        hide_professions=HideProfessions.WARRIOR,
        level0_attributes=Attributes(156, 21, 34, 86, 23, 50),
        growth_coefficients=(23.35, 3.22, 5.1, 12.88, 3.49, 0.5),
        talent=Talent("zhujin", Talents.qilinqiongyu.value),
        weapon=Weapon(Weapons.qixiangdimi.value),
        xingzhijing=Attributes(150, 0, 54, 153, 0, 8),
        xinghun={"battle_damage_reduction_percentage": 5}
    )

    zhenyin = HeroTemp(
        name="真胤",
        temp_id="zhenyin",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.sanshentongzhi,
        gender=Gender.MALE,
        element=Elements.THUNDER,
        profession=Professions.GUARD,
        hide_professions=HideProfessions.GUARD_PROTECT,
        level0_attributes=Attributes(200, 81, 41, 20, 19, 45),
        growth_coefficients=(30.06, 12.21, 6.17, 3.05, 2.82, 0.45),
        talent=Talent("zhenyin", Talents.jinlunfatian.value),
        weapon=Weapon(Weapons.budaoshensen.value),
        xingzhijing=Attributes(166, 42, 46, 0, 35, 35),
        xinghun={"battle_damage_reduction_percentage": 5}
    )

    suijiu0 = HeroTemp(
        name="隋酒",
        temp_id="suijiu",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.GUARD,
        hide_professions=HideProfessions.GUARD_PROTECT,
        level0_attributes=Attributes(197, 81, 37, 20, 28, 27),
        growth_coefficients=(29.53, 12.08, 5.5, 3.02, 4.16, 0.27),
        talent=Talent("suijiu", Talents.hanlinhuachou.value),
        weapon=Weapon(Weapons.haoliweishi.value),
        xingzhijing=Attributes(174, 61, 29, 0, 76, 7),
        xinghun={"life_percentage": 5}
    )

    suijiu1 = HeroTemp(
        name="隋酒",
        temp_id="suijiu",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.GUARD,
        hide_professions=HideProfessions.GUARD_PROTECT,
        level0_attributes=Attributes(197, 81, 37, 20, 28, 27),
        growth_coefficients=(29.53, 12.08, 5.5, 3.02, 4.16, 0.27),
        talent=Talent("suijiu", Talents.hanlinhuachou.value),
        weapon=Weapon(Weapons.haoliweishi.value),
        xingzhijing=Attributes(190, 69, 49, 0, 30, 14),
        xinghun={"battle_damage_reduction_percentage": 5}
    )

    xiaohe = HeroTemp(
        name="萧熇",
        temp_id="xiaohe",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.MALE,
        element=Elements.FIRE,
        profession=Professions.GUARD,
        hide_professions=HideProfessions.GUARD_PROTECT,
        level0_attributes=Attributes(218, 79, 41, 20, 20, 25),
        growth_coefficients=(32.75, 11.81, 6.17, 2.95, 2.95, 0.25),
        talent=Talent("xiaohe", Talents.yuzhanwushuang.value),
        weapon=Weapon(Weapons.zhenjinbailian.value),
        xingzhijing=Attributes(214, 81, 33, 0, 50, 0),
        xinghun={"life_percentage": 5}
    )

    anyi0 = HeroTemp(
        name="安逸",
        temp_id="anyi",
        basicInfo=None,
        flyable=True,
        has_formation=True,
        formation_temp=Formations.jianzhuoyanran,
        gender=Gender.MALE,
        element=Elements.FIRE,
        profession=Professions.SWORDSMAN,
        hide_professions=HideProfessions.SWORDSMAN,
        level0_attributes=Attributes(197, 83, 39, 21, 16, 36),
        growth_coefficients=(29.53, 12.48, 5.91, 3.12, 2.42, 0.37),
        talent=Talent("anyi", Talents.lianhuozhuojian.value),
        weapon=Weapon(Weapons.lijiancuihuo.value),
        xingzhijing=Attributes(209, 66, 11, 0, 96, 0),
        xinghun={"single_target_skill_damage_percentage": 5}
    )

    anyi1 = HeroTemp(
        name="安逸",
        temp_id="anyi",
        basicInfo=None,
        flyable=True,
        has_formation=False,
        formation_temp=None,
        gender=Gender.MALE,
        element=Elements.FIRE,
        profession=Professions.SWORDSMAN,
        hide_professions=HideProfessions.SWORDSMAN,
        level0_attributes=Attributes(197, 83, 39, 21, 16, 36),
        growth_coefficients=(29.53, 12.48, 5.91, 3.12, 2.42, 0.37),
        talent=Talent("anyi", Talents.lianhuozhuojian.value),
        weapon=Weapon(Weapons.lijiancuihuo.value),
        xingzhijing=Attributes(211, 56, 38, 0, 53, 14),
        xinghun={"single_target_skill_damage_percentage": 5}
    )

    shuangshuang0 = HeroTemp(
        name="双双",
        temp_id="shuangshuang",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.tianshimingguang,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.SORCERER,
        hide_professions=HideProfessions.SORCERER_DAMAGE,
        level0_attributes=Attributes(174, 21, 21, 84, 36, 39),
        growth_coefficients=(26.04, 3.15, 3.22, 12.62, 5.37, 0.39),
        talent=Talent("shuangshuang", Talents.shangshandaoxin.value),
        weapon=Weapon(Weapons.chunshichuandao.value),
        xingzhijing=Attributes(190, 0, 0, 77, 72, 14),
        xinghun={"single_target_skill_damage_percentage": 5}
    )

    shuangshuang1 = HeroTemp(
        name="双双",
        temp_id="shuangshuang",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.tianshimingguang,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.SORCERER,
        hide_professions=HideProfessions.SORCERER_DAMAGE,
        level0_attributes=Attributes(174, 21, 21, 84, 36, 39),
        growth_coefficients=(26.04, 3.15, 3.22, 12.62, 5.37, 0.39),
        talent=Talent("shuangshuang", Talents.shangshandaoxin.value),
        weapon=Weapon(Weapons.chunshichuandao.value),
        xingzhijing=Attributes(139, 0, 25, 90, 65, 7),
        xinghun={"single_target_skill_damage_percentage": 5}
    )


    liyou0 = HeroTemp(
        name="黎幽",
        temp_id="liyou",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.FEMALE,
        element=Elements.DARK,
        profession=Professions.SORCERER,
        hide_professions=HideProfessions.SORCERER_DAMAGE,
        level0_attributes=Attributes(165, 22, 23, 89, 34, 65),
        growth_coefficients=(24.69, 3.36, 3.49, 13.42, 5.1, 0.65),
        talent=Talent("liyou", Talents.youmengminqi.value),
        weapon=Weapon(Weapons.juehensugu.value),
        xingzhijing=Attributes(199, 0, 73, 118, 0, 0),
        xinghun={"range_skill_damage_percentage": 5}
    )

    liyou1 = HeroTemp(
        name="黎幽",
        temp_id="liyou",
        basicInfo=None,
        flyable=False,
        has_formation=False,
        formation_temp=None,
        gender=Gender.FEMALE,
        element=Elements.DARK,
        profession=Professions.SORCERER,
        hide_professions=HideProfessions.SORCERER_DAMAGE,
        level0_attributes=Attributes(165, 22, 23, 89, 34, 65),
        growth_coefficients=(24.69, 3.36, 3.49, 13.42, 5.1, 0.65),
        talent=Talent("liyou", Talents.youmengminqi.value),
        weapon=Weapon(Weapons.juehensugu.value),
        xingzhijing=Attributes(213, 0, 62, 61, 12, 16),
        xinghun={"range_skill_damage_percentage": 5}
    )

    yuxiaoxue0 = HeroTemp(
        name="于小雪",
        temp_id="yuxiaoxue",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.tianenmiaoxue,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.PRIEST,
        hide_professions=HideProfessions.PRIEST,
        level0_attributes=Attributes(159, 18, 32, 73, 32, 28),
        growth_coefficients=(23.89, 2.75, 4.83, 11.01, 4.83, 0.28),
        talent=Talent("yuxiaoxue", Talents.cixuewaxin.value),
        weapon=Weapon(Weapons.xiayunpizhi.value),
        xingzhijing=Attributes(236, 0, 11, 102, 61, 7),
        xinghun={"life_percentage": 5}
    )

    yuxiaoxue1 = HeroTemp(
        name="于小雪",
        temp_id="yuxiaoxue",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.tianenmiaoxue,
        gender=Gender.FEMALE,
        element=Elements.WATER,
        profession=Professions.PRIEST,
        hide_professions=HideProfessions.PRIEST,
        level0_attributes=Attributes(159, 18, 32, 73, 32, 28),
        growth_coefficients=(23.89, 2.75, 4.83, 11.01, 4.83, 0.28),
        talent=Talent("yuxiaoxue", Talents.cixuewaxin.value),
        weapon=Weapon(Weapons.xiayunpizhi.value),
        xingzhijing=Attributes(197, 0, 39, 101, 29, 7),
        xinghun={"heal_percentage": 10}
    )
