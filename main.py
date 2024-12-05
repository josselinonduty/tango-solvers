import sys

from lib import Tango, AbstractSolver

from bruteforce import BruteForceSolver

# from human import HumanSolver


def main():
    solvers: list[AbstractSolver] = [BruteForceSolver]

    for Solver in solvers:
        print("=" * 20)
        print(f"Using {Solver.name()}")

        game = Tango()
        game.load_from_file("./examples/no59.txt")
        game.apply_prechecks()

        solver = Solver(game)
        solvable = solver.solve()

        if "-v" in sys.argv:
            if solvable:
                print(game)
            else:
                print("No solution found.")
        print(f"Took: {solver.duration.total_seconds()*1000:.3f}ms")


if __name__ == "__main__":
    main()
