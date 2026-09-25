# Sudoku Solver

A small Python Sudoku solver that uses backtracking and integer bitmasks to
track values already used in each row, column, and 3x3 box.

## Requirements

- Python 3.10 or newer

## Puzzle Format

Puzzles are stored as comma-separated values with exactly 81 cells. Empty
cells are represented by empty values, not by `0`.

Example:

```text
,,,5,,,,6,,8,,9,,,,,1,,1,6,,,8,7,,,,3,,,,2,6,,,,,,7,,1,,6,,,,,,8,5,,,,3,,,,4,7,,,2,1,,4,,,,,9,,8,,8,,,,3,,,
```

Values must be digits from `1` to `9`, or empty cells. Sample puzzles are in
the `samples/` directory.

## Run the Solver

From the project root, run:

```powershell
python sudoku/solver.py
```

The current entry point reads `samples/sample-sudoku-2.txt` and prints up to
two solutions. Finding two solutions is enough to show that a puzzle is not
unique.

By default, the solver stops after two solutions:

```python
solutions = solve_all_grids(grid)
```

To find every possible solution, disable the limit explicitly:

```python
solutions = solve_all_grids(grid, max_solutions=None)
```

The exhaustive mode may take significantly longer for puzzles with many
possible solutions.

## Run the Tests

From the project root, run:

```powershell
python -m unittest discover -s tests -v
```

The tests cover malformed files, invalid grid values and shapes, duplicate
givens, unique and multiple-solution puzzles, solution limits, and input-grid
immutability.

## How It Works

Each digit is represented by one bit in an integer:

- Digit 1 uses bit 0
- Digit 2 uses bit 1
- Digit 9 uses bit 8

The solver stores one bitmask for every row, column, and 3x3 box. Candidate
values are calculated by combining those masks. The solver chooses the empty
cell with the fewest candidates, tries each candidate, and backtracks when a
choice cannot lead to a solution.

## Project Structure

```text
sudoku-solver/
|-- samples/
|   |-- sample-sudoku.txt
|   `-- sample-sudoku-2.txt
|-- tests/
|   `-- test_solver.py
|-- sudoku/
|   |-- __init__.py
|   `-- solver.py
|-- .gitignore
`-- README.md
```

## Current Limitations

- The input filename is currently configured in `solver.py`.
- The solver returns up to two solutions by default; it can enumerate every
  solution when called with `max_solutions=None`.
- Command-line argument support has not been added yet.
