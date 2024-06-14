from enum import Enum
from typing import TYPE_CHECKING

from primitives.hero.HeroBasics import Gender, Professions, HideProfessions
from primitives.hero.HeroTemp import HeroTemp
from primitives.formation.formations import Formations
from primitives.hero.Element import Elements
from primitives.hero.Attributes import Attributes
from primitives.talent.talents import Talents
from primitives.Weapons import Weapons


class HeroeTemps(Enum):
    mohuahuangfushen = HeroTemp(
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
        talent=Talents.anxingnixing.value,
        weapons=Weapons.zhiwangbupo.value,
        skills=None,
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
        talent=Talents.shenwuqimou.value,
        weapons=Weapons.shenwuhanwei.value,
        skills=None,
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
        talent=Talents.youfenhuashen.value,
        weapons=Weapons.yourifusu.value,
        skills=None,
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
        talent=Talents.qilinqiongyu.value,
        weapons=Weapons.qixiangdimi.value,
        skills=None,
    )

    zhenyin = HeroTemp(
        name="真胤",
        temp_id="zhenyin",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.sanshentongzhi,
        gender=Gender.MALE,
        element=Elements.ETHEREAL,
        profession=Professions.GUARD,
        hide_professions=HideProfessions.GUARD_PROTECT,
        level0_attributes=Attributes(200, 81, 41, 20, 19, 45),
        growth_coefficients=(30.06, 12.21, 6.17, 3.05, 2.82, 0.45),
        talent=Talents.jinlunfatian.value,
        weapons=Weapons.budaoshensen.value,
        skills=None,
    )

    zhenyin1 = HeroTemp(
        name="真胤1",
        temp_id="zhenyin",
        basicInfo=None,
        flyable=False,
        has_formation=True,
        formation_temp=Formations.sanshentongzhi,
        gender=Gender.MALE,
        element=Elements.ETHEREAL,
        profession=Professions.GUARD,
        hide_professions=HideProfessions.GUARD_PROTECT,
        level0_attributes=Attributes(200, 81, 41, 20, 19, 45),
        growth_coefficients=(30.06, 12.21, 6.17, 3.05, 2.82, 0.45),
        talent=Talents.jinlunfatian.value,
        weapons=Weapons.budaoshensen.value,
        skills=None,
    )
