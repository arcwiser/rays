# rays

a pure-python ray tracer. no libraries, no frameworks, just math.

spheres, diffuse shading, specular highlights, hard shadows, reflections, sky gradient.

### run it

```
python main.py                  # 400x250, 4x aa
python main.py 800 8            # 800x500, 8x aa — slower but cleaner
python main.py 200 1            # fast preview, no aa
```

output goes to `output.ppm` — open with any image viewer that handles PPM (irfanview, gimp, etc) or convert with `magick convert output.ppm out.png`.

### the scene

- ground plane (giant sphere)
- red sphere (left, shiny)
- green sphere (center-right, matte)
- blue sphere (far right, glossy)
- mirror ball (center-left, highly reflective)
- floating light sphere (glows)
- key light from upper-right

### files

- `main.py` — everything: vec3, ray, sphere, scene, camera, renderer, output

### how it works

for each pixel, casts a ray into the scene. if it hits a sphere, computes lighting by checking if the light is visible (shadow ray), then adds diffuse + specular + reflections recursively. output is PPM format.
