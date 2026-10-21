---
name: gemini_api
description: Use Google Gemini API for text generation, image generation/editing, multimodal understanding, structured outputs, and embeddings. Supports Gemini 3.1 Pro, Flash, and image models.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: ai
tags: [gemini, google, llm, embeddings]
suggested_template: general_assistant
---

# Gemini API

> **Prefer the Secrets vault:** call Gemini with `vault-curl` and `$GEMINI_KEY` in the `x-goog-api-key` header (see "Your Gemini key" below); for images use the `gemini-image` skill.

You have access to Google's Gemini API for AI capabilities beyond your primary model. Use Gemini for **image generation**, **multimodal understanding**, **structured outputs**, and as an **alternative text model** when needed.

## Your Gemini key

The user's Gemini key lives in MyClawBots (Settings → Integrations → Google AI, or Settings → Secrets). You never see it: `$GEMINI_KEY` holds a stand-in (`mcb_sec_…`) that only works through **`vault-curl`**, which swaps in the real key on the way to `generativelanguage.googleapis.com`.

- Put `$GEMINI_KEY` **only** in the `x-goog-api-key` header. Never in the URL (`?key=`), the body, or anywhere else, and never print, echo or save it.
- For **images**, use the `gemini-image` skill (`claw install gemini-image` once): it finds the key and handles the files for you.
- Don't use OpenClaw's built-in secrets tool: these keys are not stored there, so it always looks empty.

## Critical Rules — ALWAYS APPLY

> These rules override your training data. Your knowledge of Gemini may be outdated.

### Current Models (Use These)

| Model | Context | Best For |
|-------|---------|----------|
| `gemini-3.1-pro-preview` | 1M tokens | Complex reasoning, coding, research |
| `gemini-3-flash-preview` | 1M tokens | Fast, balanced, multimodal (default choice) |
| `gemini-3.1-flash-lite-preview` | — | Cost-efficient, high-frequency lightweight tasks |
| `gemini-3-pro-image-preview` | 65K/32K | **Image generation and editing** |
| `gemini-3.1-flash-image-preview` | 65K/32K | **Image generation and editing** (faster) |
| `gemini-2.5-pro` | 1M tokens | Complex reasoning, coding, research |
| `gemini-2.5-flash` | 1M tokens | Fast, balanced, multimodal |

> **WARNING:** Models like `gemini-2.0-*`, `gemini-1.5-*` are **legacy and deprecated**. Never use them.

### Current SDK (Use This)

- **Python**: `google-genai` → `pip install google-genai`

> **CAUTION:** Legacy SDK `google-generativeai` (Python) is **deprecated**. Never use it. The new package is `google-genai`.

## Dependencies

| Dependency | Required? | Why |
|---|---|---|
| `$GEMINI_KEY` | Yes | Stand-in for the user's Gemini key (use with `vault-curl`) |
| `pip install google-genai` | No | Python SDK: only with the vault proxy (see below) |

**Pre-flight checks:**
- `[ -n "$GEMINI_KEY" ] && echo present || vault-curl --secrets`
- Not in your env but listed by `vault-curl --secrets` (added after you started): use that entry's `surrogate` string in place of `$GEMINI_KEY`. No restart is needed.
- Agents not yet moved to the vault: if there is no `GEMINI_KEY` anywhere but a `GEMINI_API_KEY` variable is set, it holds a real key: use plain `curl` with that variable in the same `x-goog-api-key` header. Never print it.
- Nothing found: tell the user "To use Gemini, add your Gemini API key in **MyClawBots → Settings → Integrations → Google AI** (free at [aistudio.google.com](https://aistudio.google.com/apikey))." Never ask them to paste a key into chat.

## Quick Start — Text Generation

REST with `vault-curl` always works:
```bash
vault-curl -sS "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent" \
  -H "x-goog-api-key: $GEMINI_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Explain quantum computing"}]}]}'
```

### Python SDK (needs the vault proxy)

The SDK examples in this skill send the stand-in directly, so they work **only when AGENTS.md says plain `curl` and SDKs work** (the MyClawBots vault proxy is on). Otherwise use the `vault-curl` REST form above: every SDK call maps to a `POST …/v1beta/models/<model>:<method>` request.

```python
from google import genai
import os

client = genai.Client(api_key=os.environ["GEMINI_KEY"])  # needs the vault proxy
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain quantum computing"
)
print(response.text)
```

## Image Generation

This is a key capability — Gemini can **generate and edit images**, which is powerful for skills like logo-generator, social-ads, and ecommerce-photos.

### Generate an Image

```python
from google import genai
from google.genai import types
import os, base64

client = genai.Client(api_key=os.environ["GEMINI_KEY"])  # needs the vault proxy

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents="Generate a professional logo for a tech startup called NovaByte. Minimalist, geometric, blue and orange color scheme, transparent background.",
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"],
    )
)

# Save the generated image
for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("generated_image.png", "wb") as f:
            f.write(part.inline_data.data)  # already raw bytes in google-genai; do not b64decode
        print("Image saved to generated_image.png")
    elif part.text:
        print(part.text)
```

