---
name: video_creator
description: Create viral short-form reels, product demo videos, and multilingual content. Convert long-form videos into platform-ready clips with voiceovers and avatars.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: content
tags: [video, reels, short-form, voiceover]
suggested_template: content_creator
---

# Video Creator

> **IMPORTANT:** This skill requires a dashboard connection to the Video Creator API. Ensure your `${PROXY_URL}` and `$PROXY_API_KEY` are configured correctly before proceeding.

## Prerequisites — MUST READ

- You must have your Video Creator proxy URL configured as `${PROXY_URL}`
- You must have a valid API key configured as `$PROXY_API_KEY`
- All requests use these values via headers: `-H "x-api-key: $PROXY_API_KEY"`
- Video processing is asynchronous — submit a request and poll for status using the job ID
- Processing time varies: short clips (15–60 seconds) typically complete in 2–10 minutes; longer videos may take 15–30 minutes
- Always preview the generated video before publishing to social platforms
- Respect copyright and original content rights; only process videos you have permission to modify
- The API respects WhatsApp's 24-hour messaging window and social platform limits

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `${PROXY_URL}` and `$PROXY_API_KEY` | Yes | Required for video processing service |
| `google-workspace` skill | No | Optional: for saving videos to Google Drive |
| `social-manager` skill | No | Optional: for publishing to social platforms |

**Pre-flight checks:**
- Confirm `${PROXY_URL}` and `$PROXY_API_KEY` environment variables are set
- Verify video processing service is active in the dashboard
- If saving to Drive: ensure `google-workspace` skill is connected
- If publishing to social: ensure `social-manager` skill is connected
- For AI-generated video thumbnails: Confirm whether to use OpenAI DALL-E or Gemini Imagen

**Note on AI thumbnails:** If user needs AI-generated video thumbnails, ask whether to use OpenAI DALL-E or Google Gemini Imagen before proceeding.

## How it works

The Video Creator transforms long-form videos into engaging short-form content optimized for social platforms (Instagram Reels, TikTok, YouTube Shorts). You can extract highlights, add captions, background music, voiceovers, and AI avatars. You can also create product demo videos with recorded screen content, translate videos to multiple languages, and auto-generate thumbnails.

The workflow is asynchronous: submit your source video (via URL or file ID), specify your target platform and duration, request optional features like captions or AI avatars, and receive a job ID. Poll the status endpoint to monitor processing. Once complete, preview the video, make final adjustments, download it, and publish to your social accounts.

For maximum impact, start with high-quality source video, extract the most engaging 15–60 second clips, add captions for accessibility and retention, include trending background music, generate a compelling thumbnail, and publish during peak hours on your target platform.

## Available Tools

### 1. Create Short-Form Reel from Long Video

Extract highlights from a longer video and optimize for short-form platforms.

```bash
curl -X POST "${PROXY_URL}/video/reel" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "source_url": "https://example.com/long-video.mp4",
    "target_duration": "30s",
    "style": "highlights",
    "add_captions": true,
    "platform": "instagram"
  }'
```

**Expected response:** `{ "job_id": "reel_abc123", "status": "processing", "estimated_time_minutes": 5 }`

### 2. Check Video Processing Status

Poll this endpoint to check if your video is ready for download or publishing.

```bash
curl -X GET "${PROXY_URL}/video/reel_abc123/status" \
  -H "x-api-key: $PROXY_API_KEY"
```

**Expected response:** `{ "status": "completed", "video_id": "vid_xyz789", "download_url": "...", "duration": "30s" }`

### 3. Create Product Demo Video

Generate a professional product demo video from screen recordings with optional voiceover and AI avatar.

```bash
curl -X POST "${PROXY_URL}/video/product-demo" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "screen_recording_url": "https://example.com/screen.mp4",
    "voiceover": true,
    "voice": "female",
    "avatar": true,
    "background_music": "upbeat"
  }'
```

