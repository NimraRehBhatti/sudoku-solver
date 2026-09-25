import tempfile
import unittest
from pathlib import Path

from sudoku.solver import (
    EMPTY_CELL,
    build_initial_masks,
    read_grid_from_input_file,
    solve_all_grids,
)


SOLVED_GRID = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def grid_as_csv(grid: list[list[int]]) -> str:
    return ",".join(
        "" if value == EMPTY_CELL else str(value)
        for row in grid
        for value in row
    )


class ReadGridTests(unittest.TestCase):
    def test_reads_a_csv_file_with_whitespace(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "puzzle.csv"
            file_path.write_text(f"  {grid_as_csv(SOLVED_GRID)}  ", encoding="utf-8")

            self.assertEqual(read_grid_from_input_file(file_path), SOLVED_GRID)

    def test_rejects_wrong_number_of_cells(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            file_path = Path(directory) / "bad.txt"
            file_path.write_text("1,2,3", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Expected 81 values"):
                read_grid_from_input_file(file_path)

    def test_rejects_zero_and_multi_digit_values(self) -> None:
        for invalid_value in ("0", "10", "x"):
            with self.subTest(invalid_value=invalid_value):
                values = [""] * 81
                values[0] = invalid_value
                with tempfile.TemporaryDirectory() as directory:
                    file_path = Path(directory) / "bad.csv"
                    file_path.write_text(",".join(values), encoding="utf-8")

                    with self.assertRaises(ValueError):
                        read_grid_from_input_file(file_path)


class GridValidationTests(unittest.TestCase):
    def test_rejects_duplicate_values_in_a_row(self) -> None:
        grid = [row[:] for row in SOLVED_GRID]
        grid[0][1] = grid[0][0]

        with self.assertRaisesRegex(ValueError, "repeated"):
            build_initial_masks(grid)

    def test_rejects_wrong_grid_shape(self) -> None:
        with self.assertRaisesRegex(ValueError, "9 rows of 9 cells"):
            build_initial_masks([[1, 2, 3]])

    def test_rejects_values_outside_zero_through_nine(self) -> None:
        grid = [row[:] for row in SOLVED_GRID]
        grid[0][0] = 10

        with self.assertRaisesRegex(ValueError, "values from 0 to 9"):
            build_initial_masks(grid)


class SolverTests(unittest.TestCase):
    def test_finds_the_only_solution_for_one_empty_cell(self) -> None:
        puzzle = [row[:] for row in SOLVED_GRID]
        puzzle[0][0] = EMPTY_CELL

        solutions = solve_all_grids(puzzle)

        self.assertEqual(solutions, [SOLVED_GRID])

    def test_stops_after_two_solutions_for_an_empty_grid(self) -> None:
        solutions = solve_all_grids([[EMPTY_CELL] * 9 for _ in range(9)])

        self.assertEqual(len(solutions), 2)

    def test_rejects_an_invalid_solution_limit(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 1"):
            solve_all_grids(SOLVED_GRID, max_solutions=0)

    def test_does_not_mutate_the_input_grid(self) -> None:
        puzzle = [row[:] for row in SOLVED_GRID]
        puzzle[0][0] = EMPTY_CELL
        original = [row[:] for row in puzzle]

        solve_all_grids(puzzle)

        self.assertEqual(puzzle, original)


if __name__ == "__main__":
    unittest.main()
