import random


class MazeGenerator:
    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool = True,
        seed: int | None = 42,
    ) -> None:
        self._x_axis = width
        self._y_axis = height
        self._entry = entry
        self._exit = exit
        self._perfect = perfect
        self._seed = seed
        if self._seed is not None:
            random.seed(self._seed)
        self._maze: list[list[int]] = []
        self._path: list = []

    def _initialize_grid(self) -> list[list[int]]:
        return [[15 for _ in range(self._x_axis)] for _ in range(self._y_axis)]

    def _place_42_pattern(self) -> set[tuple[int, int]]:
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
        global_42_cordinates: set[tuple[int, int]] = set()
        for x_local, y_local in local_42_pattern:
            global_x = x_local + offset_x
            global_y = y_local + offset_y
            global_42_cordinates.add((global_x, global_y))
        return global_42_cordinates

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
        self, current_x: int, current_y: int, next_x: int, next_y: int,
        direction: str
    ) -> None:
        # SWNE s:7_w:11_n:13_e:14
        # S:sn W: we N: ns E: ew
        match direction:
            case "s" | "S":
                self._maze[current_x][current_y] &= 11
                self._maze[next_x][next_y] &= 14
            case "w" | "W":
                self._maze[current_x][current_y] &= 7
                self._maze[next_x][next_y] &= 13
            case "n" | "N":
                self._maze[current_x][current_y] &= 14
                self._maze[next_x][next_y] &= 11
            case "e" | "E":
                self._maze[current_x][current_y] &= 13
                self._maze[next_x][next_y] &= 7

    def generate_maze(self) -> None:
        visited = self._place_42_pattern()
        stack = []
        visited.add(self._entry)
        stack.append(self._entry)
        while stack:
            current_x, current_y = stack.pop()
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

    def _get_open_neighbors(
            self,
            x: int,
            y: int
            ) -> list[tuple[int, int, str]]:
        """
        Checks N, E, S, W from (x, y).
        Returns neighbors ONLY if the bitwise wall in that direction is open
        (bit is 0).
        Example return: [(x+1, y, 'E'), (x, y+1, 'S')]
        """
        return list()

    def _dls(
            self,
            curr_x: int,
            curr_y: int,
            limit: int,
            visited: set[tuple[int, int]],
            path: list[str]
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
        max_possible_depth = self._x_axis * self._y_axis
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
