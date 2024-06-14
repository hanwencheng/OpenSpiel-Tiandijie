import inspect
# from primitives.buff.Buff import BuffTypes
from primitives.buff.BuffTemp import BuffTemp
from primitives.Context import Context


# def is_harm_buff(buff):
#     return (
#         isinstance(buff, BuffTemp) and buff.type == BuffTypes.Harm and buff.dispellable
#     )


# def is_benefit_buff(buff):
#     return (
#         isinstance(buff, BuffTemp)
#         and buff.type == BuffTypes.Benefit
#         and buff.dispellable
#     )


def setup_context() -> Context:
    game_context = Context()

    game_context.load_buffs()

    game_context.init_formation()

    game_context.init_battlemap("yaoshanhuanjing")

    game_context.init_game_heroes()

    game_context.init_heroes_position()

    # game_context.battlemap.display_map()

    return game_context
