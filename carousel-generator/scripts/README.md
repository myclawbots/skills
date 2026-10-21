# 🎠 Carousel Studio — Automated Social Carousel Engine

Turns structured JSON decks into publication-ready, retina-crisp PNG carousel slides.

Built for autonomous AI agents and creator workflows. Content in, stunning images out. Your agent only ever writes JSON — Playwright and Vanilla CSS handle typography, layout geometry, font-fitting, and pixel-perfect rendering.

---

## ⚡ Quick Start

### 1. Installation

```bash
# Clone or navigate to the directory
cd carousel

# Install dependencies & Playwright browser
npm install
npx playwright install chromium

# Download Google fonts (one-time setup, inlines local TTF/WOFF2 fonts)
npm run fonts
```

### 2. Render Your First Deck

```bash
# Render default theme (Instagram 4:5 portrait, 2160×2700 @2x)
node render.js content.example.json out/default

# Render trending themes
node render.js content.neon-mythbusting.json out/neon --theme neon
node render.js content.earthy-wishiknew.json out/earthy --theme earthy
node render.js content.brutalist-hottakes.json out/brutalist --theme brutalist
node render.js content.luxury-stepbystep.json out/luxury --theme luxury
```

---

## 🎨 5 Distinct Themes & Layout Engines

Unlike simple color-palette switchers, each theme features its own custom layout frame, typographic hierarchy, and navigation indicators:

| Theme | Vibe & Use Case | Distinct Layout Features | Progress Indicator | CTA Slide Style |
|---|---|---|---|---|
| **`neon`** | Tech, AI, crypto, futuristic creators | Centered headlines, radial glow halo, 2-column split numbered points | Glowing bottom dot rail | Prominent logo + vibrant gradient headline |
| **`earthy`** | Coaching, wellness, business playbooks | Warm beige paper grain, pill topic badges, rounded card containers | Top-edge gradient progress bar | Warm terracotta divider lines + action badge |
| **`brutalist`** | Hot takes, thought leadership, contrarian views | Raw Stark borders, rotated geometric badges, massive uppercase text | No progress bar (raw, unfiltered) | Full-bleed inverted high-contrast screen |
| **`luxury`** | Executive, luxury brands, masterclasses | Centered serif typography, gold gradient divider rules & ornaments | Roman numerals (`I`, `II`, `III`...) | Centered gold branding + executive typography |
| **`default`** | Standard clean tech editorial | Left-aligned editorial hierarchy | Signature left vertical decode rail | Clean tech mark + handle |

---

## 📱 Multi-Platform Sizing Presets

Generate exact dimensions and aspect ratios for all major social networks with the `--platform` flag. All exports are rendered at **2x retina resolution** for crystal-clear text on high-DPI screens:

```bash
# Instagram Story / Reels / TikTok (9:16 — 1080×1920 @2x: 2160×3840)
node render.js content.neon-mythbusting.json out/story --theme neon --platform instagram-story

# LinkedIn Landscape (1.91:1 — 1200×628 @2x: 2400×1256)
node render.js content.example.json out/linkedin --platform linkedin-landscape

# Square Post (1:1 — 1080×1080 @2x: 2160×2160)
node render.js content.luxury-stepbystep.json out/square --theme luxury --platform instagram-post
```

### Supported Platform Presets (`--platform <name>`)

| Platform | Presets Available | Dimensions (1x) | Aspect Ratio |
|---|---|---|---|
| **Instagram** | `instagram-portrait` (default), `instagram-post`, `instagram-landscape`, `instagram-story`, `instagram-reel` | 1080×1350, 1080×1080, 1080×566, 1080×1920 | 4:5, 1:1, 1.91:1, 9:16 |
| **TikTok** | `tiktok` | 1080×1920 | 9:16 |
| **LinkedIn** | `linkedin-portrait`, `linkedin-post`, `linkedin-landscape`, `linkedin-story` | 1080×1350, 1080×1080, 1200×628, 1080×1920 | 4:5, 1:1, 1.91:1, 9:16 |
| **X (Twitter)** | `x-post`, `x-portrait`, `x-square` | 1600×900, 1080×1350, 1080×1080 | 16:9, 4:5, 1:1 |
| **Facebook** | `facebook-post`, `facebook-square`, `facebook-portrait`, `facebook-story` | 1200×630, 1080×1080, 1080×1350, 1080×1920 | 1.91:1, 1:1, 4:5, 9:16 |
| **YouTube** | `youtube-thumbnail`, `youtube-short`, `youtube-community` | 1280×720, 1080×1920, 1080×1080 | 16:9, 9:16, 1:1 |
| **Threads** | `threads-post`, `threads-square` | 1080×1350, 1080×1080 | 4:5, 1:1 |
| **Pinterest** | `pinterest` | 1000×1500 | 2:3 |

To view the complete platform table in your terminal, run:
```bash
node render.js --list-platforms
```

---

## 🏷️ Brand Logo Support

Add your brand logo directly to your deck JSON:

```json
{
  "topic": "AI engineering",
  "handle": "@lemmedecode",
  "logo": "./assets/logo.svg",
  "slides": [ ... ]
}
```

- **File Types**: Supports `.svg`, `.png`, `.jpg`, `.webp`.
- **Paths**: Resolved relative to the JSON file path (e.g. `./assets/logo.svg`).
- **Embedding**: Encoded into offline Base64 data-URIs before rendering.
- **Placement**: Automatically rendered in the top header and prominently on the CTA slide.
- **Graceful Fallback**: If the logo field is omitted or file is missing, headers seamlessly fall back to topic wordmarks without broken image tags.

---

