from fastcache import clru_cache

from core.ConnectXBBNN import *
from heuristics.BitsquaresHeuristic import bitsquares_heuristic
from heuristics.BitsquaresHeuristic import get_playable_lines_by_length
from util.sigmoid import scaled_sigmoid


# Winrates vs bitsquares_heuristic(reward_power=1.75)
#   30% winrate @ reward_oddeven=10
#   26% winrate @ reward_oddeven=5
#   30% winrate @ reward_oddeven=3
#   28% winrate @ reward_oddeven=2
#   52% winrate @ reward_oddeven=1
#   35% winrate @ reward_oddeven=0 - this reflects the computational penalty
def oddeven_bitsquares_heuristic(reward_power=1.75, reward_3_pair=0, reward_3_endgame=1, reward_2_endgame=0.05):
    bitsquares = bitsquares_heuristic(
        reward_power=reward_power
    )
    oddeven    = oddeven_heuristic(
        # Winrates vs bitsquares_heuristic(reward_power=1.75) @ 30 trials
        # (1,    0, 0)    = 40%     | 2 = 63% | 3 = 62% | 4 = 52%   | 5 = 57%    | 0.5 = 47%
        # (0,    1, 0)    = 80%/72% | 2 = 65% | 5 = 63% | 0.5 = 67% | 0.75 = 68% | 1.25 = 53%
        # (0,    0, 1)    = 53%     | 2 = 58% | 3 = 40% | 0.5 = 70% | 0.25 = 32% | 0.75 = 42%
        # (2,    1, 0.5)  = 23%     | /2  = 43%  | /3 = 38%
        # (0.1,  1, 0)    = 60/80%  | (0.25,1,0) = 65% | (0.5,1,0) = 73% | (1,1,0) = 47%
        # (0.01, 1, 0.05) = 52%         | (0.04,1,0.05) = 55%
        # (0,    1, 0.05) = 92%/87%/70% | (0,1,0.5)  = 47% | (0,1,0.1) = 67%  | (0,1,0.01) = 55% | (0,1,0.075) = 72% | (0,1,0.025) = 67%
        reward_3_pair=reward_3_pair,        # alone 2   = 63%
        reward_3_endgame=reward_3_endgame,  # alone 1   = 80%
        reward_2_endgame=reward_2_endgame,  # alone 0.5 = 70%
    )
    def _oddeven_bitsquares_heuristic(bitboard: np.ndarray, player_id: int) -> float:
        playable_lines   = get_playable_lines_by_length(bitboard)
        bitsquares_score = bitsquares(bitboard, player_id, playable_lines=playable_lines)
        oddeven_score    = oddeven(bitboard,    player_id, playable_lines=playable_lines)
        return bitsquares_score + oddeven_score
    return _oddeven_bitsquares_heuristic


def oddeven_heuristic(reward_3_pair=1.0, reward_3_endgame=1.0, reward_2_endgame=1.0 ):
    def _oddeven_heuristic(bitboard: np.ndarray, player_id: int, playable_lines=None) -> float:
        played_squares = bitboard[0]
        # empty_squares  = mask_board  & ~bitboard[0]

        tokens = [
            bitboard[0] & ~bitboard[1],
            bitboard[0] &  bitboard[1]
        ]
        endgame_bitboards = get_endgame_bitboard(bitboard)
        playable_lines    = playable_lines or get_playable_lines_by_length(bitboard)
        current_player    = current_player_index(bitboard)

        scores = [ 0, 0 ]
        for player in [ 0, 1 ]:
            # Safeguard against future changes to board size
            n3 = configuration.inarow - 1
            n2 = configuration.inarow - 2
            is_current_player = 0 if player == current_player else 1

            # 4 in a row
            is_4_gameover   = len(playable_lines[player][configuration.inarow])

            # 3 in a row + 2 odd or 2 even squares - opponent can't block both - doesn't seem to work in practice
            is_3_pair_count = 0
            if reward_3_pair:
                oddeven_bitboards = get_oddeven_bitboard(bitboard)
                is_3_odd   = playable_lines[player][n3] == (playable_lines[player][n3] & (tokens[player] | oddeven_bitboards[1]))
                is_3_even  = playable_lines[player][n3] == (playable_lines[player][n3] & (tokens[player] | oddeven_bitboards[0]))
                is_3_pair_count = np.count_nonzero(is_3_odd) // 2 + np.count_nonzero(is_3_even) // 2

            # For a forced double attack to work, player must force capture of one or both ends via endgame position
            is_3_endgame_count = 0
            if reward_3_endgame:
                is_3_endgame       = playable_lines[player][n3] == playable_lines[player][n3] & (played_squares | endgame_bitboards[is_current_player])
                is_3_endgame_count = np.count_nonzero( is_3_endgame )

            # 2 in a row
            is_2_endgame_count = 0
            if reward_2_endgame:
                # For a forced double attack to work, player must force capture of one or both ends via endgame position
                is_2_endgame       = playable_lines[player][n2] == playable_lines[player][n2] & (played_squares | endgame_bitboards[is_current_player])
                is_2_endgame_count = np.count_nonzero( is_2_endgame )


            # Calculate scores based on rewards
            scores[player] += np.inf          if is_4_gameover else 0
            scores[player] += reward_3_pair    * is_3_pair_count
            scores[player] += reward_3_endgame * is_3_endgame_count
            scores[player] += reward_2_endgame * is_2_endgame_count

        score = (scores[0] - scores[1]) if player_id == 1 else (scores[1] - scores[0])
        return score
    return _oddeven_heuristic



