*This project has been created as part of the 42 curriculum by maslan, achafai.*

# A-maze-ing

## Description

A-maze-ing is a maze generator written in Python. From a small
configuration file it generates a random maze, draws a hidden "42" in
fully closed cells, writes the result to a file using a hexadecimal
wall encoding, and displays everything in the terminal with an
interactive menu (regenerate, show/hide the shortest path, change wall
colours). The generation logic lives in a standalone, pip-installable
package (`mazegen`) so it can be reused in future projects.

## Instructions

Requires Python 3.10+.

```bash
git clone <repo-url> && cd a-maze-ing
make install        # installs flake8 + mypy (no runtime dependencies)
make run            # runs: python3 a_maze_ing.py config.txt
```

Other Makefile rules: `make debug` (run under pdb), `make lint`
(flake8 + mypy), `make clean` (remove caches).

Once running, the menu offers: `1` generate a new maze, `2` toggle the
shortest path overlay, `3` cycle wall colours, `4` quit. The maze is
also written to the file named by `OUTPUT_FILE` on start and on every
regeneration.

## Configuration file

One `KEY=VALUE` pair per line. Lines starting with `#` are comments.
Keys are case-insensitive. Mandatory keys:

| Key         | Meaning                            | Example              |
|-------------|------------------------------------|----------------------|
| WIDTH       | Maze width in cells                | `WIDTH=20`           |
| HEIGHT      | Maze height in cells               | `HEIGHT=15`          |
| ENTRY       | Entry cell `x,y` (0-based)         | `ENTRY=0,0`          |
| EXIT        | Exit cell `x,y`                    | `EXIT=19,14`         |
| OUTPUT_FILE | Output filename                    | `OUTPUT_FILE=maze.txt` |
| PERFECT     | Single-path maze? `True`/`False`   | `PERFECT=True`       |

Optional keys:

| Key  | Meaning                                        | Example   |
|------|------------------------------------------------|-----------|
| SEED | Integer seed for reproducible mazes (omit for random) | `SEED=42` |

Any invalid or missing value produces a clear error message; the
program never crashes on bad input. A default `config.txt` is provided
at the repository root.

## Output file format

One uppercase hexadecimal digit per cell, one row per line. Each digit
is a 4-bit wall mask: bit 0 = North, bit 1 = East, bit 2 = South,
bit 3 = West; a set bit means the wall is closed (e.g. `F` = fully
closed, `A` = East and West closed). After the grid: an empty line,
the entry coordinates, the exit coordinates, and the shortest path as
a string of `N`/`E`/`S`/`W` moves. Every line ends with `\n`.

## Algorithms

**Generation — iterative DFS (recursive backtracker).** The grid
starts with all walls closed; the "42" cells are marked as visited
before carving so the algorithm never enters them and they stay fully
closed. From the entry, the carver repeatedly opens a wall towards a
random unvisited neighbour, backtracking at dead ends. We chose it
because it is simple to reason about, produces long winding corridors
that look like a "real" maze, and guarantees a perfect maze by
construction: each cell is reached exactly once, so the open walls
form a spanning tree with a unique path between any two cells. That
same property makes 2x2 (and larger) open areas impossible, since an
open area requires a cycle. With `PERFECT=False`, a few extra internal
walls are opened to create loops; each removal is reverted if it would
create a 3x3 open area, which is how the "no large open areas" rule is
enforced.

**Solving — Iterative Deepening DFS (IDDFS).** The solver runs a
depth-limited DFS with limits 0, 1, 2, ... — the first limit that
reaches the exit yields a shortest path, so the result is optimal like
BFS while using only O(path length) memory. We chose it to explore a
less common algorithm; its optimality was verified against an
independent BFS implementation in our tests.

## Reusable module (mazegen)

The generation logic is a single class, `MazeGenerator`, in the
`mazegen` package — no dependency on the display or config code.
Prebuilt artifacts (`mazegen-1.0.0-py3-none-any.whl` and
`mazegen-1.0.0.tar.gz`) are at the repository root.

```bash
pip install ./mazegen-1.0.0-py3-none-any.whl
```

Basic usage:

```python
from mazegen import MazeGenerator

gen = MazeGenerator(20, 15, (0, 0), (19, 14), perfect=True, seed=42)
gen.generate_maze()
grid = gen.get_structure()   # list[list[int]]: 4-bit wall mask per cell
path = gen.get_solution()    # shortest path, e.g. "SSEENE..."
gen.export_to_hex_file("maze.txt")
```

Constructor parameters: `width`, `height`, `entry`, `exit` (cell
tuples), `perfect` (bool, default True), `seed` (int or None for
random). The same seed always reproduces the same maze.

Rebuilding the package from source:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install build
python3 -m build          # creates dist/*.whl and dist/*.tar.gz
```

## Team and project management

**Roles.** maslan: application side — configuration parsing and
validation, terminal rendering, interactive menu, Makefile, glue code.
achafai: engine side — the `MazeGenerator` class (DFS carving, the
"42" pattern, IDDFS solver, hex export) and the pip packaging.

**Planning and how it evolved.** We planned four stages: interface
contract, parallel development of both sides, integration, then
packaging/documentation. Agreeing early on the class interface let us
work simultaneously without blocking each other. Integration revealed
several bugs the generator's unit-level work had hidden (a grid
initialisation that was never called, an inverted axis convention, and
a stack handling bug in the DFS) — fixing them together on a dedicated
integration branch was the most instructive part of the project.

**What worked well / could be improved.** The interface-first approach
and reviewing each other's pull requests worked well. What we would
improve: branch discipline — one direct push to `main` mid-project
caused a merge conflict that cost us an evening, and we switched to
PR-only merges afterwards.

**Tools.** Git and GitHub (branches + pull requests), VS Code, flake8,
mypy, pytest, and Claude (AI assistant).

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Iterative deepening depth-first search — Wikipedia](https://en.wikipedia.org/wiki/Iterative_deepening_depth-first_search)
- [Jamis Buck: Maze generation algorithm visualisations](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- Python docs: [dataclasses](https://docs.python.org/3/library/dataclasses.html),
  [random](https://docs.python.org/3/library/random.html),
  [packaging tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

**AI usage.** We used Claude (Anthropic) as an assistant throughout:
project planning and task splitting, drafting code for the application
side (parser, renderer, menu), debugging the generator during
integration and completing its solver plumbing and export, writing
tests, and drafting this README. All AI-assisted code was reviewed,
tested and integrated by the team, and each of us can explain and
modify any part of the codebase.
