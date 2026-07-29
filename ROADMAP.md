# A-maze-ing — Game Plan

**What we ship:** `python3 a_maze_ing.py config.txt` → generates a random maze
(seed-reproducible, with a "42" drawn in closed cells) → saves it as hex digits
→ shows it in the terminal with a menu (new maze / show-hide path / colors / quit).
Generation logic also ships as a pip package `mazegen-*` at repo root.

**Quality bar (graded):** flake8 + mypy clean, type hints, docstrings, never
crashes (clear error messages), Makefile, complete README.

---

## Missions

### 🧠 achafai — The Maze Brain
1. `mazegen/generator.py` — `MazeGenerator` class: grid, DFS carving, seed, "42" pattern
2. BFS solver → shortest path as `"NESW..."` string
3. Hex export (bit0=N, bit1=E, bit2=S, bit3=W · 1 = wall closed)
4. Build the pip package, commit the `.whl` at repo root

### 🎨 maslan — The Maze Face
1. `amazeing/config.py` — parse `KEY=VALUE`, skip `#` lines, validate the 6 mandatory keys (WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT), friendly errors
2. `amazeing/renderer.py` — ASCII maze with colors (walls, entry, exit, path)
3. `amazeing/ui.py` — menu: 1 regen · 2 show/hide path · 3 colors · 4 quit
4. Output file writer + default `config.txt` + Makefile

### 🤝 Together
- `a_maze_ing.py` (glue) · README · tests · review each other's PRs

---

## The Contract (agree once, then full parallel — nobody waits)

```python
gen = MazeGenerator(width, height, entry, exit_, perfect=True, seed=42)
gen.generate()        # builds the maze
gen.grid              # list[list[int]] — wall bitmask per cell
gen.solve()           # "SSEENE..." shortest path
gen.to_hex_lines()    # lines for the output file
gen.pattern_cells     # cells of the "42" (for coloring)
```

---

## Timeline

| Day | Target |
|---|---|
| 1 | Contract agreed. achafai: maze generates. maslan: config parser done. |
| 2 | **Full pipeline runs end-to-end.** Solver + output file + basic render. |
| 3 | Menu + colors polished. Package built. Edge-case tests. |
| 4 | README done. Lint clean. Fresh-clone test: `make install && make run`. |

## Git flow

Own branch each (`achafai/generator`, `maslan/config-parser`) → push → PR → other person reviews → merge to `main`.
