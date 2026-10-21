# Instagram Media Publishing Workflow

Instagram requires media on every post. There is no text-only Instagram post:
the API rejects it. So the writer skills in this bundle produce the **caption,
hook, hashtags, and slide or shot plan**, and the **media comes from the user or
from `carousel-generator`**. Publishing is always a media flow.

Everything here runs on the **`myclawbots` MCP server**, which is pre-configured
on this machine. There is no third-party posting service and no extra API key.

## Contents

- The flow
- Container rules (what the media list becomes)
- Media limits
- Scheduling (and why Instagram cannot be scheduled)
- When there is no media
- When an upload fails

## The flow

```
1. list_social_accounts
   -> the Instagram account_id. Call this FIRST; everything below needs it.

2. create_upload_url            (per file, in slide order)
   -> { upload_url, public_url }
   curl -X PUT --data-binary @slide1.jpg -H "Content-Type: image/jpeg" "<upload_url>"
   -> the public_url is now live

3. post_to_social
   { platform: "instagram", account_id, content, media_urls: [url1, ...] }  # carousel
   { platform: "instagram", account_id, content, media_url: url }           # single image or video
```

**Both halves of step 2 are required.** `public_url` returns a 404 until the PUT
lands. Posting it early hands Instagram a dead URL, and Instagram reports that
as its own download failure — which reads like a domain-verification or
networking problem and is not one. Quote the error rather than interpreting it.

**Never combine `media_url` with `media_urls`.** One or the other.

### The small-image shortcut

If the image exists only in this conversation and not on disk, skip
`create_upload_url` and use `upload_media` with base64. One or two small files
at most; beyond that the staged-URL path is the right one.

### Images the user attached in chat

They are already on this machine — the gateway writes them under `/tmp`. Never
ask the user for a file path:

```bash
ls -t /tmp/*.png /tmp/*.jpg /tmp/*.jpeg /tmp/*.webp 2>/dev/null | head -5
```

### Stage once, reuse

A staged `public_url` works for every platform. If the user is cross-posting,
stage the file once and pass the same URL to each `post_to_social` call. Never
re-upload per platform.

## Container rules (what the media list becomes)

| Media supplied | Becomes | Notes |
|---|---|---|
| 1 image (JPEG/PNG/WebP) | a single photo post | pass as `media_url` |
| 2-10 images | a carousel, in list order | `media_urls`, order is the slide order |
| 1 video (MP4/MOV) | **always a Reel** | Instagram has no non-Reel video via the API |
| images + video together | a mixed carousel — **allowed on Instagram** | item types are auto-detected; do not pass `media_type` with `media_urls` |

Mixed carousels are an Instagram-only capability in our stack: Facebook and
LinkedIn reject them. If the same media is going to several platforms, split the
post rather than dropping the video.

## Media limits

| Item | Limit |
|---|---|
| Image formats | JPEG, PNG, WebP, GIF |
| Video formats | MP4, QuickTime |
| Image max size | 12 MB (via `create_upload_url`) |
| Video max size | 300 MB |
| Carousel items | 2-10 (API); the native app allows 20 |
| Reel duration | up to 15 min; 9:16 reads best |
| Aspect ratio | 4:5 portrait to 1.91:1 landscape; 4:5 fills the feed best |
| Caption | 2,200 chars (first ~125 visible) |
| Staged URL lifetime | ~2 hours |
| Account type | Business or Creator (personal is not supported) |

**A staged URL that has expired cannot be retried.** Post promptly after
staging. If publishing fails because the file is gone, re-stage and post
immediately — never offer to retry the same post later.

## Scheduling: Instagram cannot be scheduled

`scheduled_time` on `post_to_social` is **Facebook-only** (ISO 8601 with a timezone,
15 minutes to 29 days out; sent for Instagram it is refused, not ignored). An Instagram post publishes the moment you call
`post_to_social`.

So when `ig-content-planner` puts a post at Tuesday 11:30 AM, that is a time for
a human or a cron to act on, not something the API will hold. Hand the user the
time and post at it. Never tell the user an Instagram post is scheduled.

## When there is no media

Every writing skill still finishes its job: it returns the approved caption as a
copy-paste block plus a reminder that Instagram needs the image or video
attached. Instagram will not take the post without it, so the reminder is not
optional.

Before falling back to copy-paste, offer the two first-party paths:

- **`carousel-generator`** renders 2-10 branded slides from the plan
  (`bash run.sh deck.json out --theme neon --platform instagram-portrait`), and
  the PNGs go straight into `create_upload_url`.
- **`gemini-api`** or DALL-E generates a single feed image. Ask which provider
  first — it spends the user's credits. See
  `../sub-skills/ig-humanizer/sub-skills/illustration.md`.

## When an upload fails

There is no draft object to clean up — `post_to_social` either publishes or it
does not, so a failed PUT leaves nothing behind. Re-stage the file and post
again.

If a post published and the user wants it gone, `delete_post` removes it.
**Confirm first: it is irreversible.**

A successful post may carry a `notice` field. Relay it verbatim, and never
describe a post as live and public without positive evidence that it is.
