# print("=======================================计算伤害==================================================")
# print("calculate_skill_damage111:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
# print("攻击面板", get_attack(attacker_instance, target_instance, context, is_magic), "\n",
#       "克制伤害加成系数", attacker_elemental_multiplier, "\n",
#       "防御面板", get_defense_with_penetration(attacker_instance, target_instance, context, is_magic), "\n",
#       "基础伤害计算为", attack_defense_difference, "\n",
#       "-\n",
#       "暴击率", critical_probability, "\n",
#       "技能名", skill.temp.id if skill else "无", "\n",
#       "技能伤害系数", skill.temp.multiplier if skill else 0, "\n",
#       "伤害加成", get_damage_modifier(attacker_instance, target_instance, skill, is_magic, context), "\n",
#       "免伤加成", get_damage_reduction_modifier(target_instance, attacker_instance, is_magic, context), "\n",
#       "暴击倍率", CRIT_MULTIPLIER, "\n",
#       "暴击伤害加成", get_critical_damage_modifier(attacker_instance, target_instance, context), "\n",
#       "暴击承伤加成", get_critical_damage_reduction_modifier(target_instance, attacker_instance, context)
#       )
# from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#     accumulate_equipments_modifier, get_buff_modifier, get_formation_modifier, get_weapon_modifier
#
# print("=======================================计算增伤==================================================")
# print("get_damage_modifier:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
# print(
#     "天赋增伤", accumulate_talents_modifier("magic_damage_percentage", attacker_instance, target_instance, context),
#     "\n",
#     "技能增伤", get_skill_modifier("magic_damage_percentage", attacker_instance, target_instance, skill, context), "\n",
#     "被动增伤（属于技能）", accumulate_attribute(attacker_instance.temp.passives, "magic_damage_percentage"), "\n",
#     "临时buff增伤", get_buff_modifier("magic_damage_percentage", attacker_instance, target_instance, context), "\n",
#     "武器增伤", get_weapon_modifier("magic_damage_percentage", attacker_instance, target_instance, context), "\n",
#     "魂石套装增伤",
#     accumulate_suit_stone_attribute(attacker_instance, target_instance, "magic_damage_percentage", context), "\n",
#     "饰品增伤", accumulate_equipments_modifier("magic_damage_percentage", attacker_instance, target_instance, context),
#     "\n",
#     "战阵增伤", get_formation_modifier("magic_damage_percentage", attacker_instance, target_instance, context), "\n",
#     "单体群体增伤", get_action_type_damage_modifier(attacker_instance, target_instance, context), "\n",
#     "魂石词条增伤", accumulate_stone_attribute(attacker_instance.stones, "magic_damage_percentage"), "\n",
#     "列星+魂石词条增伤", 1 + (LIEXING_DAMAGE_INCREASE + accumulate_stone_attribute(attacker_instance.stones,
#                                                                                    "magic_damage_percentage") + LIEXING_DAMAGE_INCREASE) / 100
# )
# print("=======================================计算减伤==================================================")
# print("get_damage_modifier:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
# print(
#     "天赋减伤",
#     accumulate_talents_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context), "\n",
#     "技能减伤",
#     get_skill_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, skill, context), "\n",
#     "被动减伤（属于技能）", accumulate_attribute(target_instance.temp.passives, "magic_damage_reduction_percentage"),
#     "\n",
#     "临时buff减伤", get_buff_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context),
#     "\n",
#     "武器增伤", get_weapon_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context),
#     "\n",
#     "魂石套装减伤",
#     accumulate_suit_stone_attribute(target_instance, attacker_instance, "magic_damage_reduction_percentage", context),
#     "\n",
#     "饰品减伤",
#     accumulate_equipments_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context),
#     "\n",
#     "战阵减伤",
#     get_formation_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context), "\n",
#     "魂石词条减伤", accumulate_stone_attribute(target_instance.stones, "magic_damage_reduction_percentage"), "\n",
#     "列星+魂石词条减伤", 1 - (LIEXING_DAMAGE_REDUCTION + accumulate_stone_attribute(target_instance.stones,
#                                                                                     "magic_damage_reduction_percentage")) / 100
# )


