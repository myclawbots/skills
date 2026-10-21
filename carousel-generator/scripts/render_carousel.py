#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow>=10.0.0"]
# ///
"""
carousel/generator.py
======================
AI news carousel image generator.
Searches trending AI news → summarizes with Gemini → renders slides with Pillow.

Produces:
  carousel/output/carousel_YYYY-MM-DD_cover.png
  carousel/output/carousel_YYYY-MM-DD_slide2.png
  carousel/output/carousel_YYYY-MM-DD_slide3.png
  carousel/output/carousel_YYYY-MM-DD_follow.png
  carousel/output/carousel_YYYY-MM-DD_manifest.json

Usage:
  python3 -m carousel.generator          # generates today's carousel
  python3 -m carousel.generator 1        # use 2nd news story
"""

import os
import sys
import json
import base64
import re
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

# ── Load .env.local ───────────────────────────────────────────────────────────
def _load_env():
    cwd = Path.cwd()
    for d in [cwd, cwd.parent, cwd.parent.parent, Path(__file__).parent.parent]:
        env_path = d / ".env.local"
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break

_load_env()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("carousel_generator")

SCRIPT_DIR = Path(__file__).parent.resolve()
SKILL_DIR = SCRIPT_DIR.parent
ASSETS_DIR = str(SKILL_DIR / "assets")
OUTPUT_DIR = str(SKILL_DIR / "output")

# No API keys: this is a pure renderer (see "Main" below). It never reads a
# Gemini/OpenAI key and never calls a model API. A cover background, if any,
# is passed in as "cover_image" (a path, e.g. one made by the gemini-image
# skill through the MyClawBots vault, or a URL).
HANDLE = os.environ.get("BRAND_HANDLE", "@myclawbots.ai")

# Font search paths
def _find_system_font(name_patterns):
    search_dirs = [
        "/usr/share/fonts/truetype/inter",
        "/usr/share/fonts/opentype/inter",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/liberation",
        "/usr/local/lib/node_modules/openclaw/node_modules/pdfjs-dist/standard_fonts",
        "/System/Library/Fonts/Supplemental",
        "/Library/Fonts",
        "/usr/share/fonts",
    ]
    for d in search_dirs:
        p = Path(d)
        if p.exists():
            for pat in name_patterns:
                matches = list(p.glob(f"*{pat}*.ttf")) + list(p.glob(f"*{pat}*.otf"))
                if matches:
                    return str(matches[0])
    return None

# Only KNOWN Latin faces — a loose "*Regular*" glob can match a non-Latin
# system font and render body text as tofu boxes. If none match, load_font
# falls through to the bundled/auto-fetched Inter.
FONT_BOLD = _find_system_font(["Inter-Bold", "InterVariable", "DejaVuSans-Bold", "LiberationSans-Bold", "Arial Bold", "Helvetica"])
FONT_REGULAR = _find_system_font(["Inter-Regular", "InterVariable", "DejaVuSans.", "LiberationSans-Regular", "Arial.", "Helvetica"])
FONT_ITALIC = _find_system_font(["Inter-Italic", "DejaVuSans-Oblique", "LiberationSans-Italic", "Arial Italic"])

WIDTH  = 1080
HEIGHT = 1350

THEMES = {
    "red": {
        "bg": (15, 15, 20), "accent": (255, 59, 48), "accent_light": (255, 100, 80),
        "text": (255, 255, 255), "muted": (160, 160, 170),
        "card_bg": (25, 25, 35), "divider": (50, 50, 65),
    },
    "blue": {
        "bg": (10, 15, 30), "accent": (0, 122, 255), "accent_light": (60, 160, 255),
        "text": (255, 255, 255), "muted": (160, 170, 190),
        "card_bg": (20, 25, 45), "divider": (40, 50, 80),
    },
    "green": {
        "bg": (10, 20, 15), "accent": (48, 209, 88), "accent_light": (80, 230, 120),
        "text": (255, 255, 255), "muted": (160, 180, 165),
        "card_bg": (20, 35, 25), "divider": (40, 65, 50),
    },
    "brand": {
        "bg": (15, 12, 10), "accent": (255, 91, 0), "accent_light": (255, 165, 0),
        "text": (255, 255, 255), "muted": (180, 165, 150),
        "card_bg": (30, 22, 15), "divider": (65, 45, 30),
    },
}


