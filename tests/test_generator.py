"""Tests for the MazeGenerator: validity, optimality, reproducibility."""

from collections import deque
from pathlib import Path

from mazegen import MazeGenerator

DIRS = [(1, 0, 2), (-1, 0, 8), (0, 1, 4), (0, -1, 1)]


def bfs_distances(
    grid: list[list[int]], start: tuple[int, int]
) -> dict[tuple[int, int], int]:
    """Independent BFS used to cross-check the solver."""
    height, width = len(grid), len(grid[0])
    dist = {start: 0}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for dx, dy, bit in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height \
                    and (nx, ny) not in dist and not grid[y][x] & bit:
                dist[(nx, ny)] = dist[(x, y)] + 1
                queue.append((nx, ny))
    return dist


def make(width: int, height: int, perfect: bool = True,
         seed: int = 42) -> MazeGenerator:
    """Build and generate a maze with entry/exit in opposite corners."""
    gen = MazeGenerator(width, height, (0, 0),
                        (width - 1, height - 1), perfect, seed)
    gen.generate_maze()
    return gen


def test_wall_coherence() -> None:
    """Neighbouring cells always agree about their shared wall."""
    grid = make(20, 15).get_structure()
    for y in range(15):
        for x in range(20):
            if x + 1 < 20:
                assert bool(grid[y][x] & 2) == bool(grid[y][x + 1] & 8)
            if y + 1 < 15:
                assert bool(grid[y][x] & 4) == bool(grid[y + 1][x] & 1)


def test_borders_closed() -> None:
    """The outer border of the maze is fully walled."""
    grid = make(20, 15).get_structure()
    assert all(grid[0][x] & 1 for x in range(20))
    assert all(grid[14][x] & 4 for x in range(20))
    assert all(grid[y][0] & 8 for y in range(15))
    assert all(grid[y][19] & 2 for y in range(15))


def test_connectivity_and_42() -> None:
    """All cells are reachable except the 18 cells of the '42'."""
    grid = make(20, 15).get_structure()
    reachable = bfs_distances(grid, (0, 0))
    closed = sum(1 for row in grid for cell in row if cell == 15)
    assert closed == 18
    assert len(reachable) + closed == 20 * 15


def test_solution_is_shortest() -> None:
    """The IDDFS solution length matches an independent BFS."""
    gen = make(20, 15)
    solution = gen.get_solution()
    dist = bfs_distances(gen.get_structure(), (0, 0))
    assert len(solution) == dist[(19, 14)]


def test_perfect_maze_is_a_tree() -> None:
    """A perfect maze has exactly cells-1 open internal walls."""
    grid = make(20, 15).get_structure()
    cells = len(bfs_distances(grid, (0, 0)))
    edges = 0
    for y in range(15):
        for x in range(20):
            if x + 1 < 20 and not grid[y][x] & 2:
                edges += 1
            if y + 1 < 15 and not grid[y][x] & 4:
                edges += 1
    assert edges == cells - 1


def test_non_perfect_has_loops_but_no_open_area() -> None:
    """PERFECT=False adds loops without creating 3x3 open areas."""
    gen = make(20, 15, perfect=False)
    grid = gen.get_structure()
    cells = len(bfs_distances(grid, (0, 0)))
    edges = 0
    for y in range(15):
        for x in range(20):
            if x + 1 < 20 and not grid[y][x] & 2:
                edges += 1
            if y + 1 < 15 and not grid[y][x] & 4:
                edges += 1
    assert edges > cells - 1
    assert not gen._has_open_3x3()


def test_seed_reproducibility() -> None:
    """The same seed always produces the same maze."""
    assert make(20, 15).get_structure() == make(20, 15).get_structure()


def test_small_maze_skips_pattern(capsys: object) -> None:
    """Below 9x7 the '42' is skipped with a console message."""
    grid = make(5, 5).get_structure()
    assert all(cell != 15 for row in grid for cell in row)


def test_export_format(tmp_path: Path) -> None:
    """The output file follows the subject's exact format."""
    gen = make(20, 15)
    out = tmp_path / "maze.txt"
    gen.export_to_hex_file(str(out))
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")
    lines = text.split("\n")
    hex_rows = lines[:15]
    assert all(len(row) == 20 for row in hex_rows)
    assert all(c in "0123456789ABCDEF" for row in hex_rows for c in row)
    assert lines[15] == ""
    assert lines[16] == "0,0"
    assert lines[17] == "19,14"
    assert set(lines[18]) <= set("NESW")