# print("=======================================计算反击伤害==================================================")
# print("calculate_skill_damage111:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
# print("攻击面板", get_attack(attacker_instance, target_instance, context, is_magic), "\n",
#       "克制伤害加成系数", attacker_elemental_multiplier, "\n",
#       "防御面板", get_defense_with_penetration(attacker_instance, target_instance, context, is_magic), "\n",
#       "基础伤害计算为", attack_defense_difference, "\n",
#       "-\n",
#       "暴击率", critical_probability, "\n",
#       "反击伤害加成", get_counterattack_damage_modifier(attacker_instance, target_instance, is_magic, context), "\n",
#       "反击免伤加成",
#       get_counterattack_damage_reduction_modifier(target_instance, attacker_instance, is_magic, context), "\n",
#       "暴击倍率", CRIT_MULTIPLIER, "\n",
#       "暴击伤害加成", get_critical_damage_modifier(attacker_instance, target_instance, context), "\n",
#       "暴击承伤加成", get_critical_damage_reduction_modifier(target_instance, attacker_instance, context)
#       )
# from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#     accumulate_equipments_modifier, get_buff_modifier, get_formation_modifier, get_weapon_modifier
#
# print("=======================================计算反击增伤==================================================")
# print("get_damage_modifier:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
# print(
#     "天赋法术增伤", accumulate_talents_modifier("magic_damage_percentage", attacker_instance, target_instance, context),
#     "\n",
#     "被动法术增伤", accumulate_attribute(attacker_instance.temp.passives, "magic_damage_percentage"), "\n",
#     "临时buff法术增伤", get_buff_modifier("magic_damage_percentage", attacker_instance, target_instance, context), "\n",
#     "武器法术增伤", get_weapon_modifier("magic_damage_percentage", attacker_instance, target_instance, context), "\n",
#     "魂石套装法术增伤",
#     accumulate_suit_stone_attribute(attacker_instance, target_instance, "magic_damage_percentage", context), "\n",
#     "饰品法术增伤",
#     accumulate_equipments_modifier("magic_damage_percentage", attacker_instance, target_instance, context), "\n",
#     "战阵法术增伤", get_formation_modifier("magic_damage_percentage", attacker_instance, target_instance, context),
#     "\n",
#     "魂石词条法术增伤", accumulate_stone_attribute(attacker_instance.stones, "magic_damage_percentage"), "\n",
#     "反击词条增伤",
#     get_level2_modifier(attacker_instance, target_instance, ma.counterattack_damage_percentage, context), "\n",
#     "列星+魂石词条增伤", 1 + (LIEXING_DAMAGE_INCREASE + accumulate_stone_attribute(attacker_instance.stones,
#                                                                                    "magic_damage_percentage") + LIEXING_DAMAGE_INCREASE) / 100
# )
# print("=======================================计算反击减伤==================================================")
# print("get_damage_reduction_modifier:", "攻击者", attacker_instance.id, "被攻击者", target_instance.id)
# print(
#     "天赋减伤",
#     accumulate_talents_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context), "\n",
#     "被动减伤（属于技能）", accumulate_attribute(target_instance.temp.passives, "magic_damage_reduction_percentage"),
#     "\n",
#     "临时buff减伤", get_buff_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context),
#     "\n",
#     "武器增伤", get_weapon_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context),
#     "\n",
#     "魂石套装减伤",
#     accumulate_suit_stone_attribute(target_instance, attacker_instance, "magic_damage_reduction_percentage", context),
#     "\n",
#     "饰品减伤",
#     accumulate_equipments_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context),
#     "\n",
#     "战阵减伤",
#     get_formation_modifier("magic_damage_reduction_percentage", target_instance, attacker_instance, context), "\n",
#     "魂石词条减伤", accumulate_stone_attribute(target_instance.stones, "magic_damage_reduction_percentage"), "\n",
#     "列星+魂石词条减伤", 1 - (LIEXING_DAMAGE_REDUCTION + accumulate_stone_attribute(target_instance.stones,
#                                                                                     "magic_damage_reduction_percentage")) / 100
# )


