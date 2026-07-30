import math
import random
import sys

from vec3 import vec3


def render(width, height, scene_obj, cam, samples=4):
    print(f"rendering {width}x{height}  {samples}spp")
    pixels = []
    total = width * height
    last_pct = -1
    for y in range(height - 1, -1, -1):
        for x in range(width):
            col = vec3(0, 0, 0)
            for _ in range(samples):
                sx = x + random.random()
                sy = y + random.random()
                r = cam.get_ray(sx, sy, width, height)
                col = col + scene_obj.trace(r)

            col = col * (1.0 / samples)

            col = vec3(math.sqrt(col.x), math.sqrt(col.y), math.sqrt(col.z))
            col = vec3(min(col.x, 1), min(col.y, 1), min(col.z, 1))

            pixels.append(col.tuple())

            idx = (height - 1 - y) * width + x + 1
            pct = int(idx / total * 100)
            if pct != last_pct:
                last_pct = pct
                bar = "#" * int(pct / 5) + "." * (20 - int(pct / 5))
                sys.stdout.write(f"\r  [{bar}] {pct}%")
                sys.stdout.flush()
    print()
    return pixels


def save_ppm(pixels, width, height, path):
    with open(path, "wb") as f:
        f.write(f"P6\n{width} {height}\n255\n".encode())
        for r, g, b in pixels:
            f.write(bytes([int(r * 255), int(g * 255), int(b * 255)]))
    print(f"saved {path}")


def save_png(pixels, width, height, path):
    """fallback png save using pure python — only if no PIL available."""
    try:
        from PIL import Image
        img = Image.new("RGB", (width, height))
        img.putdata([(int(r * 255), int(g * 255), int(b * 255)) for r, g, b in pixels])
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.save(path)
        print(f"saved {path}")
    except ImportError:
        print("  PIL not available — saving as ppm instead")
        save_ppm(pixels, width, height, path.replace(".png", ".ppm"))
