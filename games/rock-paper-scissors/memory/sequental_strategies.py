# %%writefile submission.py
# Source: https://www.kaggle.com/jamesmcguigan/rock-paper-scissors-sequential-strategies


import random


def get_last_time_result(results=[-1]):
    if isinstance(results, int): results = [ results ]
    for n in range(len(ss_history['reward'])):
        if ss_history['reward'][-n] in results: return n
    else: return 0


def get_streak(results=[-1]):
    if isinstance(results, int): results = [ results ]
    for n in range(len(ss_history['reward'])):
        if ss_history['reward'][-n] not in results: return n
    else:
        return len(ss_history['reward'])


def get_previous_streak(results=[-1]):
    if isinstance(results, int): results = [ results ]
    for n in range(len(ss_history['reward'])):
        if ss_history['reward'][-n] not in results:
            for n in range(n+1, len(ss_history['reward'])):
                if ss_history['reward'][-n] not in results:
                    return n
            else:
                return len(ss_history['reward'])
    else:
        return 0


action            = 0
increment_on_lose = 1
increment_on_turn = 1
ss_history   = {
    "action":   [],
    "opponent": [],
    "reward":   [],
    "streaks":  [],
}
# observation   =  {'step': 1, 'lastOpponentAction': 1}
# configuration =  {'episodeSteps': 1000, 'agentTimeout': 60, 'actTimeout': 1, 'runTimeout': 120
def sequential_strategies(observation, configuration, nstreak=2):
    global action
    global increment_on_lose
    global increment_on_turn
    global ss_history
    if observation.step > 0:
        ss_history['opponent'].append(observation.lastOpponentAction)
        reward = (
            0 if ss_history['action'][-1] == (ss_history['opponent'][-1]) else
            1 if ss_history['action'][-1] == (ss_history['opponent'][-1] + 1) % configuration.signs else
            -1
        )
        ss_history['reward'].append(reward)
        lose_streak     = get_streak([-1])
        draw_streak     = get_streak([0, -1])
        previous_streak = get_previous_streak([-1])
        # print('reward',reward)
        # print('lose_streak', lose_streak)
        # print('previous_streak', previous_streak)

        # Counter static agent
        if observation.step > 3 and len(set(ss_history['opponent'])) == 1:
            increment_on_turn = 0
            action = list(set(ss_history['opponent']))[0] + 1

        elif (
                lose_streak >= nstreak
                or draw_streak >= nstreak*2
        ):
            increment_on_turn = random.choice([0,1,2])
            if lose_streak >= nstreak*2:
                increment_on_lose += 1
                ss_history['streaks'].append(0)
            else:
                ss_history['streaks'].append(previous_streak)

            action += increment_on_lose

            if len(ss_history['streaks']) and previous_streak >= ss_history['streaks'][-1] - 1:
                action += 1


    action += increment_on_turn

    ss_history['action'].append(action)
    return int(action) % configuration.signs
