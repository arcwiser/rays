# rays

a pure-python ray tracer. no libraries, just math.

spheres, triangle meshes, diffuse + metal + glass materials, reflections, refraction, shadows, multi-sample aa, scene files, obj loader.

### quick start

```
python main.py render                    # built-in demo scene, 400x250
python main.py render -w 800 -s 8        # higher quality
python main.py render scenes/spheres.json -w 800 -o out.ppm
python main.py preview                   # quick 160x100 check
python main.py info some_model.obj       # check an obj file
```

output is `.ppm` — open with irfanview, gimp, or convert with `magick convert output.ppm out.png`.

### scene files

json files describe the camera, objects, materials, and lights:

```json
{
  "camera": { "position": [0, 1.5, 5], "look_at": [0, 0.6, 0], "fov": 55 },
  "lights": [
    { "position": [3, 6, 4], "color": [1, 1, 1], "intensity": 2.0 }
  ],
  "objects": [
    { "type": "sphere", "center": [0, 0, 0], "radius": 1,
      "material": { "type": "metal", "color": [1, 0.2, 0.1], "fuzz": 0.1 } },
    { "type": "mesh", "file": "models/teapot.obj",
      "material": { "type": "glass", "color": [1, 1, 1], "ri": 1.5 } }
  ]
}
```

### materials

| type | params | notes |
|------|--------|-------|
| `lambertian` | `color` | matte diffuse |
| `metal` | `color`, `fuzz` | reflective, fuzz blurs reflections |
| `glass` / `dielectric` | `color`, `ri` | refraction + fresnel, `ri` = refractive index |
| `emissive` | `color`, `strength` | acts as a light source |

### files

| file | what |
|------|------|
| `vec3.py` | 3d vector math |
| `ray.py` | ray class |
| `hittable.py` | sphere, triangle, mesh, obj loader |
| `material.py` | lambertian, metal, dielectric, emissive |
| `camera.py` | camera with fov |
| `scene.py` | scene class, json loader, built-in demo |
| `renderer.py` | render loop + ppm output |
| `main.py` | cli |

### example: render a model

1. drop a `.obj` file in `models/`
2. make a scene json pointing at it
3. `python main.py render my_scene.json -o render.png`

### why

built from scratch to understand how ray tracing actually works.
