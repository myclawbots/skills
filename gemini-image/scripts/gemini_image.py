#!/usr/bin/env python3
"""
scripts/gemini_image.py
=======================
Generate or edit images with Google Gemini using the user's own Gemini key
from MyClawBots -> Secrets. The agent only holds a surrogate (mcb_sec_...);
the call goes through vault-curl, which swaps in the real key at the
api-proxy. Stdlib only. Spec: docs/secrets-vault.md section 11.1.

Usage:
    python3 /root/.openclaw/skills/gemini-image/scripts/gemini_image.py \
        --prompt "a lobster astronaut, flat illustration" \
        [--prompt-file FILE] [--input-image PATH ...] [--aspect-ratio 1:1] \
        [--model gemini-3.1-flash-image-preview] \
        [--key-env GEMINI_KEY | --key mcb_sec_...] \
        [--out /root/.openclaw/workspace/media/gemini-<utc-timestamp>.png]

stdout: exactly one JSON line {"paths":[...],"mime":"image/png","note":"..."}.
It never contains base64 image data.

Exit codes:
    0  image(s) written
    1  the API or the vault refused the call, or no image came back
    2  bad arguments (missing prompt, unreadable image, inputs over 7 MB)
    3  no usable surrogate key
"""

import argparse
import base64
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

GEMINI_HOST = 'https://generativelanguage.googleapis.com'
DEFAULT_MODEL = 'gemini-3.1-flash-image-preview'
DEFAULT_MEDIA_DIR = '/root/.openclaw/workspace/media'
SURROGATE_RE = re.compile(r'^mcb_sec_[A-Za-z0-9]{32}$')
MODEL_RE = re.compile(r'^[A-Za-z0-9._-]{1,100}$')
# The base64 body must stay under the vault's 10 MB request cap.
MAX_INPUT_BYTES = 7 * 1024 * 1024
MAX_MSG = 300
ASPECT_RATIOS = ['1:1', '16:9', '9:16', '4:3', '3:4', '2:3', '3:2', '4:5', '5:4', '21:9']
INPUT_MIME = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.webp': 'image/webp',
    '.heic': 'image/heic',
    '.heif': 'image/heif',
}
OUTPUT_EXT = {
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/webp': '.webp',
    'image/gif': '.gif',
    'image/heic': '.heic',
    'image/heif': '.heif',
}

NO_KEY_MSG = ('No Gemini key found in MyClawBots → Secrets. Ask the user to add a Google Gemini '
              'key there (name GEMINI_KEY). Never ask them to paste a key into chat.')


def fail(code, msg):
    print(f'gemini-image: {msg}'[:MAX_MSG + 40], file=sys.stderr)
    sys.exit(code)


def one_line(s, limit=MAX_MSG):
    return ' '.join(str(s).split())[:limit]


def live_surrogate(key_env):
    """A key added after this machine booted is not in the env yet. Ask the vault
    for the live listing (surrogates only): the secret named key_env, else the
    only secret allowed to reach the Gemini host. '' when there is none."""
    try:
        out = subprocess.run(vault_curl_cmd() + ['--secrets'], capture_output=True,
                             timeout=30, check=False)
        listing = json.loads(out.stdout.decode('utf-8', 'replace') or '{}')
    except (OSError, subprocess.SubprocessError, ValueError):
        return ''
    secrets = [x for x in listing.get('secrets') or [] if isinstance(x, dict)]
    for x in secrets:
        if x.get('name') == key_env:
            return str(x.get('surrogate') or '')
    host = GEMINI_HOST.split('://', 1)[1]
    gemini = [x for x in secrets if host in (x.get('allowed_hosts') or [])]
    return str(gemini[0].get('surrogate') or '') if len(gemini) == 1 else ''


