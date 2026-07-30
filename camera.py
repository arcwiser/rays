import math

from vec3 import vec3
from ray import ray


class camera:
    def __init__(self, pos, look_at, up=vec3(0, 1, 0), fov=60):
        self.pos = pos
        self.w = (pos - look_at).norm()
        self.u = up.cross(self.w).norm()
        self.v = self.w.cross(self.u)
        self.fov = fov

    def get_ray(self, sx, sy, width, height):
        aspect = width / height
        vh = 2.0 * math.tan(math.radians(self.fov) / 2.0)
        vw = aspect * vh
        px = (sx / width) * vw - vw / 2.0
        py = (sy / height) * vh - vh / 2.0
        dir = (self.u * px + self.v * py - self.w).norm()
        return ray(self.pos, dir)
