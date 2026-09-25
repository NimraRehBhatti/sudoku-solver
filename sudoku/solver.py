"""Utilities for reading and solving Sudoku puzzles with high-performance bitmasks."""
# Bit 0 represents 1, bit 1 represents 2, ..., bit 8 represents 9.
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


def main() -> None:
    """Read a sample puzzle, find up to two solutions, and print them."""
    samples_dir = Path(__file__).resolve().parent.parent / "samples"
    file_name = "sample-sudoku-4.txt"
    sample_file = samples_dir / file_name

    if not sample_file.exists():
        raise FileNotFoundError(f"Sample Sudoku file not found: {sample_file}")
    if not sample_file.is_file():
        raise ValueError(f"Sample Sudoku path is not a regular file: {sample_file}")

    try:
        sudoku_grid = read_grid_from_input_file(sample_file)
    except UnicodeDecodeError as error:
        raise ValueError(
            f"Sample Sudoku file is not valid UTF-8: {sample_file}"
        ) from error
    except OSError as error:
        raise PermissionError(
            f"Sample Sudoku file is not readable: {sample_file}"
        ) from error
    solutions = solve_all_grids(sudoku_grid, max_solutions=None)

    print(f"\nFound {len(solutions)} solution(s):")
    for index, solution in enumerate(solutions, start=1):
        print(f"\nSolution {index}:")
        for row in solution:
            print(row)


if __name__ == "__main__":
    main()