# print("=======================================计算生命值面板==========================================")
# print("get_max_life:", "统计对象", hero_instance.id, "编程职业", hero_instance.temp.hide_professions.name)
# print("黑字基础气血：", life_attribute, "\n",
#       "绿字基础气血：", get_level1_modified_result(hero_instance, ma.life,
#                                                   life_attribute) + hero_instance.temp.strength_attributes.life + hero_instance.temp.xingzhijing.life - life_attribute,
#       "\n",
#       "进图前气血：", basic_life, "\n",
#       "魂石数值词条：", accumulate_stone_attribute(hero_instance.stones, ma.life), "\n",
#       "魂石百分比词条：", accumulate_stone_attribute(hero_instance.stones, ma.life + "_percentage"), "\n",
#       "内功大成数值：", hero_instance.temp.strength_attributes.life, "\n",
#       "星之晶数值：", hero_instance.temp.xingzhijing.life, "\n",
#       )
# print("=======================================计算生命值面板(进图后)==========================================")
# from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#     accumulate_equipments_modifier, get_formation_modifier, get_passives_modifier, get_buff_modifier
#
# print(
#     "进图后气血：", basic_life * (
#             1
#             + (
#                     get_level2_modifier(
#                         hero_instance, target_instance, ma.life_percentage, context, is_basic
#                     )
#                     + JIANREN
#             ) / 100
#     ), "\n",
#     "魂石套装百分比", accumulate_suit_stone_attribute(hero_instance, target_instance, ma.life_percentage, context),
#     "\n",
#     "天赋百分比", accumulate_talents_modifier(ma.life_percentage, hero_instance, target_instance, context), "\n",
#     "饰品百分比", accumulate_equipments_modifier(ma.life_percentage, hero_instance, target_instance, context), "\n",
#     "战阵百分比", get_formation_modifier(ma.life_percentage, hero_instance, target_instance, context), "\n",
#     "被动百分比", get_passives_modifier(hero_instance.enabled_passives, ma.life_percentage), "\n",
#     "buff百分比", get_buff_modifier(ma.life_percentage, hero_instance, target_instance, context), "\n",
# )


