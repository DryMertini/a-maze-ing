"""Tests for the configuration parser."""

from pathlib import Path

import pytest

from a_maze_ing import ConfigError, parse_config

VALID = """WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
"""


def write(tmp_path: Path, text: str) -> str:
    """Write a config file and return its path as a string."""
    path = tmp_path / "config.txt"
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_valid_config(tmp_path: Path) -> None:
    """A correct file parses into the expected values."""
    config = parse_config(write(tmp_path, VALID))
    assert config.width == 20
    assert config.height == 15
    assert config.entry == (0, 0)
    assert config.exit == (19, 14)
    assert config.output_file == "maze.txt"
    assert config.perfect is True
    assert config.seed == 42


def test_lowercase_keys_and_comments(tmp_path: Path) -> None:
    """Lowercase keys and comment lines are accepted."""
    text = "# comment\n" + VALID.lower().replace("true", "True")
    config = parse_config(write(tmp_path, text))
    assert config.width == 20


def test_missing_file() -> None:
    """A missing file raises a clean ConfigError."""
    with pytest.raises(ConfigError):
        parse_config("does_not_exist.txt")


@pytest.mark.parametrize("broken", [
    VALID.replace("OUTPUT_FILE=maze.txt\n", ""),      # missing key
    VALID.replace("WIDTH=20", "WIDTH=banana"),        # non-integer
    VALID.replace("WIDTH=20", "WIDTH=0"),             # non-positive
    VALID.replace("ENTRY=0,0", "ENTRY=5"),            # bad tuple
    VALID.replace("ENTRY=0,0", "ENTRY=a,b"),          # letters
    VALID.replace("EXIT=19,14", "EXIT=25,14"),        # out of bounds
    VALID.replace("EXIT=19,14", "EXIT=0,0"),          # entry == exit
    VALID.replace("PERFECT=True", "PERFECT=yes"),     # bad boolean
    VALID.replace("SEED=42", "SEED=abc"),             # bad seed
    VALID.replace("HEIGHT=15", "HEIGHT 15"),          # no equals sign
])
def test_invalid_configs(tmp_path: Path, broken: str) -> None:
    """Every malformed config raises ConfigError, never crashes."""
    with pytest.raises(ConfigError):
        parse_config(write(tmp_path, broken))
