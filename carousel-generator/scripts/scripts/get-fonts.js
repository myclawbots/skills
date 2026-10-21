// Downloads the two brand typefaces as woff2 so rendering never depends on
// the network or on whatever fonts happen to exist in the container.
// Run once: node scripts/get-fonts.js

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const FONT_DIR = path.join(__dirname, '..', 'fonts');

// Chrome UA so Google Fonts serves woff2 rather than legacy formats.
const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/120.0 Safari/537.36';

const FACES = [
  {
    file: 'display.woff2',
    css: 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,800&display=swap',
    pick: 800,
  },
  {
    file: 'display-regular.woff2',
    css: 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500&display=swap',
    pick: 500,
  },
  {
    file: 'body.woff2',
    css: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400&display=swap',
    pick: 400,
  },
  {
    file: 'body-medium.woff2',
    css: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@600&display=swap',
    pick: 600,
  },
];

async function grab(face) {
  const css = await (await fetch(face.css, { headers: { 'User-Agent': UA } })).text();

  // Keep only the latin block, then take the last src url in it.
  const blocks = css.split('@font-face').filter((b) => b.includes('U+0000-00FF'));
  const block = blocks[blocks.length - 1] || css;
  const url = [...block.matchAll(/url\((https:[^)]+\.woff2)\)/g)].pop();
  if (!url) throw new Error('No woff2 found for ' + face.file);

  const buf = Buffer.from(await (await fetch(url[1])).arrayBuffer());
  fs.writeFileSync(path.join(FONT_DIR, face.file), buf);
  console.log(`  ${face.file}  ${(buf.length / 1024).toFixed(0)} KB`);
}

(async () => {
  fs.mkdirSync(FONT_DIR, { recursive: true });
  console.log('Fetching fonts');
  for (const face of FACES) await grab(face);
  console.log('Done. Fonts live in ./fonts and are embedded at render time.');
})();
