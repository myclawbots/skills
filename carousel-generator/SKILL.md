---
name: carousel-generator
description: >
  Carousel Studio — turn a JSON slide deck into publication-ready social
  carousel PNGs. 5 designed themes (default, neon, earthy, brutalist,
  luxury), 25+ platform size presets (Instagram, TikTok, LinkedIn, X,
  Facebook, YouTube, Threads, Pinterest), logo support, retina 2x output.
  ONE self-bootstrapping command — installs its own Chromium and fonts on
  first run. You write the deck; it renders.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [carousel, instagram, design, rendering]
suggested_template: content_creator
metadata:
  openclaw:
    emoji: "🎠"
---

# Carousel Studio

You research and write the copy as a JSON deck; this renders it. Zero setup —
the wrapper installs npm deps, Chromium, and fonts automatically on first run
(and self-heals after platform updates).

## Render (the only command you need)

```bash
cd /root/.openclaw/skills/carousel-generator/scripts
bash run.sh deck.json /root/.openclaw/workspace/media/carousel-ai-myths --theme neon --platform instagram-portrait
bash run.sh --list-platforms          # all 25+ size presets
```

First run does one-time setup (~170MB Chromium; a few minutes). Every run
after renders immediately. Output: `<outdir>/NN-<type>.png` at 2x retina.
Always render into a new folder under `/root/.openclaw/workspace/media/`:
files outside the workspace may not be delivered to the chat.

## Show the user

Put one line `MEDIA:<absolute path>` per slide in your reply, in slide order,
each on its own line and not in a code block — for example
`MEDIA:/root/.openclaw/workspace/media/carousel-ai-myths/01-hook.png`. The
`view_image` (View Image) tool shows a file only to you, never to the user:
use it to check a slide, never to deliver one. Get the user's OK on the slides
before posting them.

## The deck (what YOU write)

```json
{
  "topic": "AI news",
  "handle": "@myclawbots.ai",
  "logo": "./assets/logo.svg",
  "slides": [
    { "type": "hook",  "kicker": "TECH REALITY CHECK", "headline": "5 AI myths that need to die", "sub": "You've heard them all." },
    { "type": "point", "headline": "One clear idea", "body": "90-140 chars of explanation." },
    { "type": "stat",  "figure": "92", "unit": "%", "body": "what the number means" },
    { "type": "list",  "headline": "What works", "items": ["Three to five items", "30-60 chars each"] },
    { "type": "quote", "quote": "Strong principle or hot take.", "source": "Attribution" },
    { "type": "cta",   "headline": "Closing push", "body": "Why follow.", "action": "follow" }
  ]
}
```

Slide types: `hook` (slide 1: kicker/headline/sub) · `point`
(headline/body) · `stat` (figure/unit/body) · `list` (headline + 3-5
items) · `quote` (quote/source) · `cta` (headline/body/action — actions:
`follow`, `save`, `share`, `link`, or custom text).

**Character budgets** (auto-fit shrinks overflow, but staying inside these
looks best): hook.headline 30-50 · hook.sub 60-90 · point.headline 35-55 ·
point.body 90-140 · stat.figure 2-5 · stat.body 70-110 · list items 30-60
each · quote 60-100 · cta.headline 25-45 · cta.body 70-120.

`logo` is optional (svg/png/jpg/webp, path relative to the deck file;
falls back to a topic wordmark). Sample decks for every theme ship in this
directory (`content.*.json`); full docs in `README.md`.

## Themes — each a distinct layout, not a palette swap

| `--theme` | Vibe |
|---|---|
| `default` | clean tech editorial, left-aligned |
| `neon` | tech/AI/crypto — gradient headlines, glow, dot rail |
| `earthy` | coaching/wellness — warm paper, pill badges |
| `brutalist` | hot takes — stark borders, massive uppercase |
| `luxury` | executive — serif, gold rules, roman numerals |

## Platforms

`--platform` picks exact dimensions: `instagram-portrait` (default, 4:5),
`instagram-post`, `instagram-story`, `tiktok`, `linkedin-post`,
`linkedin-landscape`, `x-post`, `facebook-post`, `youtube-thumbnail`,
`pinterest`, and more — `bash run.sh --list-platforms` for the full table.

## Quick engine (fallback)

Constrained machine or no browser? Pillow via uv, flat takeaways format:
`uv run scripts/render_carousel.py content-quick.json`
(`{"topic", "takeaways": ["HEADLINE: detail", ...]}`)

## Pipeline

Hand the PNGs to **cloudinary-uploader** (public URLs), then
**social-publisher** (Instagram/Facebook posting).
