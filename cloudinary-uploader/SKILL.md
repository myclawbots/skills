---
name: cloudinary-uploader
description: >
  Upload local images to Cloudinary via signed upload (no SDK — Python
  stdlib only) and get back public HTTPS URLs. Takes a manifest.json from
  carousel-generator or any list of image paths; emits an updated manifest
  with hosted URLs for social-publisher.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: social
tags: [cloudinary, images, hosting, upload]
suggested_template: content_creator
metadata:
  openclaw:
    emoji: "☁️"
    requires:
      env:
        - CLOUDINARY_CLOUD_NAME
        - CLOUDINARY_API_KEY
        - CLOUDINARY_API_SECRET
---

# Cloudinary Uploader

Signed uploads straight from the agent machine — Python stdlib only (hashlib
signature, urllib multipart), no pip dependencies.

## Setup

Set the Cloudinary credentials (from your Cloudinary dashboard) as agent
environment values:

- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

## Run

```bash
python3 /root/.openclaw/skills/cloudinary-uploader/scripts/upload_cloudinary.py \
  path/to/manifest.json          # from carousel-generator
# or individual files:
python3 .../upload_cloudinary.py cover.png slide2.png slide3.png follow.png
```

## Output

Public `https://res.cloudinary.com/...` URLs, written back into the manifest
(`hosted_urls`) when a manifest was given. Those URLs are exactly what
**social-publisher** (and the platform's `/social/post` API) accept for
Instagram/Facebook publishing — Instagram requires publicly reachable HTTPS
image URLs, which is why this hop exists.
