# PyTomUtil

A collection of helpful utilties in Python.

Similar to the `tecoradors-elunico` package I have but that is just for useful decorators. This is any useful utility: function or class or other

## PyPI

[https://pypi.org/project/pytomutil-elunico/](https://pypi.org/project/pytomutil-elunico/)

## Content

`frange` class works like `range` but allows floating point values. Requires `start`, `stop`, and `step` to always be specified

```python
class frange:
    def __init__(self, start: float, stop: float, step: float) -> None:
        ...

    def __iter__(self):
        ...

    def __next__(self):
        ...
```

---

`lerp` is a function for linearly interpolating between two values according to a percentage between 0.0 and 1.0.

[Linear Interpolation in Wikipedia](https://en.wikipedia.org/wiki/Linear_interpolation)

```python
def lerp(a: float, b: float, t: float) -> float:
    return (1 - t) * a + t * b
```

---

`SRGBColor` is a class for managing colors in SRGB color space. Works with linear interpolation between colors and `luminance` values. The class accepts r, g, b and optionally an alpha channel in the range 0.0 to 1.0.

```python
class SRGBColor:
    def __init__(self, r: float, g: float, b: float, a: float = 1.0):
        ...

    def lerp(self, other: "SRGBColor", percent: float) -> "SRGBColor":
        ...

    @property
    def luminance(self) -> float:
        """Given an sRGB color as 3 RGB values between 0 and 1, return their relative luminance"""
        ...
```
