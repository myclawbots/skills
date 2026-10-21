#!/usr/bin/env node
// Renders a carousel deck (JSON) to numbered PNGs.
//
//   node render.js content.example.json out
//   node render.js content.json out --theme neon
//   node render.js content.json out --theme luxury --platform instagram-story
//   node render.js --list-platforms
//
// Every slide is its own page load, so one broken slide can't corrupt the rest.

import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
import { getTheme, listPlatforms } from './src/theme.js';
import { buildHTML } from './src/template.js';

// Runs inside the page. Steps type down until the content stops overflowing,
// which is the failure that actually happens when an agent writes the copy.
const FIT = () => {
  const box = document.querySelector('.body');
  const inner = document.querySelector('.fit');
  const els = [...document.querySelectorAll('[data-fit]')].map((el) => ({
    el,
    size: parseFloat(el.dataset.fit),
    min: parseFloat(el.dataset.min || '12'),
  }));

  const overflows = () =>
    inner.getBoundingClientRect().height > box.clientHeight + 1 ||
    els.some(({ el }) => el.scrollWidth > el.clientWidth + 1);

  let guard = 0;
  while (overflows() && guard++ < 300) {
    let moved = false;
    for (const f of els) {
      if (f.size > f.min) {
        f.size = Math.max(f.min, f.size * 0.97);
        f.el.style.fontSize = f.size + 'px';
        moved = true;
      }
    }
    if (!moved) break;
  }
  return { shrunk: els.some((f) => f.size < parseFloat(f.el.dataset.fit)) };
};

// ── Logo reader ─────────────────────────────────────────────────────
// Reads an image file and returns a base64 data-URI for embedding.
function readLogo(logoPath, jsonDir) {
  if (!logoPath) return null;
  const resolved = path.resolve(jsonDir, logoPath);
  if (!fs.existsSync(resolved)) {
    console.warn(`  ⚠ Logo not found: ${resolved} — rendering without logo`);
    return null;
  }
  const ext = path.extname(resolved).toLowerCase();
  const mime = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp',
  }[ext] || 'image/png';
  const data = fs.readFileSync(resolved);
  return `data:${mime};base64,${data.toString('base64')}`;
}

function parseArgs(argv) {
  const args = argv.slice(2);
  let input = 'content.example.json';
  let outDir = 'out';
  let themeName = 'default';
  let platformName = null;
  let showPlatforms = false;

  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--theme' && args[i + 1]) {
      themeName = args[++i];
    } else if (args[i] === '--platform' && args[i + 1]) {
      platformName = args[++i];
    } else if (args[i] === '--list-platforms') {
      showPlatforms = true;
    } else {
      positional.push(args[i]);
    }
  }
  if (positional[0]) input = positional[0];
  if (positional[1]) outDir = positional[1];

  return { input, outDir, themeName, platformName, showPlatforms };
}

async function main() {
  const { input, outDir, themeName, platformName, showPlatforms } = parseArgs(process.argv);

  // Quick reference: list all supported platforms and exit
  if (showPlatforms) {
    console.log('\nAvailable platforms:\n');
    const table = listPlatforms();
    const pad = (s, n) => String(s).padEnd(n);
    console.log(`  ${pad('Name', 24)} ${pad('Ratio', 8)} ${pad('Base', 14)} Output`);
    console.log(`  ${'-'.repeat(24)} ${'-'.repeat(8)} ${'-'.repeat(14)} ${'-'.repeat(14)}`);
    for (const r of table) {
      console.log(`  ${pad(r.name, 24)} ${pad(r.ratio, 8)} ${pad(`${r.width}×${r.height}`, 14)} ${r.px}`);
    }
    console.log(`\nUsage:  node render.js content.json out --platform instagram-story\n`);
    return;
  }

  const deck = JSON.parse(fs.readFileSync(input, 'utf8'));
  const t = getTheme(themeName, platformName);
  fs.mkdirSync(outDir, { recursive: true });

  // Read logo if provided (path relative to JSON file)
  const jsonDir = path.dirname(path.resolve(input));
  const logoDataURI = readLogo(deck.logo, jsonDir);

  const tags = [];
  if (themeName !== 'default') tags.push(`Theme: ${themeName}`);
  if (platformName) tags.push(`Platform: ${platformName} (${t.width}×${t.height} @${t.scale}x)`);
  if (logoDataURI) tags.push('Logo: ✓');
  if (tags.length) console.log(tags.join('  |  '));

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: t.width, height: t.height },
    deviceScaleFactor: t.scale,
  });

  const written = [];
  for (let i = 0; i < deck.slides.length; i++) {
    const slide = deck.slides[i];
    await page.setContent(
      buildHTML(slide, i, deck, t, themeName, logoDataURI),
      { waitUntil: 'load' },
    );
    await page.evaluate(() => document.fonts.ready);
    const { shrunk } = await page.evaluate(FIT);

    const file = path.join(outDir, `${String(i + 1).padStart(2, '0')}-${slide.type}.png`);
    await page.screenshot({ path: file, type: 'png' });
    written.push(file);
    console.log(`  ${file}${shrunk ? '   (text auto-shrunk to fit)' : ''}`);
  }

  await browser.close();
  console.log(`\n${written.length} slides at ${t.width * t.scale}×${t.height * t.scale}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
