PY = python3

install:
	pip3 install flake8 mypy

run:
	$(PY) a_maze_ing.py config.txt

debug:
	$(PY) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ .mypy_cache mazegen/__pycache__ dist build *.egg-info

lint:
	$(PY) -m flake8 .
	$(PY) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(PY) -m flake8 .
	$(PY) -m mypy . --strict

.PHONY: install run debug clean lint lint-strict
