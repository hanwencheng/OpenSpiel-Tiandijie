# import pyspiel
from state.setup import setup_context
from state.apply_action import apply_action
from primitives.Action import Action, ActionTypes
from calculation.PathFinding import bfs_move_range
from primitives.effects.Event import EventTypes
from calculation.event_calculator import event_listener_calculator


class State:
    def __init__(self, context):
        self._cur_player = 0
        self._player0_score = 0.0
        self._player1_score = 0.0
        self._is_terminal = False
        self.context = context
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
        legal_actions = []
        action = self.context.get_last_action()
        hero_list = self.context.heroes
        if action is not None and action.has_additional_action:
            actor = action.actor
            self.actionable = True
            if action.additional_action is not None and action.additional_action >= 0:
                actor.reset_actionable(self.context, action.additional_action)
                legal_actions.extend(actor.actionable_list)

            elif action.additional_skill_list and len(action.additional_skill_list) != 0:
                for additional_skill in action.additional_skill:
                    new_action = Action(actor, additional_skill.targets, additional_skill.skill, action.move_point, additional_skill.targets[0].position)
                    legal_actions.append(new_action)

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
            selectable_heroes = [hero for hero in hero_list if hero.player_id == player and hero.actionable]
            for hero in selectable_heroes:
                hero.initialize_actionable_hero(self.context)
                legal_actions.extend(hero.actionable_list)

        if not legal_actions:
            for hero in hero_list:
                event_listener_calculator(actor_instance=hero, counter_instance=None, event_type=EventTypes.turn_end, context=self.context)
                event_listener_calculator(actor_instance=hero, counter_instance=None, event_type=EventTypes.turn_start, context=self.context)
            return self._legal_actions(1 - player)
        return legal_actions

    def is_terminal(self):
        return self._is_terminal
