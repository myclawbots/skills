import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { theme as defaultTheme, css } from './theme.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const FONT_DIR = path.join(__dirname, '..', 'fonts');

// ── Fonts (base64 inlined for offline rendering) ────────────────────
const b64 = (f) => fs.readFileSync(path.join(FONT_DIR, f)).toString('base64');
let fontCss = null;
function fonts() {
  if (fontCss) return fontCss;
  const face = (family, file, weight) =>
    `@font-face{font-family:${family};font-weight:${weight};font-display:block;` +
    `src:url(data:font/woff2;base64,${b64(file)}) format('woff2');}`;
  fontCss = [
    face('Display', 'display.woff2', 800),
    face('Display', 'display-regular.woff2', 500),
    face('Body', 'body.woff2', 400),
    face('Body', 'body-medium.woff2', 600),
  ].join('\n');
  return fontCss;
}

// ── Helpers ──────────────────────────────────────────────────────────
const esc = (s = '') =>
  String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function logoTag(dataURI, cls = 'logo') {
  if (!dataURI) return '';
  return `<img class="${cls}" src="${dataURI}" alt="" />`;
}

function ctaAction(action, deck) {
  if (!action) return '';
  switch (action) {
    case 'follow':  return `Follow ${esc(deck.handle)} for more`;
    case 'save':    return '💾 Save this for later';
    case 'share':   return 'Share with someone who needs this';
    case 'link':    return esc(deck.link || '');
    default:        return esc(action);
  }
}

