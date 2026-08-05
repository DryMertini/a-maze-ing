"""A-maze-ing: generate, save and display a maze from a config file."""

import sys
from dataclasses import dataclass

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


def main() -> int:
    """Program entry point."""
    if len(sys.argv) != 2:
        print("usage: python3 a_maze_ing.py config.txt")
        return 1
    try:
        config = parse_config(sys.argv[1])
    except ConfigError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Config loaded: {config}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