#
# if is_magic:
#     print("=======================================计算法防面板==================================================")
#     print("get_attack:", "统计对象", hero_instance.id, "编程职业", hero_instance.temp.hide_professions.name)
#     print("黑字基础：", defense_attribute, "\n",
#           "绿字基础气血：", get_level1_modified_result(hero_instance, ma.magic_defense, defense_attribute) + hero_instance.temp.strength_attributes.magic_defense + hero_instance.temp.xingzhijing.magic_defense - defense_attribute, "\n",
#           "进图前气血：", basic_defense, "\n",
#           "魂石数值词条：", accumulate_stone_attribute(hero_instance.stones,  ma.magic_defense), "\n",
#           "魂石百分比词条：", accumulate_stone_attribute(hero_instance.stones, ma.magic_defense + "_percentage"), "\n",
#           "内功数值：", hero_instance.temp.strength_attributes.magic_defense, "\n",
#           "星之晶数值：", hero_instance.temp.xingzhijing.magic_defense, "\n",
#           )
# else:
#     print("=======================================计算物防面板==================================================")
#     print("get_attack:", "统计对象", hero_instance.id, "编程职业", hero_instance.temp.hide_professions.name)
#     print("黑字基础：", defense_attribute, "\n",
#           "绿字基础气血：", get_level1_modified_result(hero_instance, ma.defense, defense_attribute) + hero_instance.temp.strength_attributes.defense + hero_instance.temp.xingzhijing.defense - defense_attribute, "\n",
#           "进图前气血：", basic_defense, "\n",
#           "魂石数值词条：", accumulate_stone_attribute(hero_instance.stones,  ma.defense), "\n",
#           "魂石百分比词条：", accumulate_stone_attribute(hero_instance.stones, ma.defense + "_percentage"), "\n",
#           "内功数值：", hero_instance.temp.strength_attributes.defense, "\n",
#           "星之晶数值：", hero_instance.temp.xingzhijing.defense, "\n",
#           )
# if is_magic:
#     print("=======================================计算法防面板(进图后)==================================================")
# else:
#     print("=======================================计算物防面板(进图后)==================================================")
# from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#     accumulate_equipments_modifier, get_formation_modifier, get_passives_modifier, get_buff_modifier
# print(
#     "进图后：", basic_defense * (1 + get_level2_modifier(
# hero_instance, counter_instance, attr_name+"_percentage", context, is_basic
# )/100), "\n",
#     "进图后加成：", get_level2_modifier(
# hero_instance, counter_instance, attr_name+"_percentage", context, is_basic
# ), "\n",
#     "魂石套装百分比", accumulate_suit_stone_attribute(hero_instance, counter_instance, attr_name+"_percentage", context), "\n",
#     "天赋百分比", accumulate_talents_modifier(attr_name+"_percentage", hero_instance, counter_instance, context), "\n",
#     "饰品百分比", accumulate_equipments_modifier(attr_name+"_percentage", hero_instance, counter_instance, context), "\n",
#     "战阵百分比", get_formation_modifier(attr_name+"_percentage", hero_instance, counter_instance, context), "\n",
#     "被动百分比", get_passives_modifier(hero_instance.enabled_passives, attr_name+"_percentage"), "\n",
#     "buff百分比", get_buff_modifier(attr_name+"_percentage", hero_instance, counter_instance, context), "\n",
# )


#
#
#
# if is_magic:
#     print("=======================================计算法攻面板==================================================")
#     print("get_attack:", "统计对象", actor_instance.id, "编程职业", actor_instance.temp.hide_professions.name)
#     print("黑字基础：", attack_attribute, "\n",
#           "绿字基础气血：", get_level1_modified_result(actor_instance, ma.magic_attack, attack_attribute) + actor_instance.temp.strength_attributes.magic_attack + actor_instance.temp.xingzhijing.magic_attack - attack_attribute, "\n",
#           "进图前气血：", basic_attack, "\n",
#           "魂石数值词条：", accumulate_stone_attribute(actor_instance.stones,  ma.magic_attack), "\n",
#           "魂石百分比词条：", accumulate_stone_attribute(actor_instance.stones, ma.magic_attack + "_percentage"), "\n",
#           "内功数值：", actor_instance.temp.strength_attributes.magic_attack, "\n",
#           "星之晶数值：", actor_instance.temp.xingzhijing.magic_attack, "\n",
#           )
# else:
#     print("=======================================计算物攻面板==================================================")
#     print("get_attack:", "统计对象", actor_instance.id, "编程职业", actor_instance.temp.hide_professions.name)
#     print("黑字基础：", attack_attribute, "\n",
#           "绿字基础气血：", get_level1_modified_result(actor_instance, ma.attack, attack_attribute) + actor_instance.temp.strength_attributes.attack + actor_instance.temp.xingzhijing.attack - attack_attribute, "\n",
#           "进图前气血：", basic_attack, "\n",
#           "魂石数值词条：", accumulate_stone_attribute(actor_instance.stones,  ma.attack), "\n",
#           "魂石百分比词条：", accumulate_stone_attribute(actor_instance.stones, ma.attack + "_percentage"), "\n",
#           "内功数值：", actor_instance.temp.strength_attributes.attack, "\n",
#           "星之晶数值：", actor_instance.temp.xingzhijing.attack, "\n",
#           )
# if is_magic:
#     print("=======================================计算法攻面板(进图后)==================================================")
#     from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#         accumulate_equipments_modifier, get_formation_modifier, get_passives_modifier, get_buff_modifier
#     print(
#         "进图后：", basic_attack * (1 + get_level2_modifier(
#     actor_instance, target_instance, attr_name+"_percentage", context, is_basic
#     )/100), "\n",
#         "进图后加成：",get_level2_modifier(
#     actor_instance, target_instance, attr_name+"_percentage", context, is_basic
#     ), "\n",
#         "魂石套装百分比", accumulate_suit_stone_attribute(actor_instance, target_instance, attr_name+"_percentage", context), "\n",
#         "天赋百分比", accumulate_talents_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#         "饰品百分比", accumulate_equipments_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#         "战阵百分比", get_formation_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#         "被动百分比", get_passives_modifier(actor_instance.enabled_passives, attr_name+"_percentage"), "\n",
#         "buff百分比", get_buff_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#     )
# else:
#     print("=======================================计算物攻面板(进图后)==================================================")
#     from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#         accumulate_equipments_modifier, get_formation_modifier, get_passives_modifier, get_buff_modifier
#     print(
#         "进图后：", basic_attack * (1 + get_level2_modifier(
#     actor_instance, target_instance, attr_name+"_percentage", context, is_basic
#     )/100), "\n",
#         "进图后加成：",get_level2_modifier(
#     actor_instance, target_instance, attr_name+"_percentage", context, is_basic
#     ), "\n",
#         "魂石套装百分比", accumulate_suit_stone_attribute(actor_instance, target_instance, attr_name+"_percentage", context), "\n",
#         "天赋百分比", accumulate_talents_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#         "饰品百分比", accumulate_equipments_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#         "战阵百分比", get_formation_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#         "被动百分比", get_passives_modifier(actor_instance.enabled_passives, attr_name+"_percentage"), "\n",
#         "buff百分比", get_buff_modifier(attr_name+"_percentage", actor_instance, target_instance, context), "\n",
#     )


