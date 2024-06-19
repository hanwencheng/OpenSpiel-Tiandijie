# import pyspiel
from open_spiel.python.games.Tiandijie.state.apply_action import apply_action
from open_spiel.python.games.Tiandijie.primitives.Action import Action, ActionTypes
from open_spiel.python.games.Tiandijie.primitives.hero.Attributes import generate_max_level_attributes
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
from open_spiel.python.games.Tiandijie.calculation.PathFinding import bfs_move_range


class State:
    def __init__(self, context):
        self._cur_player = 0
        self._player0_score = 0.0
        self._player1_score = 0.0
        self._is_terminal = False
        self.context = context
        self.turn = 0
    # def __init__(self):
    #     self._cur_player = 0
    #     self._player0_score = 0.0
    #     self._player1_score = 0.0
    #     self._isterminal = False
    #     self.context = setup_context()

    def _apply_action(self, action):
        apply_action(self.context, action)
        if not action.has_additional_action:
            self._cur_player = 1 - self._cur_player

    def returns(self):
        """Total reward for each player over the course of the game so far."""
        return [self._player0_score, self._player1_score]

    # def current_player(self):
    #     return pyspiel.PlayerId.TERMINAL if self._is_terminal else self._cur_player

    def _legal_actions(self, player):   # 返回可执行的操作， 可传入apply_action的action
        if self.check_all_teams_dead():
            return []
        legal_actions = []
        hero_list = self.context.heroes
        action = self.context.get_last_action()
        if self.turn == 0:
            self.turn += 1
            for hero in hero_list:
                event_listener_calculator(actor_instance=hero, counter_instance=None, event_type=EventTypes.game_start, context=self.context)

        if action is not None and action.has_additional_action:
            actor = action.actor
            self.actionable = True
            if action.additional_action is not None and action.additional_action >= 0:
                actor.reset_actionable(self.context, action.additional_action)
                legal_actions.extend(actor.actionable_list)

            elif action.additional_skill_list and len(action.additional_skill_list) != 0:
                actions = self.get_additional_skill_action(action.actor, action.additional_skill_list)
                legal_actions.extend(actions)

            elif action.additional_move > 0:
                other_hero_list = [hero for hero in hero_list if hero.id != actor.id]
                enemies_list = [hero.position for hero in hero_list if hero.player_id != actor.player_id]
                partner_list = [hero.position for hero in other_hero_list if hero.player_id == actor.player_id]
                movable_range = bfs_move_range(action.actor.position, action.additional_move, self.context.battlemap, action.actor.temp.flyable, enemies_list, partner_list)

                for position in movable_range:
                    new_action = Action(action.actor, [], None, position, position)
                    new_action.update_action_type(ActionTypes.MOVE)
                    legal_actions.append(new_action)
        else:
            if not any(hero.actionable for hero in self.context.heroes):    # 所有角色都动过了，开启新的回合
                if not self.new_turn_event_for_state():
                    return []
                for hero in hero_list:
                    event_listener_calculator(actor_instance=hero, counter_instance=None, event_type=EventTypes.turn_end, context=self.context)
                    event_listener_calculator(actor_instance=hero, counter_instance=None, event_type=EventTypes.turn_start, context=self.context)

            selectable_heroes = [hero for hero in hero_list if hero.player_id == player and hero.actionable]
            for hero in selectable_heroes:
                hero.initialize_actionable_hero(self.context)
                legal_actions.extend(hero.actionable_list)
            # print("legal_action", player, len(legal_actions), len(selectable_heroes))
        return legal_actions

    def is_terminal(self):
        return self._is_terminal
    def new_turn_event_for_state(self):
        # print("new_turn_event_for_state")
        self.turn += 1
        print("turn", self.turn)
        if self.turn > 15:
            self._is_terminal = True
            return False
        for y in range(len(self.context.battlemap.map)):
            for x in range(len(self.context.battlemap.map[0])):
                terrain_buff = self.context.battlemap.get_terrain((y, x)).buff
                if terrain_buff is not None:
                    terrain_buff.duration -= 1
                    if terrain_buff.duration <= 0:
                        self.context.battlemap.get_terrain((y, x)).remove_buff()
        return True

    def check_all_teams_dead(self):
        if len(self.context.get_heroes_by_player_id(0)) == 0 or len(self.context.get_heroes_by_player_id(1)) == 0:
            self._is_terminal = True
            return True


    def get_additional_skill_action(self, actor, skills):
        actions = []
        new_action = Action(actor, [], None, actor.position, actor.position)
        new_action.update_action_type(ActionTypes.PASS)
        actions.append(new_action)
        from open_spiel.python.games.Tiandijie.primitives.skill.SkillTypes import SkillTargetTypes, SkillType
        from open_spiel.python.games.Tiandijie.calculation.Range import calculate_diamond_area, \
            calculate_if_targe_in_diamond_range
        from open_spiel.python.games.Tiandijie.calculation.modifier_calculator import get_level2_modifier
        from open_spiel.python.games.Tiandijie.primitives.map.TerrainType import TerrainType
        def get_new_action(self, hero_in_skill, skill, moveable_position, target_position):
            new_action = Action(self, hero_in_skill, skill, moveable_position, target_position)
            if skill.temp.skill_type == SkillType.Support:
                new_action.update_action_type(ActionTypes.SUPPORT)
            elif skill.temp.skill_type == SkillType.Heal:
                new_action.update_action_type(ActionTypes.HEAL)
            elif skill.temp.skill_type in {SkillType.Physical, SkillType.Magical}:
                new_action.update_action_type(ActionTypes.SKILL_ATTACK)
            return new_action

        def get_hero_in_skill(target, target_hero_list, skill, moveable_position):
            return [target] + [
                effect_hero for effect_hero in target_hero_list
                if effect_hero != target and skill.temp.range_instance.check_if_target_in_range(
                    moveable_position, target.position, effect_hero.position, self.context.battlemap
                )
            ]

        hero_list = self.context.heroes
        for skill in skills:
            if skill.temp.target_type == SkillTargetTypes.TERRAIN:
                target_position_list = calculate_diamond_area(actor.position, skill.temp.distance.distance_value,
                                                              self.context.battlemap)
                target_position_list = [pos for pos in target_position_list if
                                        self.context.battlemap.get_terrain(pos).terrain_type in {
                                            TerrainType.NORMAL, TerrainType.ZHUOWU}]
                for target_position in target_position_list:
                    hero_in_skill = [actor]
                    if skill.temp.skill_type in {SkillType.Support, SkillType.Heal}:
                        partner_list = [hero for hero in hero_list if
                                        hero.player_id == actor.player_id and hero.player_id != actor.player_id]
                        hero_in_skill.extend(partner for partner in partner_list if
                                             skill.temp.range_instance.check_if_target_in_range(actor.position,
                                                                                                actor.position,
                                                                                                partner.position,
                                                                                                self.context.battlemap))
                        new_action = Action(actor, hero_in_skill, skill, actor.position, actor.position)
                        new_action.update_action_type(
                            ActionTypes.SUPPORT) if skill.temp.skill_type == SkillType.Support else new_action.update_action_type(
                            ActionTypes.HEAL)
                        actions.append(new_action)
                    elif skill.temp.skill_type in {SkillType.Physical, SkillType.Magical}:
                        enemy_list = [hero for hero in hero_list if hero.player_id != actor.player_id]
                        hero_in_skill = [enemy for enemy in enemy_list if
                                         skill.temp.range_instance.check_if_target_in_range(actor.position, enemy.position,
                                                                                            target_position,
                                                                                            self.context.battlemap)]
                        new_action = Action(actor, hero_in_skill, skill, actor.position, target_position)
                        new_action.update_action_type(ActionTypes.SKILL_ATTACK)
                        actions.append(new_action)

            elif skill.temp.target_type == SkillTargetTypes.SELF:
                hero_in_skill = [actor]
                if skill.temp.skill_type in {SkillType.Support, SkillType.Heal}:
                    partner_list = [hero for hero in hero_list if
                                    hero.player_id == actor.player_id and hero.player_id != actor.player_id]
                    hero_in_skill.extend(partner for partner in partner_list if
                                         skill.temp.range_instance.check_if_target_in_range(actor.position, actor.position,
                                                                                            partner.position,
                                                                                            self.context.battlemap))

                    new_action = Action(actor, hero_in_skill, skill, actor.position, actor.position)
                    new_action.update_action_type(ActionTypes.SELF)
                    actions.append(new_action)
                elif skill.temp.skill_type in {SkillType.Physical, SkillType.Magical}:
                    enemy_list = [hero for hero in hero_list if hero.player_id != actor.player_id]
                    hero_in_skill = [enemy for enemy in enemy_list if
                                     skill.temp.range_instance.check_if_target_in_range(actor.position, actor.position,
                                                                                        enemy.position,
                                                                                        self.context.battlemap)]

                    if hero_in_skill:
                        new_action = Action(actor, hero_in_skill, skill, actor.position, actor.position)
                        new_action.update_action_type(ActionTypes.SELF)
                        actions.append(new_action)
            else:
                target_hero_list = [
                    hero for hero in hero_list if
                    (skill.temp.target_type == SkillTargetTypes.ENEMY and hero.player_id != actor.player_id) or
                    (skill.temp.target_type != SkillTargetTypes.ENEMY and hero.player_id == actor.player_id)
                ]

                skill_new_distance = (
                        skill.temp.distance.distance_value +
                        get_level2_modifier(actor, None, "active_skill_range", self.context) +
                        get_level2_modifier(
                            actor,
                            None,
                            "single_skill_range" if skill.temp.range_instance.range_value == 0 else "range_skill_range",
                            self.context
                        )
                )

                for target in target_hero_list:
                    hero_in_skill = get_hero_in_skill(target, target_hero_list, skill, actor.position)

                    if actor == target:
                        new_action = get_new_action(actor, hero_in_skill, skill, actor.position,
                                                    actor.position)
                        actions.append(new_action)
                    elif calculate_if_targe_in_diamond_range(actor.position, target.position,
                                                             int(skill_new_distance)):
                        new_action = get_new_action(actor, hero_in_skill, skill, actor.position, target.position)
                        actions.append(new_action)
            return actions

