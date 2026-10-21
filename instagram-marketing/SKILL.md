---
name: instagram_marketing
description: Plan, draft, audit, and publish Instagram content. Nine focused sub-skills — write a caption with a first-125-char hook, plan a slide-by-slide carousel, reverse-engineer the hook from a post that worked, size hashtags the 2026 way, strip AI tells, audit the profile, plan a week, repurpose cross-platform content, and read your own account's real numbers. Publishes through the myclawbots MCP tools; no third-party posting service.
author:
  name: Sergey Bulaev
  url: https://github.com/sergebulaev/instagram-skills
license: MIT
category: social
tags: [instagram, captions, hashtags, carousel, audit]
suggested_template: content_creator
metadata:
  openclaw:
    emoji: "✍️"
---

# Instagram Marketing

A bundle of 9 focused Instagram skills. Each one is single-purpose, follows the
draft → approval → publish pattern, and publishes through the **myclawbots MCP
tools** — the same connected Instagram account the dashboard manages. No
third-party posting service, no extra API key, no separate signup.

## Routing — pick the sub-skill

Each sub-skill lives at `scripts/sub-skills/<name>/SKILL.md`. Read the one you
need; do not load all nine.

| The user wants | Sub-skill |
|---|---|
| A caption (hook in the first 125 chars, body, one CTA) | `ig-caption-writer` |
| A carousel planned slide by slide | `ig-carousel-planner` |
| The hook reverse-engineered from a post they admire | `ig-hook-extractor` |
| Hashtags sized the 2026 way (3-5, not 30) | `ig-hashtag-strategist` |
| AI tells removed, or a draft audited before posting | `ig-humanizer` (plus `--mode audit`) |
| A week of Reels, carousels and stories planned | `ig-content-planner` |
| A LinkedIn post / blog / YouTube script / X thread made native here | `ig-repurposer` |
| The profile audited and rewritten (photo, NAME, bio, link, highlights, grid, pins) | `ig-profile-optimizer` |
| Their real account numbers and competitor research | `ig-audience-insights` |

Shared reference material sits in `scripts/references/`: `hook-formulas.md`,
`voice-rules.md`, `hashtag-strategy.md`, `algorithm-heuristics.md`,
`media-workflow.md`, and the user's `voice-profile.md`.

## Publishing: the myclawbots MCP flow

The **`myclawbots` MCP server is pre-configured on this machine.** Do every
publish and every read through its tools — never hand-build a Graph API call,
and never send the user to a third-party scheduler.

```
1. list_social_accounts          -> the Instagram account_id (call this FIRST)
2. create_upload_url             -> one-time upload_url + final public_url
   curl -X PUT --data-binary @slide1.jpg -H "Content-Type: image/jpeg" <upload_url>
   (repeat per file, in slide order, for a 2-10 item carousel)
3. post_to_social                -> { platform: "instagram", account_id, content,
                                       media_url | media_urls }
```

**Both halves of step 2 are required.** The `public_url` is dead until the PUT
succeeds; posting it early hands Instagram a 404, which Instagram then reports
as its own download failure. That reads like a domain-verification problem and
is not one. If the image exists only in the conversation and not on disk, use
`upload_media` with base64 instead (small images, 1-2 files max).

Full detail, container rules and limits: `scripts/references/media-workflow.md`.
The canonical tool contract and the per-platform rules live in the
**`social-manager`** skill — read it when you need anything beyond the
Instagram flow above.

### Instagram facts that change how you draft

- **Media is mandatory.** Instagram rejects text-only posts. The writer
  sub-skills produce the caption, hook, hashtags and slide plan; the user
  supplies the image or video, or `carousel-generator` renders the slides.
- **Instagram cannot be scheduled through our API.** `scheduled_time` is
  Facebook-only. An Instagram post publishes when you call `post_to_social`.
  When a plan calls for a posting time, hand the user the time and post then —
  never tell them it is scheduled.
- **Video always publishes as a Reel** (up to 15 min; 9:16 reads best).
- **Carousel is 2-10 items** via the API — the native app allows 20.
- **Mixed carousels (photos + video) are supported** on Instagram, unlike
  Facebook and LinkedIn.
- **Licensed library music cannot be attached via any API.** The audio has to be
  in the file already. Say so rather than trying.
- **Business or Creator account required.** Personal accounts cannot publish
  through the API at all.

### Images

