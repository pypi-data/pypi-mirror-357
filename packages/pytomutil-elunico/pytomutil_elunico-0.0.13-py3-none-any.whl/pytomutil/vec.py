import random
import math
import typing
import warnings
import os

from pytomutil.numeric import lerp


class ClassProperty:
    def __init__(self, supplier):
        self.supplier = supplier

    def __set_name__(self, owner, name):
        self.private_name = "_" + name

    def __get__(self, obj, objtype):
        if objtype is None:
            raise TypeError("ClassProperty should be called on class")
        return self.supplier(objtype)


class ImmutableClass(type):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __setattr__(self, attr, value):
        if os.environ.get("PYTOMUTIL_VEC_ALLOW_OVERRIDE", False):
            msg = f"attr {repr(attr)} set to {repr(value)} but {self} is an immutable class"
            warnings.warn(msg)
        else:
            msg = f"Cannot set attr {repr(attr)} to {repr(value)} because {self} is an immutable class"
            raise TypeError(msg)


class Vec2D(metaclass=ImmutableClass):
    """
    Represents a 2-dimensional vector. An (x, y) pair
    """

    origin = ClassProperty(lambda cls: cls(0, 0))

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @classmethod
    def from_magnitude_and_angle(cls, magnitude: float, angle: float) -> "Vec2D":
        x = magnitude * math.cos(angle)
        y = magnitude * math.sin(angle)
        return cls(x, y)

    @classmethod
    def from_ma(cls, mag: float, angle: float) -> "Vec2D":
        return cls.from_magnitude_and_angle(mag, angle)

    @classmethod
    def from_iter(cls, iterable: typing.Iterable[float]) -> 'Vec2D | list["Vec2D"]':
        i = iter(iterable)
        result = []
        while True:
            try:
                x = next(i)
            except StopIteration:
                break
            try:
                y = next(i)
            except StopIteration:
                raise ValueError(f"Iterable {iterable} has an odd number of elements")

            result.append(Vec2D(x, y))

        return result if len(result) != 1 else result[0]

    @property
    def polar(self) -> tuple[float, float]:
        return (self.magnitude, self.heading)

    @classmethod
    def zero(cls) -> "Vec2D":
        return cls(0, 0)

    @classmethod
    def random(cls, *, mag: float = 1.0) -> "Vec2D":
        angle = random.random() * math.pi * 2
        return cls.from_magnitude_and_angle(mag, angle)

    @property
    def magnitude(self) -> float:
        return math.sqrt(self.magSquared)

    @magnitude.setter
    def magnitude(self, value: float):
        self.normalize()
        self *= value

    @property
    def mag(self) -> float:
        return self.magnitude

    @mag.setter
    def mag(self, value: float) -> None:
        self.magnitude = value

    @property
    def magSquared(self) -> float:
        return self.x**2 + self.y**2

    def tie(self, other: "Vec2D") -> list[float]:
        return list(self) + list(other)

    def limit(self, maximum: float):
        m = self.magnitude
        if m > maximum:
            self.magnitude = maximum

    def limited(self, maximum: float) -> "Vec2D":
        result = self.copy()
        result.limit(maximum)
        return result

    def rotate(self, angle: float):
        self.heading = self.heading + angle

    def rotated(self, angle: float) -> "Vec2D":
        result = self.copy()
        result.rotate(angle)
        return result

    def lerp(self, other: "Vec2D", percent: float) -> None:
        self.x = lerp(self.x, other.x, percent)
        self.y = lerp(self.y, other.y, percent)

    def lerped(self, other: "Vec2D", percent: float) -> "Vec2D":
        result = self.copy()
        result.lerp(other, percent)
        return result

    def distance_to(self, other: "Vec2D") -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def dot(self, other: "Vec2D") -> float:
        return self.x * other.x + self.y * other.y

    def angle_between(self, other: "Vec2D") -> float:
        return math.acos(self.dot(other) / (self.magnitude * other.magnitude))

    def set(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @property
    def heading(self) -> float:
        return math.atan2(self.y, self.x)

    @heading.setter
    def heading(self, angle: float) -> None:
        m = self.magnitude
        self.x = math.cos(angle) * m
        self.y = math.sin(angle) * m

    def normalize(self) -> None:
        mag = self.magnitude
        self.x /= mag
        self.y /= mag

    def normalized(self) -> "Vec2D":
        result = self.copy()
        result.normalize()
        return result

    def copy(self):
        return Vec2D(self.x, self.y)

    def list(self):
        return [self.x, self.y]

    def swap(self) -> None:
        self.x, self.y = self.y, self.x

    def swapped(self) -> "Vec2D":
        return Vec2D(self.y, self.x)

    def __iter__(self):
        return iter([self.x, self.y])

    def __complex__(self) -> complex:
        return self.x + self.y * 1j

    def __eq__(self, value: object, /) -> bool:
        if not isinstance(value, Vec2D):
            return NotImplemented

        return value.x == self.x and value.y == self.y

    def __floor__(self) -> "Vec2D":
        return Vec2D(math.floor(self.x), math.floor(self.y))

    def __ceil__(self) -> "Vec2D":
        return Vec2D(math.ceil(self.x), math.ceil(self.y))

    def __round__(self, n: int) -> "Vec2D":
        return Vec2D(round(self.x, n), round(self.y, n))

    def __len__(self) -> int:
        return 2

    def __reversed__(self) -> "Vec2D":
        return Vec2D(self.y, self.x)

    def __getitem__(self, i: str | int) -> float:
        try:
            if isinstance(i, str):
                return {"x": self.x, "y": self.y}[i]
            elif isinstance(i, int):
                return [self.x, self.y][i]
        except (KeyError, IndexError):
            raise IndexError(f"Invalid index: {repr(i)}") from None
        else:
            raise TypeError(f"Type {repr(type(i))} is not a valid Vec2D index")

    def __setitem__(self, i: str | int, value: float) -> None:
        try:
            if i == "x" or i == 0:
                self.x = value
            elif i == "y" or i == 1:
                self.y = value
            else:
                raise IndexError()
        except (KeyError, IndexError):
            raise IndexError(f"Invalid index: {repr(i)}") from None

    def __bool__(self) -> bool:
        return bool(self.x) or bool(self.y)

    def __hash__(self) -> int:
        code = hash(self.x)
        code ^= hash(self.y)
        return code

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        return f"Vec2D(x={self.x}, y={self.y})"

    def __neg__(self) -> "Vec2D":
        return Vec2D(-self.x, -self.y)

    def __add__(self, other: "Vec2D") -> "Vec2D":
        if not isinstance(other, Vec2D):
            return NotImplemented
        return Vec2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vec2D") -> "Vec2D":
        if not isinstance(other, Vec2D):
            return NotImplemented
        return Vec2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float | int) -> "Vec2D":
        if not isinstance(other, (float, int)):
            return NotImplemented
        return Vec2D(self.x * other, self.y * other)

    def __truediv__(self, other: float | int) -> "Vec2D":
        if not isinstance(other, (float, int)):
            return NotImplemented
        return Vec2D(self.x / other, self.y / other)

    def __floordiv__(self, other: float | int) -> "Vec2D":
        if not isinstance(other, (float, int)):
            return NotImplemented
        return Vec2D(self.x // other, self.y // other)

    def __iadd__(self, other: "Vec2D") -> "Vec2D":
        if not isinstance(other, Vec2D):
            return NotImplemented
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: "Vec2D") -> "Vec2D":
        if not isinstance(other, Vec2D):
            return NotImplemented
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, other: float | int) -> "Vec2D":
        if not isinstance(other, (float, int)):
            return NotImplemented
        self.x *= other
        self.y *= other
        return self

    def __itruediv__(self, other: float | int) -> "Vec2D":
        if not isinstance(other, (float, int)):
            return NotImplemented
        self.x /= other
        self.y /= other
        return self

    def __ifloordiv__(self, other: float | int) -> "Vec2D":
        if not isinstance(other, (float, int)):
            return NotImplemented
        self.x //= other
        self.y //= other
        return self
