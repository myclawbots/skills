// Design tokens for the carousel. All visual identity lives here.
// Pick a theme with getTheme('neon') etc. Default is the original indigo.
// Pick a platform with getTheme('neon', 'instagram-story') etc.

// ── Theme definitions ───────────────────────────────────────────────

const themes = {
  // ─── Original indigo (unchanged) ──────────────────────────────────
  default: {
    base: '#17123B',
    baseDeep: '#0F0B2A',
    raise: '#241D5C',
    paper: '#F0EEFA',
    muted: '#9C93D6',
    signal: '#FFC24B',
    accent: '#8B7DFF',
    width: 1080,
    height: 1350,
    scale: 2,
  },

  // ─── Neon Gradient — cyberpunk / tech creator ─────────────────────
  neon: {
    base: '#0A0A1A',
    baseDeep: '#050510',
    raise: '#141432',
    paper: '#F0F0FF',
    muted: '#8888CC',
    signal: '#00D4FF',
    accent: '#FF3CAC',
    width: 1080,
    height: 1350,
    scale: 2,
  },

  // ─── Warm Earthy — coaching / wellness ────────────────────────────
  earthy: {
    base: '#FBF7F0',
    baseDeep: '#F3ECE0',
    raise: '#EDE4D4',
    paper: '#3D2C1E',
    muted: '#8B7355',
    signal: '#C45D3E',
    accent: '#5B7553',
    width: 1080,
    height: 1350,
    scale: 2,
  },

  // ─── Bold Brutalist — edgy / thought-leader ──────────────────────
  brutalist: {
    base: '#FFFFFF',
    baseDeep: '#F0F0F0',
    raise: '#E8E8E8',
    paper: '#000000',
    muted: '#555555',
    signal: '#CCFF00',
    accent: '#FF2200',
    width: 1080,
    height: 1350,
    scale: 2,
  },

  // ─── Dark Luxury — premium / executive ────────────────────────────
  luxury: {
    base: '#1A1A1A',
    baseDeep: '#111111',
    raise: '#2A2A2A',
    paper: '#F5F0E6',
    muted: '#9A9080',
    signal: '#D4A853',
    accent: '#2D8B6D',
    width: 1080,
    height: 1350,
    scale: 2,
  },
};

// ── Platform presets ────────────────────────────────────────────────
// Each preset defines { width, height, scale } at the native
// resolution people actually post at. scale=2 for retina crispness.

const platforms = {
  // Instagram
  'instagram-post':      { width: 1080, height: 1080, scale: 2 },  // 1:1 square
  'instagram-portrait':  { width: 1080, height: 1350, scale: 2 },  // 4:5 portrait (default)
  'instagram-landscape': { width: 1080, height:  566, scale: 2 },  // 1.91:1
  'instagram-story':     { width: 1080, height: 1920, scale: 2 },  // 9:16
  'instagram-reel':      { width: 1080, height: 1920, scale: 2 },  // 9:16

  // TikTok
  'tiktok':              { width: 1080, height: 1920, scale: 2 },  // 9:16

  // LinkedIn
  'linkedin-post':       { width: 1080, height: 1080, scale: 2 },  // 1:1
  'linkedin-portrait':   { width: 1080, height: 1350, scale: 2 },  // 4:5
  'linkedin-landscape':  { width: 1200, height:  628, scale: 2 },  // 1.91:1
  'linkedin-story':      { width: 1080, height: 1920, scale: 2 },  // 9:16

  // X (Twitter)
  'x-post':              { width: 1600, height:  900, scale: 2 },  // 16:9
  'x-portrait':          { width: 1080, height: 1350, scale: 2 },  // 4:5
  'x-square':            { width: 1080, height: 1080, scale: 2 },  // 1:1

  // Facebook
  'facebook-post':       { width: 1200, height:  630, scale: 2 },  // 1.91:1
  'facebook-square':     { width: 1080, height: 1080, scale: 2 },  // 1:1
  'facebook-portrait':   { width: 1080, height: 1350, scale: 2 },  // 4:5
  'facebook-story':      { width: 1080, height: 1920, scale: 2 },  // 9:16

  // YouTube
  'youtube-thumbnail':   { width: 1280, height:  720, scale: 2 },  // 16:9
  'youtube-short':       { width: 1080, height: 1920, scale: 2 },  // 9:16
  'youtube-community':   { width: 1080, height: 1080, scale: 2 },  // 1:1

  // Pinterest
  'pinterest':           { width: 1000, height: 1500, scale: 2 },  // 2:3

  // Threads
  'threads-post':        { width: 1080, height: 1350, scale: 2 },  // 4:5
  'threads-square':      { width: 1080, height: 1080, scale: 2 },  // 1:1
};

