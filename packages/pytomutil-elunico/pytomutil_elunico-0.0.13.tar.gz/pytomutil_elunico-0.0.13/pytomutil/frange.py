class frange:
    def __init__(self, start: float, stop: float, step: float) -> None:
        self.start = start
        self.stop = stop
        self.step = step

    def __repr__(self) -> str:
        return f"frange({self.start}, {self.stop}, {self.step})"
    
    def __str__(self) -> str:
        return f"frange({self.start}, {self.stop}, {self.step})"

    def __iter__(self):
        return type(self)(self.start, self.stop, self.step)

    def __next__(self):
        if self.start >= self.stop:
            raise StopIteration()
        result = self.start
        self.start += self.step
        return result
