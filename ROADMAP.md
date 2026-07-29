# A-maze-ing roadmap

The goal: `python3 a_maze_ing.py config.txt` reads the config, generates a random maze
(reproducible with a seed, and it has to contain a "42" made of closed cells), writes it
to a file as hex digits and shows it in the terminal with a small menu
(new maze / show or hide the path / colors / quit).
The generation part also has to be a pip package called mazegen, with the .whl at the repo root.

Stuff that gets graded: flake8 and mypy passing, type hints, docstrings, no crashes ever
(print a clear error instead), Makefile, and a proper README at the end.

## Who does what

### achafai (engine)
1. mazegen/generator.py, the MazeGenerator class: grid, DFS carving, seed, the 42 pattern
2. BFS solver, returns the shortest path as a string like "NESW..."
3. hex export (bit0=N, bit1=E, bit2=S, bit3=W, 1 means wall closed)
4. build the pip package and put the .whl at the repo root

### maslan (everything the user sees)
1. amazeing/config.py: parse KEY=VALUE, skip # lines, check the 6 mandatory keys
   (WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT), nice error messages
2. amazeing/renderer.py: ascii maze with colors, walls, entry, exit, path
3. amazeing/ui.py: the menu (1 regen, 2 path, 3 colors, 4 quit)
4. output file writer, default config.txt, Makefile

### both
a_maze_ing.py (the glue), README, tests, and we review each other's PRs.

## The interface (so we can work in parallel without waiting on each other)

To be confirmed by achafai, rename whatever you want but then we lock it:

```python
gen = MazeGenerator(width, height, entry, exit_, perfect=True, seed=42)
gen.generate()        # builds the maze
gen.grid              # list[list[int]], wall bitmask per cell
gen.solve()           # "SSEENE..." shortest path
gen.to_hex_lines()    # lines for the output file
gen.pattern_cells     # the 42 cells, for coloring
```

## Rough plan

Day 1: interface agreed, maze generates, config parser done
Day 2: whole pipeline runs end to end (solver + output file + basic render)
Day 3: menu and colors done, package built, tests for edge cases
Day 4: README, lint clean, test a fresh clone with make install && make run

## Git

Everyone works on their own branch (achafai/generator, maslan/config-parser),
push, open a PR, the other one reviews and merges. No pushing straight to main.