export function getPlatform(name) {
  const p = platforms[name];
  if (!p) {
    const valid = Object.keys(platforms).join(', ');
    throw new Error(`Unknown platform "${name}". Available:\n  ${valid}`);
  }
  return p;
}

export function listPlatforms() {
  return Object.entries(platforms).map(([name, p]) => ({
    name,
    width: p.width,
    height: p.height,
    ratio: `${p.width / gcd(p.width, p.height)}:${p.height / gcd(p.width, p.height)}`,
    px: `${p.width * p.scale}×${p.height * p.scale}`,
  }));
}

function gcd(a, b) { return b === 0 ? a : gcd(b, a % b); }

/**
 * @param {string} [name='default']    theme key
 * @param {string} [platformName]      optional platform override for dimensions
 */
export function getTheme(name = 'default', platformName) {
  const t = themes[name];
  if (!t) {
    const valid = Object.keys(themes).join(', ');
    throw new Error(`Unknown theme "${name}". Available: ${valid}`);
  }
  if (!platformName) return t;

  const p = getPlatform(platformName);
  return { ...t, width: p.width, height: p.height, scale: p.scale };
}

// Re-export for backward compat — existing code imports { theme }
export const theme = themes.default;

// ── Per-theme CSS overrides ─────────────────────────────────────────

