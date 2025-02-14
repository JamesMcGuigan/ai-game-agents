# Artificial Intelligence Games

## Games

### ConnectX 
- Source: [games/connectx](games/connectx)
- Kaggle: https://www.kaggle.com/jamesmcguigan/connectx-manually-coded-strategies
- Kaggle: https://www.kaggle.com/jamesmcguigan/connectx-alphabeta-minimax-with-numba

Writeup on a variety of approaches to competitive AI agent design, exploring classic game: Connect 4
 
- Random Agent
- Simple Rules Agent
- Minimax with AlphaBeta Pruning, Iterative Deepening and custom heuristic
    - Object Oriented / Numpy implementation (slow)
    - Bitboard Implementation (fast)
    
### Knights Isolation
- Source: [games/knights-isolation](games/knights-isolation)
- Report: [games/knights-isolation/report.ipynb](games/knights-isolation/report.ipynb)
 
 
Minimax adversarial search with alphaBeta pruning, iterative deepening, area heuristic, and persistent caching.
 
Monty Carlo Tree Search reinforcement learning 
 


## Search

### Ant Colony Optimization Algorithm with Kmeans
- Source: [search/ant_colony](search/ant_colony)
- Kaggle: https://www.kaggle.com/jamesmcguigan/ant-colony-optimization-algorithm
- Kaggle: https://www.kaggle.com/jamesmcguigan/kmeans-ant-colony-optimization

Ant Colony Solution the Travelling Salesman Problem


### ARC - Abstraction and Reasoning Corpus
- Source: [search/arc](search/arc)
- Kaggle: https://www.kaggle.com/jamesmcguigan/arc-geometry-solvers
- Kaggle: https://www.kaggle.com/jamesmcguigan/arc-solver-multimodel
- Dataset: https://github.com/fchollet/ARC

> ARC can be seen as a general artificial intelligence benchmark, as a program synthesis benchmark, or as a psychometric intelligence test. It is targeted at both humans and artificially intelligent systems that aim at emulating a human-like form of general fluid intelligence.

Object model and frameworks for reasoning by analogy function solvers. 

Brute force search of simple geometry and tessellation transformations with numpy. 

XGBoost with a large multidimensional feature map was able to auto-solve a wide range of transformations. 

AbstractSolver - Proof of Concept code using inspect.signature() to figure out all possible permutations of `f(g(h(x)))` implementing a IoC dependency injection solver.


### Pacman - A* Search
- Source: [search/pacman](search/pacman)

A* Search Algorithms to navigate Pacman round a maze 


## Puzzles

### Sudoku
- Source: [puzzles/sudoku](puzzles/sudoku)
- Kaggle: https://www.kaggle.com/jamesmcguigan/z3-sudoku-solver/

Sudoku Solver that can solve the World's Hardest Sudoku

### N Queens
- Source: [puzzles/n_queens](puzzles/n_queens)
- Kaggle: https://www.kaggle.com/jamesmcguigan/n-queens-92-solutions-in-prolog

This code solves the N-Queens problem in Prolog using the CLP(FD): Constraint Logic Programming over Finite Domain Library

### Cryptarithmetic
- Source: [puzzles/cryptarithmetic](puzzles/cryptarithmetic)
- Kaggle: https://www.kaggle.com/jamesmcguigan/cryptarithmetic-solver

This is a general purpose solver that can handle addition, subtraction, multiplication, integer division and raising to powers.
