from __future__ import annotations
from typing import TYPE_CHECKING

from typing import List
from open_spiel.python.games.Tiandijie.calculation.PathFinding import a_star_search
from open_spiel.python.games.Tiandijie.basics import Position
from open_spiel.python.games.Tiandijie.primitives.skill.skills import Skills

if TYPE_CHECKING:
    from open_spiel.python.games.Tiandijie.primitives.hero.Hero import Hero
from open_spiel.python.games.Tiandijie.primitives.skill.Skill import Skill
from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_buff_modifier
from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillType, SkillTargetTypes
from open_spiel.python.games.Tiandijie.primitives.ActionTypes import ActionTypes


class AdditionalSkill:
    def __init__(self, skill: Skill, targets: List[Hero], additional_move: int = 0):
        self.skill: Skill = skill
        self.targets: List[Hero] = targets


class Action:
    def __init__(
        self, cast_hero: Hero, affected_heroes, skill: Skill or None, move_point, action_point
    ):
        self.actor = cast_hero
        self.targets: List[Hero] = affected_heroes
        self.total_damage: float = 0
        self.is_magic: bool = skill.temp.is_magic() if skill is not None else False
        self.is_in_battle: bool = False
        self.is_with_protector: bool = False
        self.protector: Hero or None = None
        self.skill: Skill or None = skill
        self.type: ActionTypes = ActionTypes.PASS
        self.move_range: int = 0
        self.move_point: Position = move_point  # 最终移动的位置
        self.initial_position: Position = cast_hero.position
        self.action_point: Position = action_point  # 最终指定的位置：技能的目标位置
        self.movable: bool = True
        self.actionable: bool = True
        self.player_id = cast_hero.player_id
        self.has_additional_action: bool = False
        self.additional_move: int = 0
        self.additional_skill_list: [AdditionalSkill] or None = None
        self.additional_action = None

    def update_affected_heroes(self, affected_heroes: List[Hero]):
        self.targets = affected_heroes

    def update_total_damage(self, total_damage: float):
        self.total_damage = total_damage

    def update_is_in_battle(self, is_in_battle: bool):
        self.is_in_battle = is_in_battle

    def update_action_type(self, action_type: ActionTypes):
        self.type: ActionTypes = action_type

    def is_attacker(self, hero_id: str) -> bool:
        return self.actor.id == hero_id

    def get_counter_hero_in_battle(self, hero_id: str) -> Hero:
        if self.is_attacker(hero_id):
            return self.protector if self.is_with_protector else self.targets[0]
        else:
            return self.actor

    def get_defender_hero_in_battle(self) -> Hero:
        if self.is_with_protector:
            return self.protector
        else:
            return self.targets[0]

    def update_additional_move(self, actor, additional_move: int, context):
        move_disabled = get_buff_modifier("is_extra_move_range_disable", actor, None, context)
        if not move_disabled:
            self.has_additional_action = True
            self.additional_move = additional_move

    def update_additional_skill(self, additional_skill_list):
        self.has_additional_action = True
        self.additional_skill_list = [Skill(0, Skills.get_skill_by_id(skill)) for skill in additional_skill_list]

    def update_additional_action(self, additional_move, context):
        actor = self.actor
        self.has_additional_action = True
        self.additional_action = additional_move

    def get_moves(self, battle_map, enemies_list) -> int:
        path_list = a_star_search(self.initial_position, self.move_point, battle_map, self.actor.temp.flyable, enemies_list)
        return len(path_list)

    def refresh_move_point(self, battle_map):
        battle_map.hero_move(self.initial_position, self.move_point)

    def action_to_string(self, context):
        # context.battlemap.display_map()
        action_to_string = ""
        if self.protector:
            print(self.protector.id)
        if self.type == ActionTypes.MOVE:
            action_to_string = f"{self.actor.id}{self.initial_position} moves {self.move_point}"
        elif self.type == ActionTypes.PASS:
            action_to_string = f"{self.actor.id} chooses pass"
        elif self.type == ActionTypes.NORMAL_ATTACK:
            action_to_string = f"{self.actor.id}{self.initial_position} moves {self.move_point},use normal attack to{self.targets[0].id}{self.action_point}"
            if self.protector:
                action_to_string += f",was protected by {self.protector.id}"
        elif self.type == ActionTypes.SELF:
            action_to_string = f"{self.actor.id}{self.initial_position} moves {self.move_point},use {self.skill.temp.id}"
        elif self.type in [ActionTypes.HEAL, ActionTypes.SKILL_ATTACK, ActionTypes.SUPPORT]:
            if self.skill.temp.target_type == SkillTargetTypes.TERRAIN:
                action_to_string = f"{self.actor.id}{self.initial_position} moves {self.move_point}, use {self.skill.temp.id} to terrain {self.action_point}"
            else:
                action_to_string = f"{self.actor.id}{self.initial_position} moves {self.move_point},use {self.skill.temp.id} to {self.targets[0].id if self.targets else ''}, {self.action_point}"
                if self.protector:
                    action_to_string += f",was protected by {self.protector.id}"
        return action_to_string
        # elif self.type == ActionTypes.TELEPORT:
        #     action_to_string = f"{self.actor}从{self.initial_position}走到了{self.move_point},使用了{self.skill.temp.id},传送到了{self.action_point}"

    @staticmethod
    def self_calculation(actor, move_point):
        return a_star_search(actor.position, move_point, actor.temp.flyable, actor.temp.move_range)
