#!/usr/bin/env bash
cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}/..")")"  # https://stackoverflow.com/questions/3349105/how-to-set-current-working-directory-to-the-directory-of-the-script/51651602#51651602

#python3 ./submission/kaggle_compile.py src/ensemble/sample_sub/sample_sub_combine.py | tee ./submission/submission.py
#python3 ./submission/kaggle_compile.py ./src/submission.py | tee ./submission/submission.py
python3 ./submission/kaggle_compile.py ./src/main.py | tee ./submission/submission.py
time -p python3 ./submission/submission.py | tee ./submission/submission.log