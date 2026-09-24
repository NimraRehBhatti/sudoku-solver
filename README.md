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

The current entry point solves `samples/sample-sudoku-2.txt` and prints the
completed grid.

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
|-- sudoku/
|   |-- __init__.py
|   `-- solver.py
|-- .gitignore
`-- README.md
```

## Current Limitations

- The input filename is currently configured in `solver.py`.
- The solver returns the first solution it finds; it does not check whether a
	puzzle has multiple solutions.
- Automated tests and command-line argument support have not been added yet.
