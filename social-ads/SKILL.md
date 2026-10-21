---
name: social_ads
description: Generate platform-ready image ads with multiple variations for Instagram, Facebook, LinkedIn, and more. Create and post directly via connected social accounts.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [ads, creatives, instagram, facebook, linkedin]
suggested_template: marketing_strategist
---

# Social Ads Generator

## Overview
Generate platform-ready image ads with multiple variations for Instagram, Facebook, LinkedIn, and more. Create and post directly via social-manager skill.

**You generate the ads yourself** using an AI image provider for images, Python Pillow for text overlays, and social-manager skill for posting.

## Dependencies

This skill requires the following:

| Dependency | Required? | Why |
|---|---|---|
| `social-manager` skill | **Yes** — for posting ads directly to social platforms |
| `google-workspace` skill | Optional — for saving ad assets to Google Drive |
| `gemini-api` skill | **If user chooses Gemini** — for image generation via Gemini Imagen |
| `$GEMINI_KEY` (stand-in, use with `vault-curl`) | **If user chooses Gemini** — for image generation via Gemini Imagen |
| `$OPENAI_KEY` (stand-in, use with `vault-curl`) | **If user chooses OpenAI** — for image generation via DALL-E 3 |
| `Pillow` Python library | **Yes** — for adding text overlays, resizing, and image processing |

> **Before starting, check:**
> 1. Is `social-manager` skill installed and social accounts connected in the dashboard?
> 2. Which image keys do you have? `[ -n "$OPENAI_KEY" ] && echo openai; [ -n "$GEMINI_KEY" ] && echo gemini`. These are stand-ins (`mcb_sec_…`) for the user's keys, not the keys: they only work through `vault-curl`. A key added after you started is not in your env yet: run `vault-curl --secrets` and use an entry's `surrogate` string in place of `$OPENAI_KEY` / `$GEMINI_KEY`. Agents not yet moved to the vault may instead have real keys in the `OPENAI_API_KEY` / `GEMINI_API_KEY` variables: use those with plain `curl`, in the same header. Never print a key or stand-in, and never use OpenClaw's built-in secrets tool (these keys are not there). Missing keys: ask the user to add them in MyClawBots → Settings → Integrations; never ask them to paste a key into chat.
> 3. Is Pillow installed? Run `pip install Pillow` if needed.

## Provider Selection — ASK THE USER

Before generating any ad images, **you must ask the user which AI provider to use**:

> "I can generate ad images using:
> 1. **OpenAI DALL-E 3** — high quality, ~$0.04/image, great for photorealistic product shots
> 2. **Google Gemini Imagen** — cheaper (~$0.025/image), supports image editing
> 3. **Use existing image** — upload your own and I'll add text overlays with Pillow
>
> Which would you prefer?"

If only one key is available, inform the user and use that one. If neither key is set, default to offering existing image upload (free).

## Capabilities
- Generate ad images via DALL-E 3 API
- Add text overlays with Python Pillow
- Create multiple variations for A/B testing
- Resize for platform specs (IG, FB, LinkedIn, Twitter)
- Post directly via social-manager skill
- Track performance basics

## Step-by-Step Workflow

### 1. Gather Ad Brief
- Product/service name and description
- Target audience
- Key benefit/value proposition
- CTA (Call-to-Action): Shop Now, Learn More, Sign Up, Try Free
- Brand colors (primary, secondary)
- Budget and timeline

### 2. Generate Ad Image

#### Option A: OpenAI DALL-E 3 (if user chose OpenAI)
```bash
vault-curl -sS https://api.openai.com/v1/images/generations \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dall-e-3",
    "prompt": "Professional e-commerce ad for blue light blocking glasses. Product shot with lifestyle background. Modern, clean aesthetic. Person wearing glasses at computer. Bright, well-lit studio photography. Background: soft blurred office environment. Colors: blue (#1a73e8) and white accents. No text, professional product photo style.",
    "size": "1024x1024",
    "quality": "hd",
    "n": 1
  }' | jq -r '.data[0].url'
```