# ── Font loading (Prioritize bundled Inter.ttf) ──────────────────────────────
BUNDLED_FONT = SKILL_DIR / "assets" / "fonts" / "Inter.ttf"

def load_font(size, bold=False):
    """Load bundled Inter.ttf with exact point size, or fallback to system TTF."""
    if BUNDLED_FONT.exists():
        try:
            return ImageFont.truetype(str(BUNDLED_FONT), size)
        except Exception:
            pass
    # System font fallbacks
    for f in [FONT_BOLD if bold else FONT_REGULAR, FONT_REGULAR, FONT_BOLD]:
        if f:
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                pass
    # Last resort before PIL's unusable bitmap default: fetch Inter once.
    fetched = _fetch_bundled_font()
    if fetched:
        try:
            return ImageFont.truetype(fetched, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default()
    except Exception:
        return None


_FONT_FETCH_TRIED = False

def _fetch_bundled_font():
    """Best-effort one-time download of Inter into assets/fonts (the only
    network the renderer may touch besides an explicit cover_image URL)."""
    global _FONT_FETCH_TRIED
    if BUNDLED_FONT.exists():
        return str(BUNDLED_FONT)
    if _FONT_FETCH_TRIED:
        return None
    _FONT_FETCH_TRIED = True
    try:
        BUNDLED_FONT.parent.mkdir(parents=True, exist_ok=True)
        url = "https://github.com/rsms/inter/raw/master/docs/font-files/InterVariable.ttf"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        if len(data) > 100_000:
            with open(BUNDLED_FONT, "wb") as f:
                f.write(data)
            log.info(f"Fetched Inter font → {BUNDLED_FONT}")
            return str(BUNDLED_FONT)
    except Exception as e:
        log.warning(f"Font auto-fetch failed: {e}")
    return None

def _bold(size):   return load_font(size, bold=True)
def _regular(size): return load_font(size, bold=False)

WIDTH  = 1080
HEIGHT = 1350

THEMES = {
    "red": {
        "bg_top": (10, 12, 18), "bg_bot": (18, 14, 22),
        "accent": (255, 59, 48), "accent_light": (255, 120, 100),
        "text": (255, 255, 255), "muted": (200, 205, 220),
        "card_bg": (26, 24, 34), "card_border": (60, 45, 55),
    },
    "blue": {
        "bg_top": (8, 14, 28), "bg_bot": (14, 22, 42),
        "accent": (0, 145, 255), "accent_light": (80, 190, 255),
        "text": (255, 255, 255), "muted": (205, 215, 235),
        "card_bg": (20, 30, 52), "card_border": (45, 65, 100),
    },
    "green": {
        "bg_top": (8, 20, 16), "bg_bot": (12, 32, 24),
        "accent": (16, 215, 100), "accent_light": (90, 245, 155),
        "text": (255, 255, 255), "muted": (200, 225, 215),
        "card_bg": (18, 38, 30), "card_border": (40, 75, 60),
    },
    "brand": {
        "bg_top": (12, 14, 20), "bg_bot": (22, 18, 24),
        "accent": (255, 105, 0), "accent_light": (255, 175, 50),
        "text": (255, 255, 255), "muted": (210, 215, 225),
        "card_bg": (28, 26, 36), "card_border": (65, 52, 60),
    },
}


def draw_accent_bar(draw, x, y, height, color, width=4):
    draw.rectangle([x, y, x + width, y + height], fill=color)


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines



# ── Classification ────────────────────────────────────────────────────────────

def classify(title):
    t = title.lower()
    if any(w in t for w in ["breach","hack","security","vulnerability","risk","warning"]):
        return "AI SECURITY", "red"
    elif any(w in t for w in ["funding","invest","valuation","raise","billion","million","deal"]):
        return "AI BUSINESS", "green"
    elif any(w in t for w in ["regulation","ban","law","policy","govern"]):
        return "AI POLICY", "red"
    elif any(w in t for w in ["launch","release","introduces","announces","unveil"]):
        return "PRODUCT LAUNCH", "blue"
    elif any(w in t for w in ["agent","autonomous","openclaw","agentic"]):
        return "AI AGENTS", "blue"
    elif any(w in t for w in ["openai","google","anthropic","meta","microsoft"]):
        return "BIG TECH", "blue"
    elif any(w in t for w in ["breakthrough","research","paper","model"]):
        return "AI RESEARCH", "blue"
    else:
        return "AI NEWS", "red"


def clean_headline(title):
    title = re.sub(r'\s*-\s*[A-Za-z][\w\s&.]+$', '', title)
    return (title[:62].rsplit(' ', 1)[0] + "...") if len(title) > 65 else title




# ── Cover slide ───────────────────────────────────────────────────────────────

def generate_cover_image(headline, label, accent, bg_image_path=None):
    """Compose the cover. With no background image, render a themed gradient —
    fully deterministic, no external image generation."""
    if not (bg_image_path and os.path.exists(bg_image_path)):
        theme = THEMES.get(accent, THEMES["brand"])
        grad = _draw_gradient_background(theme)
        bg_image_path = os.path.join(OUTPUT_DIR, "_cover_bg.png")
        grad.save(bg_image_path)
    return _compose_cover_with_bg(bg_image_path, headline, label, accent)

def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
    x0, y0, x1, y1 = xy
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)
    draw.pieslice([x0, y0, x0 + 2*radius, y0 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x1 - 2*radius, y0, x1, y0 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1 - 2*radius, x0 + 2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1 - 2*radius, y1 - 2*radius, x1, y1], 0, 90, fill=fill)
    if outline:
        draw.rounded_rectangle(xy, radius=radius, outline=outline, width=width)


