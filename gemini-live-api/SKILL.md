---
name: gemini_live_api
description: Build real-time bidirectional voice and video streaming with Gemini Live API. WebSocket-based audio/video/text streaming, voice activity detection, native audio, function calling, session management, and ephemeral tokens.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: ai
tags: [gemini, voice, streaming, realtime]
suggested_template: general_assistant
---

# Gemini Live API Skill

The Live API provides real-time, low-latency bidirectional streaming for voice and video interactions. Use this for building conversational agents with native audio I/O, real-time video analysis, and interactive experiences.

> **Not supported with keys managed by MyClawBots.** The Live API is WebSocket-only, and the MyClawBots vault (`vault-curl` and its proxy) only carries HTTPS requests, so the stand-in `$GEMINI_KEY` (`mcb_sec_…`) cannot open a Live session. Check first (see Pre-flight): if the only Gemini key you have is `GEMINI_KEY`, tell the user real-time Live streaming isn't available on this agent and use the `gemini-api` skill's REST calls (`vault-curl` + `x-goog-api-key: $GEMINI_KEY`) for text, audio or image understanding instead. Never try to recover or print the real key.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `gemini-api` skill | No | Recommended: for basic Gemini setup reference |
| A real Gemini key in the `GEMINI_API_KEY` variable | Yes | Only agents not yet moved to the MyClawBots vault have one |
| `google-genai` SDK | Yes | Python SDK with WebSocket support (>= 1.55.0) or JavaScript (>= 1.33.0) |

**Pre-flight checks:**
- `printenv GEMINI_API_KEY >/dev/null && echo "real key present" || echo "no real key"` (prints nothing about the key itself). Only with a real key does this skill work; the SDK reads it from the env on its own (`genai.Client()`).
- No real key but `[ -n "$GEMINI_KEY" ]`: the key is managed by MyClawBots, so the Live API is unsupported here. Use `gemini-api` REST instead (see the note at the top).
- Neither: tell the user to add a Gemini key in **MyClawBots → Settings → Integrations → Google AI**, and note that Live streaming may still be unavailable with managed keys. Never ask them to paste a key into chat.
- Verify Python 3.9+ or Node.js 18+ is installed
- Verify `google-genai >= 1.55.0` is installed with WebSocket support
- Verify audio libraries are installed: `pip install pyaudio` or equivalent
- For video streaming: verify webcam/video source is available

## Prerequisites

- A real Gemini key in the environment (agents not yet moved to the MyClawBots vault; see the note at the top)
- Python 3.9+ or Node.js 18+
- WebSocket support (google-genai >= 1.55.0, @google/genai >= 1.33.0)
- Audio recording/playback libraries (pyaudio, sounddevice, etc.)

## Installation

```bash
pip install google-genai pyaudio
```

## Current Model

The Live API uses a single recommended model:

- **gemini-3.1-flash-live-preview** - Optimized for real-time voice/video streaming

**Deprecated:** gemini-3-flash-live, gemini-3-pro-live are no longer supported.

## Overview: Real-Time Streaming

The Live API enables:

- **Bidirectional audio:** Send audio, receive audio in real-time
- **Bidirectional video:** Stream webcam or pre-recorded video
- **Voice Activity Detection:** Automatic detection of speech pauses
- **Low latency:** ~200-500ms round-trip response time
- **Function calling:** Real-time tool invocation
- **Session management:** Single session per connection with ephemeral tokens

## Quick Start: Text-to-Speech Conversation

```python
import os
from google import genai

# genai.Client() reads the real key from the environment itself. A MyClawBots
# stand-in (mcb_sec_…) cannot work here: WebSockets bypass the vault.
client = genai.Client()

# Start a Live session
session = client.models.generate_content_stream(
    model="gemini-3.1-flash-live-preview",
    stream_options={"enable_realtime": True}
)

# Send text to the model
session.send_text("Hello, can you tell me a joke?")

# Receive streaming response
for chunk in session:
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

## Sending Audio Input

Stream PCM audio at 16kHz (mono):

```python
import pyaudio
import threading

def stream_audio(session):
    """Capture microphone and stream to Live API"""
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=1024)

    try:
        while True:
            audio_chunk = stream.read(1024)
            session.send_realtime_input(audio_chunk)
    except KeyboardInterrupt:
        stream.stop_stream()
        stream.close()

session = client.models.generate_content_stream(
    model="gemini-3.1-flash-live-preview",
    stream_options={"enable_realtime": True}
)

# Stream audio in background thread
audio_thread = threading.Thread(target=stream_audio, args=(session,))
audio_thread.daemon = True
audio_thread.start()

# Receive responses
for chunk in session:
    if chunk.audio:
        # Play audio response (24kHz PCM)
        print(f"Received audio: {len(chunk.audio)} bytes")
```

## Sending Video

Stream video frames as base64-encoded JPEG:

```python
import base64
import cv2

session = client.models.generate_content_stream(
    model="gemini-3.1-flash-live-preview",
    stream_options={"enable_realtime": True}
)

cap = cv2.VideoCapture(0)  # Webcam