## 📄 The Deck JSON Specification

This JSON contract is what your agent or application generates:

```json
{
  "topic": "AI news",
  "handle": "@lemmedecode",
  "logo": "./assets/logo.svg",
  "slides": [
    {
      "type": "hook",
      "kicker": "TECH REALITY CHECK",
      "headline": "5 AI myths that need to die",
      "sub": "You've heard them all. Most of them are wrong."
    },
    {
      "type": "point",
      "headline": "Prompt engineering is not coding",
      "body": "Natural language is ambiguous by default. Code is precise. Writing English to an LLM will never replace architecture."
    },
    {
      "type": "stat",
      "figure": "92",
      "unit": "%",
      "body": "of enterprise AI pilots fail to reach production without structured evaluation loops."
    },
    {
      "type": "list",
      "headline": "What actually moves the needle",
      "items": [
        "High-fidelity prompt architecture",
        "Deterministic guardrails & eval sets",
        "Tight human-in-the-loop loops"
      ]
    },
    {
      "type": "quote",
      "quote": "The best code is the code you never had to write.",
      "source": "Software Engineering Axiom"
    },
    {
      "type": "cta",
      "headline": "Stop prompting. Start engineering.",
      "body": "Subscribe to Decode for weekly deep dives into production AI architectures.",
      "action": "follow"
    }
  ]
}
```

### Slide Types & Properties

| Slide `type` | Supported Properties | Description & Best Practice |
|---|---|---|
| **`hook`** | `headline`, `sub`, `kicker` (optional) | Slide 1. The scroll stopper. Use `kicker` for category/context tags. |
| **`point`** | `headline`, `body` | The core thesis or step. One clear idea per slide. |
| **`stat`** | `figure`, `unit`, `body` | Highlights a data point. Keep `figure` short (e.g., `92`, `10x`, `4.8`). |
| **`list`** | `headline` (optional), `items` (array of strings) | Step-by-step frameworks, bullet points, or checklists (3-5 items). |
| **`quote`** | `quote`, `source` | Emphasizes a strong principle, quote, or controversial hot take. |
| **`cta`** | `headline`, `body`, `action` (optional) | Final slide. Drives engagement (follow, save, share, click link). |

### Smart CTA Actions (`"action"`)

The `"action"` field in `cta` slides supports smart shortcuts or custom strings:

- `"action": "follow"` → Displays `FOLLOW @handle FOR MORE`
- `"action": "save"` → Displays `💾 Save this for later`
- `"action": "share"` → Displays `Share with someone who needs this`
- `"action": "link"` → Displays `Link in bio`
- Or pass any custom text (e.g., `"action": "Join 15,000+ engineers at lemmedecode.com"`).

---

## 📏 Character Budgets (For AI Prompting)

The renderer features dynamic JavaScript-based text fitting (`FIT()`): if text overflows, it auto-scales down to fit. However, keeping within recommended character limits ensures maximum visual punch and legibility:

- **`hook.kicker`**: 15–30 chars
- **`hook.headline`**: 30–50 chars
- **`hook.sub`**: 60–90 chars
- **`point.headline`**: 35–55 chars
- **`point.body`**: 90–140 chars
- **`stat.figure`**: 2–5 chars
- **`stat.unit`**: 1–3 chars
- **`stat.body`**: 70–110 chars
- **`list.items`**: 3–5 items, 30–60 chars each
- **`quote.quote`**: 60–100 chars
- **`quote.source`**: 20–40 chars
- **`cta.headline`**: 25–45 chars
- **`cta.body`**: 70–120 chars

---

## 🤖 Wiring Up an LLM Agent

Prompt your LLM with the specification above and instruct it to return strictly raw JSON without markdown prose or backtick wrappers:

```javascript
import fs from 'node:fs';
import { execSync } from 'node:child_process';

// 1. Sanitize model response
const rawJson = modelOutput.replace(/```json|```/g, '').trim();
const deck = JSON.parse(rawJson);

// 2. Write to temporary deck file
fs.writeFileSync('deck.json', JSON.stringify(deck, null, 2));

// 3. Render high-res slides with desired theme and platform
execSync('node render.js deck.json ./dist/carousel --theme neon --platform instagram-portrait');
```

---

## 🛠️ Project Structure

```
carousel/
├── assets/
│   └── logo.svg                 # Brand vector logo asset
├── content.example.json         # Base tech editorial sample deck
├── content.neon-mythbusting.json# Neon / Cyberpunk sample deck
├── content.earthy-wishiknew.json# Earthy / Coaching sample deck
├── content.brutalist-hottakes.json # Brutalist / Hot takes sample deck
├── content.luxury-stepbystep.json  # Luxury / Executive sample deck
├── fonts/                       # Local fonts inlined as Base64
├── render.js                    # CLI & Playwright batch rendering engine
├── scripts/
│   └── get-fonts.js             # Font download and base64 helper
└── src/
    ├── template.js              # Multi-theme HTML layout generators & shells
    └── theme.js                 # Design tokens, platform presets, and CSS engine
```

---

## 💡 Rendering Reliability & Offline Features

- **Base64 Inlined Fonts & Assets**: Fonts and logos are embedded directly as base64 data-URIs, ensuring zero external network dependency at render time.
- **Isolated Page Contexts**: Each slide renders in an isolated DOM page context to prevent cascading layout corruption.
- **Font Ready Synchronization**: Playwright explicitly waits for `document.fonts.ready` before capturing screenshots, eliminating intermittent font flashes or fallback typography.
- **Automated Text Fitting**: Embedded `data-fit` bounding box algorithm automatically downscales fonts when content exceeds slide container height.