def _draw_gradient_background(theme):
    """Render smooth vertical background gradient."""
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)
    top_r, top_g, top_b = theme["bg_top"]
    bot_r, bot_g, bot_b = theme["bg_bot"]
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_r + (bot_r - top_r) * ratio)
        g = int(top_g + (bot_g - top_g) * ratio)
        b = int(top_b + (bot_b - top_b) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    return img


def _compose_cover_with_bg(bg_path, headline, label, accent):
    theme = THEMES["brand"]
    bg = Image.open(bg_path).convert("RGB")
    bg_w, bg_h = bg.size
    target_ratio = WIDTH / HEIGHT
    bg_ratio = bg_w / bg_h
    if bg_ratio > target_ratio:
        new_w = int(bg_h * target_ratio)
        bg = bg.crop(((bg_w - new_w) // 2, 0, (bg_w - new_w) // 2 + new_w, bg_h))
    else:
        new_h = int(bg_w / target_ratio)
        bg = bg.crop((0, (bg_h - new_h) // 2, bg_w, (bg_h - new_h) // 2 + new_h))
    bg = bg.resize((WIDTH, HEIGHT), Image.LANCZOS)

    # Gradient overlay: dark at top and heavy dark gradient at bottom for text legibility
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for y_pos in range(HEIGHT):
        if y_pos < HEIGHT * 0.25:
            alpha = int(180 - (y_pos / (HEIGHT * 0.25)) * 60)
        elif y_pos > HEIGHT * 0.45:
            progress = (y_pos - HEIGHT * 0.45) / (HEIGHT * 0.55)
            alpha = int(120 + progress * 135)
        else:
            alpha = 110
        overlay_draw.line([(0, y_pos), (WIDTH, y_pos)], fill=(8, 10, 16, alpha))
    bg = Image.alpha_composite(bg.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(bg)

    font_badge = _bold(26); font_headline = _bold(52); font_footer = _bold(26); font_handle = _bold(24)

    # Top Header
    y = 70
    badge_text = f"  🔥 {label.upper()}  "
    bb = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bb[2] - bb[0] + 30, bb[3] - bb[1] + 18
    draw_rounded_rect(draw, (70, y, 70 + bw, y + bh), 12, theme["accent"])
    draw.text((70 + 15, y + 9), badge_text, fill=(255, 255, 255), font=font_badge)

    # Brand handle top right
    handle_text = HANDLE
    hb = draw.textbbox((0, 0), handle_text, font=font_handle)
    draw_rounded_rect(draw, (WIDTH - 70 - (hb[2] - hb[0]) - 30, y, WIDTH - 70, y + bh), 12, (20, 24, 36))
    draw.text((WIDTH - 70 - (hb[2] - hb[0]) - 15, y + 9), handle_text, fill=theme["muted"], font=font_handle)

    # Headline at bottom
    headline_lines = wrap_text(headline, font_headline, WIDTH - 160, draw)[:4]
    total_hl_height = len(headline_lines) * 66
    y = HEIGHT - total_hl_height - 180

    for line in headline_lines:
        # Subtle drop shadow
        draw.text((82, y + 3), line, fill=(0, 0, 0), font=font_headline)
        draw.text((80, y), line, fill=(255, 255, 255), font=font_headline)
        y += 66

    # Accent bar
    draw.rectangle([80, y + 10, 260, y + 16], fill=theme["accent"])

    # Bottom footer row
    fy = HEIGHT - 90
    draw.text((80, fy), "SLIDE 01 / 04", fill=(180, 190, 205), font=font_footer)

    swipe = "SWIPE TO READ  ➔"
    sb = draw.textbbox((0, 0), swipe, font=font_footer)
    sw_w, sw_h = sb[2] - sb[0] + 36, sb[3] - sb[1] + 20
    draw_rounded_rect(draw, (WIDTH - 80 - sw_w, fy - 8, WIDTH - 80, fy - 8 + sw_h), 12, theme["accent"])
    draw.text((WIDTH - 80 - sw_w + 18, fy + 2), swipe, fill=(255, 255, 255), font=font_footer)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "cover.jpg")
    bg.save(path, "JPEG", quality=96)
    return path


def generate_summary_slide(points, slide_num, total_slides, label, headline, theme_name="brand"):
    theme = THEMES.get(theme_name, THEMES["brand"])
    img = _draw_gradient_background(theme)
    draw = ImageDraw.Draw(img)

    font_badge = _bold(24); font_slide_header = _bold(44); font_page = _bold(24)
    font_bullet_title = _bold(32); font_bullet_body = _regular(26); font_footer = _bold(24)

    # ── Top Navigation Bar ───────────────────────────────────────────────────
    y = 65
    badge_text = f"  {label.upper()}  "
    bb = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bb[2] - bb[0] + 24, bb[3] - bb[1] + 16
    draw_rounded_rect(draw, (70, y, 70 + bw, y + bh), 10, theme["accent"])
    draw.text((70 + 12, y + 8), badge_text, fill=(255, 255, 255), font=font_badge)

    # Slide Counter Pill on Right
    counter_text = f"  SLIDE {slide_num:02d} / {total_slides:02d}  "
    cb = draw.textbbox((0, 0), counter_text, font=font_page)
    cw, ch = cb[2] - cb[0] + 20, cb[3] - cb[1] + 16
    draw_rounded_rect(draw, (WIDTH - 70 - cw, y, WIDTH - 70, y + ch), 10, (30, 36, 50), outline=(60, 70, 95))
    draw.text((WIDTH - 70 - cw + 10, y + 8), counter_text, fill=theme["muted"], font=font_page)

    # ── Header Title ─────────────────────────────────────────────────────────
    y += bh + 35
    slide_title = "Key Highlights & Breakdown" if slide_num == 2 else "Analysis & Future Outlook"
    draw.text((70, y), slide_title, fill=(255, 255, 255), font=font_slide_header)
    y += 60

    # Thin Divider
    draw.line([(70, y), (WIDTH - 70, y)], fill=(45, 55, 75), width=2)
    y += 40

    # ── Content Cards ────────────────────────────────────────────────────────
    margin_left = 70
    card_width = WIDTH - 140
    start_num = (slide_num - 2) * 3 + 1

    card_spacing = 30
    available_height = (HEIGHT - 130) - y
    cards_count = len(points)
    card_h = int((available_height - (cards_count - 1) * card_spacing) / cards_count)
    card_h = max(200, min(card_h, 260))

    for i, point in enumerate(points):
        title_part, body_part = (point.split(":", 1) if ":" in point else ("Key Update", point))
        title_part = title_part.strip()
        body_part = body_part.strip()

        card_x0 = margin_left
        card_x1 = WIDTH - margin_left
        card_y0 = y
        card_y1 = y + card_h

        # Card container with rounded corners and subtle border
        draw_rounded_rect(draw, (card_x0, card_y0, card_x1, card_y1), 18, theme["card_bg"], outline=theme["card_border"], width=2)

        # Left Neon Accent Strip
        draw_rounded_rect(draw, (card_x0, card_y0, card_x0 + 8, card_y1), 4, theme["accent"])

        # Number Badge Circle
        num_str = f"{start_num + i:02d}"
        cx, cy = card_x0 + 35, card_y0 + 30
        draw_rounded_rect(draw, (cx, cy, cx + 54, cy + 40), 8, theme["accent"])
        nb = draw.textbbox((0, 0), num_str, font=font_badge)
        draw.text((cx + (54 - (nb[2] - nb[0])) // 2, cy + 8), num_str, fill=(255, 255, 255), font=font_badge)

        # Text Layout
        tx = cx + 75
        ty = card_y0 + 26
        inner_w = card_width - 130

        # Title
        title_lines = wrap_text(title_part, font_bullet_title, inner_w, draw)[:2]
        for tl in title_lines:
            draw.text((tx, ty), tl, fill=theme["accent_light"], font=font_bullet_title)
            ty += 42
        ty += 8

        # Body
        body_lines = wrap_text(body_part, font_bullet_body, inner_w, draw)[:3]
        for bl in body_lines:
            draw.text((tx, ty), bl, fill=theme["muted"], font=font_bullet_body)
            ty += 34

        y += card_h + card_spacing

    # ── Bottom Bar ───────────────────────────────────────────────────────────
    fy = HEIGHT - 80
    draw.text((70, fy), f"@{HANDLE.lstrip('@')}", fill=(160, 170, 190), font=font_footer)

    next_text = "SWIPE NEXT  ➔" if slide_num < total_slides else "FINAL SLIDE  ➔"
    sb = draw.textbbox((0, 0), next_text, font=font_footer)
    draw.text((WIDTH - 70 - (sb[2] - sb[0]), fy), next_text, fill=theme["accent_light"], font=font_footer)

    return img


def generate_follow_slide(handle=None, label="AI NEWS", theme_name="brand"):
    if handle is None:
        handle = HANDLE
    theme = THEMES.get(theme_name, THEMES["brand"])
    img = _draw_gradient_background(theme)
    draw = ImageDraw.Draw(img)

    font_badge = _bold(24); font_headline = _bold(46); font_handle = _bold(40)
    font_sub = _regular(28); font_bullet = _bold(28); font_footer = _bold(26)

    # Top Badge
    y = 70
    badge_text = "  ⚡ NEVER MISS AN AI UPDATE  "
    bb = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw, bh = bb[2] - bb[0] + 24, bb[3] - bb[1] + 16
    draw_rounded_rect(draw, ((WIDTH - bw) // 2, y, (WIDTH + bw) // 2, y + bh), 10, theme["accent"])
    draw.text(((WIDTH - bw) // 2 + 12, y + 8), badge_text, fill=(255, 255, 255), font=font_badge)

    # ── Main Hero Card ───────────────────────────────────────────────────────
    card_x0, card_x1 = 70, WIDTH - 70
    card_y0, card_y1 = 140, 850
    draw_rounded_rect(draw, (card_x0, card_y0, card_x1, card_y1), 24, theme["card_bg"], outline=theme["card_border"], width=2)

    # Logo
    logo_path = os.path.join(ASSETS_DIR, "logo.jpg")
    if not os.path.exists(logo_path):
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
    logo_size = 200
    logo_y = card_y0 + 50
    logo_x = (WIDTH - logo_size) // 2

    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            w, h = logo.size; min_dim = min(w, h)
            logo = logo.crop(((w - min_dim)//2, (h - min_dim)//2, (w - min_dim)//2 + min_dim, (h - min_dim)//2 + min_dim))
            hires = logo_size * 4
            logo_hr = logo.resize((hires, hires), Image.LANCZOS)
            mask_hr = Image.new("L", (hires, hires), 0)
            ImageDraw.Draw(mask_hr).ellipse([0, 0, hires-1, hires-1], fill=255)
            circle_logo = Image.new("RGBA", (hires, hires), (0,0,0,0))
            circle_logo.paste(logo_hr, (0,0), mask_hr)
            circle_logo = circle_logo.resize((logo_size, logo_size), Image.LANCZOS)

            ring_pad = 6
            draw.ellipse([logo_x-ring_pad, logo_y-ring_pad, logo_x+logo_size+ring_pad, logo_y+logo_size+ring_pad], fill=theme["accent"])
            img.paste(circle_logo, (logo_x, logo_y), circle_logo)
        except Exception as e:
            print(f"   ⚠️ Logo load error: {e}")

    # Handle & Tagline
    cy = logo_y + logo_size + 30
    tb = draw.textbbox((0, 0), handle, font=font_handle)
    draw.text(((WIDTH - (tb[2] - tb[0])) // 2, cy), handle, fill=(255, 255, 255), font=font_handle)
    cy += 55

    tagline = "Autonomous AI & Tech News Breakdowns"
    tb = draw.textbbox((0, 0), tagline, font=font_sub)
    draw.text(((WIDTH - (tb[2] - tb[0])) // 2, cy), tagline, fill=theme["accent_light"], font=font_sub)
    cy += 50

    draw.line([((WIDTH - 300) // 2, cy), ((WIDTH + 300) // 2, cy)], fill=(60, 70, 95), width=2)
    cy += 35

    # 3 Value Propositions
    props = [
        " Daily AI News & Model Launches",
        " Autonomous Agent Tutorials",
        " Practical Workflow Automation",
    ]
    for p in props:
        pb = draw.textbbox((0, 0), p, font=font_bullet)
        px = (WIDTH - (pb[2] - pb[0])) // 2
        draw.text((px, cy), p, fill=theme["muted"], font=font_bullet)
        cy += 48

    # ── Interactive Action Card ──────────────────────────────────────────────
    act_y0, act_y1 = 880, 1180
    draw_rounded_rect(draw, (card_x0, act_y0, card_x1, act_y1), 20, (20, 24, 36), outline=(50, 60, 80), width=2)

    ay = act_y0 + 40
    call_title = "Did you find this valuable?"
    cb = draw.textbbox((0, 0), call_title, font=font_headline)
    draw.text(((WIDTH - (cb[2] - cb[0])) // 2, ay), call_title, fill=(255, 255, 255), font=font_headline)
    ay += 70

    # 4 Action Pills
    actions = ["❤️ LIKE", "💬 COMMENT", "↗️ SHARE", "📌 SAVE"]
    pill_w = 200
    pill_h = 56
    total_pills_w = len(actions) * pill_w + 3 * 20
    start_px = (WIDTH - total_pills_w) // 2

    for j, act in enumerate(actions):
        cur_px = start_px + j * (pill_w + 20)
        draw_rounded_rect(draw, (cur_px, ay, cur_px + pill_w, ay + pill_h), 12, (30, 36, 52), outline=theme["accent"])
        ab = draw.textbbox((0, 0), act, font=font_badge)
        draw.text((cur_px + (pill_w - (ab[2] - ab[0])) // 2, ay + 14), act, fill=(255, 255, 255), font=font_badge)

    ay += 90
    remind = "Turn on post notifications so you never miss an insight."
    rb = draw.textbbox((0, 0), remind, font=font_sub)
    draw.text(((WIDTH - (rb[2] - rb[0])) // 2, ay), remind, fill=theme["accent_light"], font=font_sub)

    # Footer
    fy = HEIGHT - 70
    draw.text((70, fy), f"SLIDE 04 / 04", fill=(140, 150, 170), font=font_footer)
    draw.text((WIDTH - 70 - 240, fy), f"myclawbots.ai", fill=theme["accent"], font=font_footer)

    return img




# ── Main: render from a content spec ─────────────────────────────────────────
# This script is a PURE RENDERER. Research and summarization are the agent's
# job (it has web tools and is itself an LLM) — it writes content.json, this
# renders it. No API keys, no network calls (except an optional cover_image
# URL download).

def _normalize_takeaways(raw):
    points = []
    for t in raw:
        if isinstance(t, str):
            points.append(t)
        elif isinstance(t, dict):
            h = (t.get("headline") or "").strip()
            d = (t.get("detail") or "").strip()
            points.append(f"{h}: {d}" if h and d else (h or d))
    return [p for p in points if p]


def _resolve_cover_image(spec):
    ref = spec.get("cover_image")
    if not ref:
        return None
    if os.path.exists(ref):
        return ref
    if str(ref).startswith("http"):
        try:
            req = urllib.request.Request(ref, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            if len(data) > 5000:
                path = os.path.join(OUTPUT_DIR, "cover_bg_download.jpg")
                with open(path, "wb") as f:
                    f.write(data)
                return path
        except Exception as e:
            log.warning(f"cover_image download failed: {e}")
    return None


def generate(spec: dict) -> dict:
    """Render a carousel from a content spec. Returns the manifest dict."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    headline = clean_headline((spec.get("topic") or spec.get("headline") or "").strip())
    if not headline:
        print("❌ content.json needs a 'topic' (or 'headline')"); return None
    points = _normalize_takeaways(spec.get("takeaways") or [])
    if len(points) < 2:
        print("❌ content.json needs at least 2 'takeaways'"); return None

    default_label, default_accent = classify(headline)
    label = (spec.get("badge") or spec.get("label") or default_label).strip()
    accent = spec.get("accent") or default_accent
    theme = spec.get("theme") or "brand"
    handle = spec.get("cta") or spec.get("handle") or HANDLE

    bg_image_path = _resolve_cover_image(spec)

    print(f"🎨 Rendering: {headline} | {label} | {len(points)} takeaways")
    all_paths = []

    cover_path = generate_cover_image(headline, label, accent, bg_image_path)
    if cover_path:
        final_cover = os.path.join(OUTPUT_DIR, f"carousel_{today}_cover.jpg")
        Image.open(cover_path).convert("RGB").save(final_cover, "JPEG", quality=96)
        all_paths.append(("cover", final_cover))
        print(f"   ✅ cover")

    slides_data = [points[i:i + 3] for i in range(0, len(points), 3)]
    total_slides = 1 + len(slides_data) + 1
    for idx, pts in enumerate(slides_data):
        slide_num = idx + 2
        img = generate_summary_slide(pts, slide_num, total_slides, label, headline, theme_name=theme)
        path = os.path.join(OUTPUT_DIR, f"carousel_{today}_slide{slide_num}.jpg")
        img.save(path, "JPEG", quality=96)
        all_paths.append((f"slide{slide_num}", path))
        print(f"   ✅ slide {slide_num}")

    follow_img = generate_follow_slide(handle=handle, label=label, theme_name=theme)
    follow_path = os.path.join(OUTPUT_DIR, f"carousel_{today}_follow.jpg")
    follow_img.save(follow_path, "JPEG", quality=96)
    all_paths.append(("follow", follow_path))
    print(f"   ✅ follow")

    manifest = {
        "date": today,
        "headline": headline,
        "label": label,
        "accent": accent,
        "points": points,
        "slides": [{"type": t, "path": p} for t, p in all_paths],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    manifest_path = os.path.join(OUTPUT_DIR, f"carousel_{today}_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\n✅ {len(all_paths)} slides  |  {manifest_path}")
    return manifest


def main():
    if len(sys.argv) < 2:
        print("Usage: render_carousel.py <content.json>")
        print('Spec: {"topic": "...", "takeaways": ["HEADLINE: detail", ...],')
        print('       "badge"?, "accent"?, "theme"?, "cta"?, "cover_image"? (path|url)}')
        sys.exit(2)
    with open(sys.argv[1]) as f:
        spec = json.load(f)
    manifest = generate(spec)
    if not manifest:
        sys.exit(1)
    for slide in manifest["slides"]:
        print(f"SLIDE_{slide['type'].upper()}={slide['path']}")


if __name__ == "__main__":
    main()
