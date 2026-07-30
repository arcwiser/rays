import math
import random
import sys

# ---------------------------------------------------------------
# vec3 - 3d vector with basic operations
# ---------------------------------------------------------------
class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __add__(a, b):
        return vec3(a.x + b.x, a.y + b.y, a.z + b.z)

    def __sub__(a, b):
        return vec3(a.x - b.x, a.y - b.y, a.z - b.z)

    def __mul__(a, b):
        if isinstance(b, (int, float)):
            return vec3(a.x * b, a.y * b, a.z * b)
        return vec3(a.x * b.x, a.y * b.y, a.z * b.z)

    def __rmul__(a, b):
        return a.__mul__(b)

    def __neg__(self):
        return vec3(-self.x, -self.y, -self.z)

    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

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

    def norm(self):
        l = self.length()
        return vec3(self.x / l, self.y / l, self.z / l) if l > 0 else vec3(0, 0, 0)

    def lerp(a, b, t):
        return a + (b - a) * t


# ---------------------------------------------------------------
# ray
# ---------------------------------------------------------------
class ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.dir = direction.norm()

    def at(self, t):
        return self.origin + self.dir * t


# ---------------------------------------------------------------
# sphere
# ---------------------------------------------------------------
class sphere:
    def __init__(self, center, radius, color, reflect=0.0, emissive=vec3(0, 0, 0)):
        self.center = center
        self.radius = radius
        self.color = color
        self.reflect = reflect
        self.emissive = emissive

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


# ---------------------------------------------------------------
# scene
# ---------------------------------------------------------------
class scene:
    def __init__(self):
        self.spheres = []
        self.light_pos = vec3(2, 5, 3)
        self.light_color = vec3(1, 1, 1)
        self.light_intensity = 1.5
        self.ambient = vec3(0.1, 0.1, 0.15)
        self.bg_color = vec3(0.05, 0.05, 0.1)

    def add(self, s):
        self.spheres.append(s)

    def trace(self, r, depth=0):
        if depth > 6:
            return vec3(0, 0, 0)

        hit = None
        for s in self.spheres:
            h = s.hit(r)
            if h and (hit is None or h[0] < hit[0]):
                hit = h
                hit_sphere = s

        if hit is None:
            # sky gradient
            t = 0.5 * (r.dir.y + 1.0)
            return vec3.lerp(self.bg_color, vec3(0.3, 0.5, 0.8), t)

        t, pt, n = hit
        s = hit_sphere

        if s.emissive.x > 0 or s.emissive.y > 0 or s.emissive.z > 0:
            return s.emissive

        color = vec3(0, 0, 0)

        # ambient
        color = color + s.color * self.ambient

        # diffuse + specular from main light
        to_light = (self.light_pos - pt).norm()
        shad_r = ray(pt + n * 0.001, to_light)
        in_shadow = False
        for other in self.spheres:
            if other is s:
                continue
            sh = other.hit(shad_r)
            if sh and sh[0] < (self.light_pos - pt).length():
                in_shadow = True
                break

        if not in_shadow:
            ndotl = max(n.dot(to_light), 0)
            diff = s.color * ndotl * self.light_intensity
            color = color + diff

            # specular (blinn-phong)
            view_dir = (r.origin - pt).norm()
            half = (to_light + view_dir).norm()
            spec = max(n.dot(half), 0) ** 32
            color = color + vec3(1, 1, 1) * spec * 0.5 * self.light_intensity

        # reflection
        if s.reflect > 0 and depth < 5:
            reflect_dir = r.dir - n * 2.0 * r.dir.dot(n)
            reflect_r = ray(pt + n * 0.001, reflect_dir)
            reflect_color = self.trace(reflect_r, depth + 1)
            color = color + reflect_color * s.reflect

        return color


# ---------------------------------------------------------------
# camera
# ---------------------------------------------------------------
class camera:
    def __init__(self, pos, look_at, up=vec3(0, 1, 0), fov=60):
        self.pos = pos
        w = (pos - look_at).norm()
        u = up.cross(w).norm()
        v = w.cross(u)
        self.w = w
        self.u = u
        self.v = v
        self.fov = fov

    def get_ray(self, sx, sy, width, height):
        aspect = width / height
        vh = 2.0 * math.tan(math.radians(self.fov) / 2.0)
        vw = aspect * vh
        px = (sx / width) * vw - vw / 2.0
        py = (sy / height) * vh - vh / 2.0
        dir = (self.u * px + self.v * py - self.w).norm()
        return ray(self.pos, dir)


# ---------------------------------------------------------------
# render
# ---------------------------------------------------------------
def render(width, height, scene_obj, cam, samples=4):
    print(f"rendering {width}x{height} with {samples}x aa...")
    pixels = []
    total = width * height
    for y in range(height - 1, -1, -1):
        for x in range(width):
            c = vec3(0, 0, 0)
            for _ in range(samples):
                sx = x + random.random()
                sy = y + random.random()
                r = cam.get_ray(sx, sy, width, height)
                c = c + scene_obj.trace(r)

            c = c * (1.0 / samples)

            # gamma correction
            c = vec3(math.sqrt(c.x), math.sqrt(c.y), math.sqrt(c.z))
            c = vec3(min(c.x, 1), min(c.y, 1), min(c.z, 1))

            pixels.append((int(c.x * 255), int(c.y * 255), int(c.z * 255)))

            pct = (y * width + x + 1) / total * 100
            if (x == 0 and y % 10 == 0) or pct >= 100:
                bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
                sys.stdout.write(f"\r  [{bar}] {pct:.0f}%")
                sys.stdout.flush()
    print()
    return pixels


def save_ppm(pixels, width, height, path):
    with open(path, "wb") as f:
        f.write(f"P6\n{width} {height}\n255\n".encode())
        for r, g, b in pixels:
            f.write(bytes([r, g, b]))
    print(f"saved {path}")


# ---------------------------------------------------------------
# main
# ---------------------------------------------------------------
def main():
    width = int(sys.argv[1]) if len(sys.argv) > 1 else 400
    height = int(width / 1.6)
    samples = int(sys.argv[2]) if len(sys.argv) > 2 else 4

    world = scene()

    # ground
    world.add(sphere(vec3(0, -1000, 0), 1000, vec3(0.5, 0.5, 0.5), reflect=0.1))

    # center red sphere
    world.add(sphere(vec3(-1.5, 1, 0), 0.8, vec3(1, 0.2, 0.1), reflect=0.3))

    # green sphere
    world.add(sphere(vec3(0.5, 0.8, 0.5), 0.6, vec3(0.1, 0.8, 0.2), reflect=0.1))

    # blue sphere
    world.add(sphere(vec3(1.5, 0.5, -1), 0.5, vec3(0.1, 0.3, 1), reflect=0.4))

    # mirror ball
    world.add(sphere(vec3(-0.5, 0.3, -1.5), 0.3, vec3(1, 1, 1), reflect=0.9))

    # small floating light sphere (glow)
    world.add(sphere(vec3(0, 2.5, 0), 0.15, vec3(1, 1, 1), reflect=0.0,
                     emissive=vec3(3, 3, 3)))

    cam = camera(vec3(0, 1.8, 5), vec3(0, 0.8, 0))

    print(f"ray tracer — {width}x{height}  {samples}spp")
    pixels = render(width, height, world, cam, samples)
    save_ppm(pixels, width, height, "output.ppm")


if __name__ == "__main__":
    main()
