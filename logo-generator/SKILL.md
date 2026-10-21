---
name: logo_generator
description: Generate professional logo concepts using AI image generation. Create variations, download in multiple formats, and save to Google Drive.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [logo, branding, image-generation, design]
suggested_template: content_creator
---

# Logo Generator

## Overview
Generate professional logo concepts using AI image generation. Create variations, download in multiple formats, and save to Google Drive.

**You generate the logos yourself** using an AI image provider, then save to Drive.

## Dependencies

This skill requires the following:

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | **Yes** — for saving logos to Google Drive and creating brand kit docs via `gws` CLI |
| `gemini-api` skill | **If user chooses Gemini** — for image generation via `gemini-3-pro-image-preview` |
| `$OPENAI_KEY` (stand-in, use with `vault-curl`) | **If user chooses OpenAI** — for image generation via DALL-E 3 |
| `$GEMINI_KEY` (stand-in, use with `vault-curl`) | **If user chooses Gemini** — for image generation via Gemini Imagen |

> **Before starting, check:**
> 1. Is `google-workspace` skill installed and `$GWS_GOOGLE_ACCOUNT` set? If not, logos can still be generated but won't auto-save to Drive — inform the user.
> 2. Which image keys do you have? `[ -n "$OPENAI_KEY" ] && echo openai; [ -n "$GEMINI_KEY" ] && echo gemini`. These are stand-ins (`mcb_sec_…`) for the user's keys, not the keys: they only work through `vault-curl`. A key added after you started is not in your env yet: run `vault-curl --secrets` and use an entry's `surrogate` string in place of `$OPENAI_KEY` / `$GEMINI_KEY`. Agents not yet moved to the vault may instead have real keys in the `OPENAI_API_KEY` / `GEMINI_API_KEY` variables: use those with plain `curl`, in the same header. Never print a key or stand-in, and never use OpenClaw's built-in secrets tool (these keys are not there). Missing keys: ask the user to add them in MyClawBots → Settings → Integrations; never ask them to paste a key into chat.

## Provider Selection — ASK THE USER

Before generating any images, **you must ask the user which AI provider to use**:

> "I can generate logo concepts using:
> 1. **OpenAI DALL-E 3** — high quality, ~$0.04/image, great for photorealistic styles
> 2. **Google Gemini Imagen** — cheaper (~$0.025/image), supports image editing and background removal
> 3. **SVG code** — free, I'll write vector code directly (best for geometric/minimal logos)
>
> Which would you prefer? Or I can mix — Gemini/DALL-E for concepts and SVG for the final refined version."

If only one key is available, inform the user and use that one. If neither key is set, default to SVG generation (free) and tell the user how to add an API key.

## Capabilities
- Generate multiple logo concepts from text prompts
- Create variations with different colors, styles, and layouts
- Output in PNG, SVG (hand-written code), and PDF
- Save to Google Drive automatically (requires `google-workspace` skill)
- Suggest color palettes and font pairings
- Design logos for any industry or style

## Step-by-Step Workflow

### 1. Gather Requirements
- Brand name and description
- Industry/category
- Style preference (minimalist, bold, geometric, organic, etc.)
- Color preferences (primary + secondary)
- Icon type preference (abstract, symbol, lettermark, wordmark)

### 2. Generate Logo Concepts

#### Option A: OpenAI DALL-E 3 (if user chose OpenAI)
```bash
vault-curl -sS https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "Professional logo for TechVision, a software company. Modern, minimalist tech logo with abstract geometric shapes. Primary color: deep blue (#0066CC), secondary: orange (#FF6B35). Clean lines, transparent background, vector style, suitable for app icon and business card.",
    "size": "1024x1024",
    "quality": "hd",
    "n": 1
  }' | jq -r '.data[0].url'
```

Save the returned URL locally:
```bash
curl -s [IMAGE_URL] -o logo_concept_1.png
```

#### Option B: Google Gemini Imagen (if user chose Gemini)
Easiest, and always works: the `gemini-image` skill (`claw install gemini-image` once). It finds the key itself and calls Gemini through the vault:
```bash
python3 /root/.openclaw/skills/gemini-image/scripts/gemini_image.py \
  --prompt "Professional logo for TechVision, a software company. Minimalist, geometric, deep blue and orange, transparent background." \
  --out /root/.openclaw/workspace/media/logo_concept_1.png
```
To edit an existing image, add `--input-image PATH`. The Python SDK below sends the stand-in directly, so it works **only when AGENTS.md says plain `curl` and SDKs work** (the MyClawBots vault proxy is on).

