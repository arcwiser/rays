#!/usr/bin/env python3
import argparse
import os
import sys
import time

from scene import load_scene, demo_scene
from renderer import render, save_ppm, save_png


def cmd_render(args):
    if args.scene == "demo":
        s, cam = demo_scene()
    else:
        if not os.path.exists(args.scene):
            print(f"scene file not found: {args.scene}")
            sys.exit(1)
        s, cam = load_scene(args.scene)

    h = args.height if args.height else int(args.width / 1.6)
    print(f"objects: {len(s.objects)}  lights: {len(s.lights)}")
    start = time.time()
    pixels = render(args.width, h, s, cam, args.samples)
    elapsed = time.time() - start
    print(f"took {elapsed:.1f}s")

    if args.output.endswith(".png"):
        save_png(pixels, args.width, h, args.output)
    else:
        save_ppm(pixels, args.width, h, args.output)


def cmd_preview(args):
    """quick low-res render to check composition, then exit"""
    s, cam = demo_scene() if args.scene == "demo" else load_scene(args.scene)
    pixels = render(160, 100, s, cam, 2)
    save_ppm(pixels, 160, 100, "_preview.ppm")
    print("  preview saved to _preview.ppm")


def cmd_info(args):
    if args.file.endswith(".obj"):
        from hittable import load_obj
        tris = load_obj(args.file)
        print(f"obj file: {args.file}")
        print(f"  triangles: {len(tris)}")
        if tris:
            verts = set()
            for t in tris:
                verts.add((t.v0.x, t.v0.y, t.v0.z))
                verts.add((t.v1.x, t.v1.y, t.v1.z))
                verts.add((t.v2.x, t.v2.y, t.v2.z))
            print(f"  vertices: {len(verts)}")
    elif args.file.endswith(".json"):
        import json
        with open(args.file) as f:
            d = json.load(f)
        print(f"scene: {args.file}")
        print(f"  objects: {len(d.get('objects', []))}")
        print(f"  lights: {len(d.get('lights', []))}")
    else:
        print(f"unknown file type: {args.file}")


def main():
    p = argparse.ArgumentParser(description="rays — ray tracer from scratch")
    sub = p.add_subparsers(dest="cmd", required=True)

    # render
    r = sub.add_parser("render", help="render a scene to image")
    r.add_argument("scene", nargs="?", default="demo", help="scene.json or 'demo'")
    r.add_argument("-w", "--width", type=int, default=400)
    r.add_argument("--height", type=int, default=0, help="auto if 0")
    r.add_argument("-s", "--samples", type=int, default=4)
    r.add_argument("-o", "--output", default="output.ppm")

    # preview
    pr = sub.add_parser("preview", help="quick 160x100 preview")
    pr.add_argument("scene", nargs="?", default="demo")

    # info
    info = sub.add_parser("info", help="show info about a scene or model file")
    info.add_argument("file", help="path to .json or .obj file")

    args = p.parse_args()

    if args.cmd == "render":
        cmd_render(args)
    elif args.cmd == "preview":
        cmd_preview(args)
    elif args.cmd == "info":
        cmd_info(args)


if __name__ == "__main__":
    main()
