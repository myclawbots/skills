---
name: ecommerce_photos
description: Turn raw product photos into lifestyle scenes, clean white-background shots and platform-sized versions with Gemini, then hand them to social publishing.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [product-photos, ecommerce, gemini, images]
suggested_template: content_creator
---

# eCommerce Photos

Turns a seller's raw product photo into new images of the **same product**:
lifestyle scenes, clean studio shots, flat lays, seasonal variations. It uses
Gemini image editing with the user's own Gemini API key, through one script
that needs nothing installed.

## Before you start

1. **The key.** You don't need to check it: the script finds the user's Gemini
   key itself — a key from Settings → Integrations, or one saved in
   **Settings → Secrets** (including one added after this machine started).
   Never use OpenClaw's built-in secrets tool to look for it: vault keys are
   never stored there, so it always looks empty. Only if the script says
   `No Gemini key found`, tell the user: "Add a Google Gemini API key in
   **Settings → Secrets** (free to create at aistudio.google.com/apikey)."
   Never ask them to paste a key into chat.
2. **Find the photo.** If the message has an `[attachment note: …]` with
   `curl` commands, run them: they save the attached photos as files. For a
   photo pasted straight into the chat, look for OpenClaw's copy, newest first:
   `ls -t /root/.openclaw/media/inbound/ | head -5`. If there is none, the
   photo is only visible to you, not on disk: ask the user for a link to it.
   If the user gave a URL, download it with `curl -L -o`.

## Make an image

```bash
mkdir -p /root/.openclaw/workspace/media
python3 /root/.openclaw/skills/ecommerce-photos/scripts/edit_photo.py \
  --input /tmp/upload-1.jpg \
  --prompt "Worn by a woman on a ranch at golden hour, warm light, shallow depth of field" \
  --aspect 1:1 \
  --out /root/.openclaw/workspace/media/hat-ranch-1x1.png
```

- `--input` can be repeated for extra angles of the same product.
- `--aspect`: `1:1` Instagram/Facebook feed, `4:5` Instagram portrait, `2:3`
  Pinterest, `9:16` TikTok/Reels/Stories, `16:9` YouTube and banners.
- Always write `--out` under `/root/.openclaw/workspace/media/`: files outside
  the workspace may not be delivered to the chat.
- Prints JSON: `{"model": "...", "files": ["/root/.openclaw/workspace/media/..."], "note": "..."}`.
- Exit code 1 means bad input or no key; exit code 2 means Gemini refused or
  returned no image; the message says why. For a refusal, rephrase the scene
  (for example, drop a real person's name) and retry once.
- The script already tells Gemini to keep the product unchanged. Put only the
  scene in `--prompt`.

Run one command per image. For three scenes in two sizes, that is six runs;
name the files so the user can refer to them (`hat-ranch-1x1.png`,
`hat-ranch-9x16.png`).

## Scene ideas by style

| Style | Prompt starter |
|---|---|
| Clean white | "On a seamless pure white background with a soft shadow, centered, studio lighting" |
| Lifestyle | "In use by a person in [setting], natural light, candid" |
| Flat lay | "Overhead flat lay on [surface] with [2–3 props that fit the brand]" |
| Seasonal | "In a [holiday/season] setting with [props], cozy, warm tones" |
| Outdoor | "Outdoors at [place] at golden hour, shallow depth of field" |

## Show before you use

1. **Check every image yourself first.** Models sometimes change a logo, text
   or small detail. If the product no longer matches the original, regenerate
   it; don't ship it.
2. **Show every image** to the user before doing anything else with it: one
   line `MEDIA:<path>` per file in your reply, on its own line and not in a
   code block — for example `MEDIA:/root/.openclaw/workspace/media/hat-ranch-1x1.png`.
   The `view_image` (View Image) tool shows a file only to you, never to the
   user: use it to check an image, never to deliver one.
3. Accept edits in plain words ("redo 2 with softer light, no coffee cup")
   and rerun only that image.

## Publishing

This skill makes images; it does not post them. To publish, use the
MyClawBots social tools you already have: stage each file with
`create_upload_url` (PUT the bytes, get a public URL), then `post_to_social`.
Always show the user the final captions and where each image goes, and get an
explicit yes before posting.

## Rules

- Never alter the product itself: no new colors, logos, text or features.
- Don't put real, identifiable people in scenes, and don't use other brands'
  logos.
- Gemini bills image generation to the user's key, usually a few cents per
  image. For a large batch (more than 20 images), say so before starting.