function toRoman(n) {
  const map = [[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']];
  let r = '';
  for (const [v, s] of map) { while (n >= v) { r += s; n -= v; } }
  return r;
}

// ── Progress indicators ─────────────────────────────────────────────

function verticalRail(index, total) {
  const seg = Array.from({ length: total }, (_, i) => {
    const cls = i < index ? 'on' : i === index ? 'here' : '';
    return `<i class="${cls}"></i>`;
  }).join('');
  return `<div class="rail">${seg}</div>`;
}

function horizontalDots(index, total) {
  const dots = Array.from({ length: total }, (_, i) => {
    const cls = i < index ? 'on' : i === index ? 'here' : '';
    return `<i class="dot ${cls}"></i>`;
  }).join('');
  return `<div class="dots">${dots}</div>`;
}

function progressBar(index, total) {
  const pct = ((index + 1) / total * 100).toFixed(1);
  return `<div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  DEFAULT LAYOUTS  — left-aligned, vertical rail
// ═══════════════════════════════════════════════════════════════════

const defaultLayouts = {
  hook: (s, ctx) => `
    <div class="body"><div class="fit">
      ${s.kicker ? `<p class="kicker" data-fit="28" data-min="18">${esc(s.kicker)}</p>` : ''}
      <h1 data-fit="118" data-min="66">${esc(s.headline)}</h1>
      ${s.sub ? `<p class="lede" data-fit="38" data-min="28">${esc(s.sub)}</p>` : ''}
    </div></div>`,

  point: (s, ctx) => `
    <div class="body"><div class="fit">
      <h2 data-fit="78" data-min="46">${esc(s.headline)}</h2>
      ${s.body ? `<p class="copy" data-fit="40" data-min="28">${esc(s.body)}</p>` : ''}
    </div></div>`,

  stat: (s, ctx) => `
    <div class="body"><div class="fit">
      <div class="figure" data-fit="260" data-min="120">${esc(s.figure)}${
        s.unit ? `<small>${esc(s.unit)}</small>` : ''
      }</div>
      ${s.body ? `<p class="copy" data-fit="40" data-min="28">${esc(s.body)}</p>` : ''}
    </div></div>`,

  quote: (s, ctx) => `
    <div class="body"><div class="fit">
      <div class="quote" data-fit="72" data-min="42">&ldquo;${esc(s.quote)}&rdquo;</div>
      ${s.source ? `<div class="attrib">${esc(s.source)}</div>` : ''}
    </div></div>`,

  cta: (s, ctx) => {
    const actionLine = s.action ? `<p class="action-text" data-fit="32" data-min="22">${ctaAction(s.action, ctx.deck)}</p>` : '';
    return `
    <div class="body"><div class="fit">
      ${ctx.logo ? `<div class="cta-logo">${logoTag(ctx.logo, 'logo-lg')}</div>` : ''}
      <div class="cta-mark" data-fit="96" data-min="56">${esc(s.headline)}</div>
      ${s.body ? `<p class="copy" data-fit="40" data-min="28">${esc(s.body)}</p>` : ''}
      ${actionLine}
    </div></div>`;
  },

  list: (s, ctx) => {
    const items = (s.items || []).map((item, i) =>
      `<div class="list-item">
        <span class="list-num">${i + 1}</span>
        <span class="list-text" data-fit="36" data-min="24">${esc(item)}</span>
      </div>`
    ).join('');
    return `
    <div class="body"><div class="fit">
      ${s.headline ? `<h2 data-fit="68" data-min="42">${esc(s.headline)}</h2>` : ''}
      <div class="list-stack">${items}</div>
    </div></div>`;
  },
};

// ── Default shell ───────────────────────────────────────────────────

function defaultShell(content, ctx) {
  const swipe = ctx.isLast ? '' : `<span class="swipe">Swipe</span>`;
  return `
  <div class="slide">
    ${verticalRail(ctx.index, ctx.total)}
    <div class="top">
      <span>${ctx.logo ? logoTag(ctx.logo, 'logo-sm') + ' ' : ''}${esc(ctx.deck.topic || '')}</span>
      <span>${ctx.index + 1}<b> / ${ctx.total}</b></span>
    </div>
    ${content}
    <div class="foot">
      <span class="handle">${esc(ctx.deck.handle || '')}</span>
      ${swipe}
    </div>
  </div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  NEON  — centered, immersive, bottom dot nav, numbered points
// ═══════════════════════════════════════════════════════════════════

const neonLayouts = {
  hook: (s, ctx) => `
    <div class="body"><div class="fit">
      <div class="glow-halo"></div>
      ${s.kicker ? `<p class="kicker centered" data-fit="28" data-min="18">${esc(s.kicker)}</p>` : ''}
      <h1 class="centered" data-fit="118" data-min="60">${esc(s.headline)}</h1>
      ${s.sub ? `<p class="tagline centered" data-fit="36" data-min="24">${esc(s.sub)}</p>` : ''}
    </div></div>`,

  point: (s, ctx) => {
    // Find this point's number among all points in the deck
    const pointSlides = ctx.deck.slides.filter(sl => sl.type === 'point');
    const pointIdx = pointSlides.indexOf(s) + 1 || (ctx.index);
    const num = String(pointIdx).padStart(2, '0');
    return `
    <div class="body"><div class="fit">
      <div class="num-row">
        <span class="num-big">${num}</span>
        <div class="num-content">
          <h2 data-fit="64" data-min="40">${esc(s.headline)}</h2>
          ${s.body ? `<p class="copy" data-fit="34" data-min="24">${esc(s.body)}</p>` : ''}
        </div>
      </div>
    </div></div>`;
  },

  cta: (s, ctx) => {
    const actionLine = s.action
      ? `<p class="action-text centered" data-fit="32" data-min="22">${ctaAction(s.action, ctx.deck)}</p>`
      : '';
    return `
    <div class="body"><div class="fit cta-centered">
      ${ctx.logo ? `<div class="cta-logo centered">${logoTag(ctx.logo, 'logo-lg')}</div>` : ''}
      <div class="cta-mark centered" data-fit="84" data-min="48">${esc(s.headline)}</div>
      ${s.body ? `<p class="tagline centered" data-fit="34" data-min="24">${esc(s.body)}</p>` : ''}
      ${actionLine}
    </div></div>`;
  },

  list: (s, ctx) => {
    const items = (s.items || []).map((item, i) =>
      `<div class="num-row list-row">
        <span class="num-big small">${String(i + 1).padStart(2, '0')}</span>
        <span class="list-text" data-fit="34" data-min="22">${esc(item)}</span>
      </div>`
    ).join('');
    return `
    <div class="body"><div class="fit">
      ${s.headline ? `<h2 class="centered" data-fit="64" data-min="38">${esc(s.headline)}</h2>` : ''}
      <div class="list-stack">${items}</div>
    </div></div>`;
  },
};

function neonShell(content, ctx) {
  const swipe = ctx.isLast ? '' : `<span class="swipe">Swipe →</span>`;
  return `
  <div class="slide">
    <div class="neon-top">
      ${ctx.logo ? logoTag(ctx.logo, 'logo-sm') : `<span class="handle">${esc(ctx.deck.handle || '')}</span>`}
      <span class="topic-tag">${esc(ctx.deck.topic || '')}</span>
    </div>
    ${content}
    <div class="bottom-bar">
      <span class="handle">${esc(ctx.deck.handle || '')}</span>
      ${horizontalDots(ctx.index, ctx.total)}
      ${swipe}
    </div>
  </div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  EARTHY  — warm, card panels, progress bar at top, pill tags
// ═══════════════════════════════════════════════════════════════════

const earthyLayouts = {
  hook: (s, ctx) => `
    <div class="body earthy-hook"><div class="fit">
      ${s.kicker ? `<p class="kicker earthy-kicker" data-fit="26" data-min="18">${esc(s.kicker)}</p>` : ''}
      <h1 data-fit="108" data-min="60">${esc(s.headline)}</h1>
      ${s.sub ? `<p class="lede" data-fit="36" data-min="26">${esc(s.sub)}</p>` : ''}
      <div class="earthy-line"></div>
    </div></div>`,

  point: (s, ctx) => `
    <div class="body"><div class="fit">
      <div class="earthy-card">
        <h2 data-fit="68" data-min="42">${esc(s.headline)}</h2>
        ${s.body ? `<p class="copy" data-fit="36" data-min="26">${esc(s.body)}</p>` : ''}
      </div>
    </div></div>`,

  cta: (s, ctx) => {
    const actionLine = s.action
      ? `<p class="action-text" data-fit="30" data-min="20">${ctaAction(s.action, ctx.deck)}</p>`
      : '';
    return `
    <div class="body"><div class="fit">
      ${ctx.logo ? `<div class="cta-logo">${logoTag(ctx.logo, 'logo-lg')}</div>` : ''}
      <div class="earthy-line"></div>
      <div class="cta-mark" data-fit="80" data-min="48">${esc(s.headline)}</div>
      ${s.body ? `<p class="copy" data-fit="34" data-min="24">${esc(s.body)}</p>` : ''}
      ${actionLine}
      <div class="earthy-line"></div>
    </div></div>`;
  },

  list: (s, ctx) => {
    const items = (s.items || []).map((item, i) =>
      `<div class="earthy-card list-card">
        <span class="list-num earthy-num">${i + 1}.</span>
        <span class="list-text" data-fit="34" data-min="22">${esc(item)}</span>
      </div>`
    ).join('');
    return `
    <div class="body"><div class="fit">
      ${s.headline ? `<h2 data-fit="64" data-min="38">${esc(s.headline)}</h2>` : ''}
      <div class="list-stack">${items}</div>
    </div></div>`;
  },
};

function earthyShell(content, ctx) {
  const swipe = ctx.isLast ? '' : `<span class="swipe">Swipe →</span>`;
  return `
  <div class="slide">
    ${progressBar(ctx.index, ctx.total)}
    <div class="top earthy-top">
      <span class="pill">${esc(ctx.deck.topic || '')}</span>
      ${ctx.logo ? logoTag(ctx.logo, 'logo-sm') : `<span>${ctx.index + 1}<b> / ${ctx.total}</b></span>`}
    </div>
    ${content}
    <div class="foot">
      <span class="handle">${esc(ctx.deck.handle || '')}</span>
      ${swipe}
    </div>
  </div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  BRUTALIST  — raw, oversized, split layouts, no progress indicator
// ═══════════════════════════════════════════════════════════════════

const brutalistLayouts = {
  hook: (s, ctx) => `
    <div class="body"><div class="fit">
      ${s.kicker ? `<p class="kicker brutal-kicker" data-fit="30" data-min="20">${esc(s.kicker)}</p>` : ''}
      <h1 class="brutal-massive" data-fit="140" data-min="72">${esc(s.headline)}</h1>
      ${s.sub ? `<p class="lede brutal-sub" data-fit="36" data-min="24">${esc(s.sub)}</p>` : ''}
    </div></div>`,

  point: (s, ctx) => {
    const pointSlides = ctx.deck.slides.filter(sl => sl.type === 'point');
    const pointIdx = pointSlides.indexOf(s) + 1 || ctx.index;
    return `
    <div class="body"><div class="fit">
      <div class="brutal-split">
        <div class="brutal-split-num">${String(pointIdx).padStart(2, '0')}</div>
        <div class="brutal-split-content">
          <h2 data-fit="72" data-min="42">${esc(s.headline)}</h2>
          ${s.body ? `<p class="copy" data-fit="36" data-min="24">${esc(s.body)}</p>` : ''}
        </div>
      </div>
    </div></div>`;
  },

  cta: (s, ctx) => {
    const actionLine = s.action
      ? `<p class="action-text brutal-action" data-fit="36" data-min="22">${ctaAction(s.action, ctx.deck)}</p>`
      : '';
    return `
    <div class="body brutal-cta-body"><div class="fit">
      ${ctx.logo ? `<div class="cta-logo">${logoTag(ctx.logo, 'logo-lg brutal-logo')}</div>` : ''}
      <div class="cta-mark" data-fit="100" data-min="56">${esc(s.headline)}</div>
      ${s.body ? `<p class="copy" data-fit="36" data-min="24">${esc(s.body)}</p>` : ''}
      ${actionLine}
    </div></div>`;
  },

  list: (s, ctx) => {
    const items = (s.items || []).map((item, i) =>
      `<div class="brutal-split list-row">
        <div class="brutal-split-num small">${String(i + 1).padStart(2, '0')}</div>
        <span class="list-text" data-fit="34" data-min="22">${esc(item)}</span>
      </div>`
    ).join('');
    return `
    <div class="body"><div class="fit">
      ${s.headline ? `<h2 data-fit="68" data-min="40">${esc(s.headline)}</h2>` : ''}
      <div class="list-stack">${items}</div>
    </div></div>`;
  },
};

function brutalistShell(content, ctx) {
  return `
  <div class="slide">
    ${content}
    <div class="foot brutal-foot">
      <span class="handle">${esc(ctx.deck.handle || '')}</span>
      ${ctx.isLast ? '' : `<span class="swipe">SWIPE →</span>`}
    </div>
  </div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  LUXURY  — centered, gold rules, roman numerals, elegant
// ═══════════════════════════════════════════════════════════════════

const luxuryLayouts = {
  hook: (s, ctx) => `
    <div class="body"><div class="fit luxury-centered">
      <div class="gold-rule"></div>
      ${s.kicker ? `<p class="kicker luxury-kicker" data-fit="24" data-min="16">${esc(s.kicker)}</p>` : ''}
      <h1 class="luxury-headline" data-fit="100" data-min="56">${esc(s.headline)}</h1>
      <div class="gold-rule"></div>
      ${s.sub ? `<p class="lede luxury-lede" data-fit="34" data-min="24">${esc(s.sub)}</p>` : ''}
    </div></div>`,

  point: (s, ctx) => `
    <div class="body"><div class="fit luxury-centered">
      <div class="gold-ornament">&mdash;</div>
      <h2 class="luxury-headline" data-fit="72" data-min="42">${esc(s.headline)}</h2>
      <div class="gold-ornament">&mdash;</div>
      ${s.body ? `<p class="copy luxury-copy" data-fit="36" data-min="26">${esc(s.body)}</p>` : ''}
    </div></div>`,

  cta: (s, ctx) => {
    const actionLine = s.action
      ? `<p class="action-text luxury-action" data-fit="30" data-min="20">${ctaAction(s.action, ctx.deck)}</p>`
      : '';
    return `
    <div class="body"><div class="fit luxury-centered">
      ${ctx.logo ? `<div class="cta-logo centered">${logoTag(ctx.logo, 'logo-lg')}</div>` : ''}
      <div class="gold-rule wide"></div>
      <div class="cta-mark luxury-cta-mark" data-fit="80" data-min="48">${esc(s.headline)}</div>
      ${s.body ? `<p class="copy luxury-copy" data-fit="34" data-min="24">${esc(s.body)}</p>` : ''}
      ${actionLine}
      <div class="gold-rule wide"></div>
      <p class="luxury-handle">${esc(ctx.deck.handle || '')}</p>
    </div></div>`;
  },

  list: (s, ctx) => {
    const items = (s.items || []).map((item, i) =>
      `<div class="list-item luxury-list-item">
        <span class="list-num luxury-num">${toRoman(i + 1)}</span>
        <span class="list-text" data-fit="34" data-min="22">${esc(item)}</span>
      </div>`
    ).join('');
    return `
    <div class="body"><div class="fit luxury-centered">
      ${s.headline ? `<h2 class="luxury-headline" data-fit="64" data-min="38">${esc(s.headline)}</h2>` : ''}
      <div class="gold-rule"></div>
      <div class="list-stack">${items}</div>
    </div></div>`;
  },
};

function luxuryShell(content, ctx) {
  const roman = toRoman(ctx.index + 1);
  const swipe = ctx.isLast ? '' : `<span class="swipe">Swipe</span>`;
  const footHandle = ctx.isLast ? '' : `<span class="handle">${esc(ctx.deck.handle || '')}</span>`;
  const footBorder = ctx.isLast ? 'style="border-top:none;"' : '';
  return `
  <div class="slide">
    <div class="top luxury-top">
      ${ctx.logo ? logoTag(ctx.logo, 'logo-sm') : `<span class="luxury-topic">${esc(ctx.deck.topic || '')}</span>`}
      <span class="luxury-roman">${roman}</span>
    </div>
    ${content}
    <div class="foot luxury-foot" ${footBorder}>
      ${footHandle}
      ${swipe}
    </div>
  </div>`;
}

// ═══════════════════════════════════════════════════════════════════
//  REGISTRY  — maps theme names to their overrides
// ═══════════════════════════════════════════════════════════════════

const themeLayoutMap = {
  neon:      neonLayouts,
  earthy:    earthyLayouts,
  brutalist: brutalistLayouts,
  luxury:    luxuryLayouts,
};

const shellMap = {
  default:   defaultShell,
  neon:      neonShell,
  earthy:    earthyShell,
  brutalist: brutalistShell,
  luxury:    luxuryShell,
};

// ═══════════════════════════════════════════════════════════════════
//  buildHTML  — public entry point
// ═══════════════════════════════════════════════════════════════════

/**
 * @param {object} slide          slide data
 * @param {number} index          0-based slide index
 * @param {object} deck           full deck JSON
 * @param {object} [themeObj]     theme tokens (default: original indigo)
 * @param {string} [themeName]    theme key for per-theme CSS overrides
 * @param {string} [logoDataURI]  base64 data-URI for the logo image
 */
export function buildHTML(slide, index, deck, themeObj, themeName, logoDataURI) {
  const t = themeObj || defaultTheme;
  const tName = themeName || 'default';

  // Merge theme-specific layouts over defaults
  const layouts = { ...defaultLayouts, ...(themeLayoutMap[tName] || {}) };
  const layout = layouts[slide.type];
  if (!layout) throw new Error(`Unknown slide type "${slide.type}"`);

  const total = deck.slides.length;
  const isLast = index === total - 1;
  const ctx = { index, total, deck, themeObj: t, themeName: tName, logo: logoDataURI, isLast };

  const content = layout(slide, ctx);
  const shell = shellMap[tName] || defaultShell;
  const html = shell(content, ctx);

  return `<!doctype html><html><head><meta charset="utf-8">
<style>${fonts()}${css(t, tName)}</style></head><body>
${html}
</body></html>`;
}
