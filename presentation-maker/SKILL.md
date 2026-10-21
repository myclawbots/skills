---
name: presentation_maker
description: Generate professional slide decks from custom inputs or AI-researched content. Create .pptx files and save to Google Drive.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [slides, pptx, presentations, google-drive]
suggested_template: general_assistant
---

# Presentation Maker

## Overview
Generate professional slide decks from custom inputs or AI-researched content. Create .pptx files and save to Google Drive.

**You write the presentation logic yourself** using python-pptx library. This skill teaches the approach and code patterns.

## Dependencies

This skill requires the following:

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | **Yes** — for saving presentations to Google Drive |
| `python-pptx` library | **Yes** — for generating PPTX files (install: `pip install python-pptx`) |
| `gemini-api` skill | Conditional — needed **only if generating AI slide images** (via Gemini Imagen) |
| `$OPENAI_KEY` (stand-in, use with `vault-curl`) | Conditional — needed **only if generating AI slide images** (via DALL-E 3) |
| `$GEMINI_KEY` (stand-in, use with `vault-curl`) | Conditional — needed **only if generating AI slide images** (via Gemini Imagen) |

> **Before starting, check:**
> 1. Is `google-workspace` skill installed? Run `gws --version` to verify.
> 2. Is `python-pptx` installed? Run `pip install python-pptx`.
> 3. Are API keys available **only if the user wants AI-generated slide images** (charts, illustrations). Plain text slides don't require image generation.
>    Which image keys do you have? `[ -n "$OPENAI_KEY" ] && echo openai; [ -n "$GEMINI_KEY" ] && echo gemini`. These are stand-ins (`mcb_sec_…`) for the user's keys, not the keys: they only work through `vault-curl`. A key added after you started is not in your env yet: run `vault-curl --secrets` and use an entry's `surrogate` string in place of `$OPENAI_KEY` / `$GEMINI_KEY`. Agents not yet moved to the vault may instead have real keys in the `OPENAI_API_KEY` / `GEMINI_API_KEY` variables: use those with plain `curl`, in the same header. Never print a key or stand-in, and never use OpenClaw's built-in secrets tool (these keys are not there). Missing keys: ask the user to add them in MyClawBots → Settings → Integrations; never ask them to paste a key into chat.

## Provider Selection — ASK ONLY IF USER WANTS AI IMAGES

If the user asks for **AI-generated slide illustrations or charts**, ask which provider to use:

> "For slide images, I can generate illustrations using:
> 1. **OpenAI DALL-E 3** — high quality, ~$0.04/image
> 2. **Google Gemini Imagen** — cheaper (~$0.025/image), also supports editing
> 3. **No AI images** — I'll create text-only slides with python-pptx (free)
>
> Which would you prefer?"

If the user only wants text and bullet points, **no image generation provider is needed** — proceed with plain slides.

## Capabilities
- Generate presentations from outline or topic
- Create slide layouts: title, content, two-column, image
- Add speaker notes to every slide
- Use custom fonts and colors
- Export as PPTX
- Save to Google Drive
- Adapt for any audience (investor, client, team, public)

## Step-by-Step Workflow

### 1. Gather Requirements
- Presentation topic or title
- Target audience and context (investor pitch, client update, team training, etc.)
- Estimated slide count (rule of thumb: 1 min per slide)
- Style preference (corporate, creative, minimal, pitch deck)
- Brand colors (optional)

### 2. Create Outline
Structure the presentation logically:
```
1. Title Slide (topic + date)
2. Agenda / Overview
3-N. Content slides (2-3 minutes each)
N+1. Key Takeaways
N+2. Call to Action / Q&A
```

Example outline for "The Future of Remote Work":
- Title
- Current State of Remote Work
- Key Benefits (productivity, flexibility, cost savings)
- Challenges (collaboration, isolation, security)
- Technology Trends (async tools, AI, infrastructure)
- Future Predictions
- Takeaways & Action Items

### 3. Write Content for Each Slide
Keep each slide concise:
- **Title:** 5-8 words, clear topic
- **Content:** Max 5 bullet points, 1 sentence each
- **Speaker Notes:** 2-3 sentences providing context/talking points

### 4. Generate PPTX with Python

Install python-pptx if not present:
```bash
pip install python-pptx
```

Write a Python script to build the deck:
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Create presentation
prs = Presentation()
prs.slide_width = Inches(10)
prs.slide_height = Inches(7.5)

# Define color scheme
PRIMARY_COLOR = RGBColor(0, 102, 204)  # Blue
SECONDARY_COLOR = RGBColor(255, 107, 53)  # Orange
TEXT_COLOR = RGBColor(50, 50, 50)  # Dark gray

# Slide 1: Title Slide
slide1 = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout
background = slide1.background
fill = background.fill
fill.solid()
fill.fore_color.rgb = PRIMARY_COLOR

title_box = slide1.shapes.add_textbox(Inches(1), Inches(2.5), Inches(8), Inches(2))
title_frame = title_box.text_frame
title_frame.text = "The Future of Remote Work"
title_frame.paragraphs[0].font.size = Pt(54)
title_frame.paragraphs[0].font.bold = True
title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

