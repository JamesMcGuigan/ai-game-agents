# %%writefile submission.py
# Source: https://www.kaggle.com/jamesmcguigan/rock-paper-scissors-multi-stage-decision-tree

import random
import time
from typing import Dict, List

import numpy as np
from sklearn.tree import DecisionTreeClassifier


def random_agent(observation, configuration):
    # random.seed(None)
    return random.randint(0, configuration.signs-1)


def get_winstats(history) -> Dict[str,int]:
    total = len(history['action'])
    wins = 0
    draw = 0
    loss = 0
    for n in range(total):
        if   history['action'][n] == history['opponent'][n] + 1: wins +=  1
        elif history['action'][n] == history['opponent'][n]:     draw +=  1
        elif history['action'][n] == history['opponent'][n] - 1: loss +=  1
    return { "wins": wins, "draw": draw, "loss": loss }

def get_winrate(history):
    winstats = get_winstats(history)
    winrate  = winstats['wins'] / (winstats['wins'] + winstats['loss']) if (winstats['wins'] + winstats['loss']) else 0
    return winrate


# Initialize starting history
dt_history = {
    "step":        [],
    "prediction1": [],
    "prediction2": [],
    "expected":    [],
    "action":      [],
    "opponent":    [],
}

# NOTE: adding statistics causes the DecisionTree to make random moves
def get_statistics(values) -> List[float]:
    values = np.array(values)
    return [
        np.count_nonzero(values == n) / len(values)
        if len(values) else 0.0
        for n in [0,1,2]
    ]


