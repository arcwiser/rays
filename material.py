import math
import random

from vec3 import vec3, random_in_unit_sphere
from ray import ray


# ----- helpers -----

def reflect(v, n):
    return v - n * 2.0 * v.dot(n)


def refract(uv, n, etai_over_etat):
    cos_theta = min((-uv).dot(n), 1.0)
    r_out_perp = (uv + n * cos_theta) * etai_over_etat
    r_out_parallel = n * -math.sqrt(abs(1.0 - r_out_perp.length_squared()))
    return r_out_perp + r_out_parallel


def schlick(cosine, ri):
    r0 = (1.0 - ri) / (1.0 + ri)
    r0 = r0 * r0
    return r0 + (1.0 - r0) * (1.0 - cosine) ** 5


# ----- materials -----

class lambertian:
    def __init__(self, color):
        self.color = color

    def shade(self, hit, r_in, scene, depth):
        return self.direct(hit, scene) + self.ambient(hit, scene)

    def direct(self, hit, scene):
        col = vec3(0, 0, 0)
        for light in scene.lights:
            to_light = (light.pos - hit.point).norm()
            shad_r = ray(hit.point + hit.normal * 0.001, to_light)
            blocked = False
            for obj in scene.objects:
                h = obj.hit(shad_r)
                if h and h[0] < (light.pos - hit.point).length():
                    if not getattr(obj.mat, "emissive", False):
                        blocked = True
                        break
            if not blocked:
                ndotl = max(hit.normal.dot(to_light), 0)
                col = col + self.color * ndotl * light.intensity * light.color
        return col

    def ambient(self, hit, scene):
        return self.color * scene.ambient


class metal:
    def __init__(self, color, fuzz=0.0):
        self.color = color
        self.fuzz = fuzz

    def shade(self, hit, r_in, scene, depth):
        col = vec3(0, 0, 0)
        # direct
        for light in scene.lights:
            to_light = (light.pos - hit.point).norm()
            shad_r = ray(hit.point + hit.normal * 0.001, to_light)
            blocked = False
            for obj in scene.objects:
                h = obj.hit(shad_r)
                if h and h[0] < (light.pos - hit.point).length():
                    if not getattr(obj.mat, "emissive", False):
                        blocked = True
                        break
            if not blocked:
                ndotl = max(hit.normal.dot(to_light), 0)
                diff = self.color * ndotl * light.intensity * light.color
                col = col + diff
                # specular
                view = (r_in.origin - hit.point).norm()
                half = (to_light + view).norm()
                spec = max(hit.normal.dot(half), 0) ** 32
                col = col + vec3(1, 1, 1) * spec * 0.5 * light.intensity

        col = col + self.color * scene.ambient

        # reflection
        if depth < 5:
            reflected = reflect(r_in.dir, hit.normal)
            reflected = reflected + random_in_unit_sphere() * self.fuzz
            r = ray(hit.point + hit.normal * 0.001, reflected)
            col = col + scene.trace(r, depth + 1) * 0.8

        return col


class dielectric:
    def __init__(self, color, ri=1.5):
        self.color = color
        self.ri = ri

    def shade(self, hit, r_in, scene, depth):
        if depth >= 5:
            return vec3(0, 0, 0)

        front_face = r_in.dir.dot(hit.normal) < 0
        n = hit.normal if front_face else -hit.normal
        ri_ratio = 1.0 / self.ri if front_face else self.ri

        unit_dir = r_in.dir.norm()
        cos_theta = min((-unit_dir).dot(n), 1.0)
        sin_theta = math.sqrt(1.0 - cos_theta * cos_theta)

        cannot_refract = ri_ratio * sin_theta > 1.0
        reflect_prob = schlick(cos_theta, ri_ratio) if not cannot_refract else 1.0

        if random.random() < reflect_prob or cannot_refract:
            r_dir = reflect(unit_dir, n)
        else:
            r_dir = refract(unit_dir, n, ri_ratio)
            if r_dir is None:
                r_dir = reflect(unit_dir, n)

        scattered = ray(hit.point + n * 0.001, r_dir)
        col = scene.trace(scattered, depth + 1)

        # beer's law — color absorption through glass
        t = (scattered.origin - hit.point).length() if front_face else 0.01
        absorption = vec3(
            math.exp(-(1 - self.color.x) * t),
            math.exp(-(1 - self.color.y) * t),
            math.exp(-(1 - self.color.z) * t),
        )
        return col * absorption


class emissive:
    def __init__(self, color, strength=1.0):
        self.color = color
        self.strength = strength
        self.emissive = True

    def shade(self, hit, r_in, scene, depth):
        return self.color * self.strength

    def direct(self, hit, scene):
        return vec3(0, 0, 0)

    def ambient(self, hit, scene):
        return vec3(0, 0, 0)
