import json
import os

from vec3 import vec3
from ray import ray
from hittable import sphere, triangle, mesh, load_obj
from material import lambertian, metal, dielectric, emissive


class light:
    def __init__(self, pos, color=vec3(1, 1, 1), intensity=1.0):
        self.pos = pos
        self.color = color
        self.intensity = intensity


class scene:
    def __init__(self):
        self.objects = []
        self.lights = []
        self.ambient = vec3(0.08, 0.08, 0.12)
        self.bg = vec3(0.04, 0.04, 0.1)

    def add(self, obj):
        self.objects.append(obj)

    def add_light(self, l):
        self.lights.append(l)

    def trace(self, r, depth=0):
        if depth > 8:
            return vec3(0, 0, 0)

        best = None
        best_obj = None
        for obj in self.objects:
            h = obj.hit(r)
            if h and (best is None or h[0] < best[0]):
                best = h
                best_obj = obj

        if best is None:
            t = 0.5 * (r.dir.y + 1.0)
            return vec3.lerp(self.bg, vec3(0.3, 0.5, 0.8), t)

        t, pt, n = best
        mat = best_obj.mat

        hit_rec = lambda: None
        hit_rec.point = pt
        hit_rec.normal = n
        hit_rec.t = t
        hit_rec.mat = mat

        return mat.shade(hit_rec, r, self, depth)


def _parse_vec3(v):
    if isinstance(v, list) and len(v) == 3:
        return vec3(v[0], v[1], v[2])
    return vec3(0, 0, 0)


_mat_types = {
    "lambertian": lambertian,
    "metal": metal,
    "dielectric": dielectric,
    "glass": dielectric,
    "emissive": emissive,
}


def load_scene(path):
    s = scene()
    with open(path) as f:
        data = json.load(f)

    # camera
    cam_data = data.get("camera", {})
    from camera import camera as cam_cls
    cam = cam_cls(
        _parse_vec3(cam_data.get("position", [0, 1.8, 5])),
        _parse_vec3(cam_data.get("look_at", [0, 0.8, 0])),
        fov=cam_data.get("fov", 60),
    )

    # settings
    settings = data.get("settings", {})
    s.ambient = _parse_vec3(settings.get("ambient", [0.08, 0.08, 0.12]))
    s.bg = _parse_vec3(settings.get("background", [0.04, 0.04, 0.1]))

    # lights
    for ldata in data.get("lights", []):
        l = light(
            _parse_vec3(ldata.get("position", [0, 5, 0])),
            _parse_vec3(ldata.get("color", [1, 1, 1])),
            ldata.get("intensity", 1.0),
        )
        s.add_light(l)

    # objects
    for odata in data.get("objects", []):
        obj_type = odata.get("type", "sphere")

        mdata = odata.get("material", {"type": "lambertian", "color": [0.5, 0.5, 0.5]})
        mtype = mdata.get("type", "lambertian")
        mcolor = _parse_vec3(mdata.get("color", [0.5, 0.5, 0.5]))
        if mtype == "metal":
            mat = metal(mcolor, fuzz=mdata.get("fuzz", 0.0))
        elif mtype in ("glass", "dielectric"):
            mat = dielectric(mcolor, ri=mdata.get("ri", 1.5))
        elif mtype == "emissive":
            mat = emissive(mcolor, strength=mdata.get("strength", 1.0))
        else:
            mat = lambertian(mcolor)

        if obj_type == "sphere":
            s.add(sphere(
                _parse_vec3(odata.get("center", [0, 0, 0])),
                odata.get("radius", 0.5),
                mat,
            ))

        elif obj_type == "mesh":
            filepath = odata.get("file", "")
            if not os.path.isabs(filepath):
                filepath = os.path.join(os.path.dirname(path), filepath)
            tris = load_obj(filepath, material=mat)
            if tris:
                s.add(mesh(tris, mat))
            else:
                print(f"  warning: no triangles loaded from {filepath}")

    return s, cam


def demo_scene():
    s = scene()

    # ground
    s.add(sphere(vec3(0, -1000, 0), 1000, lambertian(vec3(0.45, 0.45, 0.5))))

    # colored spheres
    s.add(sphere(vec3(-1.5, 0.8, 0), 0.7, metal(vec3(1, 0.2, 0.1), fuzz=0.15)))
    s.add(sphere(vec3(0.5, 0.7, 0.5), 0.6, lambertian(vec3(0.1, 0.7, 0.2))))
    s.add(sphere(vec3(1.8, 0.5, -0.8), 0.5, metal(vec3(0.2, 0.3, 0.95), fuzz=0.1)))

    # glass ball
    s.add(sphere(vec3(-0.3, 0.3, -1.2), 0.3, dielectric(vec3(0.95, 0.95, 0.5), ri=1.5)))

    # lights
    s.add_light(light(vec3(2, 5, 3), vec3(1, 1, 1), 1.8))
    s.add_light(light(vec3(-2, 3, 1), vec3(0.6, 0.7, 1), 0.6))

    from camera import camera as cam_cls
    cam = cam_cls(vec3(0, 1.5, 4.5), vec3(0, 0.6, 0))

    return s, cam
