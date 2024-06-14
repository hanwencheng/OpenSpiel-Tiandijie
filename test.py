from open_spiel.python import rl_environment
from open_spiel.python import rl_tools
from open_spiel.python.algorithms import tabular_qlearner
from absl import flags, app
import pyspiel
from open_spiel.python import games  # pylint: disable=unused-import
FLAGS = flags.FLAGS
flags.DEFINE_string("game_string", "tiandijie", "Game string")

def main(_):
    env = rl_environment.Environment("tiandijie")
    num_players = env.num_players
    num_actions = env.action_spec()["num_actions"]
    print(num_actions, num_players)
    agents = [
        tabular_qlearner.QLearner(player_id=idx, num_actions=num_actions)
        for idx in range(num_players)
    ]
    for cur_episode in range(10000):
        print("                                             Episode: ", cur_episode)
        time_step = env.reset()
        while not time_step.last():
            player_id = time_step.observations["current_player"]
            if player_id == pyspiel.PlayerId.TERMINAL:
                break
            agent_output = agents[player_id].step(time_step)
            time_step = env.step([agent_output.action])

        for agent in agents:
            agent.step(time_step)

    print("Done")

    from open_spiel.python.algorithms import random_agent
    eval_agents = [agents[0], random_agent.RandomAgent(1, num_actions, "Entropy Master 2000") ]
    time_step = env.reset()
    while not time_step.last():
        player_id = time_step.observations["current_player"]
        if player_id == pyspiel.PlayerId.TERMINAL:
            break
        agent_output = eval_agents[player_id].step(time_step)
        print(f"Agent {player_id} chooses {env._state.action_to_string(agent_output.action)}")
        env._state.shows_cemetery()
        time_step = env.step([agent_output.action])

    env._state.display_map()
    print(time_step.rewards)

if __name__ == '__main__':
    app.run(main)
