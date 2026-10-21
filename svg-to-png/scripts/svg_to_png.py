#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["resvg-py==0.5.0"]
# ///
"""
Convert SVG files to PNG with resvg (a Rust renderer; prebuilt wheels, no
system libraries needed).

Usage:
  uv run svg_to_png.py logo.svg                      # -> logo.png next to it
  uv run svg_to_png.py logo.svg --width 1024         # height keeps the aspect ratio
  uv run svg_to_png.py icons/ --out png/ --scale 2   # every .svg in a folder, 2x
  uv run svg_to_png.py a.svg b.svg --background white
  cat logo.svg | uv run svg_to_png.py - --out logo.png

Prints one JSON line per file: {"input", "output", "width", "height", "bytes"}
or {"input", "error"}. Exit code 0 when every file converted, 1 otherwise,
2 on bad arguments.
"""
import argparse
import json
import os
import struct
import sys

MAX_SIDE = 16384          # resvg can allocate width*height*4 bytes; keep it sane
MAX_SVG_BYTES = 20 * 1024 * 1024


def png_size(data: bytes) -> tuple[int, int]:
    # IHDR is always the first chunk: width and height are big-endian at 16..24.
    return struct.unpack(">II", data[16:24])


def output_path(src: str, out: str | None, many: bool) -> str:
    stem = "stdin" if src == "-" else os.path.splitext(os.path.basename(src))[0]
    if out is None:
        if src == "-":
            return os.path.abspath("stdin.png")
        return os.path.splitext(os.path.abspath(src))[0] + ".png"
    if many or out.endswith(os.sep) or os.path.isdir(out):
        os.makedirs(out, exist_ok=True)
        return os.path.join(os.path.abspath(out), stem + ".png")
    parent = os.path.dirname(os.path.abspath(out))
    os.makedirs(parent, exist_ok=True)
    return os.path.abspath(out if out.lower().endswith(".png") else out + ".png")


def collect(inputs: list[str]) -> list[str]:
    files: list[str] = []
    for item in inputs:
        if item == "-":
            files.append("-")
        elif os.path.isdir(item):
            for name in sorted(os.listdir(item)):
                if name.lower().endswith((".svg", ".svgz")):
                    files.append(os.path.join(item, name))
        else:
            files.append(item)
    return files


def installed_font_families() -> dict:
    """
    resvg maps generic names (sans-serif, serif, monospace) to Arial / Times
    New Roman / Courier New by default, which the agent image does not have,
    so text using them would silently vanish. Point them at the fonts the
    image does install (fonts-inter, fonts-dejavu-core) when they are there.
    """
    found = set()
    for root in ("/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts")):
        for _dir, _sub, names in os.walk(root):
            for n in names:
                found.add(n.lower())
    has = lambda prefix: any(n.startswith(prefix) for n in found)
    families = {}
    if has("inter"):
        families.update(font_family="Inter", sans_serif_family="Inter")
    elif has("dejavusans"):
        families.update(font_family="DejaVu Sans", sans_serif_family="DejaVu Sans")
    if has("dejavuserif"):
        families["serif_family"] = "DejaVu Serif"
    if has("dejavusansmono"):
        families["monospace_family"] = "DejaVu Sans Mono"
    return families


def convert(resvg_py, src: str, args) -> dict:
    kwargs = dict(installed_font_families())
    if args.width:
        kwargs["width"] = args.width
    if args.height:
        kwargs["height"] = args.height
    if args.scale and not (args.width or args.height):
        kwargs["zoom"] = args.scale
    if args.background:
        kwargs["background"] = args.background
    if args.dpi:
        kwargs["dpi"] = args.dpi
    if args.font_dir:
        kwargs["font_dirs"] = args.font_dir
    if src == "-":
        svg = sys.stdin.read()
        if len(svg.encode("utf-8")) > MAX_SVG_BYTES:
            raise ValueError("SVG is larger than 20 MB")
        kwargs["svg_string"] = svg
    else:
        if not os.path.isfile(src):
            raise FileNotFoundError(f"no such file: {src}")
        if os.path.getsize(src) > MAX_SVG_BYTES:
            raise ValueError("SVG is larger than 20 MB")
        kwargs["svg_path"] = src
        # Relative <image href="..."> resolves next to the SVG.
        kwargs["resources_dir"] = os.path.dirname(os.path.abspath(src))
    data = bytes(resvg_py.svg_to_bytes(**kwargs))
    width, height = png_size(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"rendered size {width}x{height} is over {MAX_SIDE}px; pass a smaller --width/--scale")
    return {"data": data, "width": width, "height": height}


def main() -> int:
    p = argparse.ArgumentParser(description="Convert SVG to PNG.")
    p.add_argument("inputs", nargs="+", help="SVG files, folders of SVGs, or - for stdin")
    p.add_argument("--out", help="output .png (one input) or folder (several)")
    p.add_argument("--width", type=int, help="output width in px (keeps aspect ratio unless --height is set too)")
    p.add_argument("--height", type=int, help="output height in px")
    p.add_argument("--scale", type=float, help="zoom multiplier on the SVG's own size, e.g. 2 for @2x (ignored with --width/--height)")
    p.add_argument("--background", help='CSS colour behind the drawing, e.g. white or "#0b0a16"; default transparent')
    p.add_argument("--dpi", type=float, help="DPI for physical units (mm, in, pt) in the SVG")
    p.add_argument("--font-dir", action="append", help="folder of .ttf/.otf fonts the SVG's text uses (repeatable)")
    args = p.parse_args()

    for name in ("width", "height"):
        v = getattr(args, name)
        if v is not None and not (1 <= v <= MAX_SIDE):
            p.error(f"--{name} must be 1..{MAX_SIDE}")
    if args.scale is not None and not (0 < args.scale <= 16):
        p.error("--scale must be > 0 and <= 16")

    files = collect(args.inputs)
    if not files:
        print(json.dumps({"error": "no .svg files found"}))
        return 1
    many = len(files) > 1

    import resvg_py  # after arg checks, so --help works without the dependency

    ok = True
    for src in files:
        try:
            result = convert(resvg_py, src, args)
            dest = output_path(src, args.out, many)
            with open(dest, "wb") as fh:
                fh.write(result["data"])
            print(json.dumps({"input": src, "output": dest, "width": result["width"],
                              "height": result["height"], "bytes": len(result["data"])}))
        except Exception as exc:  # one bad file must not stop the batch
            ok = False
            print(json.dumps({"input": src, "error": str(exc)}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