function extraCSS(name, t) {
  switch (name) {
    // ─── Neon: centered, gradient glow, bottom-bar dots, numbered points ─
    case 'neon':
      return `
      .slide {
        padding: 72px 88px 120px;
        text-align: center;
        background:
          radial-gradient(ellipse 80% 50% at 10% 90%, rgba(255,60,172,.18) 0%, transparent 60%),
          radial-gradient(ellipse 70% 40% at 85% 15%, rgba(0,212,255,.15) 0%, transparent 55%),
          radial-gradient(120% 90% at 12% 0%, ${t.raise} 0%, ${t.base} 46%, ${t.baseDeep} 100%);
      }
      h1, h2 {
        max-width: none;
        background: linear-gradient(135deg, ${t.signal} 0%, #7B2FFF 40%, ${t.accent} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      .centered { text-align: center; }
      h1.centered, h2.centered { margin-left: auto; margin-right: auto; }
      .tagline {
        font-size: 36px;
        line-height: 1.4;
        color: ${t.muted};
        margin-top: 36px;
      }
      .tagline.centered { margin-left: auto; margin-right: auto; }

      /* Glow halo behind hook */
      .glow-halo {
        position: absolute;
        top: 30%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 500px;
        height: 500px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(0,212,255,.12) 0%, rgba(255,60,172,.08) 50%, transparent 70%);
        pointer-events: none;
        z-index: 0;
      }

      /* Neon top bar */
      .neon-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 32px;
        font-size: 24px;
        color: ${t.muted};
      }
      .neon-top .topic-tag {
        font-size: 20px;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: ${t.muted};
        opacity: .6;
      }
      .neon-top .handle { font-weight: 600; color: ${t.paper}; }

      /* Bottom bar with dots */
      .bottom-bar {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 40px 88px;
        font-size: 24px;
        color: ${t.muted};
      }
      .bottom-bar .handle { font-weight: 600; color: ${t.paper}; font-size: 24px; }
      .bottom-bar .swipe { color: ${t.signal}; font-weight: 600; }
      .dots {
        display: flex;
        gap: 10px;
        align-items: center;
      }
      .dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: rgba(255,255,255,.12);
        display: block;
      }
      .dot.on { background: ${t.accent}; }
      .dot.here { background: ${t.signal}; box-shadow: 0 0 14px ${t.signal}; }

      /* Numbered points */
      .num-row {
        display: flex;
        align-items: flex-start;
        gap: 48px;
        text-align: left;
      }
      .num-big {
        font-family: Display;
        font-weight: 800;
        font-size: 160px;
        line-height: .78;
        letter-spacing: -.04em;
        background: linear-gradient(135deg, ${t.signal} 0%, ${t.accent} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        flex-shrink: 0;
      }
      .num-big.small { font-size: 72px; }
      .num-content { flex: 1; min-width: 0; }
      .num-content h2 { text-align: left; }
      .num-content .copy { text-align: left; }

      .cta-mark {
        background: linear-gradient(135deg, ${t.signal} 0%, ${t.accent} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      .cta-centered { text-align: center; }
      .figure {
        text-shadow: 0 0 80px rgba(0,212,255,.35), 0 0 160px rgba(0,212,255,.15);
      }
      .quote {
        border-left: none;
        padding-left: 0;
        text-align: center;
        margin-left: 0;
        text-indent: 0;
        max-width: none;
      }
      .quote::before {
        content: '\\201C';
        position: absolute;
        top: -30px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 180px;
        line-height: 1;
        background: linear-gradient(135deg, ${t.signal}, ${t.accent});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        opacity: .2;
        font-family: Display;
        font-weight: 800;
      }
      .attrib { justify-content: center; }
      .foot { display: none; }
      `;

    // ─── Earthy: progress bar, pill tags, card panels ────────────────
    case 'earthy':
      return `
      .slide {
        padding: 52px 88px 84px 88px;
        background:
          radial-gradient(ellipse 100% 80% at 50% 100%, rgba(196,93,62,.06) 0%, transparent 60%),
          linear-gradient(175deg, ${t.base} 0%, ${t.baseDeep} 100%);
      }
      /* warm grain overlay */
      .slide::after {
        content: '';
        position: absolute;
        inset: 0;
        background-image: url("data:image/svg+xml;utf8,${encodeURIComponent(
          '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><filter id="n"><feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4"/></filter><rect width="200" height="200" filter="url(#n)" opacity="0.4"/></svg>'
        )}");
        opacity: .06;
        mix-blend-mode: multiply;
        pointer-events: none;
      }

      /* Progress bar */
      .progress-bar {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: rgba(61,44,30,.08);
        z-index: 10;
      }
      .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, ${t.signal}, ${t.accent});
        border-radius: 0 3px 3px 0;
        transition: width .3s ease;
      }

      /* Pill topic tag */
      .pill {
        display: inline-block;
        background: rgba(61,44,30,.08);
        color: ${t.paper};
        font-size: 22px;
        font-weight: 600;
        padding: 8px 24px;
        border-radius: 100px;
        letter-spacing: .02em;
      }

      /* Earthy top bar */
      .earthy-top {
        margin-top: 24px;
        margin-bottom: 48px;
      }

      /* Card panels */
      .earthy-card {
        background: rgba(61,44,30,.04);
        border: 1px solid rgba(61,44,30,.08);
        border-radius: 24px;
        padding: 56px 48px;
      }
      .list-card {
        padding: 28px 36px;
        margin-bottom: 12px;
      }

      /* Earthy typography contrast */
      p.copy {
        color: ${t.paper};
        opacity: 0.88;
      }
      p.lede {
        color: ${t.muted};
      }
      .list-text {
        color: ${t.paper};
      }
      .action-text {
        color: ${t.signal};
        font-weight: 600;
      }

      /* Earthy hook */
      .earthy-hook { justify-content: flex-end; }
      .earthy-kicker {
        color: ${t.signal};
        font-weight: 600;
        letter-spacing: .04em;
        text-transform: uppercase;
      }
      .earthy-line {
        width: 80px;
        height: 3px;
        background: ${t.signal};
        margin: 32px 0;
        border-radius: 2px;
      }
      .earthy-num {
        color: ${t.signal};
        font-family: Display;
        font-weight: 800;
      }

      h1, h2 { color: ${t.paper}; }
      .figure { color: ${t.signal}; }
      .cta-mark { color: ${t.signal}; }
      .foot { border-top: 2px solid rgba(61,44,30,.1); }
      .foot .handle { color: ${t.paper}; }
      .foot .swipe { color: ${t.signal}; }
      .top b { color: ${t.paper}; }
      .rail { display: none; }
      .quote { font-style: italic; color: ${t.paper}; }
      .attrib::before { background: ${t.accent}; }
      `;

    // ─── Brutalist: raw, oversized, split, no progress ───────────────
    case 'brutalist':
      return `
      .slide {
        background: ${t.base};
        border: 8px solid ${t.paper};
        padding: 72px 72px 72px 72px;
      }
      .slide::before {
        content: '';
        position: absolute;
        top: 24px;
        right: 24px;
        width: 80px;
        height: 80px;
        border: 6px solid ${t.signal};
        transform: rotate(12deg);
        z-index: 0;
      }

      /* No progress indicator */
      .rail { display: none; }
      .top { display: none; }

      /* Massive hook text */
      .brutal-massive {
        font-size: 140px;
        text-transform: uppercase;
        letter-spacing: -.05em;
        line-height: .88;
        max-width: none;
      }
      .brutal-kicker {
        text-transform: uppercase;
        letter-spacing: .1em;
        font-weight: 800;
        color: #111111;
        margin-bottom: 24px;
        background: ${t.signal};
        display: inline-block;
        padding: 4px 12px;
      }
      .brutal-sub {
        text-transform: uppercase;
        letter-spacing: .02em;
        color: #444444;
      }

      /* Split layout for points */
      .brutal-split {
        display: flex;
        align-items: flex-start;
        gap: 48px;
      }
      .brutal-split-num {
        font-family: Display;
        font-weight: 800;
        font-size: 200px;
        line-height: .78;
        letter-spacing: -.04em;
        color: ${t.signal};
        flex-shrink: 0;
        -webkit-text-stroke: 3px #111111;
      }
      .brutal-split-num.small { font-size: 80px; }
      .brutal-split-content { flex: 1; min-width: 0; padding-top: 16px; }

      /* High contrast copy */
      p.lede {
        color: #444444;
      }
      p.copy {
        color: #222222;
        font-weight: 500;
      }
      .list-text {
        color: #111111;
      }
      .action-text {
        color: #111111;
      }

      /* Inverted CTA */
      .brutal-cta-body {
        background: ${t.signal};
        margin: -72px;
        padding: 72px;
        height: calc(100% + 144px);
        display: flex;
        flex-direction: column;
        justify-content: center;
      }
      .brutal-cta-body .cta-mark { color: ${t.paper}; }
      .brutal-cta-body .copy { color: ${t.paper}; opacity: .9; }
      .brutal-cta-body .action-text { color: ${t.paper}; font-weight: 800; }
      .brutal-logo { filter: brightness(0); }

      h1, h2 {
        text-transform: uppercase;
        letter-spacing: -.04em;
        color: ${t.paper};
        max-width: none;
      }
      .figure {
        color: ${t.accent};
        -webkit-text-stroke: 3px ${t.accent};
      }
      .cta-mark {
        color: ${t.signal};
        text-transform: uppercase;
      }
      p.lede, p.copy {
        text-transform: uppercase;
        font-size: 34px;
        letter-spacing: .02em;
        line-height: 1.5;
      }

      /* Brutal footer */
      .brutal-foot {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 24px 72px;
        border-top: 4px solid ${t.paper};
      }
      .brutal-foot .handle { color: ${t.paper}; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; }
      .brutal-foot .swipe { color: #111111; font-weight: 800; text-transform: uppercase; letter-spacing: .04em; background: ${t.signal}; padding: 2px 8px; }
      .foot { display: none; }

      .quote {
        text-transform: uppercase;
        letter-spacing: -.01em;
        border-left: 10px solid ${t.signal};
        padding-left: 36px;
        color: #111111;
      }
      .attrib { text-transform: uppercase; letter-spacing: .06em; font-size: 26px; color: #444444; }
      .attrib::before { background: ${t.accent}; height: 4px; }
      `;

    // ─── Luxury: centered, gold rules, roman numerals ────────────────
    case 'luxury':
      return `
      .slide {
        padding: 72px 100px 72px;
        background:
          radial-gradient(ellipse 60% 50% at 80% 20%, rgba(212,168,83,.06) 0%, transparent 60%),
          radial-gradient(120% 90% at 12% 0%, ${t.raise} 0%, ${t.base} 46%, ${t.baseDeep} 100%);
      }
      .rail { display: none; }

      /* Luxury top */
      .luxury-top {
        margin-bottom: 40px;
      }
      .luxury-topic {
        font-size: 20px;
        letter-spacing: .1em;
        text-transform: uppercase;
        color: ${t.muted};
      }
      .luxury-roman {
        font-family: Display;
        font-weight: 500;
        font-size: 28px;
        letter-spacing: .12em;
        color: ${t.signal};
      }

      /* Gold rules / ornaments */
      .gold-rule {
        width: 80px;
        height: 2px;
        background: linear-gradient(90deg, transparent, ${t.signal}, transparent);
        margin: 32px 0;
      }
      .gold-rule.wide { width: 160px; }
      .gold-ornament {
        font-size: 40px;
        color: ${t.signal};
        letter-spacing: .5em;
        margin: 24px 0;
      }

      /* Centered compositions */
      .luxury-centered {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
      }
      .luxury-headline {
        text-align: center;
        max-width: none;
        letter-spacing: -.015em;
        line-height: .98;
      }
      .luxury-kicker {
        letter-spacing: .12em;
        text-transform: uppercase;
        color: ${t.signal};
        margin-bottom: 16px;
      }
      .luxury-lede {
        text-align: center;
        max-width: 26ch;
        color: ${t.muted};
      }
      .luxury-copy {
        text-align: center;
        max-width: 28ch;
        color: rgba(245,240,230,.75);
      }
      .luxury-cta-mark {
        letter-spacing: -.01em;
      }
      .luxury-handle {
        font-size: 28px;
        color: ${t.signal};
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-top: 24px;
      }
      .luxury-num {
        font-family: Display;
        font-weight: 500;
        color: ${t.signal};
        font-size: 28px;
        letter-spacing: .08em;
        min-width: 60px;
      }
      .luxury-list-item {
        padding: 16px 0;
        border-bottom: 1px solid rgba(212,168,83,.12);
      }
      .luxury-action {
        color: ${t.signal};
        letter-spacing: .06em;
        text-transform: uppercase;
      }

      /* Luxury footer */
      .luxury-foot {
        border-top: 1px solid rgba(212,168,83,.25);
      }
      .luxury-foot .handle { color: ${t.signal}; letter-spacing: .04em; }
      .luxury-foot .swipe { color: ${t.signal}; letter-spacing: .04em; }

      h1 { font-size: 100px; letter-spacing: -.015em; line-height: .98; }
      h2 { font-size: 72px; letter-spacing: -.01em; }
      .figure { color: ${t.signal}; letter-spacing: -.03em; }
      .cta-mark { color: ${t.signal}; letter-spacing: -.01em; }
      p.lede { font-size: 34px; letter-spacing: .01em; line-height: 1.52; }
      p.copy { font-size: 36px; letter-spacing: .005em; line-height: 1.52; color: rgba(245,240,230,.75); }
      .top b { color: ${t.paper}; }
      .quote {
        font-size: 66px;
        line-height: 1.2;
        letter-spacing: -.01em;
        font-style: italic;
        text-align: center;
        border-left: none;
        padding-left: 0;
        margin-left: 0;
        text-indent: 0;
        max-width: none;
      }
      .attrib { justify-content: center; letter-spacing: .04em; text-transform: uppercase; font-size: 24px; }
      .attrib::before { background: ${t.signal}; width: 44px; height: 1px; }
      `;

    default:
      return '';
  }
}

