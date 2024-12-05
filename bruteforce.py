"""Brute-force solving

This solver goes through each cell in order.
It fills the current cell with one available possibility, then tries to solve the new grid.
If no solution is found at one point, it backtracks and removes the last value, and tries the next one.
If it runs out of possibilities, it marks the grid unsolvable
"""

from lib import AbstractSolver, Cell


class BruteForceSolver(AbstractSolver):
    __solver_name__ = "Brute-force Solver"

    def _solve(self) -> bool:
        # print("-" * 20)
        # print(self.grid)

        remaining_cells = self.grid.get_empty_cells()

        if not remaining_cells:
            return True

        x, y = remaining_cells[0]
        remaining_values = self.grid.get_remaining_at(x, y)
        # print(f"Remaining values at {x}, {y}: {remaining_values}")
        if remaining_values[Cell.Moon] == 0 and remaining_values[Cell.Sun] == 0:
            return False

        available_values = [k for k, v in remaining_values.items() if v > 0]
        # print(f"Available values at {x}, {y}: {available_values}")

        for v in available_values:
            if self.grid.is_valid_at(x, y, v):
                self.grid.set_cell_at(x, y, v)
            else:
                continue

            solved = self._solve()
            if solved:
                return True
            else:
                self.grid.set_empty_at(x, y)
                # print(f"Backtracking from ({x}, {y}) = {v}")
                # print(self.grid)

        return False


__all__ = ["BruteForceSolver"]