### Sigmoids

def oddeven_bitsquares_heuristic_sigmoid(reward_power=1.75, reward_3_pair=0, reward_3_endgame=1, reward_2_endgame=0.05, sigmoid_width=6.0, sigmoid_height=1.0):
    heuristic = oddeven_bitsquares_heuristic(reward_power=reward_power,
                                             reward_3_pair=reward_3_pair,
                                             reward_3_endgame=reward_3_endgame,
                                             reward_2_endgame=reward_2_endgame)
    def _oddeven_bitsquares_heuristic_sigmoid(bitboard: np.ndarray, player_id: int) -> float:
        score = heuristic(bitboard=bitboard, player_id=player_id)
        score = scaled_sigmoid(score, sigmoid_width, sigmoid_height)
        return score
    return _oddeven_bitsquares_heuristic_sigmoid


def oddeven_heuristic_sigmoid(reward_3_pair=0.0, reward_3_endgame=1.0, reward_2_endgame=0.05, sigmoid_width=6.0, sigmoid_height=1.0):
    heuristic = oddeven_heuristic(reward_3_pair=reward_3_pair,
                                  reward_3_endgame=reward_3_endgame,
                                  reward_2_endgame=reward_2_endgame)
    def _oddeven_heuristic_sigmoid(bitboard: np.ndarray, player_id: int) -> float:
        score = heuristic(bitboard=bitboard, player_id=player_id)
        score = scaled_sigmoid(score, sigmoid_width, sigmoid_height)
        return score
    return _oddeven_heuristic_sigmoid



### Predefine masks

# 7x1 Bitmasks representing the individual columns
mask_columns = np.array([
    np.sum([ 1 << (col + row * configuration.columns) for row in range(configuration.rows) ])
    for col in range(configuration.columns)
], dtype=np.int64)


### Utility Functions

def get_oddeven_bitboard( bitboard: np.ndarray ) -> Tuple[int,int]:
    # This is the slow but simple method, loop over the grid and draw the odd/even bit pixels one by one
    column_values = (bitboard[0] & mask_columns[:])
    even_columns = [
        get_even_column(column_value, col)  # OPTIMIZATION: cache the inner loop
        for col, column_value in enumerate(column_values)
    ]
    even = sum(even_columns)
    odd  = ~even & ~bitboard[0] & mask_board
    return (even, odd)

@clru_cache(None)  # size = 2**configuration.rows * configuration.columns == 448
def get_even_column( column_bitmask: int, col: int ) -> int:
    column_count = np.count_nonzero( bitcount_mask[:] & column_bitmask )
    column_space = configuration.rows - column_count

    even = 0
    for height, row in enumerate(range(column_space-1, -1, -1)):
        if height % 2 == 0:       # is even
            index = (col + row * configuration.columns)
            even |= (1 << index)  # set even pixel
    return even


def get_endgame_bitboard( bitboard: np.ndarray, endgame_columns=None ) -> Tuple[int,int]:
    oddeven_bitboard = get_oddeven_bitboard(bitboard)
    endgame_columns  = get_endgame_oddeven_columns(bitboard) if endgame_columns is None else endgame_columns
    endgame = int(np.sum([
        mask_columns[col] & oddeven_bitboard[endgame_columns[col]]
        for col in range(len(mask_columns))
    ]))
    return ( endgame, ~endgame & mask_board )  # Needs to be this way round to work with with player_index


def get_endgame_oddeven_columns(bitboard: np.ndarray) -> np.ndarray:
    """
    If all other squares outside the column where played, which player would be forced to play first in this column
    Returns 7x1 int8 array, indicating player number
    """
    column_counts   = get_column_counts(bitboard)
    total_spaces    = np.sum(column_counts)
    player_turn     = total_spaces % 2  # p1 to move if number of spaces is even
    endgame_columns = (player_turn + total_spaces - column_counts[:]) % 2
    return endgame_columns

def get_column_counts(bitboard: np.ndarray) -> np.ndarray:
    """ Return the number of empty spaces in each column """
    column_spaces = (mask_board & ~bitboard[0] & mask_columns[:])
    column_counts = np.array([
        np.count_nonzero( bitcount_mask[:] & column_bitmask )
        for column_bitmask in column_spaces
    ])
    return column_counts

