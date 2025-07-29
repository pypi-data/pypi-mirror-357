from numeric import lerp


class HSLColor:
    def __init__(self, h: float, s: float, l: float) -> None:
        self.hue = h
        self.saturation = s
        self.luminance = l


class SRGBColor:
    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def lerp(self, other: "SRGBColor", percent: float) -> "SRGBColor":
        return SRGBColor(
            lerp(self.r, other.r, percent),
            lerp(self.g, other.g, percent),
            lerp(self.b, other.b, percent),
            lerp(self.a, other.a, percent),
        )

    @property
    def luminance(self) -> float:
        """Given an sRGB color as 3 RGB values between 0 and 1, return their relative luminance"""
        return 0.2126 * self.r + 0.7152 * self.g + 0.0722 * self.b

    def __str__(self) -> str:
        return "SRGBColor({}, {}, {}, {})".format(self.r, self.g, self.b, self.a)

    def hsl(self) -> "HSLColor":
        return HSLColor(self.hue, self.saturation, self.luminance)

    @property
    def saturation(self) -> float:
        all_vals = [self.r, self.g, self.b]
        l = self.luminance
        if l < 1:
            s = (max(all_vals) - min(all_vals)) / (1 - abs(2 * l - 1))
        elif l == 1:
            s = 0
        else:
            raise AssertionError("invalid SRGBColor")

        return s

    @property
    def hue(self) -> float:
        minimum = min([self.r, self.g, self.b])
        if self.r == self.g and self.g == self.b:
            return 0
        val = None
        if self.r >= self.g and self.r >= self.b:
            val = (self.g - self.b) / (self.r - minimum)
        if self.g >= self.r and self.g >= self.b:
            val = 2.0 + (self.b - self.r) / (self.g - minimum)
        if self.b >= self.r and self.b >= self.g:
            val = 4.0 + (self.r - self.g) / (self.b - minimum)

        assert val is not None, "Invalid SRGB state"
        val *= 60
        if val < 0:
            val += 360
        return val


if __name__ == "__main__":
    from frange import frange

    ONE_TENTH = (
        1 / 16 + 1 / 32 + 1 / 256 + 1 / 512 + 1 / 1024 - 1 / 2048 - 1 / 8192 + 1 / 16384
    )

    for val in frange(0, 1, ONE_TENTH):
        print(round(val, 3))
