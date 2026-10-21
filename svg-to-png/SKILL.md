---
name: svg_to_png
description: Convert SVG files to PNG — logos, icons, charts, diagrams, or SVG code you wrote yourself — at any size or scale, with a transparent or solid background. Use it whenever something needs a PNG (posting, uploading, email, docs) and you have an SVG.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [svg, png, conversion, images]
suggested_template: content_creator
---

# SVG to PNG

Turns SVG into PNG with resvg, a fast and accurate renderer. Runs on this machine; no API key, no account, nothing leaves the machine.

Social platforms, Google Drive previews and most email clients don't accept SVG, so convert first whenever the user wants to post, upload or share an SVG.

## Convert

```bash
uv run /root/.openclaw/skills/svg-to-png/scripts/svg_to_png.py logo.svg
```

That writes `logo.png` next to the SVG, at the SVG's own size, with a transparent background. The first run downloads the renderer, which takes a few seconds; later runs are instant.

Common options:

| Want | Add |
|---|---|
| A set width (height keeps the aspect ratio) | `--width 1080` |
| A set height | `--height 512` |
| Retina / sharper output | `--scale 2` (or `3`) |
| Solid background instead of transparent | `--background white` or `--background "#0b0a16"` |
| Choose where it goes | `--out path/to/file.png` (one file) or `--out folder/` (several) |
| Every SVG in a folder | pass the folder: `... icons/ --out png/` |
| SVG you just wrote, without saving it first | `cat <<'EOF' \| uv run .../svg_to_png.py - --out logo.png` |
| A custom font the SVG's text uses | `--font-dir /path/to/fonts` (folder of .ttf/.otf) |

Sizes people ask for: Instagram post 1080×1080 (`--width 1080` on a square SVG), story 1080×1920, favicon 512×512, social avatar 400×400, email header about 600 wide.

## Reading the result

The script prints one JSON line per file:

```json
{"input": "logo.svg", "output": "/root/work/logo.png", "width": 1024, "height": 512, "bytes": 9216}
```

On failure the line has `"error"` instead, and the exit code is 1 (2 for a bad option). One broken file never stops the rest of a folder. Tell the user the output path and the pixel size.

## Things to know

- **Text:** SVG text renders with the fonts on this machine (Inter for sans-serif, DejaVu for serif and monospace). If the design names another font and it matters, get the .ttf and pass `--font-dir`, or convert the text to outlines in the SVG.
- **Images inside the SVG:** local image references resolve next to the SVG file. Remote (`http…`) images inside an SVG are not fetched; download them first and point the SVG at the local copy.
- **Limits:** SVGs up to 20 MB; output up to 16384 px on a side.
- **Posting it:** to publish the PNG, stage it with the myclawbots `create_upload_url` tool and post its `public_url` with `post_to_social`. Show the user the image first and get a yes, as for any post.
