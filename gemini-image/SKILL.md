---
name: gemini_image
description: Generate and edit images with Google Gemini through the user's own Gemini key, saved in MyClawBots → Secrets. The key stays in the vault (you only hold a stand-in); images are saved to disk and only the file path enters the conversation.
author:
  name: MyClawBots
  url: https://myclawbots.ai
license: MIT
category: ai
tags: [gemini, image-generation, secrets-vault]
suggested_template: content_creator
---

# Gemini Image

Text-to-image and image editing with Gemini, paid for by the user's own Gemini key. You never see the real key: you hold a stand-in token (`mcb_sec_…`) and the script sends it through `vault-curl`, which swaps in the real key at the MyClawBots vault.

## Pre-flight

Just run the script. It finds the key on its own, including one the user added after you started: it asks the vault for the live list (`vault-curl --secrets`), so no restart and no settings save is needed.

- A key with another name: pass `--key-env NAME`.
- Exit code 3 with "No Gemini key found": ask the user to add a Google Gemini key in MyClawBots → Settings → Secrets (name `GEMINI_KEY`). Never ask them to paste a key into chat.
- To see the saved keys yourself, run `vault-curl --secrets` or call the myclawbots `list_secrets` tool. **Not** OpenClaw's built-in secrets tool: vault keys are never stored there, so it will always look empty.

## Generate

```bash
python3 /root/.openclaw/skills/gemini-image/scripts/gemini_image.py \
  --prompt "a lobster astronaut, flat illustration, pastel background" \
  --aspect-ratio 1:1
```

## Edit (or use reference images)

```bash
python3 /root/.openclaw/skills/gemini-image/scripts/gemini_image.py \
  --prompt "make the background a sunset beach, keep the product unchanged" \
  --input-image /root/.openclaw/workspace/media/product.png \
  --out /root/.openclaw/workspace/media/product-beach.png
```

Options:

| Option | Meaning |
|---|---|
| `--prompt TEXT` / `--prompt-file FILE` | What to draw or change (long prompts: use a file) |
| `--input-image PATH` | Image to edit or use as a reference; repeat for several (png, jpg, webp, heic; 7 MB total) |
| `--aspect-ratio` | `1:1`, `16:9`, `9:16`, `4:3`, `3:4` (also `2:3`, `3:2`, `4:5`, `5:4`, `21:9`) |
| `--model` | Default `gemini-3.1-flash-image-preview`; `gemini-3-pro-image-preview` for higher quality |
| `--key-env NAME` / `--key mcb_sec_…` | Which saved key to use (default env var `GEMINI_KEY`) |
| `--out PATH` | Where to save (default `/root/.openclaw/workspace/media/gemini-<timestamp>.png`) |

Output is one JSON line:

```json
{"paths":["/root/.openclaw/workspace/media/gemini-20260925T101500Z.png"],"mime":"image/png","note":"Here is your illustration."}
```

With several images the files are named `name-1.png`, `name-2.png`, and so on.

## Rules

- Never `cat` the image or a JSON response, and never base64 an image into the chat. Only the file path goes in the conversation.
- Pass only the surrogate (`mcb_sec_…`) or `--key-env`. The script refuses a real key (exit 3).
- Don't call Gemini with plain `curl`, Python `requests` or an SDK: they send the stand-in and Gemini rejects it.
- Exit codes: `1` the API or vault refused (one line on stderr says why), `2` bad arguments or inputs over 7 MB, `3` no usable key.

## Deliver to the user

The file is on your machine; the user cannot see it until you deliver it. Put one line `MEDIA:<path>` per image in your reply — the paths from `paths`, each on its own line and not in a code block, for example `MEDIA:/root/.openclaw/workspace/media/gemini-20260925T101500Z.png`.

OpenClaw turns each such line into an attachment, in the web chat and in Telegram. Keep `--out` under `/root/.openclaw/workspace/` (the default is): files elsewhere may not be delivered. The `view_image` (View Image) tool shows an image only to you, never to the user — use it to check a result, never to deliver one.

Only if the user asks for a shareable link: call `create_upload_url` with `content_type` set to the `mime` from the output, upload with `curl -X PUT --data-binary @<path> -H "Content-Type: <mime>" "<upload_url>"`, and give them the `public_url` (it expires after 2 hours).

## To post the image

Do the same `create_upload_url` upload, then pass the `public_url` as the media URL to `post_to_social`. Show the user the image and the caption and get an explicit yes before posting.

## Errors

| stderr says | Meaning | What to do |
|---|---|---|
| `HTTP 403: host_not_allowed` | The key's allowed hosts don't include `generativelanguage.googleapis.com` | Ask the user to add that host to the key in Secrets |
| `HTTP 403: unknown_token` | The key was deleted or its stand-in regenerated | Call `list_secrets` again and use the current surrogate |
| `HTTP 403: surrogate_not_allowed_here` | The key isn't allowed in header `x-goog-api-key` | Ask the user to allow header `x-goog-api-key` for the key |
| `HTTP 403: daily_cap_exceeded` | The key's daily call limit is used up | Tell the user; try again tomorrow or ask them to raise the cap |
| `HTTP 403: agent_key_not_bound` | This agent's settings predate the vault | Ask the user to save this agent's settings once (no restart needed) |
| `HTTP 401` (`vault_unauthorized`) | The vault didn't recognise this agent | Tell the user; don't retry |
| `HTTP 400` from Gemini | Prompt blocked by safety filters or malformed | Rephrase the prompt; don't retry the same one |
| `HTTP 429` | Gemini quota, or the vault is busy (`vault_busy`, `vault_rate_limited`) | Wait a minute and retry once |

Never try to print, guess or recover the real key.
