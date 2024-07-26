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
#     "列星+魂石词条增伤", 1 + (XINGYAO_DAMAGE_INCREASE + accumulate_stone_attribute(attacker_instance.stones,
#                                                                                    "magic_damage_percentage") + XINGYAO_DAMAGE_INCREASE) / 100
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
#     "列星+魂石词条减伤", 1 - (XINGYAO_DAMAGE_REDUCTION + accumulate_stone_attribute(target_instance.stones,
#                                                                                     "magic_damage_reduction_percentage")) / 100
# )

# print((6268-1596*0.8)*0.3*1.23*1.08)
# #A类 兵刃 5  及身 10     B类
# fabao = [1]
# if fabao:
#     print(1)
# else:
#     print(2)
# from open_spiel.python.games.Tiandijie.primitives.hero.BasicAttributes import NeigongAmplifier
# def get_hero_in_skill(target, target_hero_list, skill, moveable_position):
#     return [target] + [
#         effect_hero for effect_hero in target_hero_list
#         if effect_hero != target and skill.temp.range_instance.check_if_target_in_range(
#             moveable_position, target.position, effect_hero.position, context.battlemap
#         )
#     ]


print(3385/(1.1*1.1))
print(3383-2797.5206611570243)
print(585.4793388429757/1469)