Save the image:
```bash
curl -s [IMAGE_URL] -o ad_image_1.png
```

#### Option B: Google Gemini Imagen (if user chose Gemini)
Easiest, and always works: the `gemini-image` skill (`claw install gemini-image` once). It finds the key itself and calls Gemini through the vault:
```bash
python3 /root/.openclaw/skills/gemini-image/scripts/gemini_image.py \
  --prompt "Professional e-commerce ad for blue light blocking glasses. Lifestyle product shot, no text." \
  --out /root/.openclaw/workspace/media/ad_image_1.png
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
    contents="Professional e-commerce ad for blue light blocking glasses. Product shot with lifestyle background. Modern, clean aesthetic. Person wearing glasses at computer. Bright, well-lit studio photography. Background: soft blurred office environment. Colors: blue (#1a73e8) and white accents. No text, professional product photo style.",
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"],
    )
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("ad_image_1.png", "wb") as f:
            f.write(base64.b64decode(part.inline_data.data))
        print("Saved ad_image_1.png")
```

### 3. Add Text Overlay with Python Pillow

Install Pillow:
```bash
pip install Pillow
```

Python script to add text:
```python
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Open base image
img = Image.open('ad_image_1.png')
width, height = img.size

# Create drawing context
draw = ImageDraw.Draw(img)

# Load font (use system font)
try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
    body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    cta_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
except:
    title_font = ImageFont.load_default()
    body_font = ImageFont.load_default()
    cta_font = ImageFont.load_default()

# Add semi-transparent overlay for text readability
overlay = Image.new('RGBA', img.size, (0, 0, 0, 150))
img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
draw = ImageDraw.Draw(img)

# Add headline
headline = "Protect Your Eyes\nBoost Your Focus"
text_bbox = draw.textbbox((0, 0), headline, font=title_font)
text_width = text_bbox[2] - text_bbox[0]
text_x = (width - text_width) // 2
draw.text((text_x, 80), headline, fill=(255, 255, 255), font=title_font)

# Add description
description = "Premium blue light blocking lenses"
text_bbox = draw.textbbox((0, 0), description, font=body_font)
text_width = text_bbox[2] - text_bbox[0]
text_x = (width - text_width) // 2
draw.text((text_x, 280), description, fill=(240, 240, 240), font=body_font)

# Add CTA button background
button_y = 450
button_height = 80
draw.rectangle([100, button_y, width-100, button_y+button_height], fill=(26, 115, 232))

# Add CTA text
cta_text = "SHOP NOW"
text_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
text_width = text_bbox[2] - text_bbox[0]
text_x = (width - text_width) // 2
draw.text((text_x, button_y+15), cta_text, fill=(255, 255, 255), font=cta_font)

# Save
img.save('ad_image_1_with_text.png', quality=95)
print('✓ Ad image created: ad_image_1_with_text.png')
```

Run it:
```bash
python add_ad_text.py
```

### 4. Create Variations

Generate 3-5 variations with different:
- **Copy:** Different headlines, benefits, angles
- **Colors:** Different primary colors
- **Layout:** Text position, button style
- **Style:** Minimalist, bold, lifestyle, product-focused

For each variation, repeat step 2-3 with modified DALL-E prompt or Pillow overlay.

### 5. Resize for Each Platform

Platform specs:
- **Instagram Feed:** 1080x1350 (4:5)
- **Instagram Story:** 1080x1920 (9:16)
- **Facebook Feed:** 1200x628 (1.91:1)
- **LinkedIn:** 1200x627 (1.91:1)
- **Twitter:** 1600x900 (16:9)
- **TikTok:** 1080x1920 (9:16)

