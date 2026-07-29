# A-maze-ing roadmap

The goal: `python3 a_maze_ing.py config.txt` reads the config, generates a random maze
(reproducible with a seed, and it has to contain a "42" made of closed cells), writes it
to a file as hex digits and shows it in the terminal with a small menu
(new maze / show or hide the path / colors / quit).
The generation part also has to be a pip package called mazegen, with the .whl at the repo root.

Stuff that gets graded: flake8 and mypy passing, type hints, docstrings, no crashes ever
(print a clear error instead), Makefile, and a proper README at the end.

## Project structure (agreed)

```
a_maze_ing.py         # parse_config(), display_ascii_maze(), run_interactive_menu(), main()
config.txt            # default config, KEY=VALUE
Makefile              # install, run, debug, clean, lint
.gitignore
README.md
pyproject.toml        # build config for the mazegen package
mazegen/
    __init__.py       # exposes MazeGenerator
    generator.py      # the MazeGenerator class
```

## Who does what

### achafai (engine, everything in mazegen/)
MazeGenerator class:
- `__init__(width, height, entry, exit, perfect, seed)`
- `generate_maze()` — grid of wall bitmasks, DFS carving, the 42 pattern (fully closed cells)
- `get_structure()` — returns the grid, list[list[int]], bitmask per cell
- `get_solution()` — BFS shortest path as a string like "NESW..."
- `export_to_hex_file(path)` — writes the output file (hex digits, then entry, exit, path)
  (bit0=N, bit1=E, bit2=S, bit3=W, 1 means wall closed)

Plus: build the pip package and put the .whl at the repo root.

### maslan (everything in a_maze_ing.py)
- `parse_config()` — KEY=VALUE, skip # lines, check the 6 mandatory keys
  (WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT), nice error messages
- `display_ascii_maze()` — ascii render with colors, walls, entry, exit, path
  (the 42 cells are the ones with bitmask 15, can color them differently)
- `run_interactive_menu()` — 1 regen, 2 path, 3 colors, 4 quit
- `main()` — glue it all together
- default config.txt, Makefile

### both
README, tests, and we review each other's PRs.

## Rough plan

Day 1: maze generates, config parser done
Day 2: whole pipeline runs end to end (generate + output file + basic render)
Day 3: menu and colors done, package built, tests for edge cases
Day 4: README, lint clean, test a fresh clone with make install && make run

## Git

Everyone works on their own branch (achafai/generator, maslan/main-app),
push, open a PR, the other one reviews and merges. No pushing straight to main.
