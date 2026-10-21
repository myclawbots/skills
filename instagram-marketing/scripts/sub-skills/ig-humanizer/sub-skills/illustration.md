# Sub-skill: Generate an illustration for an Instagram post

Adds an optional image to a draft (feed image, carousel slide, or quote-card)
and attaches it on publish. Everything here is first-party: slides come from
**`carousel-generator`**, single images from **`gemini-api`** or DALL-E, and the
file reaches Instagram through `create_upload_url` + `post_to_social`.

## When this runs

- User says "add an image", "make an illustration", "make a quote-card", or
  "make a carousel" for an Instagram post.
- Offer it once after a draft is approved, when a visual would lift reach.
- Instagram rejects text-only posts, so if the user has no media of their own,
  this is not a nicety — it is the difference between publishable and not.

## Pick the path

| What you need | Use |
|---|---|
| 2-10 branded carousel slides from a plan | `carousel-generator` |
| A single generated feed image or quote-card | `gemini-api` (Imagen) or DALL-E 3 |
| The user's own photo | it is already on this machine under `/tmp` |

### Ask before spending

Image generation bills the user's own key. **Ask which provider before
generating**, unless they have already said:

> I can generate the image with:
> 1. **Google Gemini Imagen** — ~$0.025/image, and it can edit an existing photo
> 2. **OpenAI DALL-E 3** — ~$0.04/image, strong on lifestyle and product shots
> 3. **Your own photo** — I'll work with what you have
>
> Which would you like?

If only one key is set, say so and use it. If neither is, offer path 3 and the
copy-paste fallback. Never silently pick the expensive one, and never generate
a second image to "try something" without asking.

## Carousel slides — `carousel-generator`

Write the deck as JSON (slide types: `hook`, `point`, `stat`, `list`, `quote`,
`cta`), then render:

```bash
cd /root/.openclaw/skills/carousel-generator/scripts
bash run.sh deck.json out --theme neon --platform instagram-portrait
```

- `--platform instagram-portrait` is the 4:5 frame that fills the Instagram
  feed. `instagram-story` for 9:16.
- Themes: `default`, `neon`, `earthy`, `brutalist`, `luxury`. Pick from the
  user's brand, not at random.
- Set `handle` and `logo` in the deck from Voice & Brand Profile section 6 so
  every slide is stamped consistently.
- Output lands in `out/NN-<type>.png` at 2x retina, already in slide order.

First run installs Chromium and fonts (a few minutes); every run after is
immediate. Tell the user that once, so a slow first render does not read as a
hang.

## Single image — Gemini or DALL-E

1. **Craft the prompt.** Subject, composition, style, palette. Default to a
   clean professional look unless Voice & Brand Profile section 6 sets a visual
   style. **Do not bake the post's words into the art** — generated lettering
   comes out mangled. Put real text on the image as an overlay instead, or use
   `carousel-generator`'s `quote` slide, which typesets it properly.
2. **Aspect ratio.** 4:5 portrait for the feed (it takes the most screen), 1:1
   square, 9:16 for a story or Reel cover.
3. **Generate** with the `gemini-image` skill, or the OpenAI images API through
   `vault-curl` with `-H "Authorization: Bearer $OPENAI_KEY"` (`$OPENAI_KEY` is a
   stand-in for the user's key; it only works through `vault-curl`, and only in
   that header). Never print a key. A key added after you started: run
   `vault-curl --secrets` and use its `surrogate` string in place of `$OPENAI_KEY`.
   Agents not yet moved to the vault may instead have real keys in the
   `GEMINI_API_KEY` / `OPENAI_API_KEY` variables: use those with plain `curl`,
   in the same header (`x-goog-api-key` for Gemini, `Authorization: Bearer` for
   OpenAI). Never print a key.

## Attach it

Generated files land on this machine, so they go through the normal flow:

```
create_upload_url  ->  curl -X PUT --data-binary @image.png ...  ->  post_to_social
```

Pass a single image as `media_url`, 2-10 slides as `media_urls` in order. Staged
URLs live ~2h, so post promptly after staging. Full flow:
`../../../references/media-workflow.md`.

## Refining instead of regenerating

When the user wants a tweak ("darker background", "swap the headline", "more
whitespace"):

- **Carousel slides** — edit the JSON deck and re-render. It is free and
  deterministic, so never regenerate slides with an image model to fix text.
- **Generated images** — Gemini can edit an existing image rather than starting
  over, which is cheaper and keeps the composition. Reach for that before a
  fresh generation.

## Hard rules

- Ask which provider before spending the user's credits; never upgrade to a
  pricier model on your own.
- Real words belong in a typeset overlay or a `quote` slide, never in the image
  prompt.
- Generate one image per request. For carousel slides use `carousel-generator`,
  not N separate generations.
- **Never attach an image the user has not seen and approved.**
- If generation fails or no key is set, draft the prompt and hand it over. It
  never blocks the draft.