date_box = slide1.shapes.add_textbox(Inches(1), Inches(5), Inches(8), Inches(1))
date_frame = date_box.text_frame
date_frame.text = "March 29, 2026"
date_frame.paragraphs[0].font.size = Pt(24)
date_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

# Slide 2: Content Slide
slide2 = prs.slides.add_slide(prs.slide_layouts[6])
bg2 = slide2.background
fill2 = bg2.fill
fill2.solid()
fill2.fore_color.rgb = RGBColor(255, 255, 255)

# Title
title_box2 = slide2.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(0.8))
title_frame2 = title_box2.text_frame
title_frame2.text = "Current State of Remote Work"
title_frame2.paragraphs[0].font.size = Pt(44)
title_frame2.paragraphs[0].font.bold = True
title_frame2.paragraphs[0].font.color.rgb = PRIMARY_COLOR

# Content bullets
content_box = slide2.shapes.add_textbox(Inches(1), Inches(1.8), Inches(8), Inches(4.5))
text_frame = content_box.text_frame
text_frame.word_wrap = True

bullets = [
    "48% of workforce now works hybrid or fully remote",
    "Leading companies: Google, Microsoft, Amazon investing in remote infrastructure",
    "Global market for collaboration tools: $42B+ annually",
    "Emerging norms: async-first, outcome-based evaluation, flexible schedules"
]

for i, bullet in enumerate(bullets):
    if i == 0:
        p = text_frame.paragraphs[0]
    else:
        p = text_frame.add_paragraph()
    p.text = bullet
    p.level = 0
    p.font.size = Pt(18)
    p.font.color.rgb = TEXT_COLOR
    p.space_before = Pt(6)
    p.space_after = Pt(6)

# Add speaker notes
notes_slide = slide2.notes_slide
text_frame_notes = notes_slide.notes_text_frame
text_frame_notes.text = "Emphasize the rapid adoption. Reference recent surveys. Mention that flexibility is now table stakes for talent retention."

# Save presentation
prs.save('presentation.pptx')
print("✓ Presentation created: presentation.pptx")
```

Run the script:
```bash
python generate_presentation.py
```

### 5. Upload to Google Drive

Use google-workspace skill:
```bash
gws drive +upload --file presentation.pptx --folder "[folder_id]"
```

Or create a Google Slides version by uploading the PPTX to Google Drive and converting it.

### 6. Add Images (Optional)

To add images to slides:
```python
from pptx.util import Inches

slide = prs.slides.add_slide(prs.slide_layouts[6])
left = Inches(1)
top = Inches(2)
pic = slide.shapes.add_picture('chart.png', left, top, width=Inches(8))
```

For charts, generate via DALL-E, Gemini, or matplotlib, then embed.

**Option A: Generate charts with DALL-E**
```bash
vault-curl -sS https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "Professional bar chart showing quarterly revenue growth: Q1 $2M, Q2 $2.5M, Q3 $3M, Q4 $3.5M. Clean design, blue bars, white background, no text labels.",
    "size": "1024x1024",
    "quality": "hd",
    "n": 1
  }' | jq -r '.data[0].url'
```

**Option B: Generate charts with Gemini**
Easiest, and always works: the `gemini-image` skill (`claw install gemini-image` once). It finds the key itself and calls Gemini through the vault:
```bash
python3 /root/.openclaw/skills/gemini-image/scripts/gemini_image.py \
  --prompt "Professional bar chart showing quarterly revenue growth. Clean design, blue bars, white background." \
  --out /root/.openclaw/workspace/media/chart.png
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
    contents="Professional bar chart showing quarterly revenue growth: Q1 $2M, Q2 $2.5M, Q3 $3M, Q4 $3.5M. Clean design, blue bars, white background.",
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"],
    )
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("chart.png", "wb") as f:
            f.write(base64.b64decode(part.inline_data.data))
```

## Common Slide Layouts

### Title Slide
```
[Logo/Background]
          PRESENTATION TITLE
        Subtitle or Presenter Name
                Date
```

### Content Slide (Bullets)
```
SLIDE TITLE
• Bullet point 1
• Bullet point 2
• Bullet point 3
• Bullet point 4
```

### Two-Column Slide
```
TITLE
[Left Content]  |  [Right Content]
```

### Image + Caption
```
SLIDE TITLE
[Large Image]
Short caption explaining the image
```

## Cost

- **python-pptx library:** Free (open source)
- **DALL-E for slide images:** ~$0.04-0.08 per image (optional)
- **Google Drive storage:** Free (15GB)

**Total cost per presentation:** $0 (base) + $0.20-0.40 (if adding AI-generated images).

## Pro Tips

- **1 minute per slide rule:** 10-minute talk = 10 slides max (including title/closing)
- **Text minimalism:** Slides should support your talking points, not repeat them
- **Speaker notes are essential:** Add 2-3 sentences per slide with context, transitions, key stats
- **Visual hierarchy:** Title largest, body text smaller, emphasize key numbers/words
- **Consistent spacing:** Use the same padding, font sizes, and colors throughout
- **Transitions:** Keep them minimal (fade is good, spinning boxes are not)
- **Practice the talk:** Read speaker notes aloud to catch awkward phrasing
- **Mobile view:** Test how slides look on phone (for sharing/remote attendance)