With the vault proxy on, Python:
```python
from google import genai
from google.genai import types
import os, base64

client = genai.Client(api_key=os.environ["GEMINI_KEY"])  # needs the vault proxy

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Professional logo for TechVision, a software company. Modern, minimalist tech logo with abstract geometric shapes. Primary color: deep blue (#0066CC), secondary: orange (#FF6B35). Clean lines, transparent background, vector style.",
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"],
    )
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("logo_concept_1.png", "wb") as f:
            f.write(base64.b64decode(part.inline_data.data))
        print("Saved logo_concept_1.png")
```

**Gemini bonus:** You can also **edit** an existing logo (remove background, change colors):
```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        types.Content(parts=[
            types.Part.from_bytes(data=open("logo_v1.png","rb").read(), mime_type="image/png"),
            types.Part.from_text("Remove the background, make it fully transparent. Keep the logo intact."),
        ])
    ],
    config=types.GenerateContentConfig(response_modalities=["image", "text"])
)
```

#### Option C: SVG Code (always available, free)
You can write SVG code directly — best for geometric and minimalist logos:
```xml
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0066CC;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#FF6B35;stop-opacity:1" />
    </linearGradient>
  </defs>
  <circle cx="100" cy="100" r="95" fill="none" stroke="url(#grad)" stroke-width="3"/>
  <path d="M 100 50 L 130 100 L 100 150 L 70 100 Z" fill="url(#grad)"/>
</svg>
```

### 3. Create Multiple Variations
Generate 3-5 concepts by varying the prompt:
- Change style: minimalist → bold → geometric → organic
- Change icon type: abstract → symbol → lettermark
- Vary layout: vertical → horizontal → square

**Show the user each concept:** save the files under
`/root/.openclaw/workspace/media/` (for example
`/root/.openclaw/workspace/media/logo_concept_1.png`) and put one line
`MEDIA:<absolute path>` per file in your reply, on its own line and not in a
code block. The `view_image` (View Image) tool shows a file only to you, never
to the user.

### 4. Resize for Multiple Uses
Common logo sizes:
- **Favicon:** 32x32 (PNG)
- **Social profile:** 400x400 (PNG)
- **Website header:** 200x80 (PNG or SVG)
- **App icon:** 512x512 (PNG)
- **Print:** 300 DPI (PDF)

Use Python Pillow to resize:
```bash
pip install Pillow -q
python3 -c "
from PIL import Image
img = Image.open('logo_concept_1.png')
img.resize((32, 32)).save('favicon.png')
img.resize((512, 512)).save('app-icon.png')
img.resize((400, 400)).save('social-profile.png')
"
```

### 5. Save to Google Drive
**Depends on:** `google-workspace` skill

Upload all logo versions to Drive:
```bash
gws drive +upload --file logo_concept_1.png --folder "[folder_id]"
gws drive +upload --file logo_concept_1.svg --folder "[folder_id]"
```

### 6. Create Brand Kit Document
**Depends on:** `google-workspace` skill

Write a brand guidelines document and save as Google Doc:
```bash
gws docs +create --title "Brand Guidelines" --content "[markdown content]"
```

Include: logo files, color palette (hex + RGB), clear space rules, usage guidelines.

## Cost

| Provider | Cost per image | Notes |
|---|---|---|
| OpenAI DALL-E 3 | ~$0.04 (1024x1024 HD) | High quality, photorealistic capable |
| Gemini Imagen | ~$0.025-0.04 | Cheaper, supports editing existing images |
| SVG code | Free | You write it, best for geometric/minimal |
| Google Drive upload | Free | Via `google-workspace` skill |

**Typical project:** $0.15-0.40 for 3-5 AI-generated concepts + SVG refinements.

## Example Prompt Template

```
Professional logo for [BRAND_NAME], a [INDUSTRY] company. [STYLE] style logo.
Primary colors: [COLOR1], [COLOR2].
Icon type: [ABSTRACT/SYMBOL/WORDMARK].
Clean, modern design suitable for web and print.
Transparent background, vector-ready appearance.
No text, icon-only.
```

## Pro Tips

- Start with 3-5 diverse concepts (different styles) rather than subtle variations
- Always include "transparent background" in prompts for web use
- SVG logos are infinitely scalable — provide both PNG (quick use) and SVG (print/design)
- Test logos at small sizes (favicon, social icon) to ensure clarity
- Create both full-color and single-color (monochrome) versions
- If using Gemini, leverage its **image editing** to refine logos (remove bg, adjust colors)
- Get user feedback before spending time on detailed refinements
- Trademark check: suggest user verify brand name isn't trademarked before finalization
