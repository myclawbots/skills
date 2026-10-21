---
name: podcast_creator
description: Convert blog posts, research papers, or articles into engaging podcast-style audio. Generate scripts, add narration, and distribute to podcast platforms.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [podcast, audio, narration, repurposing]
suggested_template: content_creator
---

# Podcast Creator

> **IMPORTANT:** This skill converts written content into audio podcasts. It respects original content — always cite sources and ask for permission before converting published work. Audio files are generated via the proxy and can be saved to Google Drive or distributed to podcast platforms. You just use the `${PROXY_URL}` and `$PROXY_API_KEY` headers.

## Dependencies

This skill requires the following:

| Dependency | Required? | Why |
|---|---|---|
| `google-workspace` skill | Optional — for saving audio files to Google Drive |
| Text-to-speech provider | **Yes** — for narrating the podcast script. See "Provider Selection" below. |
| `${PROXY_URL}` and `$PROXY_API_KEY` | **Yes** — configured in your environment for audio generation |

> **Before starting, check:**
> 1. Is the proxy API `${PROXY_URL}` and `$PROXY_API_KEY` configured?
> 2. Which text-to-speech provider should be used? (See Provider Selection below)
> 3. Is `google-workspace` skill installed for Drive backup (optional)?

## Provider Selection — ASK ABOUT TTS VOICE

Before generating podcast audio, **ask the user which text-to-speech voice they prefer**:

