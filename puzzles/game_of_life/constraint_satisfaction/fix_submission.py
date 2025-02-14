#!/usr/bin/env python3
import time

import numpy as np
from numba import njit

from utils.datasets import sample_submission_df
from utils.datasets import submission_df
from utils.datasets import submission_file
from utils.datasets import test_df
from utils.game import life_step
from utils.util import csv_to_delta_list
from utils.util import csv_to_numpy
from utils.util import csv_to_numpy_list
from utils.util import numpy_to_series


@njit
def is_valid_solution(start: np.ndarray, stop: np.ndarray, delta: int) -> bool:
    # we are rewriting data, so lets double check our work
    test_board = start
    is_valid   = np.count_nonzero(test_board) != 0
    if not is_valid: return False
    for t in range(delta):
        test_board = life_step(test_board)
        is_valid   = is_valid and np.count_nonzero(test_board) != 0
        if not is_valid: return False
    is_valid = is_valid and np.all(test_board == stop)
    return is_valid

@njit
def is_valid_solution_3d(solution_3d: np.ndarray) -> bool:
    return is_valid_solution(solution_3d[0], solution_3d[-1], delta=len(solution_3d)-1)


def fix_submission(max_offset=1):
    """
    There was a bug in game_of_life_solver() that was solving to T=-(delta+1) rather than delta.
    The result of this was seemingly random scores on the leaderboard, and extra compute time for an additional delta
    The fix is to play each submission entry forwards, and find the correct delta for start

    See: tests/test_submission.py
    """
    time_start = time.perf_counter()

    invalid_idxs = set(submission_df.index) - set(sample_submission_df.index)
    if len(invalid_idxs):
        submission_df.drop(invalid_idxs, inplace=True)
        print( f'fix_submission() non-submission idxs: {invalid_idxs}' )

    missing_idxs = set(sample_submission_df.index) - set(submission_df.index)
    if len(missing_idxs):
        print( f'fix_submission() missing idxs: {missing_idxs}' )
        for idx in missing_idxs:
            stop = csv_to_numpy(test_df, idx, key='stop')
            submission_df.loc[idx] = numpy_to_series(np.zeros(stop.shape, dtype=np.int), key='start')  # zero out the entry and retry

    idxs   = [ idx for idx in submission_df.index if np.count_nonzero(submission_df.loc[idx]) if idx in test_df.index ]
    deltas = csv_to_delta_list(test_df.loc[idxs])
    starts = csv_to_numpy_list(submission_df.loc[idxs], key='start')
    stops  = csv_to_numpy_list(test_df.loc[idxs],       key='stop')
    stats  = {
        "time":    time.perf_counter() - time_start,
        "empty":   len(submission_df.index) - len(idxs),
        "total":   len(submission_df.index),
        "valid":   0,
        "fixed":   len(missing_idxs),
        "invalid": len(invalid_idxs),
    }
    for idx, delta, start, stop in zip(idxs, deltas, starts, stops):
        try:
            assert np.count_nonzero(start), idx
            assert np.count_nonzero(stop),  idx

            if is_valid_solution(start, stop, delta):
                stats['valid'] += 1
                continue  # submission.csv is valid for idx, so skip

            solution = start
            for t in range(1, max_offset+1):
                solution = life_step(solution)
                if is_valid_solution(solution, stop, delta):
                    submission_df.loc[idx] = numpy_to_series(solution, key='start')
                    stats['fixed'] += 1
                    break
            else:
                submission_df.loc[idx] = numpy_to_series(np.zeros(stop.shape), key='start')  # zero out the entry and retry
                print( f'fix_submission() invalid solution | idx: {idx} | delta: {delta} | cells: {np.count_nonzero(solution != stop)}' )
                stats['invalid'] += 1
                pass
        except Exception as exception:
            print( f'fix_submission() idx: {idx} | exception: {exception}' )
            stats['invalid'] += 1
            pass
    # assert stats['total'] == stats['valid'] + stats['fixed'] + stats['invalid']

    # if stats['fixed'] + stats['invalid'] > 0:
    submission_df.sort_index().astype(np.int).to_csv(submission_file)
    print( f'fix_submission() wrote: {submission_file}' )

    time_taken = time.perf_counter() - time_start
    stats['time'] = f'{time_taken:.1f}'
    print('fix_submission()', stats)



if __name__ == '__main__':
    fix_submission()
