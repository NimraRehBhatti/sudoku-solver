import unittest
from pathlib import Path

from sudoku.test import (
    ALL_DIGITS_MASK,
    EMPTY_CELL,
    GRID_SIZE,
    build_initial_masks,
    parse_cell_token,
    read_grid_from_input_file,
    solve_all_grids,
)


def load_sample_puzzles() -> list[tuple[str, list[list[int]]]]:
    samples_dir = Path(__file__).parent.parent / "samples"
    return [
        (file_path.name, read_grid_from_input_file(file_path))
        for file_path in sorted(samples_dir.glob("*.txt"))
    ]


SAMPLE_PUZZLES = load_sample_puzzles()


class BasicInputTests(unittest.TestCase):
    def test_parses_empty_and_digit_tokens(self) -> None:
        self.assertEqual(parse_cell_token("", 1), EMPTY_CELL)
        self.assertEqual(parse_cell_token("5", 2), 5)

        with self.assertRaises(ValueError):
            parse_cell_token("x", 3)

    def test_rejects_invalid_grids(self) -> None:
        with self.assertRaisesRegex(ValueError, "9 rows of 9 cells"):
            build_initial_masks([[1, 2, 3]])

        duplicate_grid = [[EMPTY_CELL] * GRID_SIZE for _ in range(GRID_SIZE)]
        duplicate_grid[0][0] = 1
        duplicate_grid[0][1] = 1
        with self.assertRaisesRegex(ValueError, "repeated"):
            build_initial_masks(duplicate_grid)


class SolverTests(unittest.TestCase):
    def test_solves_each_sample_puzzle(self) -> None:
        self.assertTrue(SAMPLE_PUZZLES, "No sample puzzles were found")

        for file_name, puzzle in SAMPLE_PUZZLES:
            with self.subTest(puzzle=file_name):
                original = [row[:] for row in puzzle]
                solutions = solve_all_grids(puzzle, max_solutions=2)

                self.assertTrue(solutions, f"Puzzle {file_name} has no solution")
                self.assertEqual(puzzle, original)

                for solution in solutions:
                    row_masks, column_masks, box_masks = build_initial_masks(solution)
                    self.assertEqual(row_masks, [ALL_DIGITS_MASK] * GRID_SIZE)
                    self.assertEqual(column_masks, [ALL_DIGITS_MASK] * GRID_SIZE)
                    self.assertEqual(box_masks, [ALL_DIGITS_MASK] * GRID_SIZE)
                    for row in range(GRID_SIZE):
                        for column in range(GRID_SIZE):
                            if puzzle[row][column] != EMPTY_CELL:
                                self.assertEqual(solution[row][column], puzzle[row][column])


if __name__ == "__main__":
    unittest.main()