> "I can narrate your podcast using:
> 1. **Google Cloud Text-to-Speech** — natural sounding, multiple voices and accents
> 2. **ElevenLabs** — highly realistic voices, supports multiple languages
> 3. **OpenAI TTS (the user's OpenAI key, `$OPENAI_KEY`)** — integrated with OpenAI, natural pacing
> 4. **AWS Polly** — diverse voices, good for commercial distribution
>
> For interview format (dual-voice), I'll use different voices for each speaker.
>
> Which provider do you prefer, or should I check which ones are available in your environment?"

If only one TTS provider is configured, use that by default and inform the user.

**OpenAI TTS with the user's key:** `$OPENAI_KEY` is a stand-in (`mcb_sec_…`), not the key. It only works through `vault-curl`, and only in the `Authorization` header. Write the audio to a file, never to stdout:

```bash
vault-curl -sS https://api.openai.com/v1/audio/speech \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini-tts", "voice": "alloy", "input": "Welcome to the show."}' \
  -o /root/.openclaw/workspace/media/podcast-intro.mp3
```

Not in your env? Run `vault-curl --secrets` (a key added after you started) and use the `OPENAI_KEY` entry's `surrogate` string in its place. Agents not yet moved to the vault may instead have a real key in the `OPENAI_API_KEY` variable: use it with plain `curl` in the same header. Never print a key, and never use OpenClaw's built-in secrets tool (these keys are not there). No key at all: ask the user to add one in MyClawBots → Settings → Integrations.

## Prerequisites — MUST READ

1. **Source Content**: Have a blog post, article, research paper, or document URL ready (or text pasted).
2. **Podcast Style**: Choose a format — conversational (casual), interview (Q&A), narrative (storytelling), educational (teaching).
3. **Target Duration**: Decide length — 5min (quick), 10min (standard), 15min (medium), 30min (deep dive).
4. **Voice Preference**: Choose narrator voice — male, female, or dual (for interview style).
5. **Series Planning** (optional): If creating recurring content, plan series structure and naming.
6. **API Key**: Your `$PROXY_API_KEY` is configured in your environment.

## How it works

This skill transforms written content into engaging podcast audio. Upload a blog post, paste text, or provide a URL. The AI analyzes the content, generates a conversational script optimized for audio, adds intro/outro segments, and synthesizes natural-sounding narration. Download the audio, save to Google Drive, or push directly to Spotify, Apple Podcasts, and other platforms.

The workflow:
1. Provide source content (URL, document, or text)
2. Choose podcast style and duration target
3. AI generates engaging script with intro/outro
4. Review script and approve
5. Generate audio with natural voice narration
6. Download or save to Drive
7. Optionally create a series for recurring content
8. Distribute to Spotify, Apple Podcasts, and RSS feeds

## Available Tools

### 1. Generate Podcast from Content

Transform a blog post, article, or document into a podcast episode.

```bash
curl -X POST ${PROXY_URL}/podcast/generate \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "url",
    "source": "https://example.com/blog/ai-trends-2026",
    "style": "conversational",
    "duration_target": "15min",
    "voice": "female",
    "include_intro": true,
    "include_outro": true
  }'
```

**source_type**: `url`, `text`, `document` (uploaded file).

**style**: `conversational` (casual chat), `interview` (Q&A format), `narrative` (story-driven), `educational` (teaching).

**duration_target**: `5min`, `10min`, `15min`, `30min`.

**voice**: `male`, `female`, `dual` (for interview style).

**Response**: Returns `job_id` for tracking generation.

### 2. Check Generation Status

Poll for completion and retrieve the generated audio file.

```bash
curl -X GET ${PROXY_URL}/podcast/generate/{job_id} \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Status (processing/complete), episode_id, audio_url, duration_seconds, script_text, transcript.

### 3. Get Episode Details

Retrieve metadata for a generated podcast episode.

```bash
curl -X GET ${PROXY_URL}/podcast/{id} \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Title, description, duration, voice, style, source_url, creation_date, series_id (if part of series).

### 4. Download Audio File

Download the generated podcast episode as MP3.

```bash
curl -X GET ${PROXY_URL}/podcast/{id}/download \
  -H "x-api-key: $PROXY_API_KEY" \
  -o episode.mp3
```

**Response**: MP3 file download (typically 20-150MB depending on duration).

### 5. Save to Google Drive

Push the podcast episode to Google Drive for storage and sharing.

```bash
curl -X POST ${PROXY_URL}/podcast/{id}/save-to-drive \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "1a2b3c4d5e6f7g8h9i0j"
  }'
```

**Response**: Google Drive link and folder path.

### 6. Generate Script Only

Create just the podcast script without audio (useful for review, editing, or reading aloud yourself).

```bash
curl -X POST ${PROXY_URL}/podcast/script \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "text",
    "source": "Your article text here...",
    "style": "narrative",
    "duration_target": "10min"
  }'
```

**Response**: Script text with section markers, timing cues, and speaker notes.

### 7. Retrieve Episode History

List all podcasts you've generated.

```bash
curl -X GET "${PROXY_URL}/podcast/episodes?limit=20" \
  -H "x-api-key: $PROXY_API_KEY"
```

**Response**: Array of episodes with IDs, titles, durations, styles, creation dates, status.

### 8. Create a Podcast Series

Set up a recurring podcast series for multiple episodes.

```bash
curl -X POST ${PROXY_URL}/podcast/series \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Trends Weekly",
    "description": "Weekly podcast covering AI, automation, and emerging technologies",
    "cover_art_url": "https://example.com/cover-art.jpg",
    "schedule": "weekly"
  }'
```

**schedule**: `weekly`, `biweekly`, `monthly`, or `adhoc`.

**Response**: Series ID for assigning future episodes.

### 9. Distribute to Podcast Platforms

Submit generated podcast to Spotify, Apple Podcasts, Google Podcasts, and RSS feeds.

```bash
curl -X POST ${PROXY_URL}/podcast/distribute \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "episode_id": "ep_12345",
    "platforms": [
      "spotify",
      "apple_podcasts",
      "google_podcasts",
      "rss"
    ]
  }'
```

**platforms**: `spotify`, `apple_podcasts`, `google_podcasts`, `rss`, `amazon_music`, `youtube`.

**Response**: Distribution confirmation with links to live episodes on each platform.

## Important Rules

1. **Always generate and show script first** — let humans review content before audio production.
2. **Respect original content** — cite sources and ask permission before converting published work.
3. **Offer multiple duration options** — 5min for quick tips, 10-15min for articles, 30min for deep dives.
4. **Suggest series creation** — if converting recurring blog content, propose a podcast series for consistency.
5. **Preview audio quality** — let humans listen to a sample before distributing to public platforms.
6. **Include intro/outro** — brand segments help with series continuity and listener recognition.
7. **Maintain attribution** — always credit original sources in episode descriptions.
8. **Optimize for distribution** — ensure proper metadata (title, description, cover art) for podcast platforms.

## Smart Strategy

1. **Identify content source**: Blog posts, research papers, articles, or customer case studies are ideal.
2. **Generate script**: Create engaging, audio-friendly script with intro, key points, and outro.
3. **Review with human**: Show the script and let them approve/edit before audio production.
4. **Choose voice and style**: Match narrator voice and format to your brand (conversational for product blogs, educational for research).
5. **Generate audio**: Produce episode with natural-sounding narration.
6. **Save to Drive**: Store MP3 and script in Google Drive for archival and team access.
7. **Create series if recurring**: If publishing weekly content, set up a series for consistency.
8. **Distribute to platforms**: Push to Spotify, Apple Podcasts, Google Podcasts, and RSS feed.
9. **Track listens**: Monitor downloads and engagement across platforms.
10. **Repurpose content**: Convert top-performing blog posts into podcast episodes for expanded reach.
