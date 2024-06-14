from open_spiel.python import rl_environment
from open_spiel.python import rl_tools
from open_spiel.python.algorithms import tabular_qlearner

env = rl_environment.Environment("tic_tac_toe")
num_players = env.num_players
num_actions = env.action_spec()["num_actions"]

agents = [
    tabular_qlearner.QLearner(player_id=idx, num_actions=num_actions)
    for idx in range(num_players)
]

for cur_episode in range(100000):
    if cur_episode % 1000 == 0:
        print("Episode: ", cur_episode)
    time_step = env.reset()
    print("reset in test", time_step.rewards)
    while not time_step.last():
        player_id = time_step.observations["current_player"]
        print("player_id in test", player_id, time_step.rewards)
        agent_output = agents[player_id].step(time_step)
        time_step = env.step([agent_output.action])

    for agent in agents:
        agent.step(time_step)

print("Done")

from open_spiel.python.algorithms import random_agent

eval_agents = [agents[0], agents[1]]
time_step = env.reset()
while not time_step.last():
    print(env.get_state)
    player_id = time_step.observations["current_player"]
    agent_output = eval_agents[player_id].step(time_step)
    print(f"Agent {player_id} chooses {env.get_state.action_to_string(agent_output.action)}")
    time_step = env.step([agent_output.action])

print(env.get_state)
print(time_step.rewards)
