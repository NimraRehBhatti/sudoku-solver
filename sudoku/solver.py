"""Utilities for reading and solving Sudoku puzzles with high-performance bitmasks."""
# Bit 0 represents 1, bit 1 represents 2, ..., bit 8 represents 9.
import argparse
from pathlib import Path

GRID_SIZE = 9
BOX_SIZE = 3
EXPECTED_CELL_COUNT = GRID_SIZE * GRID_SIZE
EMPTY_CELL = 0
ALL_DIGITS_MASK = (1 << GRID_SIZE) - 1


def read_grid_from_input_file(file_path: Path) -> list[list[int]]:
    """Read and validate a comma-separated Sudoku grid from a file."""
    with file_path.open("r", encoding="utf-8") as file:
        text = file.read()

    tokens = text.strip().split(",")
    if len(tokens) != EXPECTED_CELL_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_CELL_COUNT} values, got {len(tokens)}."
        )

    values: list[int] = []
    for position, token in enumerate(tokens, start=1):
        token = token.strip()
        if token == "":
            values.append(EMPTY_CELL)
            continue
        if len(token) != 1 or token not in "123456789":
            raise ValueError(
                f"Invalid value {token!r} at position {position}."
            )
        values.append(int(token))

    return [
        values[row * GRID_SIZE:(row + 1) * GRID_SIZE]
        for row in range(GRID_SIZE)
    ]


def build_initial_masks(
    grid: list[list[int]],
) -> tuple[list[int], list[int], list[int]]:
    """Build row, column, and box masks from the puzzle's given values."""
    if len(grid) != GRID_SIZE or any(len(row) != GRID_SIZE for row in grid):
        raise ValueError("Sudoku grid must contain 9 rows of 9 cells.")

    row_masks = [0] * GRID_SIZE
    column_masks = [0] * GRID_SIZE
    box_masks = [0] * GRID_SIZE

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            value = grid[row][column]
            if value == EMPTY_CELL:
                continue
            if value not in range(1, GRID_SIZE + 1):
                raise ValueError("Sudoku cells must contain values from 0 to 9.")

            bit = 1 << (value - 1)
            box = (row // BOX_SIZE) * BOX_SIZE + column // BOX_SIZE

            if (
                row_masks[row] & bit
                or column_masks[column] & bit
                or box_masks[box] & bit
            ):
                raise ValueError(
                    f"Value {value} is repeated near row {row + 1}, "
                    f"column {column + 1}."
                )

            row_masks[row] |= bit
            column_masks[column] |= bit
            box_masks[box] |= bit

    return row_masks, column_masks, box_masks


def find_cell_with_fewest_candidates(
    grid: list[list[int]],
    row_masks: list[int],
    column_masks: list[int],
    box_masks: list[int],
) -> tuple[int, int, int]:
    """Return the empty cell with the fewest candidates and its mask."""
    best_row, best_column = -1, -1
    fewest_candidates = GRID_SIZE + 1
    best_mask = 0

    for row in range(GRID_SIZE):
        for column in range(GRID_SIZE):
            if grid[row][column] != EMPTY_CELL:
                continue

            box = (row // BOX_SIZE) * BOX_SIZE + column // BOX_SIZE
            used_mask = row_masks[row] | column_masks[column] | box_masks[box]
            candidate_mask = ALL_DIGITS_MASK & ~used_mask
            candidate_count = candidate_mask.bit_count()

            if candidate_count == 0:
                return row, column, 0

            if candidate_count < fewest_candidates:
                fewest_candidates = candidate_count
                best_row, best_column = row, column
                best_mask = candidate_mask

                if candidate_count == 1:
                    return best_row, best_column, best_mask

    return best_row, best_column, best_mask


def solve_all_grids(
    sudoku_grid: list[list[int]],
    max_solutions: int | None = 2,
) -> list[list[list[int]]]:
    """Return solutions, stopping after two unless another limit is given."""
    if max_solutions is not None and max_solutions < 1:
        raise ValueError("max_solutions must be at least 1 or None.")

    grid_copy = [row[:] for row in sudoku_grid]
    row_masks, column_masks, box_masks = build_initial_masks(grid_copy)
    solutions: list[list[list[int]]] = []

    def backtrack() -> None:
        row, column, candidate_mask = find_cell_with_fewest_candidates(
            grid_copy, row_masks, column_masks, box_masks
        )

        if row == -1 and column == -1:
            solutions.append([current_row[:] for current_row in grid_copy])
            return max_solutions is not None and len(solutions) >= max_solutions

        if candidate_mask == 0:
            return False

        box = (row // BOX_SIZE) * BOX_SIZE + column // BOX_SIZE

        local_candidates = candidate_mask
        while local_candidates:
            bit = local_candidates & -local_candidates
            local_candidates ^= bit
            value = bit.bit_length()

            grid_copy[row][column] = value
            row_masks[row] |= bit
            column_masks[column] |= bit
            box_masks[box] |= bit

            reached_limit = backtrack()

            grid_copy[row][column] = EMPTY_CELL
            row_masks[row] ^= bit
            column_masks[column] ^= bit
            box_masks[box] ^= bit

            if reached_limit:
                return True

        return False

    backtrack()
    return solutions


def positive_integer(value: str) -> int:
    """Convert a command-line value to a positive integer."""
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return number


def print_solution(solution: list[list[int]]) -> None:
    """Print a Sudoku solution in a readable format."""
    for row_index, row in enumerate(solution):
        if row_index in (3, 6):
            print("------+-------+------")

        print(
            f"{row[0]} {row[1]} {row[2]} | "
            f"{row[3]} {row[4]} {row[5]} | "
            f"{row[6]} {row[7]} {row[8]}"
        )


def main() -> None:
    """Run the Sudoku solver command-line interface."""
    parser = argparse.ArgumentParser(
        description="Solve a Sudoku puzzle stored in a file."
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="path to a file containing exactly 81 Sudoku values",
    )

    solution_limit = parser.add_mutually_exclusive_group()
    solution_limit.add_argument(
        "--max-solutions",
        type=positive_integer,
        default=2,
        help="maximum number of solutions to find (default: 2)",
    )
    solution_limit.add_argument(
        "--all",
        action="store_true",
        help="find every possible solution",
    )

    args = parser.parse_args()

    try:
        sudoku_grid = read_grid_from_input_file(args.input_file)
        max_solutions = None if args.all else args.max_solutions
        solutions = solve_all_grids(
            sudoku_grid,
            max_solutions=max_solutions,
        )
    except FileNotFoundError:
        parser.error(f"file not found: {args.input_file}")
    except IsADirectoryError:
        parser.error(f"expected a file, got a directory: {args.input_file}")
    except UnicodeDecodeError:
        parser.error(f"file is not valid UTF-8: {args.input_file}")
    except OSError as error:
        parser.error(f"could not read {args.input_file}: {error}")
    except ValueError as error:
        parser.error(str(error))

    print(f"Found {len(solutions)} solution(s).")

    if not solutions:
        print("The puzzle has no solution.")
        return

    for index, solution in enumerate(solutions, start=1):
        print(f"\nSolution {index}:")
        print_solution(solution)


if __name__ == "__main__":
    main()