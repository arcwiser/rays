from vec3 import vec3


class ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.dir = direction.norm()

    def at(self, t):
        return self.origin + self.dir * t
