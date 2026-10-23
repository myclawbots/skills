# Video / Podcasts

Subtitles and transcripts for YouTube, Bilibili, and Xiaoyuzhou podcasts.

## YouTube (yt-dlp)

### Get Video Metadata

```bash
yt-dlp --dump-json "URL"
```

### Download Subtitles

```bash
# Download subtitles (without downloading the video)
yt-dlp --write-sub --write-auto-sub --sub-lang "zh-Hans,zh,en" --skip-download -o "/tmp/%(id)s" "URL"

# Then read the .vtt files
cat /tmp/VIDEO_ID.*.vtt
```

### Get Comments

```bash
# Extract comments (best effort; completeness is not guaranteed)
yt-dlp --write-comments --skip-download --write-info-json \
  --extractor-args "youtube:max_comments=20" \
  -o "/tmp/%(id)s" "URL"
# Comments are in the comments field of the .info.json file
```

### Search Videos

```bash
yt-dlp --dump-json "ytsearch5:query"
```

> **Subtitle note**: Manually uploaded subtitles can be extracted reliably; automatically generated subtitles may repeat content across lines and require post-processing.
> **Comment note**: `--write-comments` uses web scraping (not the YouTube Data API), so some comments may be missing.

### Retry Sequence When Subtitles Fail (Follow in Order; Stop Once You Obtain Actual Content)

`doctor` only confirms that yt-dlp itself and the JS runtime can execute; it does not
request a specific video. Therefore, `active_backend: yt-dlp` does not mean the target
video's subtitles have been verified live.

1. Start with the `yt-dlp --write-sub --write-auto-sub` command above.
2. If a bot check appears, the subtitle response is empty, or no subtitle file is created, and OpenCLI is connected:
   `opencli youtube transcript "URL" -f yaml`.
3. If OpenCLI returns `Caption URL returned empty response`, retry up to 3 times. Expiring
   subtitle URLs sometimes fail intermittently; do not interpret an empty response as “the video has no subtitles.”
4. If this still fails or the video genuinely has no subtitles, use `agent-reach transcribe "URL"` to download and transcribe the audio.

Success means obtaining nonempty subtitle/transcript content, not merely a successful command exit code or a version check from `doctor`.

### Fallback for Missing Subtitles: Whisper Audio Transcription

```bash
# Fallback when a video has no subtitles: download audio and transcribe with Whisper (a free Groq key is sufficient)
agent-reach transcribe "https://www.youtube.com/watch?v=VIDEO_ID"
agent-reach transcribe ./local_audio.mp3 -o /tmp/transcript.txt
```

> `agent-reach transcribe` accepts only public http(s) URLs or local audio files. When searching with `ytsearch5:`, first select a specific video URL from the yt-dlp results, then transcribe it.
> Configure a key first: `agent-reach configure groq-key` (hidden input; free, console.groq.com)
> or `agent-reach configure openai-key`. The default auto mode uses only the first configured
> provider (Groq preferred, otherwise OpenAI) and stops on failure; it does not automatically
> send the audio to another provider.
> `--allow-provider-fallback` explicitly authorizes fallback across providers. The same audio
> may be processed by both Groq and OpenAI, and OpenAI charges may apply. Use this only after
> confirming that the content may be shared with both providers.

## Bilibili (bili-cli as the Primary Tool; OpenCLI for Subtitles)

> ⚠️ **Do not use yt-dlp to read Bilibili**: Bilibili's risk controls now block yt-dlp with 412 responses (tests with the latest version, direct connections, proxies, and cookies all failed). Use yt-dlp only for YouTube.

### Video Details / Search / Trending / Rankings (bili-cli; Read-Only Access Requires No Login)

```bash
# Video details (title / creator / duration / views and engagement / subtitle availability)
bili video BVxxx

# Search videos
bili search "query" --type video -n 5

# Trending videos / rankings
bili hot -n 10
bili rank -n 10

# Download audio and split it into ASR-ready WAV files (use agent-reach transcribe when subtitles are unavailable)
bili audio BVxxx
```

### Subtitles (OpenCLI; Requires Desktop Chrome)

```bash
# Sentence-by-sentence subtitles with timestamps
opencli bilibili subtitle BVxxx

# OpenCLI can also search / read video metadata (fallback)
opencli bilibili search "query" -f yaml
opencli bilibili video BVxxx -f yaml
```

### Zero-Configuration Fallback: Direct Search API Access

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
curl -s -c /tmp/bili_ck.txt -o /dev/null -A "$UA" "https://www.bilibili.com/"
curl -s -b /tmp/bili_ck.txt -A "$UA" -e "https://www.bilibili.com/" \
  "https://api.bilibili.com/x/web-interface/search/all/v2?keyword=QUERY&page=1"
```

> **Install bili-cli**: `pipx install bilibili-cli` (upstream has been unmaintained since March 2026, but testing shows it still works; read-only use requires no login, while scanning the QR code from `bili login` unlocks personal features such as activity feeds and favorites).

## Xiaoyuzhou Podcast

### Transcribe a Podcast Episode (Optional --polish for Better Punctuation)

```bash
# Write a Markdown file to /tmp/. --polish uses Llama 3.3 70B to add Chinese punctuation and sensible paragraph breaks
~/.agent-reach/tools/xiaoyuzhou/transcribe.sh --polish "https://www.xiaoyuzhoufm.com/episode/EPISODE_ID"
```

> The transcription prompt already asks Whisper to output Chinese punctuation. If punctuation is still unsatisfactory, add `--polish` to use the free Llama 3.3 70B model on Groq for punctuation and sensible paragraph breaks (approximately 7 extra seconds for a 9-minute podcast). This adds one LLM call per transcription; use it as needed.

### Prerequisites

1. **ffmpeg**: `brew install ffmpeg`
2. **Groq API Key** (free): https://console.groq.com/keys
3. **Configure the key**: `agent-reach configure groq-key` (hidden input)
4. **First run**: `agent-reach install --env=auto --system --channels=xiaoyuzhou` (requires explicit user authorization)

### Check Status

```bash
agent-reach doctor
```

> Output Markdown files are saved to `/tmp/` by default.

## Selection Guide

| Use case | Recommended tool |
|----------|------------------|
| YouTube subtitles | yt-dlp; on failure, OpenCLI (up to 3 attempts) → agent-reach transcribe |
| Bilibili video details / search | bili-cli |
| Bilibili subtitles | opencli bilibili subtitle |
| Podcast transcription | Xiaoyuzhou transcribe.sh |
| Audio/video without subtitles | agent-reach transcribe (for Bilibili audio, run `bili audio` first) |
