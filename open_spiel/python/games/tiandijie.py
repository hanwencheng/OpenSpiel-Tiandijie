from open_spiel.python.games.Tiandijie import tiandijie_base


import pyspiel
from typing import Any, Callable, Dict, OrderedDict, List, Tuple, Union

GAME_TYPE = pyspiel.GameType(
        short_name='tiandijie',
        long_name='TianDiJie Game',
        utility=pyspiel.GameType.Utility.ZERO_SUM,
        provides_information_state_string=True,
        provides_information_state_tensor=True,
        **tiandijie_base.GAME_TYPE_KWARGS)


class ChatGameObserver(tiandijie_base.TianDiJieObserver):
    """Observer, conforming to the PyObserver interface (see observation.py)."""
    def _build_str_to_info_state(self) -> bool:
        """Initializes map from str to infostate. Returns True if successful."""
        # Build a string tokenizer here
        # --------------------------- #
        # Build a string tokenizer here
        return True


class TianDiJieGame(tiandijie_base.TianDiJieGame):
    def __init__(
            self,
            params: Dict[str, Any] = tiandijie_base.DEFAULT_PARAMS,
    ):
        super().__init__(params)  # initializes self.game_info via base init

    def new_initial_state(self):
        """Returns a state corresponding to the start of a game."""
        return tiandijie_base.TianDiJieState(self)


pyspiel.register_game(GAME_TYPE, TianDiJieGame)
