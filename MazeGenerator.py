import random


class MazeGenerator():
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exit: tuple[int, int],
            perfect: bool = True,
            seed: int | None = 42
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
        return [[15 for _ in range(self._x_axis)]
                for _ in range(self._y_axis)]

    def _place_42_pattern(self) -> set[tuple[int, int]]:
        if self._x_axis < 9 or self._y_axis < 7:
            print("Error: Maze is too small to fit the '42' pattern.")
            return set()
        local_42_pattern = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 3), (2, 4),
            (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2), (4, 2),
            (4, 3), (4, 4), (5, 4), (6, 4)
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
            self,
            x: int,
            y: int,
            visited: set[tuple[int, int]]
            ) -> list[tuple[int, int, str]]:
        neighbors = list()
        if (x > 0) and (x-1, y) not in visited:
            neighbors.append((x-1, y, 'W'))
        if (x < self._x_axis - 1) and (x+1, y) not in visited:
            neighbors.append((x+1, y, 'E'))
        if (y > 0) and (x, y-1) not in visited:
            neighbors.append((x, y-1, 'N'))
        if (y < self._y_axis - 1) and (x, y+1) not in visited:
            neighbors.append((x, y+1, 'S'))
        return neighbors

    def _break_wall(
            self,
            current_x: int,
            current_y: int,
            next_x: int,
            next_y: int,
            direction: str
            ) -> None:
        # SWNE s:7_w:11_n:13_e:14
        # S:sn W: we N: ns E: ew
        match direction:
            case 's' | 'S':
                self._maze[current_x][current_y] &= 11
                self._maze[next_x][next_y] &= 14
            case 'w' | 'W':
                self._maze[current_x][current_y] &= 7
                self._maze[next_x][next_y] &= 13
            case 'n' | 'N':
                self._maze[current_x][current_y] &= 14
                self._maze[next_x][next_y] &= 11
            case 'e' | 'E':
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