def resolve_key(args):
    """The surrogate, from --key, the env var named by --key-env, or the vault's
    live listing. Never echoed."""
    key = args.key if args.key is not None else os.environ.get(args.key_env, '')
    key = key.strip()
    if not key and args.key is None:
        key = live_surrogate(args.key_env).strip()
    if not key:
        print(NO_KEY_MSG, file=sys.stderr)
        sys.exit(3)
    if not SURROGATE_RE.match(key):
        fail(3, 'pass the surrogate, not a raw key. Use the mcb_sec_… string from list_secrets '
                '(or --key-env NAME); never ask the user to paste a real key.')
    return key


def vault_curl_cmd():
    found = shutil.which('vault-curl')
    if found:
        return [found]
    # Agents whose pinned image predates vault-curl use the copy shipped here.
    bundled = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vault-curl.sh')
    if os.path.isfile(bundled):
        return ['bash', bundled]
    fail(1, 'vault-curl is not installed on this machine')


def read_prompt(args):
    parts = []
    if args.prompt:
        parts.append(args.prompt)
    if args.prompt_file:
        try:
            with open(args.prompt_file, 'r', encoding='utf-8') as f:
                parts.append(f.read())
        except OSError as e:
            fail(2, f'cannot read --prompt-file: {e.strerror}')
    prompt = '\n\n'.join(p.strip() for p in parts if p and p.strip())
    if not prompt:
        fail(2, 'give --prompt or --prompt-file')
    return prompt


def load_input_images(paths):
    images = []
    total = 0
    for p in paths:
        ext = os.path.splitext(p)[1].lower()
        mime = INPUT_MIME.get(ext)
        if not mime:
            fail(2, f'{os.path.basename(p)}: unsupported image type (use png, jpg, webp, heic)')
        try:
            total += os.path.getsize(p)
        except OSError:
            fail(2, f'{p}: file not found')
        if total > MAX_INPUT_BYTES:
            fail(2, 'input images total more than 7 MB; resize or send fewer')
        images.append((p, mime))
    out = []
    for p, mime in images:
        try:
            with open(p, 'rb') as f:
                out.append((mime, base64.b64encode(f.read()).decode('ascii')))
        except OSError as e:
            fail(2, f'{p}: {e.strerror}')
    return out


def build_body(prompt, images, aspect_ratio):
    parts = [{'text': prompt}]
    for mime, data in images:
        parts.append({'inline_data': {'mime_type': mime, 'data': data}})
    gen = {'responseModalities': ['TEXT', 'IMAGE']}
    if aspect_ratio:
        gen['imageConfig'] = {'aspectRatio': aspect_ratio}
    return {'contents': [{'role': 'user', 'parts': parts}], 'generationConfig': gen}


def default_out():
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return os.path.join(DEFAULT_MEDIA_DIR, f'gemini-{ts}.png')


def error_summary(resp_path):
    """One short line from an error body: the vault reason or Gemini's message."""
    try:
        with open(resp_path, 'r', encoding='utf-8', errors='replace') as f:
            body = json.load(f)
    except (OSError, ValueError):
        return 'no readable error body'
    err = body.get('error') if isinstance(body, dict) else None
    if not isinstance(err, dict):
        return 'no readable error body'
    msg = err.get('message') or err.get('status') or err.get('code') or ''
    reason = err.get('reason')
    if reason:
        # Vault refusal (x-mcb-vault: blocked): {code:'vault_blocked', reason, message}
        return one_line(f'{reason}: {msg}' if msg else reason)
    code = err.get('code')
    if isinstance(code, str) and code and code not in str(msg):
        return one_line(f'{code}: {msg}')
    return one_line(msg) or 'unknown error'


def extract(resp):
    """(images [(mime, b64)], text) from a generateContent response. Skips thought parts."""
    images, texts = [], []
    for cand in resp.get('candidates') or []:
        content = (cand or {}).get('content') or {}
        for part in content.get('parts') or []:
            if not isinstance(part, dict) or part.get('thought'):
                continue
            blob = part.get('inlineData') or part.get('inline_data')
            if isinstance(blob, dict) and blob.get('data'):
                mime = blob.get('mimeType') or blob.get('mime_type') or 'image/png'
                images.append((mime, blob['data']))
            elif isinstance(part.get('text'), str):
                texts.append(part['text'])
    return images, one_line(' '.join(texts))


