import math

from vec3 import vec3
from material import lambertian


# ----- sphere -----

class sphere:
    def __init__(self, center, radius, material):
        self.center = center
        self.radius = radius
        self.mat = material

    def hit(self, r):
        oc = r.origin - self.center
        a = r.dir.dot(r.dir)
        b = 2.0 * oc.dot(r.dir)
        c = oc.dot(oc) - self.radius * self.radius
        disc = b * b - 4.0 * a * c
        if disc < 0:
            return None
        t = (-b - math.sqrt(disc)) / (2.0 * a)
        if t < 0.001:
            t = (-b + math.sqrt(disc)) / (2.0 * a)
        if t < 0.001:
            return None
        pt = r.at(t)
        n = (pt - self.center).norm()
        return (t, pt, n)


# ----- triangle (moller-trumbore) -----

class triangle:
    def __init__(self, v0, v1, v2, material):
        self.v0 = v0
        self.v1 = v1
        self.v2 = v2
        self.mat = material
        self._normal = (v1 - v0).cross(v2 - v0).norm()

    def hit(self, r):
        EPS = 0.0000001
        e1 = self.v1 - self.v0
        e2 = self.v2 - self.v0
        p = r.dir.cross(e2)
        det = e1.dot(p)
        if -EPS < det < EPS:
            return None
        inv_det = 1.0 / det
        s = r.origin - self.v0
        u = s.dot(p) * inv_det
        if u < 0 or u > 1:
            return None
        q = s.cross(e1)
        v = r.dir.dot(q) * inv_det
        if v < 0 or u + v > 1:
            return None
        t = e2.dot(q) * inv_det
        if t < 0.001:
            return None
        pt = r.at(t)
        # use interpolated normal for smooth shading if available, else face normal
        n = self._normal
        # flip normal based on ray direction
        if n.dot(r.dir) > 0:
            n = -n
        return (t, pt, n)


# ----- triangle mesh -----

class mesh:
    def __init__(self, triangles, material=None):
        self.tris = triangles
        if material and not all(t.mat is material for t in triangles):
            for t in triangles:
                t.mat = material
        self.mat = material

    def hit(self, r):
        best = None
        for tri in self.tris:
            h = tri.hit(r)
            if h and (best is None or h[0] < best[0]):
                best = h
        return best


# ----- load obj -----

def load_obj(path, material=None):
    verts = []
    tris = []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "v":
            verts.append(vec3(float(parts[1]), float(parts[2]), float(parts[3])))
        elif parts[0] == "f":
            # parse face — handle v/vt/vn formats
            def get_vi(s):
                return int(s.split("/")[0]) - 1
            # triangulate ngons
            for i in range(1, len(parts) - 1):
                v0 = verts[get_vi(parts[1])]
                v1 = verts[get_vi(parts[i + 1])]
                v2 = verts[get_vi(parts[i + 2])]
                tris.append(triangle(v0, v1, v2, material))
    return tris
