from typing import List

from functools import partial
from open_spiel.python.games.Tiandijie.helpers import is_normal_attack_magic
from open_spiel.python.games.Tiandijie.primitives.hero.Element import Elements
from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import Gender, Professions, HideProfessions
from open_spiel.python.games.Tiandijie.primitives.hero.Attributes import Attributes, generate_max_level_attributes, get_neigong_enum_value
from open_spiel.python.games.Tiandijie.primitives.hero.BasicAttributes import AttributesTuple
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTemp import create_normal_attack_skill
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives import Passive


class HeroTemp:
    def __init__(
        self,
        name,
        temp_id,
        basicInfo,
        flyable,
        has_formation,
        formation_temp,
        gender,
        element,
        profession,
        hide_professions,
        level0_attributes,
        growth_coefficients,
        talent,
        weapon,
        xingzhijing,
        xinghun=None,
        fabao=None,
    ):
        self.current_life: float = 1
        self.name = name or "玄羽"
        self.rarity = "绝"
        self.temp_id = temp_id or "xuanyu"
        self.is_normal_attack_magic = is_normal_attack_magic(profession)
        self.normal_attack = create_normal_attack_skill(element, profession, None)
        self.flyable = flyable or False
        self.has_formation = has_formation
        self.formation_temp = formation_temp
        self.passives: List[Passive] = []
        self.gender = gender or Gender.FEMALE
        if self.gender not in Gender:
            raise ValueError("性别必须是‘男’或‘女’")
        self.element: Elements = element
        self.profession: Professions = profession
        self.hide_professions: HideProfessions = hide_professions
        self.movement: profession.value[2]
        self.level0_attributes: Attributes = level0_attributes or Attributes(172, 89, 31, 22, 23, 60)
        self.growth_coefficients: AttributesTuple = growth_coefficients
        self.talent = talent or "玄翎鸩影"
        self.initial_skill = "逐风破"
        self.skills = {
            "初级": ["魔", "幽镝戒杀"],
            "中级": ["飞羽憾魄"],
            "高级": ["迅", "奋力", "漫天箭雨", "摧心闇矢"],
            "特级": ["晦弓在弦"],
            "极级": ["魂", "贯甲咒"],
        }
        self.weapon = weapon
        self.weapon_features = self.weapon.temp.weapon_features
        # Attributes initialization
        self.current_attributes: Attributes = self.level0_attributes
        self.strength_attributes: Attributes = Attributes(*get_neigong_enum_value(self.hide_professions.name))
        self.xingzhijing: Attributes = xingzhijing
        self.initialize_attributes()
        self.content: int = 0
        self.has_shield: int = True if self.profession == Professions.WARRIOR else False
        self.xinghun = xinghun
        self.jishen = self.init_jishen()
        self.fabao = fabao

    def initialize_attributes(self):
        generate_max_level_attributes(
            self.current_attributes, self.growth_coefficients, self.hide_professions, self.temp_id
        )
        self.current_life = self.current_attributes.life

    def init_jishen(self):
        return ModifierEffect(partial(Rs.is_battle_attack_target), {"magic_damage_reduction_percentage": 10}) if self.is_normal_attack_magic else ModifierEffect(partial(Rs.is_battle_attack_target), {"physical_damage_reduction_percentage": 10})