// ── Stylesheet generator ────────────────────────────────────────────

export function css(t, themeName = 'default') {
  return `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html, body {
    width: ${t.width}px;
    height: ${t.height}px;
    overflow: hidden;
    background: ${t.base};
    color: ${t.paper};
    font-family: Body, system-ui, sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: geometricPrecision;
  }

  .slide {
    position: relative;
    width: ${t.width}px;
    height: ${t.height}px;
    display: flex;
    flex-direction: column;
    padding: 96px 88px 84px 132px;
    background:
      radial-gradient(120% 90% at 12% 0%, ${t.raise} 0%, ${t.base} 46%, ${t.baseDeep} 100%);
  }

  /* Signature element: the decode rail. Segments = slides, filled = where
     the reader is. It carries real information, so it earns its place. */
  .rail {
    position: absolute;
    left: 64px;
    top: 96px;
    bottom: 84px;
    width: 6px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .rail i { flex: 1; border-radius: 3px; background: rgba(240,238,250,.14); }
  .rail i.on   { background: ${t.accent}; }
  .rail i.here { background: ${t.signal}; }

  .top {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    font-size: 26px;
    letter-spacing: .01em;
    color: ${t.muted};
    margin-bottom: 64px;
  }
  .top b { font-family: Body; font-weight: 600; color: ${t.paper}; }

  .body {
    flex: 1 1 0;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  /* Inner wrapper exists so the fitter can measure true content height.
     Measuring .body alone misses overflow that spills upward when centred. */
  .fit { display: block; }

  h1 {
    font-family: Display;
    font-weight: 800;
    font-size: 118px;
    line-height: .94;
    letter-spacing: -.03em;
    max-width: 15ch;
  }
  h2 {
    font-family: Display;
    font-weight: 800;
    font-size: 78px;
    line-height: 1.02;
    letter-spacing: -.02em;
    max-width: 17ch;
  }
  p.lede {
    font-size: 38px;
    line-height: 1.42;
    color: ${t.muted};
    max-width: 34ch;
    margin-top: 40px;
  }
  p.copy {
    font-size: 40px;
    line-height: 1.46;
    max-width: 32ch;
    margin-top: 36px;
    color: #DAD5F5;
  }

  /* stat slide */
  .figure {
    font-family: Display;
    font-weight: 800;
    font-size: 260px;
    line-height: .82;
    letter-spacing: -.045em;
    color: ${t.signal};
  }
  .figure small { font-size: .38em; letter-spacing: -.02em; }

  /* quote slide */
  .quote {
    font-family: Display;
    font-weight: 500;
    font-size: 72px;
    line-height: 1.16;
    letter-spacing: -.015em;
    max-width: 20ch;
    margin-left: .42em;
    text-indent: -.42em;
  }
  .attrib {
    margin-top: 48px;
    font-size: 30px;
    color: ${t.muted};
    display: flex;
    align-items: center;
    gap: 18px;
  }
  .attrib::before {
    content: '';
    width: 56px; height: 3px;
    background: ${t.signal};
    display: block;
  }

  /* cta slide */
  .cta-mark {
    font-family: Display;
    font-weight: 800;
    font-size: 96px;
    line-height: 1;
    letter-spacing: -.03em;
    color: ${t.signal};
  }

  .foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 26px;
    color: ${t.muted};
    padding-top: 40px;
    border-top: 2px solid rgba(240,238,250,.12);
  }
  .foot .handle { color: ${t.paper}; font-weight: 600; }
  .foot .swipe { color: ${t.signal}; font-weight: 600; }

  /* ── Logo ── */
  .logo-sm {
    height: 32px;
    width: auto;
    vertical-align: middle;
    margin-right: 12px;
  }
  .logo-lg {
    height: 72px;
    width: auto;
    display: block;
  }
  .cta-logo {
    margin-bottom: 36px;
  }
  .cta-logo.centered {
    display: flex;
    justify-content: center;
  }

  /* ── Kicker ── */
  .kicker {
    font-size: 28px;
    line-height: 1.3;
    color: ${t.muted};
    margin-bottom: 20px;
    letter-spacing: .01em;
  }

  /* ── List slide ── */
  .list-stack {
    margin-top: 36px;
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  .list-item {
    display: flex;
    align-items: flex-start;
    gap: 24px;
  }
  .list-num {
    font-family: Display;
    font-weight: 800;
    font-size: 48px;
    line-height: .9;
    color: ${t.signal};
    flex-shrink: 0;
    min-width: 48px;
  }
  .list-text {
    font-size: 36px;
    line-height: 1.38;
    color: ${t.paper};
    flex: 1;
  }
  .list-row {
    padding: 12px 0;
    border-bottom: 1px solid rgba(240,238,250,.06);
  }

  /* ── Action text ── */
  .action-text {
    font-size: 32px;
    line-height: 1.4;
    color: ${t.signal};
    font-weight: 600;
    margin-top: 32px;
  }
  .action-text.centered { text-align: center; }

  /* ── theme-specific overrides ── */
  ${extraCSS(themeName, t)}
  `;
}
