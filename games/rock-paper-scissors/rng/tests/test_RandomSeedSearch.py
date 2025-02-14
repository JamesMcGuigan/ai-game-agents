# %%writefile test_RandomSeedSearch.py
import numpy as np
import pytest
from joblib import delayed, Parallel
from kaggle_environments import evaluate

from rng.IrrationalAgent import IrrationalAgent
from rng.IrrationalSearchAgent import IrrationalSearchAgent
from rng.random_agent_seeded import random_agent_seeded
from rng.RandomSeedSearch import RandomSeedSearch


@pytest.mark.parametrize("name",   IrrationalSearchAgent.irrationals.keys())
@pytest.mark.parametrize("offset", [0,1,2])
def test_RandomSeedSearch_vs_named_irrational(name, offset):
    """ Assert we can find the full irrational sequence every time """
    assert len(RandomSeedSearch.cache)  # check cache filepath can be found
    episodeSteps = 100
    results = evaluate(
        "rps",
        [
            IrrationalAgent(name=name, offset=offset, verbose=False),
            RandomSeedSearch(verbose=False)
        ],
        configuration={
            "episodeSteps": episodeSteps,
            "tieRewardThreshold":  1,     # Disable draws
            "actTimeout":          1000,  # Prevent TimeoutError
        },
        # debug=True  # pull request
    )
    results = np.array(results).reshape((-1,2))
    assert len(results[ results == None ]) == 0   # No errored matches
    assert (results[0][0] + episodeSteps/2.1) < results[0][1]


def test_RandomSeedSearch_vs_seeded_rng():
    """ Assert we can find the full irrational sequence every time """
    assert len(RandomSeedSearch.cache)  # check cache filepath can be found
    episodeSteps = 100
    results = evaluate(
        "rps",
        [
            random_agent_seeded,
            RandomSeedSearch(verbose=False)
        ],
        configuration={
            "episodeSteps": episodeSteps,
            "tieRewardThreshold":  1,     # Disable draws
            "actTimeout":          1000,  # Prevent TimeoutError
        },
        # debug=True  # pull request
    )
    assert results[0][0] < results[0][1], results



def test_RandomSeedSearch_vs_Irrational():
    """ Show we don't have a statistical advantage inside the opening book vs irrational """
    episodeSteps = 100
    results = Parallel(-1)( delayed(evaluate)(
        "rps",
        [
            IrrationalAgent(verbose=False),
            RandomSeedSearch(verbose=False)
        ],
        configuration={
            "episodeSteps": episodeSteps,
            "tieRewardThreshold":  1,     # Disable draws
            "actTimeout":          1000,  # Prevent TimeoutError
        },
        num_episodes=1
        # debug=True,  # pull request
    ) for _ in range(int(1000/episodeSteps)) )
    results = np.array(results).reshape((-1,2))
    assert len(results[ results == None ]) == 0   # No errored matches

    totals  = np.mean(results, axis=0)
    std     = np.std(results, axis=0).round(2)
    winrate = [ np.sum(results[:,0] > results[:,1]),
                np.sum(results[:,0] < results[:,1]) ]

    print('results', results)
    print('totals',  totals)
    print('std',     std)
    print('winrate', winrate)

    assert np.abs(totals[0]) < 0.2 * episodeSteps  # scores are within 20%
    assert np.abs(totals[1]) < 0.2 * episodeSteps  # scores are within 20%
    assert np.abs(std[0])    < 0.2 * episodeSteps  # std  within 20%
    assert np.abs(std[1])    < 0.2 * episodeSteps  # std  within 20%



def test_RandomSeedSearch_vs_unseeded_RNG():
    """ Show we have a statistical advantage vs RNG """
    episodeSteps = 100
    results = Parallel(-1)( delayed(evaluate)(
        "rps",
        [
            "rng/random_agent_unseeded.py",
            RandomSeedSearch(verbose=False)
        ],
        configuration={
            "episodeSteps": episodeSteps,
            "tieRewardThreshold":  1,     # Disable draws
            "actTimeout":          1000,  # Prevent TimeoutError
        },
        num_episodes=1
        # debug=True,  # pull request
    ) for _ in range(int(1000/episodeSteps)) )
    results = np.array(results).reshape((-1,2))
    assert len(results[ results == None ]) == 0   # No errored matches

    totals  = np.sum(results, axis=0)
    std     = np.std(results, axis=0).round(2)
    winrate = [ np.sum(results[:,0] > results[:,1]),
                np.sum(results[:,0] < results[:,1]) ]

    print('results', results)
    print('totals',  totals)
    print('std',     std)
    print('winrate', winrate)

    assert winrate[0] <= winrate[1], winrate      # We have a winrate advantage or draw
    assert totals[0]  <  totals[1],  totals       # We have a statistical advantage
    # assert np.abs(std[0]) < 0.2 * episodeSteps  # std within 20%
    # assert np.abs(std[1]) < 0.2 * episodeSteps  # std within 20%