session.send_text("What do you see?")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Encode to JPEG
    _, jpeg = cv2.imencode('.jpg', frame)
    b64 = base64.b64encode(jpeg.tobytes()).decode()

    # Send to Live API
    session.send_realtime_input(
        {
            "data": b64,
            "mime_type": "image/jpeg"
        }
    )

    # Receive analysis
    for chunk in session:
        if chunk.text:
            print(chunk.text, end="", flush=True)

cap.release()
```

## CRITICAL: send_realtime_input vs send_client_content

**Use `send_realtime_input()` for:**
- Audio chunks (PCM 16-bit, 16kHz)
- Video frames (JPEG/PNG base64)
- Real-time streaming data

**Use `send_client_content()` for:**
- Text messages
- System instructions (at session start)
- Non-streaming structured data

```python
# CORRECT: Audio streaming
session.send_realtime_input(audio_bytes)

# INCORRECT for audio (will fail)
# session.send_client_content(audio_bytes)

# CORRECT: Text message
session.send_text("Hello")

# INCORRECT (will fail)
# session.send_realtime_input("Hello")
```

## Session Management & Ephemeral Tokens

Each Live session has limits:

- **Max duration:** 15 minutes per session
- **Ephemeral token:** Auto-generated, expires with session
- **Reconnect:** Create new session; previous tokens invalid
- **State:** Session maintains context across sends/receives

```python
# Session auto-expires after 15 minutes
session = client.models.generate_content_stream(
    model="gemini-3.1-flash-live-preview",
    stream_options={"enable_realtime": True}
)

# Use session within 15 minutes
session.send_text("Quick question?")

# For longer interactions, create a new session
```

## Voice Activity Detection

The model auto-detects speech pauses:

```python
# Model automatically pauses when it detects silence
# and sends accumulated response
session.send_text("Tell me a story")

# Listen for natural speech pauses
for chunk in session:
    if chunk.text:
        print("Response:", chunk.text)
        # Model waited for silence before responding
```

## Function Calling in Real-Time

Define tools for live execution:

```python
session = client.models.generate_content_stream(
    model="gemini-3.1-flash-live-preview",
    tools=[
        {
            "name": "get_time",
            "description": "Get current time",
            "parameters": {"type": "object", "properties": {}}
        }
    ],
    stream_options={"enable_realtime": True}
)

session.send_text("What time is it?")

for chunk in session:
    if chunk.function_call:
        print(f"Model called: {chunk.function_call.name}")
        # Execute tool and send result
        result = handle_tool(chunk.function_call.name)
        session.send_client_content(
            {"function_result": result}
        )
```

## Audio Format Requirements

- **Input:** PCM 16-bit signed, mono, 16kHz sample rate
- **Output:** PCM 16-bit signed, mono, 24kHz sample rate
- **Buffer size:** 1024 bytes typical for real-time

## Limitations

- **Single mode per session:** Use TEXT or AUDIO input, not both simultaneously
- **Session timeout:** 15 minutes max
- **Context window:** ~128K tokens (same as gemini-3.1-flash)
- **No interaction history:** Each Live session is independent

## Migration from 2.5 to 3.1

If using Gemini 2.5 Live API:

- Model changed: `gemini-2.5-pro-live` → `gemini-3.1-flash-live-preview`
- Improved latency and audio quality
- Function calling more reliable
- API compatibility maintained

## Best Practices

1. **Handle disconnections:** Implement reconnect logic with exponential backoff
2. **Audio quality:** Ensure clean, noise-reduced microphone input
3. **Session reuse:** Keep sessions active during interaction; don't create per-message
4. **Rate limiting:** Respect WebSocket rate limits (check dashboard)
5. **Error handling:** Catch WebSocket errors and gracefully close sessions

## Documentation Lookup

- [Official Live API docs](https://ai.google.dev/api/python/google/genai/types/LiveConnectWebSocketConnection)
- [Audio format specifications](https://ai.google.dev/docs/live_streaming)
- Check `llms.txt` for model capabilities

## Cost

Live API pricing:
- **Input (audio/video):** $0.10 per 1M tokens
- **Output (audio/video):** $0.30 per 1M tokens
- Same rates as gemini-3.1-flash

## Related Skills

- **gemini-api:** Text and image generation
- **gemini-interactions-api:** Stateful conversations with history
- **vertex-ai-api:** Enterprise Live API via Vertex AI

## Example: Voice Assistant Bot

```python
import os
import pyaudio
import threading

def run_voice_assistant():
    client = genai.Client()  # real key from the environment; see the note at the top

    session = client.models.generate_content_stream(
        model="gemini-3.1-flash-live-preview",
        stream_options={"enable_realtime": True}
    )

    # Greet user
    session.send_text("Hi! I'm your voice assistant. How can I help?")

    # Stream microphone
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                    input=True, frames_per_buffer=1024)

    def capture_audio():
        try:
            for _ in range(16000):  # 1 second
                data = stream.read(1024)
                session.send_realtime_input(data)
        except:
            pass

    # Capture and process
    capture_thread = threading.Thread(target=capture_audio)
    capture_thread.start()

    for chunk in session:
        if chunk.text:
            print("Assistant:", chunk.text)

    stream.stop_stream()
    stream.close()

if __name__ == "__main__":
    run_voice_assistant()
```
