---
name: social-publisher
description: >
  Publish single images or multi-image carousels to Instagram, Facebook,
  Threads, LinkedIn and (when a Pinterest account is connected) Pinterest through the MyClawBots Social API proxy. Python stdlib
  only. Takes hosted image URLs (e.g. from cloudinary-uploader) plus a caption,
  handles Instagram's container/FINISHED polling, and posts.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [instagram, facebook, carousel, publishing]
suggested_template: content_creator
metadata:
  openclaw:
    emoji: "📣"
---

# Social Publisher

Posts to Instagram, Facebook, Threads, LinkedIn and Pinterest via the platform's Social
API proxy — your connected social accounts, the platform's container-polling
logic, no platform tokens on this machine.

Pick the target with `--platform` (`instagram` default, `facebook`, `threads`,
`linkedin`, `pinterest`). Per-platform limits worth knowing:

- **instagram** — media is required; text-only posts are rejected
- **linkedin** — text or images only, no video. Posts go to the person's profile;
  when a LinkedIn Page account is connected, `--account-type page` posts as the company
- **threads** — 500 character limit
- **pinterest** (only when a Pinterest account is connected) — an image is required,
  JPEG or PNG only, **no video** through this script (video Pins, where enabled, and
  editing Pins go through the MCP `post_to_social` / `edit_post` tools). The caption is the Pin description (≤800 characters).
  `--board-id` picks the board (ids are on the account's `boards` in
  `list_social_accounts`; ask the user when there is more than one); optional
  `--title`, `--link`, `--alt-text`, and `--ai-disclosure AI_MODIFIED` for an
  AI-generated image. Show the user each Pin and get a yes for **that** Pin — no bulk
  pinning. For now a Pin is visible only to the user: never call it public, and
  never mention Pinterest access levels or approvals. With no boards, use the MCP
  `post_to_social` flow (it can create one board
  after the user agrees); this script does not create boards.
- **carousels** — 2–10 images, except **Pinterest: 2–5**

## Requirements

Connected accounts in the dashboard (Settings → Social).
The proxy connection is preconfigured on this agent:

- Proxy: `${PROXY_URL}`
- Auth: uses this agent's `PROXY_API_KEY` (already in the environment)

## Run

```bash
python3 /root/.openclaw/skills/social-publisher/scripts/post_social.py \
  --caption "Your caption here" \
  --images https://res.cloudinary.com/.../cover.jpg https://.../slide2.jpg
# or straight from a manifest produced by carousel-generator + cloudinary-uploader:
python3 .../post_social.py --manifest path/to/manifest.json
# preview without publishing:
python3 .../post_social.py --manifest m.json --dry-run
# also cross-post to Facebook:
python3 .../post_social.py --manifest m.json --also-facebook
# post the same hosted images to another platform — no re-upload needed:
python3 .../post_social.py --manifest m.json --platform threads
```

Hosted URLs are reusable: to publish one carousel to several platforms, run this
script once per platform with the same URLs rather than re-hosting the images.

## Pipeline composition

The three skills chain via the manifest:

1. **carousel-generator** → renders PNGs + `manifest.json`
2. **cloudinary-uploader** → adds `hosted_urls` to the manifest
3. **social-publisher** → posts the hosted URLs with your caption

Each stage also works standalone with explicit arguments.
