class ModifierAttributes:
    attack = "attack"
    magic_attack = "magic_attack"
    defense = "defense"
    magic_defense = "magic_defense"
    heal = "heal"
    life = "life"
    luck = "luck"
    critical_percentage = "critical"  # critical_damage
    critical_percentage_reduction = "critical_reduction"
    suffer_critical_percentage = "suffer_critical"  # 受到暴击绿
    suffer_critical_damage_percentage = "suffer_critical_damage"  # 受到暴击伤害减免
    attack_percentage = "attack_percentage"
    skill_damage_percentage = "skill_damage_percentage"
    single_target_skill_damage_percentage = "single_target_skill_damage_percentage"
    single_target_skill_damage_reduction_percentage = (
        "single_target_skill_damage_reduction_percentage"
    )
    range_skill_damage_percentage = "range_skill_damage_percentage"
    range_skill_damage_reduction_percentage = "range_skill_damage_reduction_percentage"
    normal_attack_damage_percentage = "normal_attack_damage_percentage"
    normal_attack_damage_reduction_percentage = (
        "normal_attack_damage_reduction_percentage"
    )
    physical_penetration_percentage = "physical_penetration_percentage"
    magic_penetration_percentage = "magic_penetration_percentage"
    battle_damage_percentage = "battle_damage_percentage"
    battle_damage_reduction_percentage = "battle_damage_reduction_percentage"
    magic_attack_percentage = "magic_attack_percentage"
    defense_percentage = "defense_percentage"
    magic_defense_percentage = "magic_defense_percentage"
    physical_damage_percentage = "physical_damage_percentage"
    physical_damage_reduction_percentage = "physical_damage_reduction_percentage"
    active_damage_percentage = "active_damage_percentage"
    counterattack_damage_percentage = "counterattack_damage_percentage"
    magic_damage_percentage = "magic_damage_percentage"
    magic_damage_reduction_percentage = "magic_damage_reduction_percentage"
    heal_percentage = "heal_percentage"
    life_percentage = "life_percentage"
    luck_percentage = "luck_percentage"
    critical_damage_percentage = "critical_damage_percentage"
    critical_damage_reduction_percentage = (
        "critical_damage_reduction_percentage"  # 暴击伤害降低
    )
    fixed_damage_percentage = "fixed_damage_percentage"
    fixed_damage_reduction_percentage = "fixed_damage_reduction_percentage"
    move_range = "move_range"
    max_move_range = "max_move_range "
    attack_range = "attack_range"
    physical_protect_range = "physical_protect_range"
    magic_protect_range = "magic_protect_range"
    counterattack_first_limit = "counterattack_first_limit"
    counterattack_range = "counterattack_range"
    range_skill_range = "range_skill_range"
    single_skill_range = "single_skill_range"
    active_skill_range = "active_skill_range"
    shield_percentage = "shield_percentage"
    restrict_area = "restrict_area"
    chase_attack_percentage = "chase_attack_percentage"
    suffer_physical_damage_percentage = "suffer_physical_damage_percentage"
    suffer_magic_damage_percentage = "suffer_magic_damage_percentage"
    suffer_physical_damage_reduction_percentage = (
        "suffer_physical_damage_reduction_percentage"
    )
    suffer_magic_damage_reduction_percentage = (
        "suffer_magic_damage_reduction_percentage"
    )

    # 属相免伤
    fire_damage_reduction_percentage = "fire_damage_reduction_percentage"
    thunder_damage_reduction_percentage = "thunder_damage_reduction_percentage"
    water_damage_reduction_percentage = "water_damage_reduction_percentage"
    ethereal_damage_reduction_percentage = "ethereal_damage_reduction_percentage"
    light_damage_reduction_percentage = "light_damage_reduction_percentage"
    dark_damage_reduction_percentage = "dark_damage_reduction_percentage"

    element_attacker_multiplier = "element_attacker_multiplier"
    element_defender_multiplier = "element_defender_multiplier"
    ignore_element_advantage = "ignore_element_advantage"

    is_passives_skill_disabled = "passives_disabled"  # 禁用被动绝学
    is_active_skill_disabled = "active_skill_disabled"  # 禁用主动绝学
    is_counterattack_disabled = "counterattack_disabled"  # 禁用反击
    is_double_attack_disabled = "double_attack_disabled"  # 禁用连击
    is_chase_attack_disabled = "chase_attack_disabled"  # 禁用追击
    is_dodge_disabled = "dodge_disabled"  # 禁用闪避
    is_action_disabled = "action_disabled"  # 无法行动
    is_extra_move_disabled = "extra_move_disabled"  # 禁用额外移动
    is_extra_action_disabled = "is_extra_action_disabled"  # 禁用额外行动
    is_extra_move_range_disable = "is_extra_move_range_disable"  # 禁止在移动
    is_certain_skill_disabled = "certain_skill_disabled"  # 禁用特定技能
    is_heal_disabled = "is_heal_disabled"  # 禁用治疗
    is_repelled_disabled = "is_repelled_disabled"  # 禁用位移
    is_block_fatal_damage_disabled = (
        "is_block_fatal_damage_disabled"  # 禁用抵挡致命伤害
    )
    is_attack_disabled = "is_attack_disabled"  # 禁用攻击

    is_double_attack = "double_attack"  # 是否连击
    is_dodge_attack = "is_dodge_attack"  # 是否闪避攻击
    is_counterattack_first = "counterattack_first"  # 是否先攻
    is_non_selectable = "non_selectable"  # 无法被选中

    is_ignore_protector = "ignore_protector"  # 光环：敌人无法护卫
    restrict_by_obstacles_range = (
        "restrict_by_obstacles_range"  # 光环：具有轻功能力的角色翻越障碍能力失效
    )
    is_ignore_block = "is_ignore_block"  # 光环：无视敌人障碍
    is_ignore_obstacle = "ignore_obstacle"  # 可跨越障碍
    prevent_death = "prevent_death"  # 无法死亡
    is_unconsume_move_range = "is_unconsume_move_range"  # 不消耗移动力
    is_only_move_to_caster = "is_only_move_to_caster"  # 只能移动到施法者
    is_only_attack_to_caster = "is_only_attack_to_caster"  # 只能攻击施法者
    is_attack_to_caster_disable = "is_attack_to_caster_disable"  # 禁止攻击施法者
    is_immunity_fix_damage = "is_immunity_fix_damage"  # 免疫固伤

    is_wufangjiejie_disabled = "wufangjiejie_disabled"
    is_jixing_disabled = "jixing_disabled"
