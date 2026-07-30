class MazeGenerator():
    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple,
            exit: tuple,
            perfect=True,
            seed=42):
        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit
        self._perfect = perfect
        self._seed = seed
