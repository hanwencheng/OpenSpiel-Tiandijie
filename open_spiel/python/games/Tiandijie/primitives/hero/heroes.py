from enum import Enum
from typing import TYPE_CHECKING

from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Gender, Professions, HideProfessions
from open_spiel.python.games.Tiandijie.primitives.hero.HeroTemp import HeroTemp
from open_spiel.python.games.Tiandijie.primitives.formation.formations import Formations
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.hero.Attributes import Attributes
from open_spiel.python.games.Tiandijie.primitives.talent.talents import Talents
from open_spiel.python.games.Tiandijie.primitives.Weapons import Weapons
from open_spiel.python.games.Tiandijie.primitives.fabao import Fabaos


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
        xingzhijing=Attributes(194, 56, 61, 0, 59, 22),
        xinghun={"critical_damage_percentage": 5}
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
        xingzhijing=Attributes(188, 0, 25, 92, 36, 14),
        xinghun={"heal_percentage": 10},
        fabao=Fabaos.shierpinliantai.value

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
        talent=Talents.qilinqiongyu.value,
        weapons=Weapons.qixiangdimi.value,
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
        talent=Talents.jinlunfatian.value,
        weapons=Weapons.budaoshensen.value,
        xingzhijing=Attributes(166, 42, 46, 0, 35, 35),
        xinghun={"battle_damage_reduction_percentage": 5}
    )

    zhenyin1 = HeroTemp(
        name="真胤1",
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
        talent=Talents.jinlunfatian.value,
        weapons=Weapons.budaoshensen.value,
        xingzhijing=Attributes(166, 42, 46, 0, 35, 35),
        xinghun={"battle_damage_reduction_percentage": 5}
    )
