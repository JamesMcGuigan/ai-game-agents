#!/usr/bin/env python3
import itertools

from kaggle_environments import make
from kaggle_environments.envs.connectx.connectx import negamax_agent
from kaggle_environments.envs.connectx.connectx import random_agent

from agents.AlphaBetaAgent.AlphaBetaAgent import AlphaBetaAgent
from agents.AlphaBetaAgent.AlphaBetaBitboard import AlphaBetaBitboard
from agents.AlphaBetaAgent.AlphaBetaBitsquares import AlphaBetaBitsquares
from agents.AlphaBetaAgent.AlphaBetaOddEven import AlphaBetaOddEven
from agents.MontyCarlo.AntColonyTreeSearch import AntColonyTreeSearchNode
from agents.MontyCarlo.MontyCarloBitsquares import MontyCarloBitsquares
from agents.MontyCarlo.MontyCarloHeuristic import MontyCarloHeuristic
from agents.MontyCarlo.MontyCarloPure import MontyCarloPure
from agents.Negamax.Negamax import Negamax

training_agents = [
    # AntColonyTreeSearch(),
    # MontyCarloPure(),
    # MontyCarloHeuristic(),
    MontyCarloBitsquares(),
    # MinimaxBitboard.agent(),
]
opponent_agents = [
    random_agent,
    negamax_agent,
    AlphaBetaAgent.agent(),
    AlphaBetaBitboard.agent(),
    AlphaBetaBitsquares.agent(),
    AlphaBetaOddEven.agent(),
    AntColonyTreeSearchNode.agent(),
    MontyCarloPure(),
    MontyCarloHeuristic(),
    MontyCarloHeuristic(),
    Negamax(),

    AlphaBetaAgent.agent(),
    AlphaBetaBitboard.agent(),
    AlphaBetaBitsquares.agent(),
    AlphaBetaOddEven.agent(),

    *[ AlphaBetaBitboard.agent(search_max_depth=max_depth)   for max_depth in range(1,8+1) ],
    *[ AlphaBetaBitsquares.agent(search_max_depth=max_depth) for max_depth in range(1,8+1) ],
    *[ AlphaBetaOddEven.agent(search_max_depth=max_depth)    for max_depth in range(1,8+1) ],
    *[ Negamax(max_depth=max_depth)                          for max_depth in range(1,8+1) ],
    *[ random_agent                                          for _ in range(7**2) ],  # depth=2 opening book
]
# random.shuffle(training_agents)
# random.shuffle(opponent_agents)


env = make("connectx", debug=True)
env.render()
env.reset()

def print_results(env, agent_order):
    try:
        if   env.state[0].reward == env.state[1].reward:  print(f'Draw: {agent_order[0].__name__} vs {agent_order[1].__name__}')
        elif env.state[0].reward  > env.state[1].reward:  print(f'Winner player 1: {agent_order[0].__name__} | Loser player 2: {agent_order[1].__name__}')
        else:                                             print(f'Winner player 2: {agent_order[1].__name__} | Loser player 1: {agent_order[0].__name__}')
    except:
        print(f'Error: {agent_order[0].__name__} vs {agent_order[1].__name__}')
    print()


safety_time = 0.25
for timeout in [1,3,7]:
    timeout += safety_time
    env.configuration.timeout = timeout

    # # Next play 100 rounds against random agent (7x7x2 = 98) which should cover most 2-deep opening positions
    # for agent_1 in training_agents:
    #     agent_2 = random_agent
    #     for round in range(100):
    #         agent_order = [agent_1, agent_2] if round % 2 == 0 else [agent_2, agent_1]
    #         env.run(agent_order)
    #         print_results(env, agent_order)
    #         env.reset()
    #
    # # Have each training agent play against each other
    # for agent_1, agent_2 in itertools.product(training_agents, training_agents):
    #     for round in range(2):
    #         agent_order = [agent_1, agent_2] if round % 2 == 0 else [agent_2, agent_1]
    #         env.run(agent_order)
    #         print_results(env, agent_order)
    #         env.reset()

    # Train against real opponents
    for agent_1, agent_2 in itertools.product(training_agents, opponent_agents):
        for round in range(2):
            agent_order = [agent_1, agent_2] if round % 2 == 0 else [agent_2, agent_1]
            env.run(agent_order)
            print_results(env, agent_order)
            env.reset()