#
# if actor_hero.id == "fuyayu1":
#     print("=======================================计算会心力面板==================================================")
#     print("get_luck:", "统计对象", actor_hero.id, "编程职业", actor_hero.temp.hide_professions.name)
#     print("黑字基础会心：", actor_hero.initial_attributes.luck, "\n",
#           "绿字基础会心：", total_luck - actor_hero.initial_attributes.luck, "\n",
#           "星之晶数值：", actor_hero.temp.xingzhijing.luck, "\n",
#           "进图前会心：", luck_attribute, "\n",
#           )
#     print(
#         "=======================================计算会心面板(进图后)==================================================")
#     from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import accumulate_talents_modifier, \
#         accumulate_equipments_modifier, get_formation_modifier, get_passives_modifier, get_buff_modifier
#
#     print(
#         "进图后会心：", total_luck, "\n",
#         "魂石套装百分比", accumulate_suit_stone_attribute(actor_hero, counter_instance, ma.luck_percentage, context), "\n",
#         "天赋百分比", accumulate_talents_modifier(ma.luck_percentage, actor_hero, counter_instance, context), "\n",
#         "饰品百分比", accumulate_equipments_modifier(ma.luck_percentage, actor_hero, counter_instance, context), "\n",
#         "战阵百分比", get_formation_modifier(ma.luck_percentage, actor_hero, counter_instance, context), "\n",
#         "被动百分比", get_passives_modifier(actor_hero.enabled_passives, ma.luck_percentage), "\n",
#         "buff百分比", get_buff_modifier(ma.luck_percentage, actor_hero, counter_instance, context), "\n",
#     )




from open_spiel.python.games.Tiandijie.primitives.hero.BasicAttributes import NeigongAmplifier
from open_spiel.python.games.Tiandijie.primitives.hero.HeroBasics import HideProfessions
from open_spiel.python.games.Tiandijie.primitives.hero.Attributes import Attributes
def get_neigong_enum_value(identifier):
    return NeigongAmplifier[identifier].value
a = Attributes(*get_neigong_enum_value(HideProfessions.SORCERER_DAMAGE.name))
print(a.magic_attack)