**Expected response:** `{ "job_id": "demo_def456", "status": "processing", "estimated_time_minutes": 8 }`

### 4. Translate Video to Other Languages

Translate your video to multiple languages with optional lip-sync synchronization.

```bash
curl -X POST "${PROXY_URL}/video/translate" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "vid_xyz789",
    "target_languages": ["es", "fr", "de", "ja"],
    "lip_sync": true
  }'
```

**Expected response:** `{ "job_id": "trans_ghi789", "status": "processing", "languages": [...] }`

### 5. Get Video Details

Retrieve metadata and details about a generated or processed video.

```bash
curl -X GET "${PROXY_URL}/video/vid_xyz789" \
  -H "x-api-key: $PROXY_API_KEY"
```

**Expected response:** `{ "id": "vid_xyz789", "duration": "30s", "platform": "instagram", "captions": true }`

### 6. Download Processed Video

Download your final video file in the requested format.

```bash
curl -X GET "${PROXY_URL}/video/vid_xyz789/download" \
  -H "x-api-key: $PROXY_API_KEY" \
  -o "final_video.mp4"
```

### 7. Save Video to Google Drive

Export your video directly to Google Drive for backup and sharing with collaborators.

```bash
curl -X POST "${PROXY_URL}/video/vid_xyz789/save-to-drive" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "folder_id": "1a2b3c4d5e6f"
  }'
```

### 8. Publish Video to Social Media

Publish your finalized video to connected social media accounts with optional captions and scheduled posting.

```bash
curl -X POST "${PROXY_URL}/video/vid_xyz789/publish" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "ig_12345",
    "caption": "Check out our new product feature! 🚀 #ProductDemo",
    "scheduled_time": "2026-03-30T18:00:00Z"
  }'
```

### 9. View Video History

Retrieve all videos you've previously created and processed.

```bash
curl -X GET "${PROXY_URL}/video/history?limit=20" \
  -H "x-api-key: $PROXY_API_KEY"
```

### 10. Generate Video Thumbnail

Create an eye-catching thumbnail for your video with optional custom text.

```bash
curl -X POST "${PROXY_URL}/video/thumbnail" \
  -H "x-api-key: $PROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "vid_xyz789",
    "style": "auto",
    "text": "Must Watch!"
  }'
```

**Expected response:** `{ "thumbnail_url": "https://...", "format": "1280x720" }`

## Important Rules

1. Always preview the generated video before publishing to any social platform.
2. Respect copyright and content rights — only process videos you have explicit permission to modify.
3. Suggest platform-optimal dimensions (1080x1920 for Instagram Reels, 1080x1350 for feed posts, 1200x675 for YouTube).
4. Duration limits: Instagram Reels up to 90 seconds, TikTok up to 10 minutes, YouTube Shorts up to 60 seconds.
5. Always add captions for accessibility and to boost engagement and watch time.
6. Show estimated processing time before submitting long video jobs; warn if it will take 15+ minutes.
7. Include trending background music but confirm licensing; suggest royalty-free music libraries.
8. When translating to multiple languages, confirm the target languages and preview dubbed audio.
9. For product demos, ensure screen clarity and consider adding on-screen text annotations.
10. Schedule posts during peak engagement hours (typically 11 AM–1 PM and 7 PM–9 PM in the user's timezone).

## Smart Strategy

Start with a high-quality source video or screen recording. Decide on the target platform and clip duration. Extract the most engaging highlights or create a product demo with voiceover and avatar. Add captions for accessibility and retention. Select trending background music or custom audio. Generate a custom thumbnail that stands out. Preview the final video and make any last-minute adjustments. Publish to connected social accounts with an engaging caption. Monitor initial engagement and adjust posting times or content style based on performance. For long-form videos, create multiple clips targeting different platforms (Instagram Reels, TikTok, YouTube Shorts) simultaneously to maximize reach.
