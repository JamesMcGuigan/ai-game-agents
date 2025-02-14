#!/usr/bin/env python3
#
# Merge Submission Files
#   find ./ -name 'submission*.csv' | xargs cat | sort -nr | awk -F',' '!a[$1]++' | sort -n | sponge > output/submission.csv
#   grep ',1,' output/submission.csv | wc -l   # count number of non-zero entries
#
# Run Main Script:
#   PYTHONUNBUFFERED=1 time -p nice ././constraint_satisfaction/z3_solver.run.py | tee -a submission.log
#
from constraint_satisfaction.solve_dataframe import solve_dataframe
from utils.datasets import submission_file, test_df

if __name__ == '__main__':
    solve_dataframe(test_df, savefile=submission_file, modulo=(1, 0), exact=False, max_timeout=0.1*60*60)
