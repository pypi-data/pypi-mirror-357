import math


def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b


def qerp(a: float, b: float, c: float, t: float) -> float:
    return lerp(lerp(a, b, t), lerp(b, c, t), t)


def cerp(a: float, b: float, c: float, d: float, t: float) -> float:
    return lerp(qerp(a, b, c, t), qerp(b, c, d, t), t)


def terp(a: float, b: float, c: float, d: float, e: float, t: float) -> float:
    return lerp(cerp(a, b, c, d, t), cerp(b, c, d, e, t), t)


class Resolution:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    @property
    def diagonal_pixels(self) -> float:
        return math.sqrt(self.width**2 + self.height**2)

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height

    def ppi(self, diag_inches: float) -> float:
        return math.sqrt(self.height**2 + self.width**2) / diag_inches

    def __str__(self) -> str:
        return f"{self.width}×{self.height}"

    def __repr__(self) -> str:
        return f"Resolution(width={self.width}, height={self.height})"


def ppi(pixelw: int, pixelh: int, screen_diag: float):
    return math.sqrt(pixelh**2 + pixelw**2) / screen_diag


def arcppi(screen_diag: float, ppi: int, aspect_ratio: float) -> tuple[int, int]:
    angle = math.atan(aspect_ratio)
    pix_diag = ppi * screen_diag
    x = math.cos(angle) * pix_diag
    y = math.sin(angle) * pix_diag
    return int(x), int(y)
