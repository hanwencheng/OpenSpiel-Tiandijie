from enum import Enum
from open_spiel.python.games.Tiandijie.calculation.ModifierAttributes import ModifierAttributes as Ma
from open_spiel.python.games.Tiandijie.primitives.RequirementCheck.RequirementsCheck import RequirementCheck as Rs
from open_spiel.python.games.Tiandijie.primitives.effects.ModifierEffect import ModifierEffect
from open_spiel.python.games.Tiandijie.primitives.effects.EventListener import EventListener
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.calculation.Effects import Effects
from functools import partial


class Stone:
    def __init__(self, id, effect, value, event=None, max_stack=1):
        self.id = id
        self.effect = effect  # [天, 地, 荒]
        self.value = value  # [带两个, 带三个]
        self.event = event
        self.stack = 0
        self.max_stack = max_stack


class Stones(Enum):
    # wumian = Stone(
    #     effect = ["life", attack", "defense", "magic_attack", "magic_defense", "luck"],
    #     value = [0, 0, 0, 0, 0],
    #     percentage = [0, 0, 0, 0, 0]
    # )
    @classmethod
    def get_stone_by_id(cls, stone_id):
        for stone in cls:
            if stone.value.id == stone_id:
                return stone.value
        return None

    wumian = Stone(
        id="wumian",
        effect=[
            {
                "life": 747,
                "attack": 403,
                "defense": 0,
                "magic_attack": 0,
                "magic_defense": 0,
            },
            {
                "life": 0,
                "attack": 0,
                "defense": 282,
                "magic_attack": 0,
                "magic_defense": 242,
            },
            {
                "life": 868,
                "attack": 363,
                "defense": 0,
                "magic_attack": 0,
                "magic_defense": 0,
            },
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.luck_percentage: 25}),
            ],
            [
                ModifierEffect(
                    partial(Rs.self_is_batter_attacker_and_luck_is_higher),
                    {Ma.battle_damage_percentage: 10, Ma.critical_percentage: 10},
                ),
            ],
        ],
    )

    wanghuan = Stone(
        id="wanghuan",
        effect=[
            {
                "life": 747,
                "attack": 403,
                "life_percentage": 4,
                "attack_percentage": 10,
                "physical_damage_percentage": 8,
                "critical_percentage": 7,
            },
            {
                "defense": 242,
                "magic_defense": 282,
                "life_percentage": 10,
                "magic_damage_reduction_percentage": 8,
                "defense_percentage": 7,
                "physical_damage_percentage": 5,
            },
            {
                "life": 868,
                "attack": 363,
                "physical_damage_reduction_percentage": 5,
                "life_percentage": 6,
                "magic_damage_reduction_percentage": 5,
                "attack_percentage": 7,
            },
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.life_percentage: 10}),
            ],
            [
                ModifierEffect(
                    partial(Rs.BuffChecks.wanghuan_stack_count),
                    {
                        Ma.attack_percentage: 3,
                        Ma.magic_attack_percentage: 3,
                        Ma.defense_percentage: 3,
                        Ma.magic_defense_percentage: 3,
                        Ma.luck_percentage: 3,
                    },
                ),
            ],
        ],
    )

    # 三枚	对友方使用绝学后，40%概率使目标获得1个随机「有益状态」。
    minkui = Stone(
        id="minkui",
        effect=[
            {
                "life": 706,
                "magic_attack": 363,
                Ma.counterattack_damage_percentage: 5,
                Ma.magic_attack_percentage: 10,
                Ma.magic_damage_reduction_percentage: 5,
                Ma.life_percentage: 5,
            },
            {
                "defense": 262,
                "magic_defense": 343,
                Ma.magic_damage_reduction_percentage: 10,
                Ma.physical_damage_reduction_percentage: 6,
                Ma.life_percentage: 9,
                Ma.magic_damage_percentage: 3,
            },
            {
                "life": 807,
                "magic_attack": 323,
                Ma.life_percentage: 4,
                Ma.physical_damage_reduction_percentage: 7,
                Ma.magic_defense_percentage: 6,
                Ma.magic_attack_percentage: 3,
            },
        ],
        value=[
            [
                ModifierEffect(Rs.always_true, {Ma.life_percentage: 10}),
            ],
            [],
        ],
        event=[
            EventListener(
                EventTypes.skill_end,
                1,
                partial(Rs.skill_is_no_damage_and_target_is_partner),
                partial(Effects.take_effect_of_minkui),
            )
        ],
    )

    # 两枚	法攻+5%
    # 三枚	使用绝学时伤害提升10%，使用范围绝学时伤害额外提高5%
    zhuyanmohuo = Stone(
        "zhuyanmohuo",
        [
            {
                "life": 666,
                "magic_attack": 403,
                Ma.counterattack_damage_percentage: 10,
                Ma.magic_attack_percentage: 10,
                Ma.magic_damage_percentage: 10,
                Ma.magic_penetration_percentage: 4,
            },
            {
                "defense": 242,
                "magic_defense": 323,
                Ma.magic_damage_percentage: 3,
                Ma.magic_attack_percentage: 5,
                Ma.magic_penetration_percentage: 4,
                Ma.life_percentage: 9
            },
            {
                "life": 767,
                "magic_attack": 363,
                Ma.suffer_critical_damage_reduction_percentage: 3,
                Ma.magic_damage_percentage: 5,
                Ma.critical_percentage: 4,
                Ma.magic_attack_percentage: 7,
            },
        ],
        [
            [
                ModifierEffect(Rs.always_true, {Ma.magic_attack_percentage: 5}),
            ],
            [
                ModifierEffect(
                    Rs.always_true,
                    {
                        Ma.skill_damage_percentage: 10,
                        Ma.range_skill_damage_percentage: 5,
                    },
                ),
            ],
        ],
    )

    # 两枚	物防、法防+5%
    # 三枚	免伤提升10%
    zhoushibing = Stone(
        "zhoushibing",
        [
            {
                "life": 908,
                "attack": 363,
                Ma.defense_percentage: 2,
                Ma.magic_defense_percentage: 2,
                Ma.physical_damage_reduction_percentage: 4,
                Ma.life_percentage: 4,
            },
            {
                "defense": 363,
                "magic_defense": 201,
                Ma.life_percentage: 8,
                Ma.suffer_critical_damage_reduction_percentage: 7,
                Ma.physical_damage_reduction_percentage: 10,
                Ma.magic_damage_reduction_percentage: 8
            },
            {
                "life": 1070,
                "attack": 323,
                Ma.attack_percentage: 3,
                Ma.magic_damage_reduction_percentage: 7,
                Ma.defense_percentage: 4,
                Ma.life_percentage: 7,
            },
        ],
        [
            [
                ModifierEffect(
                    Rs.always_true,
                    {Ma.defense_percentage: 5, Ma.magic_defense_percentage: 5},
                ),
            ],
            [
                ModifierEffect(
                    Rs.always_true,
                    {
                        Ma.physical_damage_reduction_percentage: 10,
                        Ma.magic_damage_reduction_percentage: 10,
                    },
                ),
            ],
        ],
    )

    # 两枚 法攻 + 5 %
    # 三枚 使用绝学时伤害提高8 %，主动攻击「对战中」伤害提升10 %。
    yuanhu = Stone(
        "yuanhu",
        [
            {
                "life": 666,
                "magic_attack": 403,
                "life_percentage": 4,
                Ma.magic_damage_percentage: 10,
                Ma.physical_damage_reduction_percentage: 3,
                Ma.magic_attack_percentage: 10,
            },
            {
                Ma.defense: 242,
                Ma.magic_defense: 323,
                Ma.counterattack_damage_percentage: 2,
                Ma.life_percentage: 8,
                Ma.magic_damage_percentage: 4,
                Ma.magic_attack_percentage: 5,
            },
            {
                "life": 767,
                "magic_attack": 363,
                Ma.counterattack_damage_percentage: 5,
                Ma.magic_damage_percentage: 6,
                Ma.life_percentage: 7,
                Ma.magic_attack_percentage: 7
            },
        ],
        [
            [
                ModifierEffect(Rs.always_true, {Ma.magic_attack_percentage: 5}),
            ],
            [
                ModifierEffect(
                    partial(Rs.self_is_used_active_skill),
                    {Ma.magic_damage_percentage: 8, Ma.physical_damage_percentage: 8},
                ),
                ModifierEffect(
                    partial(Rs.self_is_battle_attacker),
                    {Ma.battle_damage_percentage: 10},
                ),
            ],
        ],
    )
