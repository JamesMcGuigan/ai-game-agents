import math
from copy import deepcopy
from typing import Callable
from typing import Type
from typing import Union

import numpy as np
import pytest
from kaggle_environments import make

from core.ConnectX import ConnectX
from core.ConnextXBitboard import ConnectXBitboard
from core.Heuristic import Heuristic


@pytest.fixture
def env():
    env = make("connectx", debug=True)
    env.configuration.timeout = 24*60*60
    return env

@pytest.fixture
def observation(env):
    return env.state[0].observation

@pytest.fixture
def configuration(env):
    return env.configuration

@pytest.fixture
def heuristic_class() -> Union[None,Type[Heuristic]]:
    return None

@pytest.fixture
def heuristic_fn() -> Union[None,Type[Heuristic]]:
    return None

@pytest.fixture
def game(observation, configuration, heuristic_class: Callable=None, heuristic_fn: Callable=None) -> ConnectX:
    return ConnectXBitboard(
        observation     = observation,
        configuration   = configuration,
        heuristic_class = heuristic_class,
        heuristic_fn    = heuristic_fn
    )


def test_cast_numpy(game):
    test_cases = {
        0:      [0,0,0,0,0,0,0],
        1 << 0: [1,0,0,0,0,0,0],
        1 << 1: [0,1,0,0,0,0,0],
        1 << 2: [0,0,1,0,0,0,0],
        1 << 3: [0,0,0,1,0,0,0],
        1 << 4: [0,0,0,0,1,0,0],
        1 << 5: [0,0,0,0,0,1,0],
        1 << 6: [0,0,0,0,0,0,1],
    }
    for input, expected in test_cases.items():
        output = game.cast_numpy(input)
        actual = output[0,:].tolist()  # top row
        assert actual == expected, f'input = {input}'

def test_get_actions(observation, configuration):
    observation = deepcopy(observation)
    full_board  = [1] * (6*7)
    for i in range(7):
        for j in range(7):
            board = deepcopy(full_board)
            board[i] = 0
            board[j] = 0
            observation.board = board
            game     = ConnectXBitboard(observation, configuration, None)
            expected = list({ i,j })
            actual   = game.get_actions()
            assert actual == expected, f'input = {input}'


def test_actions_returns_list_of_int(game: ConnectX):
    assert isinstance(game.actions, list)
    assert all( isinstance(action, int) for action in game.actions )


def test_game_result_actions_1(game):
    assert game.actions == [0,1,2,3,4,5,6]
    bitboards = [ game.result(action).board for action in game.actions ]
    results   = [ game.cast_numpy(bitboard)[-1,:].tolist() for bitboard in bitboards ]
    assert results == [
        [1,0,0,0,0,0,0],
        [0,1,0,0,0,0,0],
        [0,0,1,0,0,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,0,1,0,0],
        [0,0,0,0,0,1,0],
        [0,0,0,0,0,0,1],
    ]

def test_game_result_actions_2(game):
    game = game.result(3)
    assert game.actions == [0,1,2,3,4,5,6]
    bitboards = [ game.result(action).board for action in game.actions ]
    results   = [ game.cast_numpy(bitboard)[-1,:].tolist() for bitboard in bitboards ]
    assert results == [
        [2,0,0,1,0,0,0],
        [0,2,0,1,0,0,0],
        [0,0,2,1,0,0,0],
        [0,0,0,1,0,0,0],
        [0,0,0,1,2,0,0],
        [0,0,0,1,0,2,0],
        [0,0,0,1,0,0,2],
    ]


def test_get_gameovers(game):
    """test each gameover mask has exactly 4 bits and is unique"""
    gameovers    = game.get_gameovers(game.rows, game.columns, game.inarow)
    gameovers_np = [ game.cast_numpy(gameover).tolist() for gameover in gameovers ]

    assert len(gameovers) == len(set(gameovers)), f'must be unique: {gameovers}'
    for gameover in gameovers_np:
        assert np.count_nonzero(gameover) == game.inarow, f'{gameover} count_nonzero'


def test_utility(game):
    test_actions_utility = {
        (0,1,0,1,0,1,0):         math.inf,  # 4 in a row vertical
        (0,1,0,1,0,1,0,5):      -math.inf,  # 4 in a row vertical | -inf score from perspective of last player to move
        (0,0,1,1,2,2,3):         math.inf,  # 4 in a row horizontal
        (0,1,2,3,1,2,2,4,3,3,3): math.inf,  # 4 in a row diagonal up
    }
    for actions, expected in test_actions_utility.items():
        actions_reversed        = tuple( game.columns-1 - action for action in actions )
        actions_offset          = tuple( action+1 for action in actions )
        actions_reversed_offset = tuple( action-1 for action in actions_reversed )
        for actions_order in [ actions, actions_reversed, actions_offset, actions_reversed_offset ]:
            actual = game
            for action in actions_order: actual = actual.result(action)
            assert actual.utility() == expected, f"{actions} -> {actual}"


def test_score(game):
    test_actions_score = {
        (0,):        0.3,  # 3 possible single lines (up, right, diagonal)
        (0,0):       0.1,  # 3 possible single lines (up, right, diagonal) - 2 opponent singles (right, diagonal)
        (1,):        0.4,  # 4 possible single lines (up, left/right*2, diagonal)
        (1,1):       0.2,  # 5 possible single lines (up, left/right*2, diagonal*2) - 3 opponent singles (left/right*2, diagonal)
        (3,):        0.7,  # 7 possible single lines (up, left/right*4, diagonal*2)
        (3,3):       0.3,  # 9 possible single lines (up, left/right*3, diagonal*4) - 6 opponent singles (left/right*3, diagonal*2)
        (0,0,1,1):   0.3,  # p2 = 1 multi + 4 singles | p1 = 1 multi + 1 single
        (0,0,1,1,2): 0.9,  # p1 = 2 multi + 3 singles | p2 = 1 multi + 4 singles
    }
    for actions, expected in test_actions_score.items():
        actions_reversed = tuple( game.columns-1 - action for action in actions )
        for actions_order in [ actions, actions_reversed ]:
            actual = game
            for action in actions_order: actual = actual.result(action)
            assert np.math.isclose(actual.score(), expected, abs_tol=0.01), f"{actions} -> {actual} | {actual.score()} != {expected}"
