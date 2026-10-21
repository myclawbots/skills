#!/bin/bash
# run.sh — self-bootstrapping renderer. First run installs everything
# (npm deps, Chromium, fonts); every run after just renders. Also self-heals
# after platform image updates (which wipe the Chromium cache on the rootfs).
#
#   bash run.sh <deck.json> <outdir> [--theme neon] [--platform instagram-story]
#   bash run.sh --list-platforms
set -e
cd "$(dirname "$0")"

if [ ! -d node_modules/playwright ]; then
    echo "[setup] installing npm dependencies…"
    npm install --no-audit --no-fund
fi

# Chromium present? (playwright keeps it under ~/.cache/ms-playwright)
if ! node -e 'const {chromium}=require("playwright");const p=chromium.executablePath();require("fs").accessSync(p);' 2>/dev/null; then
    echo "[setup] installing Chromium (~170MB, one-time; re-runs after platform updates)…"
    npx playwright install --with-deps chromium
fi

if [ ! -f fonts/body-medium.woff2 ] && [ ! -d fonts ] || [ -z "$(ls fonts 2>/dev/null)" ]; then
    echo "[setup] fetching fonts…"
    node scripts/get-fonts.js
fi

exec node render.js "$@"
