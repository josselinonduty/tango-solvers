import numpy as np


class Cell:
    Sun = 1
    Moon = 2


class Constraint:
    Equal = 1
    Different = 2


class Tango:
    def __init__(self):
        self.board: np.ndarray = np.zeros((6, 6), dtype=int)
        self.constraints: list[dict[str, Constraint | tuple[int, int]]] = []

    def load_from_file(self, filename: str):
        with open(filename, "r") as f:
            for i, line in enumerate(f):
                if i < 6:
                    for j, value in enumerate(list(line)):
                        if value == "S":
                            self.board[i, j] = Cell.Sun
                        elif value == "M":
                            self.board[i, j] = Cell.Moon
                else:
                    constraint = line.strip().split(",")
                    structured_constraint = {
                        "type": (
                            Constraint.Different
                            if constraint[2] == "x"
                            else Constraint.Equal
                        ),
                        "from": (int(constraint[0]), int(constraint[1])),
                        "to": (int(constraint[3]), int(constraint[4])),
                    }
                    self.constraints.append(structured_constraint)

    @staticmethod
    def get_complete_list() -> list:
        return [Cell.Sun] * 3 + [Cell.Moon] * 3

    def apply_prechecks(self):
        """Fills all direct constraints.
        Required to avoid removing initial data."""

        for constraint in self.constraints:
            if (
                self.get_cell_at(*constraint["from"]) == 0
                and self.get_cell_at(*constraint["to"]) != 0
            ):
                self.set_cell_at(
                    *constraint["to"], self.get_cell_at(*constraint["to"])
                )  # Apply chaining rules
                print(f"[Precheck] Applied constraint {constraint}")
            elif (
                self.get_cell_at(*constraint["to"]) == 0
                and self.get_cell_at(*constraint["from"]) != 0
            ):
                self.set_cell_at(
                    *constraint["from"], self.get_cell_at(*constraint["from"])
                )  # Apply chaining rules
                print(f"[Precheck] Applied constraint {constraint}")

    def get_empty_cells(self) -> list:
        return list(np.add(np.argwhere(self.board == 0), 1))

    def has_constraint_at(self, x: int, y: int) -> bool:
        for constraint in self.constraints:
            if (constraint["from"] == (x, y)) or (constraint["to"] == (x, y)):
                return True
        return False

    def get_constraints_at(self, x: int, y: int) -> Constraint:
        return [
            constraint
            for constraint in self.constraints
            if constraint["from"] == (x, y) or constraint["to"] == (x, y)
        ]

    def get_cell_at(self, x: int, y: int) -> Cell:
        assert 0 < x <= 6
        assert 0 < y <= 6

        return self.board[x - 1, y - 1]

    def set_cell_at(self, x: int, y: int, v: Cell, seen=[]):
        assert 0 < x <= 6
        assert 0 < y <= 6
        assert self.is_valid_at(x, y, v)

        self.board[x - 1, y - 1] = v

        # constraints = self.get_constraints_at(x, y)
        # constraints = [
        #     constraint
        #     for constraint in constraints
        #     if constraint["from"] not in seen or constraint["to"] not in seen
        # ]

        # for constraint in constraints:
        #     if v == 0:
        #         self.set_empty_at(*constraint["from"], seen=[*seen, (x, y)])
        #         self.set_empty_at(*constraint["to"], seen=[*seen, (x, y)])
        #         continue

        #     target = None
        #     if constraint["from"] == (x, y):
        #         target = constraint["to"]
        #     elif constraint["to"] == (x, y):
        #         target = constraint["from"]

        #     if constraint["type"] == Constraint.Equal:
        #         self.set_cell_at(*target, v, seen=[*seen, (x, y)])
        #     elif constraint["type"] == Constraint.Different:
        #         self.set_cell_at(
        #             *target,
        #             Cell.Sun if v == Cell.Moon else Cell.Moon,
        #             seen=[*seen, (x, y)],
        #         )

    def is_empty_at(self, x: int, y: int) -> bool:
        assert 0 < x <= 6
        assert 0 < y <= 6

        return self.get_cell_at(x, y) == 0

    def set_empty_at(self, x: int, y: int, seen=[]):
        assert 0 < x <= 6
        assert 0 < y <= 6

        self.set_cell_at(x, y, 0, seen=seen)

    def get_row_list(self, r: int) -> tuple:
        assert 0 < r <= 6

        values, counts = np.unique(self.board[r - 1], return_counts=True)
        idx = values != 0
        values = values[idx]
        counts = counts[idx]
        return values, counts

    def get_col_list(self, c: int) -> tuple:
        assert 0 < c <= 6

        values, counts = np.unique(self.board[:, c - 1], return_counts=True)
        idx = values != 0
        values = values[idx]
        counts = counts[idx]
        return values, counts

    def get_remaining_at(self, x: int, y: int) -> dict[Cell, int]:
        """Returns the list of possible values for a cell."""

        assert 0 < x <= 6
        assert 0 < y <= 6

        row_values, row_counts = self.get_row_list(x)
        col_values, col_counts = self.get_col_list(y)

        # Calc the 3's complement of each value. For rows and cols. Keep the intersection.
        remaining_sun = 3 - max(
            [row_counts[row_values == Cell.Sun], col_counts[col_values == Cell.Sun]]
        )
        if len(remaining_sun) == 0:
            remaining_sun = [3]
        remaining_sun = remaining_sun[0]

        remaining_moon = 3 - max(
            [row_counts[row_values == Cell.Moon], col_counts[col_values == Cell.Moon]]
        )
        if len(remaining_moon) == 0:
            remaining_moon = [3]
        remaining_moon = remaining_moon[0]

        return {Cell.Sun: remaining_sun, Cell.Moon: remaining_moon}

    def get_longest_sequence_around(self, x: int, y: int, v: int) -> int:
        """Returns the longest sequence of the same value in the row or column
        that is directly connected to the cell at (x, y)."""

        assert 0 < x <= 6
        assert 0 < y <= 6
        assert v in [Cell.Sun, Cell.Moon]

        # We will use a simple window to check the longest sequence
        # We will check the row and the column separately

        row = self.board[x - 1, :].copy()
        col = self.board[:, y - 1].copy()

        row[y - 1] = v
        col[x - 1] = v

        # Find the longest sequence in the row
        longest_row = 0
        current_row = 0
        for cell in row:
            if cell == v:
                current_row += 1
            else:
                longest_row = max(longest_row, current_row)
                current_row = 0

        longest_row = max(longest_row, current_row)

        # Find the longest sequence in the column
        longest_col = 0
        current_col = 0
        for cell in col:
            if cell == v:
                current_col += 1
            else:
                longest_col = max(longest_col, current_col)
                current_col = 0

        longest_col = max(longest_col, current_col)

        return max(longest_row, longest_col)

    def is_valid_at(self, x: int, y: int, v: int, seen=[]) -> bool:
        """Checks if a value can be placed in a cell without breaking the constraints.
        Make sure that the cell is empty before calling this method and
        that constraints are also verified."""

        assert 0 < x <= 6
        assert 0 < y <= 6
        assert v in [Cell.Sun, Cell.Moon, 0]

        # print(f"[Check] checking: ({x},{y})")

        remaining = self.get_remaining_at(x, y)
        if v == Cell.Sun:
            if remaining[Cell.Sun] <= 0:
                # print("[Check] fail: 3 suns")
                return False
        elif v == Cell.Moon:
            if remaining[Cell.Moon] <= 0:
                # print("[Check] fail: 3 moons")
                return False

        if self.has_constraint_at(x, y):
            constraints = self.get_constraints_at(x, y)

            for constraint in constraints:
                if constraint["from"] == (x, y):
                    target = constraint["to"]
                elif constraint["to"] == (x, y):
                    target = constraint["from"]

                cell_at_target = self.get_cell_at(*target)
                if cell_at_target == 0:
                    continue

                if constraint["type"] == Constraint.Equal:
                    if v != 0 and v != cell_at_target:
                        # print(f"[Check] fail: constraint ({constraint})")
                        return False
                elif constraint["type"] == Constraint.Different:
                    if v != 0 and v == cell_at_target:
                        # print(f"[Check] fail: constraint ({constraint})")
                        return False

        # constraints = self.get_constraints_at(x, y)
        # constraints = [
        #     constraint
        #     for constraint in constraints
        #     if (constraint["from"] not in seen and constraint["to"] not in seen)
        # ]
        # print(f"[Check] recurse: {constraints} ({seen})")

        # for constraint in constraints:
        #     if constraint["from"] == (x, y):
        #         target = constraint["to"]
        #     elif constraint["to"] == (x, y):
        #         target = constraint["from"]

        #     if not self.is_valid_at(*target, v, seen=[*seen, (x, y)]):
        #         print(f"[Check] fail: constraint ({constraint})")
        #         return False

        if v != 0:
            longest = self.get_longest_sequence_around(x, y, v)
            if longest >= 3:
                # print("[Check] fail: sequence of 3")
                return False

        return True

    def __str__(self):
        """Create a string representation of the board, then the constraints list."""

        def cell_to_str(cell: Cell):
            if cell == Cell.Sun:
                return "S"
            elif cell == Cell.Moon:
                return "M"
            else:
                return "*"

        def constraint_to_str(constraint: Constraint):
            if constraint == Constraint.Different:
                return "x"
            elif constraint == Constraint.Equal:
                return "="
            else:
                raise ValueError("Invalid constraint value.")

        board_str = "\n".join(
            " ".join(cell_to_str(cell) for cell in row) for row in self.board
        )

        constraints_str = "\n".join(
            f"{constraint_to_str(constraint["type"])} {constraint["from"]} {constraint["to"]}"
            for constraint in self.constraints
        )

        return f"{board_str}\n{constraints_str}"


__all__ = ["Tango"]