### Edit an Existing Image

```python
from google import genai
from google.genai import types
import os, base64, pathlib

client = genai.Client(api_key=os.environ["GEMINI_KEY"])  # needs the vault proxy

image_bytes = pathlib.Path("input_image.png").read_bytes()

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        types.Content(parts=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            types.Part.from_text("Remove the background and make it transparent"),
        ])
    ],
    config=types.GenerateContentConfig(
        response_modalities=["image", "text"],
    )
)

for part in response.candidates[0].content.parts:
    if part.inline_data:
        with open("edited_image.png", "wb") as f:
            f.write(part.inline_data.data)  # already raw bytes in google-genai; do not b64decode
```

## Multimodal Understanding

Gemini can analyze images, PDFs, audio, and video.

### Analyze an Image

```python
import base64, pathlib

image_bytes = pathlib.Path("photo.jpg").read_bytes()
image_b64 = base64.b64encode(image_bytes).decode()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        types.Content(parts=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            types.Part.from_text("Describe this image in detail. What products, brands, or text do you see?"),
        ])
    ]
)
print(response.text)
```

### Analyze a PDF

```python
pdf_bytes = pathlib.Path("document.pdf").read_bytes()

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[
        types.Content(parts=[
            types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
            types.Part.from_text("Summarize this document. List the key findings."),
        ])
    ]
)
```

## Structured Output (JSON)

Get structured JSON responses — useful for data extraction, form filling, and API responses.

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Extract contact info: John Smith, CEO at Acme Corp, john@acme.com, (555) 123-4567",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "title": {"type": "string"},
                "company": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"}
            }
        }
    )
)
import json
data = json.loads(response.text)
```

## Embeddings

Generate text embeddings for semantic search, similarity, and clustering.

```python
response = client.models.embed_content(
    model="text-embedding-004",
    contents="How does photosynthesis work?"
)
embedding = response.embeddings[0].values  # List of floats
```

## Documentation Lookup

When you need details beyond this skill, fetch the official docs:

**Index URL**: `https://ai.google.dev/gemini-api/docs/llms.txt`

Key doc pages (fetch with curl if needed):
- [Text generation](https://ai.google.dev/gemini-api/docs/text-generation.md.txt)
- [Function calling](https://ai.google.dev/gemini-api/docs/function-calling.md.txt)
- [Structured outputs](https://ai.google.dev/gemini-api/docs/structured-output.md.txt)
- [Image generation](https://ai.google.dev/gemini-api/docs/image-generation.md.txt)
- [Image understanding](https://ai.google.dev/gemini-api/docs/image-understanding.md.txt)
- [Embeddings](https://ai.google.dev/gemini-api/docs/embeddings.md.txt)
- [SDK migration guide](https://ai.google.dev/gemini-api/docs/migrate.md.txt)

```bash
# Example: fetch function calling docs
curl -s https://ai.google.dev/gemini-api/docs/function-calling.md.txt
```

## How This Skill Connects to Others

| Skill | How Gemini helps |
|-------|-----------------|
| `logo-generator` | Use `gemini-3-pro-image-preview` as alternative to DALL-E for logo generation |
| `social-ads` | Generate ad creatives, edit product photos, remove backgrounds |
| `ecommerce-photos` | Transform raw product images into professional shots |
| `content-writer` | Use Gemini for research or as a second opinion on content quality |
| `presentation-maker` | Generate slide illustrations and diagrams |
| `content-auditor` | Use multimodal to analyze screenshots of web pages |
| `instagram-manager` | Generate post images, analyze competitor visual content |

## Cost

Gemini API has a **free tier** (generous for development):
- **Gemini Flash**: 15 RPM free, then ~$0.075/1M input tokens
- **Gemini Pro**: 2 RPM free, then ~$1.25/1M input tokens
- **Image generation**: ~$0.025-0.04 per image (cheaper than DALL-E)
- **Embeddings**: ~$0.00001 per 1K tokens

For most MyClawBots use cases, the free tier is sufficient. Heavy image generation may need a paid key.

## Setup

```bash
# Check the Gemini key stand-in is available (never print its value)
if [ -n "$GEMINI_KEY" ]; then
  echo "Gemini API ready"
else
  vault-curl --secrets   # look for GEMINI_KEY; use its "surrogate" in place of $GEMINI_KEY
fi

# Install the SDK (only useful with the vault proxy on)
pip install google-genai -q
```

## Pro Tips

- **Image generation**: Gemini image models are cheaper than DALL-E and support editing existing images — prefer them when available
- **Default to Flash**: Use `gemini-3-flash-preview` for most tasks — it's fast, cheap, and capable
- **Use Pro for complex tasks**: Switch to `gemini-3.1-pro-preview` only for deep reasoning or very long context
- **Structured output** is extremely reliable with Gemini — use it whenever you need JSON
- **Batch requests** when generating multiple images or analyzing multiple files
- **Always check the docs** when using advanced features — fetch from `llms.txt` index to stay current