def output_paths(out, explicit, mimes):
    stem, ext = os.path.splitext(out)
    if len(mimes) == 1:
        # The default name follows the returned type; an explicit --out is kept as given.
        if explicit:
            return [out]
        return [stem + OUTPUT_EXT.get(mimes[0], ext or '.png')]
    return [f'{stem}-{i}{OUTPUT_EXT.get(m, ext or ".png")}' for i, m in enumerate(mimes, 1)]


def main():
    ap = argparse.ArgumentParser(description='Generate or edit images with Gemini via the Secrets vault.')
    ap.add_argument('--prompt')
    ap.add_argument('--prompt-file')
    ap.add_argument('--input-image', action='append', default=[], metavar='PATH',
                    help='image to edit or use as reference (repeatable)')
    ap.add_argument('--aspect-ratio', choices=ASPECT_RATIOS)
    ap.add_argument('--model', default=DEFAULT_MODEL)
    ap.add_argument('--key-env', default='GEMINI_KEY')
    ap.add_argument('--key', help='surrogate (mcb_sec_…) from list_secrets')
    ap.add_argument('--out')
    args = ap.parse_args()

    key = resolve_key(args)
    if not MODEL_RE.match(args.model):
        fail(2, 'invalid --model')
    prompt = read_prompt(args)
    images = load_input_images(args.input_image)
    cmd = vault_curl_cmd()
    out = os.path.abspath(args.out or default_out())

    url = f'{GEMINI_HOST}/v1beta/models/{args.model}:generateContent'
    tmp = tempfile.mkdtemp(prefix='gemini-image-')
    try:
        req_path = os.path.join(tmp, 'req.json')
        resp_path = os.path.join(tmp, 'resp.json')
        with open(req_path, 'w', encoding='utf-8') as f:
            json.dump(build_body(prompt, images, args.aspect_ratio), f)

        # The surrogate goes ONLY in the x-goog-api-key header; anywhere else
        # the vault refuses it (surrogate_not_allowed_here).
        run = cmd + [
            '-sS', '-X', 'POST', url,
            '-H', f'x-goog-api-key: {key}',
            '-H', 'Content-Type: application/json',
            '--data-binary', f'@{req_path}',
            '-o', resp_path,
            '-w', '%{http_code}',
            '--max-time', '150',
        ]
        try:
            proc = subprocess.run(run, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            fail(1, 'request timed out')
        status = (proc.stdout or '').strip()[-3:]
        if not status.isdigit() or status == '000':
            detail = one_line((proc.stderr or '').strip().splitlines()[-1] if proc.stderr.strip() else '')
            fail(1, f'request failed: {detail.replace(key, "<surrogate>") or "no response"}')
        if not status.startswith('2'):
            fail(1, f'HTTP {status}: {error_summary(resp_path).replace(key, "<surrogate>")}')

        try:
            with open(resp_path, 'r', encoding='utf-8') as f:
                resp = json.load(f)
        except (OSError, ValueError):
            fail(1, f'HTTP {status} but the response was not JSON')
        found, note = extract(resp if isinstance(resp, dict) else {})
        if not found:
            fail(1, f'no image returned. Model said: {note or "(nothing)"}')

        paths = output_paths(out, bool(args.out), [m for m, _ in found])
        for (_, data), p in zip(found, paths):
            try:
                raw = base64.b64decode(data)
            except (ValueError, TypeError):
                fail(1, 'the image data in the response could not be decoded')
            os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
            with open(p, 'wb') as f:
                f.write(raw)

        print(json.dumps({'paths': paths, 'mime': found[0][0], 'note': note}))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
