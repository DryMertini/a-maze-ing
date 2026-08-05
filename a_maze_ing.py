"""A-maze-ing: generate, save and display a maze from a config file."""

import sys
from dataclasses import dataclass
from typing import Any

MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


@dataclass
class Config:
    """Holds the validated maze settings."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def _parse_coords(value: str, key: str) -> tuple[int, int]:
    """Turn a string like '19,14' into an (x, y) tuple of ints."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{key} must be 'x,y' with two numbers, got '{value}'"
        )
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        raise ConfigError(
            f"{key} coordinates must be integers, got '{value}'"
        ) from None


def _parse_bool(value: str, key: str) -> bool:
    """Turn 'True'/'False' (any casing) into a real bool."""
    # bool("False") would be True (any non-empty string is truthy),
    # so we compare the lowercase text explicitly.
    low = value.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    raise ConfigError(f"{key} must be True or False, got '{value}'")


def _read_pairs(path: str) -> dict[str, str]:
    """Read the config file into a {KEY: value} dict, skipping comments."""
    pairs: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as file:
            for number, raw in enumerate(file, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"line {number}: expected KEY=VALUE, got '{line}'"
                    )
                key, _, value = line.partition("=")
                pairs[key.strip().upper()] = value.strip()
    except FileNotFoundError:
        raise ConfigError(f"config file not found: {path}") from None
    except OSError as exc:
        raise ConfigError(f"cannot read '{path}': {exc}") from None
    return pairs


def parse_config(path: str) -> Config:
    """Read and validate a KEY=VALUE config file into a Config object."""
    pairs = _read_pairs(path)
    missing = [key for key in MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")
    try:
        width = int(pairs["WIDTH"])
        height = int(pairs["HEIGHT"])
    except ValueError:
        raise ConfigError("WIDTH and HEIGHT must be integers") from None
    if width < 1 or height < 1:
        raise ConfigError("WIDTH and HEIGHT must be positive")
    entry = _parse_coords(pairs["ENTRY"], "ENTRY")
    exit_ = _parse_coords(pairs["EXIT"], "EXIT")
    for name, (x, y) in (("ENTRY", entry), ("EXIT", exit_)):
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(
                f"{name} ({x},{y}) is outside the {width}x{height} maze"
            )
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")
    perfect = _parse_bool(pairs["PERFECT"], "PERFECT")
    seed: int | None = None
    if "SEED" in pairs:
        try:
            seed = int(pairs["SEED"])
        except ValueError:
            raise ConfigError("SEED must be an integer") from None
    return Config(
        width, height, entry, exit_, pairs["OUTPUT_FILE"], perfect, seed
    )


RESET = "\033[0m"
WALL_COLORS = ("\033[97m", "\033[93m", "\033[92m", "\033[96m", "\033[95m")
ENTRY_COLOR = "\033[95m"
EXIT_COLOR = "\033[91m"
PATH_COLOR = "\033[94m"
PATTERN_COLOR = "\033[90m"
MOVES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}


def _path_cells(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    """Walk a NESW path string from the entry, return the visited cells."""
    x, y = entry
    cells = {(x, y)}
    for step in path:
        if step not in MOVES:
            continue
        dx, dy = MOVES[step]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def _cell_interior(
    cell: tuple[int, int],
    walls: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: set[tuple[int, int]],
) -> str:
    """Return the coloured 2-char interior of one cell."""
    if cell == entry:
        return f"{ENTRY_COLOR}██{RESET}"
    if cell == exit_:
        return f"{EXIT_COLOR}██{RESET}"
    if cell in path:
        return f"{PATH_COLOR}▓▓{RESET}"
    if walls == 15:
        return f"{PATTERN_COLOR}░░{RESET}"
    return "  "


def display_ascii_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: str = "",
    color_index: int = 0,
) -> None:
    """Print the maze with walls, entry, exit and an optional path."""
    if not grid or not grid[0]:
        return
    wall = WALL_COLORS[color_index % len(WALL_COLORS)]

    def seg(closed: bool, chars: str) -> str:
        """One wall segment: coloured when closed, blank when open."""
        return f"{wall}{chars}{RESET}" if closed else " " * len(chars)

    corner = f"{wall}█{RESET}"
    shown = _path_cells(entry, path) if path else set()
    height, width = len(grid), len(grid[0])
    for y in range(height):
        top = "".join(
            corner + seg(bool(grid[y][x] & 1), "██") for x in range(width)
        )
        print(top + corner)
        mid = "".join(
            seg(bool(grid[y][x] & 8), "█")
            + _cell_interior((x, y), grid[y][x], entry, exit_, shown)
            for x in range(width)
        )
        print(mid + seg(bool(grid[y][width - 1] & 2), "█"))
    bottom = "".join(
        corner + seg(bool(grid[height - 1][x] & 4), "██")
        for x in range(width)
    )
    print(bottom + corner)


def _build_generator(config: Config, seed: int | None) -> Any:
    """Create a MazeGenerator from the config (imported lazily)."""
    try:
        from mazegen import MazeGenerator
    except ImportError:
        raise ConfigError(
            "the mazegen package is not installed or not built yet"
        ) from None
    return MazeGenerator(
        config.width, config.height, config.entry, config.exit,
        config.perfect, seed,
    )


def run_interactive_menu(config: Config) -> None:
    """Generate the maze, display it and handle user interactions."""
    generator = _build_generator(config, config.seed)
    generator.generate_maze()
    generator.export_to_hex_file(config.output_file)
    show_path = False
    color = 0
    while True:
        path = generator.get_solution() if show_path else ""
        display_ascii_maze(
            generator.get_structure(), config.entry, config.exit,
            path, color,
        )
        print("=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice == "1":
            generator = _build_generator(config, None)
            generator.generate_maze()
            generator.export_to_hex_file(config.output_file)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color += 1
        elif choice == "4":
            return
        else:
            print("Please enter a number between 1 and 4.")


def main() -> int:
    """Program entry point."""
    if len(sys.argv) != 2:
        print("usage: python3 a_maze_ing.py config.txt")
        return 1
    try:
        config = parse_config(sys.argv[1])
        run_interactive_menu(config)
    except ConfigError as exc:
        print(f"Error: {exc}")
        return 1
    except Exception as exc:  # last-resort net: never crash on the user
        print(f"Error: unexpected problem: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
