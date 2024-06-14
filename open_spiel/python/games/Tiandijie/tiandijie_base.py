import traceback

import pyspiel
from open_spiel.python.games.Tiandijie.state.setup import setup_context
from open_spiel.python.games.Tiandijie.state.apply_action import apply_action
from open_spiel.python.games.Tiandijie.primitives.Action import Action, ActionTypes
from open_spiel.python.games.Tiandijie.calculation.PathFinding import bfs_move_range
from open_spiel.python.games.Tiandijie.primitives.effects.Event import EventTypes
from open_spiel.python.games.Tiandijie.calculation.event_calculator import event_listener_calculator
from open_spiel.python.observation import IIGObserverForPublicInfoGame

_NUM_PLAYERS = 2
_MAX_GAME_LENGTH = 15

DEFAULT_PARAMS = {'num_distinct_actions': 1000,
                  'num_players': _NUM_PLAYERS,
                  'players': 0,  # open_spiel tests use this for `num_players`
                  'min_utility': -10000.0,
                  'max_utility': 10000.0,
                  'num_max_replies': 1}

GAME_TYPE_KWARGS = {
    'dynamics': pyspiel.GameType.Dynamics.SEQUENTIAL,
    'chance_mode': pyspiel.GameType.ChanceMode.SAMPLED_STOCHASTIC,
    'information': pyspiel.GameType.Information.PERFECT_INFORMATION,
    'reward_model': pyspiel.GameType.RewardModel.TERMINAL,
    'max_num_players': _NUM_PLAYERS,
    'min_num_players': _NUM_PLAYERS,
    'provides_observation_string': True,
    'provides_observation_tensor': True,
    'provides_factored_observation_string': True,
    'parameter_specification': DEFAULT_PARAMS,
    'default_loadable': True
    }

_GAME_TYPE = pyspiel.GameType(
    short_name="tiandijie",
    long_name="TianDiJie",
    utility=pyspiel.GameType.Utility.ZERO_SUM,
    provides_information_state_string=True,
    provides_information_state_tensor=True,
    **GAME_TYPE_KWARGS)

_GAME_INFO = pyspiel.GameInfo(
    num_distinct_actions=1000,
    max_chance_outcomes=100,
    num_players=_NUM_PLAYERS,
    min_utility=-10000,
    max_utility=10000,
    max_game_length=_MAX_GAME_LENGTH*3*10,
    utility_sum=0.0)



class TianDiJieGame(pyspiel.Game):
  """A Python version of the TianDiJie game."""

  def __init__(self, params=None):
    super().__init__(_GAME_TYPE, _GAME_INFO, params or dict())

  def new_initial_state(self):
    """Returns a state corresponding to the start of a game."""
    return TianDiJieState(self)

  def make_py_observer(self, iig_obs_type=None, params=None):
    """Returns an object used for observing game state."""
    if ((iig_obs_type is None) or
        (iig_obs_type.public_info and not iig_obs_type.perfect_recall)):
      return TianDiJieObserver(params)
    else:
      return IIGObserverForPublicInfoGame(iig_obs_type, params)


class TianDiJieState(pyspiel.State):
    def __init__(self, game):
        super().__init__(game)
        self.game = game
        self.turn = 0
        self._cur_player = 0
        self._player0_score = 0.0
        self._is_terminal = False
        self.context = setup_context()
        self.legal_actions_dic = {0: [], 1: []}

    def apply_action(self, action):
        if action is not None:
            action_instance = self.legal_actions_dic[self._cur_player][action]
            apply_action(self.context, action_instance)
            self.check_next_player(action_instance)
        else:
            self.check_next_player()

    def check_next_player(self, action_instance=None):
        def has_actionable_hero(player_id):
            return any(hero.actionable for hero in self.context.get_heroes_by_player_id(player_id))

        if action_instance is None or not action_instance.has_additional_action:
            next_player = 1 - self._cur_player
            # if action_instance:
            #     print(f"此时是{action_instance.actor.id}动, 对方有未动的", has_actionable_hero(next_player), "己方有未动的", has_actionable_hero(self._cur_player))
            # else:
            #     print(f"此时是{self._cur_player}动, 对方有未动的", has_actionable_hero(next_player), "己方有未动的", has_actionable_hero(self._cur_player))

            if has_actionable_hero(next_player):
                self._cur_player = next_player
            elif not has_actionable_hero(self._cur_player):
                self._cur_player = next_player

            # print(f"xian zai zhuan huan wei : {self._cur_player}")

    def current_player(self):
        return pyspiel.PlayerId.TERMINAL if self._is_terminal else self._cur_player

    def legal_actions(self, player):
        actions = []
        self.legal_actions_dic[player] = self.legal_actions_in_action(player)

        for i in range(len(self.legal_actions_dic[player])):
            actions.append(i)
        # print("legal_action", player, len(actions), len([hero for hero in self.context.heroes if hero.player_id == player and hero.actionable]))
        return actions

    def legal_actions_in_action(self, player):   # 返回可执行的操作， 可传入apply_action的action
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

    def new_turn_event_for_state(self):
        # print("new_turn_event_for_state")
        self.turn += 1
        print("turn", self.turn)
        if self.turn > _MAX_GAME_LENGTH:
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

    def is_terminal(self):
        return self._is_terminal

    def _action_to_string(self, player, action):
        # print(player, action)
        action_instance = self.legal_actions_dic[player][action]
        return action_instance.action_to_string(self.context)

    def rewards(self):
        """Total reward for each player over the course of the game so far."""
        score0 = self.context.calculate_score(0)
        score1 = self.context.calculate_score(1)
        self._player0_score = score0 - score1
        return [self._player0_score, -self._player0_score]

    def shows_cemetery(self):
        print("墓地的英灵:")
        for hero in self.context.cemetery:
            print(hero.id)

    def display_map(self):
        self.context.battlemap.display_map()

    def setup_game_state(self, map_name, player0_heroes, player1_heroes):
        self.context.init_battlemap(map_name)


class TianDiJieObserver:
    def __init__(self, params):
        if params:
            raise ValueError(f"Observation parameters not supported; passed {params}")