- Images the user attached in chat are **already on this machine** under `/tmp`.
  Find the newest rather than asking for a path:
  `ls -t /tmp/*.png /tmp/*.jpg /tmp/*.jpeg /tmp/*.webp 2>/dev/null | head -5`
- Need slides generated? Use the **`carousel-generator`** skill (5 themes,
  `--platform instagram-portrait`), then stage the PNGs with `create_upload_url`.
- Need a single generated image? Use **`gemini-image`** (Gemini, through the
  vault) or DALL-E with `vault-curl` and `$OPENAI_KEY` (a stand-in for the
  user's OpenAI key). Agents not yet moved to the vault may instead have real
  keys in the `GEMINI_API_KEY` / `OPENAI_API_KEY` variables: use those with plain
  `curl`, in the same header. Never print a key. Ask the user which provider
  before spending their credits.
  Workflow: `scripts/sub-skills/ig-humanizer/sub-skills/illustration.md`.
- Accepted types: jpeg, png, webp, gif, mp4, quicktime. Images ≤12MB, video
  ≤300MB. Staged URLs live ~2h — **stage, then post promptly**; an expired URL
  cannot be retried, it has to be re-staged.

## Reading real numbers

`ig-audience-insights` covers this in full. The short version of what is and is
not readable:

- **The user's own connected account** — `get_account_insights`,
  `get_recent_posts`, `get_post_insights`, `get_post_comments`. Real reach,
  saves and shares, not estimates. This is better data than any scraper returns.
- **Competitors** — `search_public_pages` and `get_public_page_metrics` are
  **Facebook-only**; `lookup_threads_profile` reads a public Threads profile.
  There is no Instagram competitor-stats tool and no hashtag scanner. When the
  user wants a niche scan, say that plainly and offer the paste path — never
  invent numbers, and never imply we can scrape Instagram.
- Instagram may return comments **with no author**: Meta withholds the username
  on comments the account does not own. The response carries a `note` — relay it
  and stop. Nothing is broken and reconnecting will not fix it.

## Approval is not optional

Every publish goes under the user's name on their real account. Show the
approval card — formula, the hook with its character count, the full caption,
the hashtag set, the media, the primary goal — and get an explicit "post it"
before calling `post_to_social`. Confirm again before `delete_post`, which is
irreversible.

A successful post may come back with a `notice` field. **Relay it verbatim.**
Never describe a post as live and public without positive evidence.

## Voice rules (baked into every sub-skill)

1. Em dashes (`—`) capped at about 1 per 100 words (1-2 per caption, 1 per slide); replace the excess with a comma, colon, parentheses or a line break, never a period. A single em dash is not a tell. No en dashes between clauses, no double dashes.
2. Use `..` or a line break as a soft pause when rhythm calls for it.
3. Capitalize all personal, company, and product names.
4. Sentence starts can be lowercase (native caption voice); names stay capitalized.
5. Avoid AI vocabulary: `leverage`, `fundamentally`, `streamline`, `harness`, `delve`, `unlock`, `elevate`, `foster`.
6. Specific numbers beat adjectives. "47 minutes" beats "fast".
7. One idea per caption. The first 125 chars carry the hook (the "more" fold).
8. Hashtags are sizing, not volume: 3-5 sized tags, not 30.

Canonical reference: `scripts/references/voice-rules.md`.

## How Instagram URLs map

| URL shape | Parsed to |
|---|---|
| `https://www.instagram.com/p/SHORTCODE/` | shortcode, type `post` |
| `https://www.instagram.com/reel/SHORTCODE/` | shortcode, type `reel` |
| `https://www.instagram.com/USERNAME/` | username, type `profile` |
| `https://www.instagram.com/stories/USER/ID/` | username + id, type `story` |

A carousel shares the `/p/` path with a single image; the carousel is detected
from the media, not the URL.

## Related skills

- **`social-manager`** — the canonical myclawbots MCP tool contract and the
  cross-platform rules. Read it for anything past the Instagram flow above.
- **`carousel-generator`** — renders the slide PNGs `ig-carousel-planner` writes.
- **`instagram-manager`** — the always-on account-manager persona. This bundle
  is the craft layer it reaches for when drafting.
- **`google-workspace`** — optional, for saving content calendars to Sheets.

## Attribution

Adapted from [instagram-skills](https://github.com/sergebulaev/instagram-skills)
by Sergey Bulaev (MIT, see `LICENSE.upstream`). The strategy, formulas and
humanizer research are theirs; the publish and read layers were rewritten for
the myclawbots MCP tools.
