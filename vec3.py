import math
import random


class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(a, b):
        if isinstance(b, (int, float)):
            return vec3(a.x + b, a.y + b, a.z + b)
        return vec3(a.x + b.x, a.y + b.y, a.z + b.z)

    def __radd__(a, b):
        return a.__add__(b)

    def __sub__(a, b):
        if isinstance(b, (int, float)):
            return vec3(a.x - b, a.y - b, a.z - b)
        return vec3(a.x - b.x, a.y - b.y, a.z - b.z)

    def __rsub__(a, b):
        return vec3(b.x - a.x, b.y - a.y, b.z - a.z)

    def __mul__(a, b):
        if isinstance(b, (int, float)):
            return vec3(a.x * b, a.y * b, a.z * b)
        return vec3(a.x * b.x, a.y * b.y, a.z * b.z)

    def __rmul__(a, b):
        if isinstance(b, (int, float)):
            return vec3(a.x * b, a.y * b, a.z * b)
        return vec3(a.x * b.x, a.y * b.y, a.z * b.z)

    def __truediv__(a, b):
        if isinstance(b, (int, float)):
            return vec3(a.x / b, a.y / b, a.z / b)
        return vec3(a.x / b.x, a.y / b.y, a.z / b.z)

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def __repr__(self):
        return f"({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

    def dot(a, b):
        return a.x * b.x + a.y * b.y + a.z * b.z

    def cross(a, b):
        return vec3(
            a.y * b.z - a.z * b.y,
            a.z * b.x - a.x * b.z,
            a.x * b.y - a.y * b.x,
        )

    def length(self):
        return math.sqrt(self.dot(self))

    def length_squared(self):
        return self.dot(self)

    def norm(self):
        l = self.length()
        return vec3(self.x / l, self.y / l, self.z / l) if l > 0 else vec3(0, 0, 0)

    def lerp(a, b, t):
        return a + (b - a) * t

    # for convenience — unpack to tuple
    def tuple(self):
        return (self.x, self.y, self.z)


def random_in_unit_sphere():
    while True:
        p = vec3(random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
        if p.length() < 1:
            return p