Use ImageMagick or PIL to resize:
```python
from PIL import Image

def resize_for_platform(input_file, platform):
    img = Image.open(input_file)

    specs = {
        'instagram_feed': (1080, 1350),
        'instagram_story': (1080, 1920),
        'facebook': (1200, 628),
        'linkedin': (1200, 627),
        'twitter': (1600, 900),
    }

    width, height = specs[platform]
    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
    img_resized.save(f'ad_{platform}.png', quality=95)
    print(f'✓ {platform}: ad_{platform}.png')

# Resize for all platforms
for platform in ['instagram_feed', 'instagram_story', 'facebook', 'linkedin', 'twitter']:
    resize_for_platform('ad_image_1_with_text.png', platform)
```

### 6. Post to Social Media

Use social-manager skill (already installed):
```bash
# Instagram
social-manager +post \
  --platform instagram \
  --image ad_instagram_feed.png \
  --caption "Protect your eyes, boost your focus 👀 Premium blue light blocking glasses. Shop now with code SAVE10 #BlueLight #EyeHealth"

# Facebook
social-manager +post \
  --platform facebook \
  --image ad_facebook.png \
  --caption "Introducing our premium blue light glasses. Reduce eye strain by 85%. Shop now →"

# LinkedIn
social-manager +post \
  --platform linkedin \
  --image ad_linkedin.png \
  --caption "How I protect my eyes during long work sessions: premium blue light blocking glasses. If you spend 8+ hours at a screen, these are worth trying. Link in bio."

# Twitter
social-manager +post \
  --platform twitter \
  --image ad_twitter.png \
  --caption "Spending all day in front of screens? Protect your eyes with our premium blue light glasses. 85% less eye strain. Shop now 🛒"
```

### 7. Monitor Performance

Track metrics manually or via platform analytics:
- **Click-through rate (CTR):** % of people who clicked
- **Conversion rate:** % of clicks that became sales
- **Cost per result:** Total spend / conversions
- **Engagement:** Likes, comments, shares

## Platform Specifications & Best Practices

### Instagram Feed (1080x1350)
- **Best times:** 11am, 7-9pm EST
- **Max caption:** 2,200 chars
- **Hashtags:** 5-30 relevant tags
- **Copy style:** Aspirational, lifestyle-focused

### Facebook (1200x628)
- **Best times:** 1-3pm EST, 7-9pm EST
- **Max caption:** 125 chars (visible before "more")
- **Copy style:** Benefit-driven, pain-point focused
- **CTA button options:** Learn More, Shop Now, Sign Up

### LinkedIn (1200x627)
- **Best times:** 8-10am EST, Tuesday-Thursday
- **Max caption:** 3,000 chars
- **Copy style:** Professional, B2B, thought leadership
- **Avoid:** Aggressive sales language

### Twitter (1600x900)
- **Best times:** 9am, 5pm EST
- **Max text:** 280 chars (including link)
- **Copy style:** Conversational, quick value prop
- **Engagement:** Reply to comments immediately

## Cost

- **DALL-E 3 image generation:** ~$0.04-0.08 per 1024x1024 image (HD)
- **Pillow image processing:** Free (open source)
- **Social media posting:** Free (via social-manager skill)

**Total cost per campaign:** $0.20-0.50 for 3-5 concept images + variations.

## Pro Tips

- **A/B test variations:** Always test 3-5 versions to find what resonates
- **Use contrasting colors:** Make CTA button pop against ad background
- **Clear value prop:** Lead with the biggest benefit, not features
- **Mobile-first:** Test how ads look on phone (narrow screens)
- **People + product:** Lifestyle ads (people using product) outperform product-only shots
- **Test different CTAs:** "Shop Now" vs "Learn More" vs "Try Free" can have big impact
- **Posting schedule:** Post when audience is most active (platform-specific)
- **Negative space:** Don't overcrowd the ad; whitespace draws attention to key elements
- **Font legibility:** Test on small screens; use bold, clean fonts
- **Compliance:** Follow platform ad policies (no misleading claims, clear disclaimers)
