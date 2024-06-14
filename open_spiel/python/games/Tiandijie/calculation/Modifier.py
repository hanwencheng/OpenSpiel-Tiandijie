from calculation.ModifierAttributes import ModifierAttributes


class Modifier:
    def __init__(self, modifier_dict):
        # self.attack: float = 0
        # self.magic_attack: float = 0
        # self.defense: float = 0
        # self.magic_defense: float = 0
        # self.magic_damage: float = 0
        # self.magic_damage_reduction: float = 0
        # self.heal: float = 0
        # self.life: float = 0
        # self.luck: float = 0
        # self.critical: float = 0
        # self.critical_reduction: float = 0
        #
        # self.attack_percentage: float = 0
        # self.skill_damage_percentage: float = 0
        # self.single_target_skill_damage_percentage: float = 0
        # self.multi_target_skill_damage_percentage: float = 0
        # self.normal_attack_damage_percentage: float = 0
        # self.battle_damage_percentage: float = 0
        #
        # self.magic_attack_percentage: float = 0
        # self.defense_percentage: float = 0
        # self.magic_defense_percentage: float = 0
        # self.physical_damage_percentage: float = 0
        # self.physical_damage_reduction_percentage: float = 0
        # self.magic_damage_percentage: float = 0
        # self.magic_damage_reduction_percentage: float = 0
        # self.heal_percentage: float = 0
        # self.life_percentage: float = 0
        #
        # self.luck_percentage: float = 0
        # self.critical_damage_percentage: float = 0
        # self.critical_damage_reduction_percentage: float = 0
        # self.fixed_damage_reduction_percentage: float = 0
        #
        # self.move_range: int = 0
        # self.attack_range: int = 0
        #
        # self.absolute_defense_range: int = 0
        # self.counterattack_first_limit: int = 0

        # self.is_passives_disabled: bool = False
        # self.is_action_disabled: bool = False
        # self.counterattack_disabled: bool = False
        # self.is_counterattack_first: bool = False

        for attribute_name in dir(ModifierAttributes):
            # if attribute_name.startswith("is_"):
            #     attribute_name = getattr(ModifierAttributes, attribute_name)
            #     setattr(self, attribute_name, False)
            if not attribute_name.startswith("__"):
                attribute_key = getattr(ModifierAttributes, attribute_name)
                setattr(self, attribute_key, 0)

        # Update attributes from dictionary
        for key, value in modifier_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