# observation   =  {'step': 1, 'lastOpponentAction': 1}
# configuration =  {'episodeSteps': 10, 'agentTimeout': 60, 'actTimeout': 1, 'runTimeout': 1200, 'isProduction': False, 'signs': 3}
def decision_tree_agent(observation, configuration, window=10, stages=2, random_freq=0, warmup_period=5, max_samples=1000):
    global dt_history
    warmup_period   = warmup_period  # if os.environ.get('KAGGLE_KERNEL_RUN_TYPE','') != 'Interactive' else 0
    models          = [ None ] + [ DecisionTreeClassifier() ] * stages

    time_start      = time.perf_counter()
    actions         = list(range(configuration.signs))  # [0,1,2]

    step            = observation.step
    last_action     = dt_history['action'][-1]          if len(dt_history['action']) else 2
    opponent_action = observation.lastOpponentAction if observation.step > 0   else 2

    if observation.step > 0:
        dt_history['opponent'].append(opponent_action)

    winrate  = get_winrate(dt_history)
    winstats = get_winstats(dt_history)

    # Set default values
    prediction1 = random.randint(0,2)
    prediction2 = random.randint(0,2)
    prediction3 = random.randint(0,2)
    expected    = random.randint(0,2)

    # We need at least some turns of dt_history for DecisionTreeClassifier to work
    if observation.step >= window:
        # First we try to predict the opponents next move based on move dt_history
        # TODO: create windowed dt_history
        try:
            n_start = max(1, len(dt_history['opponent']) - window - max_samples)
            # print('stats: ', { key: get_statistics(dt_history[key]) for key in dt_history.keys() })
            if stages >= 1:
                X = np.stack([
                    np.array([
                        # get_statistics(dt_history['action'][:n+window]),
                        # get_statistics(dt_history['opponent'][:n-1+window]),
                        dt_history['action'][n:n + window],
                        dt_history['opponent'][n:n + window]
                    ]).flatten()
                    for n in range(n_start, len(dt_history['opponent']) - window)
                ])
                Y = np.array([
                    dt_history['opponent'][n + window]
                    for n in range(n_start, len(dt_history['opponent']) - window)
                ])
                Z = np.array([
                    # get_statistics(dt_history['action']),
                    # get_statistics(dt_history['opponent']),
                    dt_history['action'][-window + 1:] + [last_action],
                    dt_history['opponent'][-window:]
                ]).flatten().reshape(1, -1)

                models[1].fit(X, Y)
                expected = prediction1 = models[1].predict(Z)[0]

            if stages >= 2:
                # Now retrain including prediction dt_history
                X = np.stack([
                    np.array([
                        # get_statistics(dt_history['action'][:n+window]),
                        # get_statistics(dt_history['prediction1'][:n+window]),
                        # get_statistics(dt_history['opponent'][:n-1+window]),
                        dt_history['action'][n:n + window],
                        dt_history['prediction1'][n:n + window],
                        dt_history['opponent'][n:n + window],
                    ]).flatten()
                    for n in range(n_start, len(dt_history['opponent']) - window)
                ])
                Y = np.array([
                    dt_history['opponent'][n + window]
                    for n in range(n_start, len(dt_history['opponent']) - window)
                ])
                Z = np.array([
                    # get_statistics(dt_history['action']),
                    # get_statistics(dt_history['prediction1']),
                    # get_statistics(dt_history['opponent']),
                    dt_history['action'][-window + 1:] + [last_action],
                    dt_history['prediction1'][-window + 1:] + [prediction1],
                    dt_history['opponent'][-window:]
                ]).flatten().reshape(1, -1)

                models[2].fit(X, Y)
                expected = prediction2 = models[2].predict(Z)[0]

            if stages >= 3:
                # Now retrain including prediction dt_history
                X = np.stack([
                    np.array([
                        # get_statistics(dt_history['action'][:n+window]),
                        # get_statistics(dt_history['prediction1'][:n+window]),
                        # get_statistics(dt_history['prediction2'][:n+window]),
                        # get_statistics(dt_history['opponent'][:n-1+window]),
                        dt_history['action'][n:n + window],
                        dt_history['prediction1'][n:n + window],
                        dt_history['prediction2'][n:n + window],
                        dt_history['opponent'][n:n + window],
                    ]).flatten()
                    for n in range(n_start, len(dt_history['opponent']) - window)
                ])
                Y = np.array([
                    dt_history['opponent'][n + window]
                    for n in range(n_start, len(dt_history['opponent']) - window)
                ])
                Z = np.array([
                    # get_statistics(dt_history['action']),
                    # get_statistics(dt_history['prediction1']),
                    # get_statistics(dt_history['prediction2']),
                    # get_statistics(dt_history['opponent']),
                    dt_history['action'][-window + 1:] + [last_action],
                    dt_history['prediction1'][-window + 1:] + [prediction1],
                    dt_history['prediction2'][-window + 1:] + [prediction2],
                    dt_history['opponent'][-window:]
                ]).flatten().reshape(1, -1)

                models[3].fit(X, Y)
                expected = prediction3 = models[3].predict(Z)[0]

        except Exception as exception:
            print(exception)

    # During the warmup period, play random to get a feel for the opponent
    if (observation.step <= max(warmup_period,window)):
        actor  = 'warmup'
        action = random_agent(observation, configuration)

        # Play a purely random move occasionally, which will hopefully distort any opponent statistics
    elif (random.random() <= random_freq):
        actor  = 'random'
        action = random_agent(observation, configuration)

    # But mostly use DecisionTreeClassifier to predict the next move
    else:
        actor  = 'DecisionTree'
        action = (expected + 1) % configuration.signs

    # Persist state
    dt_history['step'].append(step)
    dt_history['prediction1'].append(prediction1)
    dt_history['prediction2'].append(prediction2)
    dt_history['expected'].append(expected)
    dt_history['action'].append(action)
    if observation.step == 0:  # keep arrays equal length
        dt_history['opponent'].append(random.randint(0, 2))


    # Print debug information
    time_taken = time.perf_counter() - time_start
    # print(f'{1000*time_taken:3.0f}ms | {step:4d} | opp = {opponent_action} | pred1 = {prediction1} | pred2 = {prediction2} | exp = {expected} | act = {action} | {winrate:.2f} {actor:7s}')
    print(f'{1000*time_taken:3.0f}ms | {step:4d} | opp = {opponent_action} | exp = {expected} | act = {action} | {actor:7s} | {100*winrate:5.1f}% {winstats}')
    return int(action)
