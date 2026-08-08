"""Mazegen: reusable maze generator with DFS carving and IDDFS solving."""

import random
import sys


class MazeGenerator:
    """Generates, solves and exports a random maze.

    The maze is a grid of cells; each cell stores its walls as a 4-bit
    mask (bit0=North, bit1=East, bit2=South, bit3=West, 1 = closed).
    WSEN
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool = True,
        seed: int | None = 42,
    ) -> None:
        """Store the maze parameters and seed the random generator."""
        self._x_axis = width
        self._y_axis = height
        self._entry = entry
        self._exit = exit
        self._perfect = perfect
        self._seed = seed
        if self._seed is not None:
            random.seed(self._seed)
        self._maze: list[list[int]] = []
        self._path: list[str] = []
        self._solution: str | None = None
        self._pattern: set[tuple[int, int]] = set()

    def _initialize_grid(self) -> list[list[int]]:
        return [[15 for _ in range(self._x_axis)] for _ in range(self._y_axis)]

    def _place_42_pattern(self) -> set[tuple[int, int]]:
        """Return the cells drawing a '42', or an empty set if impossible."""
        if self._x_axis < 9 or self._y_axis < 7:
            print("Error: Maze is too small to fit the '42' pattern.")
            return set()
        local_42_pattern = [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (2, 4),
            (4, 0),
            (5, 0),
            (6, 0),
            (6, 1),
            (6, 2),
            (5, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (5, 4),
            (6, 4),
        ]
        offset_x = (self._x_axis - 7) // 2
        offset_y = (self._y_axis - 5) // 2
        global_42_cords: set[tuple[int, int]] = set()
        for x_local, y_local in local_42_pattern:
            global_x = x_local + offset_x
            global_y = y_local + offset_y
            global_42_cords.add((global_x, global_y))
        if self._entry in global_42_cords or self._exit in global_42_cords:
            print("Error: entry or exit overlaps '42' pattern", end=' ')
            print("pattern omitted.")
            return set()
        return global_42_cords

    def _get_unvisited_neighbors(
        self, x: int, y: int, visited: set[tuple[int, int]]
    ) -> list[tuple[int, int, str]]:
        neighbors = list()
        if (x > 0) and (x - 1, y) not in visited:
            neighbors.append((x - 1, y, "W"))
        if (x < self._x_axis - 1) and (x + 1, y) not in visited:
            neighbors.append((x + 1, y, "E"))
        if (y > 0) and (x, y - 1) not in visited:
            neighbors.append((x, y - 1, "N"))
        if (y < self._y_axis - 1) and (x, y + 1) not in visited:
            neighbors.append((x, y + 1, "S"))
        return neighbors

    def _break_wall(
        self,
        current_x: int, current_y: int,
        next_x: int, next_y: int,
        direction: str
    ) -> None:
        # SWNE s:7_w:11_n:13_e:14
        # S:sn W: we N: ns E: ew
        match direction:
            case "s" | "S":
                self._maze[current_y][current_x] &= 11
                self._maze[next_y][next_x] &= 14
            case "w" | "W":
                self._maze[current_y][current_x] &= 7
                self._maze[next_y][next_x] &= 13
            case "n" | "N":
                self._maze[current_y][current_x] &= 14
                self._maze[next_y][next_x] &= 11
            case "e" | "E":
                self._maze[current_y][current_x] &= 13
                self._maze[next_y][next_x] &= 7

    def generate_maze(self) -> None:
        """Carve a maze with iterative DFS, avoiding the '42' cells."""
        self._maze = self._initialize_grid()
        self._solution = None
        self._pattern = self._place_42_pattern()
        visited = set(self._pattern)
        stack = []
        visited.add(self._entry)
        stack.append(self._entry)
        while stack:
            current_x, current_y = stack[-1]
            neighbors = self._get_unvisited_neighbors(current_x, current_y,
                                                      visited)
            if neighbors:
                next_x, next_y, direction = random.choice(neighbors)
                self._break_wall(current_x, current_y, next_x, next_y,
                                 direction)
                visited.add((next_x, next_y))
                stack.append((next_x, next_y))
            else:
                stack.pop()
        if not self._perfect:
            self._add_loops()

    def _has_open_3x3(self) -> bool:
        """Return True if any 3x3 block of cells has no internal wall."""
        for by in range(self._y_axis - 2):
            for bx in range(self._x_axis - 2):
                fully_open = True
                for j in range(3):
                    for i in range(3):
                        cell = self._maze[by + j][bx + i]
                        if i < 2 and cell & 2:
                            fully_open = False
                        if j < 2 and cell & 4:
                            fully_open = False
                if fully_open:
                    return True
        return False

    def _add_loops(self) -> None:
        """Open extra internal walls so multiple paths exist.

        Each removal is reverted if it would create a 3x3 open area.
        """
        target = max(1, (self._x_axis * self._y_axis) // 20)
        opened = 0
        attempts = 0
        while opened < target and attempts < target * 20:
            attempts += 1
            x = random.randrange(self._x_axis)
            y = random.randrange(self._y_axis)
            if random.random() < 0.5 and x < self._x_axis - 1:
                next_x, next_y, direction = x + 1, y, "E"
            elif y < self._y_axis - 1:
                next_x, next_y, direction = x, y + 1, "S"
            else:
                continue
            if (x, y) in self._pattern or (next_x, next_y) in self._pattern:
                continue
            bit = 2 if direction == "E" else 4
            if not self._maze[y][x] & bit:
                continue
            before = (self._maze[y][x], self._maze[next_y][next_x])
            self._break_wall(x, y, next_x, next_y, direction)
            if self._has_open_3x3():
                self._maze[y][x], self._maze[next_y][next_x] = before
            else:
                opened += 1

    def _get_open_neighbors(
            self, x: int, y: int
            ) -> list[tuple[int, int, str]]:
        """
        Checks N, E, S, W from (x, y).
        Returns neighbors ONLY if the bitwise wall in that direction is open
        (bit is 0).
        Example return: [(x+1, y, 'E'), (x, y+1, 'S')]
        """
        walls = self._maze[y][x]
        neighbors = []
        if not walls & 1 and y > 0:
            neighbors.append((x, y - 1, "N"))
        if not walls & 2 and x < self._x_axis - 1:
            neighbors.append((x + 1, y, "E"))
        if not walls & 4 and y < self._y_axis - 1:
            neighbors.append((x, y + 1, "S"))
        if not walls & 8 and x > 0:
            neighbors.append((x - 1, y, "W"))
        return neighbors

    def _dls(
        self,
        curr_x: int,
        curr_y: int,
        limit: int,
        visited: set[tuple[int, int]],
        path: list[str],
    ) -> bool:
        """
        Depth-Limited Search helper.
        Returns True if the exit is found within 'limit' steps,
        False otherwise.
        """
        # 1. Base Case: Did we reach the exit?
        if (curr_x, curr_y) == self._exit:
            return True
        # 2. Base Case: Did we run out of steps?
        if limit <= 0:
            return False
        # 3. Explore open neighbors:
        for next_x, next_y, direction in self._get_open_neighbors(curr_x,
                                                                  curr_y):
            if (next_x, next_y) not in visited:
                visited.add((next_x, next_y))
                path.append(direction)
                if self._dls(next_x, next_y, limit - 1, visited, path):
                    return True
                # Backtrack if that branch failed:
                path.pop()
                visited.remove((next_x, next_y))
        # 4. If no path worked at this limit:
        return False

    def solve_maze_iddfs(self) -> str:
        """
        Runs Iterative Deepening DFS to find the shortest path
        from entry to exit.
        Returns the path as a string of N, E, S, W characters.
        """
        cells = self._x_axis * self._y_axis
        sys.setrecursionlimit(max(1000, cells + 200))
        max_possible_depth = cells
        # Loop from depth 0 up to max_possible_depth
        for depth_limit in range(max_possible_depth + 1):
            visited: set[tuple[int, int]] = {self._entry}
            path: list[str] = []
            # Try to reach the exit within the current depth_limit
            if self._dls(self._entry[0], self._entry[1], depth_limit, visited,
                         path):
                # We found the shortest path!
                # Join the list into a string and store it.
                solution_str = "".join(path)
                self._path = path  # Optional: store if needed elsewhere
                return solution_str
        return ""  # Should never reach here if the maze is solvable

    def get_structure(self) -> list[list[int]]:
        """Return the maze grid: one wall bitmask per cell, row by row."""
        return self._maze

    def get_solution(self) -> str:
        """Return the shortest entry-to-exit path (cached per maze)."""
        if self._solution is None:
            self._solution = self.solve_maze_iddfs()
        return self._solution

    def export_to_hex_file(self, path: str) -> None:
        """Write the maze, entry, exit and solution to the output file."""
        lines = ["".join(format(cell, "X") for cell in row)
                 for row in self._maze]
        with open(path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")
            file.write("\n")
            file.write(f"{self._entry[0]},{self._entry[1]}\n")
            file.write(f"{self._exit[0]},{self._exit[1]}\n")
            file.write(self.get_solution() + "\n")
