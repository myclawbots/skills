#!/usr/bin/env python3
"""
edit_photo.py — turn a product photo into a new image with Gemini.

Stdlib only (no pip installs). Calls Gemini's generateContent REST endpoint
with the product photo inline plus a text instruction, and writes every image
Gemini returns next to --out.

    python3 edit_photo.py --input /tmp/hat.jpg \
        --prompt "Worn outdoors on a ranch at golden hour" \
        --aspect 1:1 --out /root/.openclaw/workspace/media/hat-ranch.png

The key, first found wins (docs/secrets-vault-integrations.md 7.5):
  1. GEMINI_KEY      - the vault surrogate (mcb_sec_...), put in the env at
                       boot: the managed copy of the Settings -> Integrations
                       Google AI key, or a key saved in Settings -> Secrets.
  2. GEMINI_API_KEY  - a real key from Settings -> Integrations, only on agents
                       not yet moved to the vault (legacy). Called directly.
  3. the live vault listing (`vault-curl --secrets`), for a key saved after
     boot: the secret named GEMINI_KEY, else the only secret allowed to reach
     generativelanguage.googleapis.com.
A surrogate is only a stand-in: the call goes through vault-curl, which swaps
in the real key at the api-proxy. The key rides only in the x-goog-api-key
header, and stdout never carries image data.

Exit codes: 0 ok, 1 bad input or no key, 2 Gemini refused or returned no image.
"""
import argparse
import base64
import json
import mimetypes
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

GEMINI_HOST = "generativelanguage.googleapis.com"
API = "https://" + GEMINI_HOST + "/v1beta/models/{model}:generateContent"
SURROGATE_PREFIX = "mcb_sec_"
# The vault caps a request body at 10 MB; base64 grows the photos by a third.
MAX_VAULT_INPUT_BYTES = 7 * 1024 * 1024

NO_KEY_MSG = ("No Gemini key found. Ask the user to add a Google Gemini API key in "
              "Settings -> Integrations -> Google AI (or in Settings -> Secrets, named "
              "GEMINI_KEY; free to create at aistudio.google.com/apikey). Never ask "
              "them to paste a key into chat.")

# Newest first. A 404 on one (renamed or retired) falls through to the next.
MODELS = [
    "gemini-3.1-flash-image",
    "gemini-3.1-flash-image-preview",
    "gemini-2.5-flash-image",
]

ASPECTS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"]

# Appended to every instruction: the one thing a seller cannot accept is a
# product that no longer matches what they actually ship.
FIDELITY = (
    "Use the product in the attached photo exactly as it is: same shape, colors, "
    "materials, logo, text and stitching. Do not redesign, recolor or add branding. "
    "Photorealistic, professional product photography."
)


def fail(code: int, message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def call(model: str, key: str, body: dict) -> dict:
    req = urllib.request.Request(
        API.format(model=model),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as res:
        return json.loads(res.read())


class VaultHTTPError(Exception):
    """A non-2xx answer on the vault path, shaped like urllib's HTTPError."""

    def __init__(self, code: int, detail: str):
        super().__init__(f"HTTP {code}")
        self.code = code
        self.detail = detail


def vault_curl() -> str:
    found = shutil.which("vault-curl")
    if not found:
        fail(1, "this key is a vault surrogate (mcb_sec_...) but vault-curl is not installed "
                "on this machine, so it cannot be used. Tell the user the agent needs a "
                "restart or a newer runtime to use keys from Settings -> Secrets.")
    return found


def vault_listing() -> list:
    """The live vault listing (names, surrogates, hosts; never real keys)."""
    exe = shutil.which("vault-curl")
    if not exe:
        return []
    try:
        out = subprocess.run([exe, "--secrets"], capture_output=True, timeout=30, check=False)
        listing = json.loads(out.stdout.decode("utf-8", "replace") or "{}")
    except (OSError, subprocess.SubprocessError, ValueError):
        return []
    if not isinstance(listing, dict):
        return []
    return [x for x in listing.get("secrets") or [] if isinstance(x, dict)]


def listed_surrogate() -> str:
    """A key saved after boot is not in the env yet: the secret named
    GEMINI_KEY, else the only one allowed to reach the Gemini host."""
    secrets = vault_listing()
    for x in secrets:
        if x.get("name") == "GEMINI_KEY" and x.get("surrogate"):
            return str(x["surrogate"]).strip()
    gemini = [x for x in secrets if GEMINI_HOST in (x.get("allowed_hosts") or []) and x.get("surrogate")]
    if len(gemini) > 1:
        names = ", ".join(sorted(str(x.get("name") or "?") for x in gemini))
        fail(1, f"several saved secrets can reach {GEMINI_HOST} ({names}). Ask the user which "
                "one to use, or to name the Gemini one GEMINI_KEY in Settings -> Secrets.")
    return str(gemini[0]["surrogate"]).strip() if gemini else ""


def resolve_key() -> str:
    # Vault surrogate first; the legacy plaintext key only if there is none.
    for name in ("GEMINI_KEY", "GEMINI_API_KEY"):
        key = os.environ.get(name, "").strip()
        if key:
            return key
    key = listed_surrogate()
    if not key:
        fail(1, NO_KEY_MSG)
    return key


def vault_error(resp_path: str) -> str:
    """One short line from an error body: the vault's reason or Gemini's message."""
    try:
        with open(resp_path, "r", encoding="utf-8", errors="replace") as f:
            body = json.load(f)
    except (OSError, ValueError):
        return ""
    err = body.get("error") if isinstance(body, dict) else None
    if not isinstance(err, dict):
        return ""
    msg = str(err.get("message") or err.get("status") or "")
    reason = err.get("reason")
    return " ".join((f"{reason}: {msg}" if reason else msg).split())[:400]


def call_vault(exe: str, model: str, key: str, body: dict) -> dict:
    """Same request as call(), sent through vault-curl, which swaps the
    surrogate for the real key at the api-proxy. Request and response live in
    a temp dir, so image data never reaches stdout or argv."""
    tmp = tempfile.mkdtemp(prefix="edit-photo-")
    try:
        req_path = os.path.join(tmp, "req.json")
        resp_path = os.path.join(tmp, "resp.json")
        with open(req_path, "w", encoding="utf-8") as f:
            json.dump(body, f)
        # The surrogate goes ONLY in the x-goog-api-key header; anywhere else
        # the vault refuses it (surrogate_not_allowed_here).
        run = [exe, "-sS", "-X", "POST", API.format(model=model),
               "-H", f"x-goog-api-key: {key}",
               "-H", "Content-Type: application/json",
               "--data-binary", f"@{req_path}",
               "-o", resp_path,
               "-w", "%{http_code}",
               "--max-time", "180"]
        try:
            proc = subprocess.run(run, capture_output=True, text=True, timeout=200)
        except subprocess.TimeoutExpired:
            fail(2, "the request to Gemini timed out")
        status = (proc.stdout or "").strip()[-3:]
        if not status.isdigit() or status == "000":
            lines = (proc.stderr or "").strip().splitlines()
            detail = " ".join(lines[-1].split())[:300] if lines else "no response"
            fail(2, f"could not reach Gemini through the vault: {detail.replace(key, '<surrogate>')}")
        if not status.startswith("2"):
            raise VaultHTTPError(int(status), vault_error(resp_path).replace(key, "<surrogate>"))
        try:
            with open(resp_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            fail(2, f"HTTP {status} from Gemini, but the response was not JSON")
        return data if isinstance(data, dict) else {}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input", required=True, action="append",
                   help="product photo (repeat for extra angles of the same product)")
    p.add_argument("--prompt", required=True, help="the scene or edit to make")
    p.add_argument("--aspect", default="1:1", choices=ASPECTS)
    p.add_argument("--out", required=True, help="output path, e.g. /root/.openclaw/workspace/media/hat-ranch.png (under the workspace, so MEDIA: lines can deliver it)")
    p.add_argument("--model", help="force one model id instead of the fallback list")
    a = p.parse_args()

    key = resolve_key()
    via_vault = key.startswith(SURROGATE_PREFIX)
    exe = vault_curl() if via_vault else ""

    parts = []
    for path in a.input:
        f = pathlib.Path(path)
        if not f.is_file():
            fail(1, f"input not found: {path}")
        mime = mimetypes.guess_type(f.name)[0] or "image/jpeg"
        if not mime.startswith("image/"):
            fail(1, f"not an image: {path}")
        parts.append({"inlineData": {"mimeType": mime, "data": base64.b64encode(f.read_bytes()).decode()}})
    if via_vault and sum(pathlib.Path(x).stat().st_size for x in a.input) > MAX_VAULT_INPUT_BYTES:
        fail(1, "input photos total more than 7 MB; resize them or send fewer")
    parts.append({"text": f"{a.prompt.strip()}\n\n{FIDELITY}"})

    body = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": a.aspect},
        },
    }

    data, used, last_error = None, None, ""
    for model in ([a.model] if a.model else MODELS):
        if via_vault:
            try:
                data, used = call_vault(exe, model, key, body), model
                break
            except VaultHTTPError as e:
                last_error = f"{model}: HTTP {e.code} {e.detail}".strip()
                if e.code == 404:
                    continue  # model id not available; try the next one
                fail(2, last_error)
        try:
            data, used = call(model, key, body), model
            break
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]
            last_error = f"{model}: HTTP {e.code} {detail}"
            if e.code == 404:
                continue  # model id not available; try the next one
            fail(2, last_error)
        except urllib.error.URLError as e:
            fail(2, f"could not reach Gemini: {e.reason}")
    if data is None:
        fail(2, f"no image model available. Last error: {last_error}")

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    written, notes = [], []
    for cand in data.get("candidates", []):
        for part in (cand.get("content") or {}).get("parts", []):
            blob = part.get("inlineData") or part.get("inline_data")
            if blob and blob.get("data"):
                ext = mimetypes.guess_extension(blob.get("mimeType") or blob.get("mime_type") or "") or ".png"
                target = out if not written else out.with_name(f"{out.stem}-{len(written) + 1}{out.suffix or ext}")
                if not target.suffix:
                    target = target.with_suffix(ext)
                target.write_bytes(base64.b64decode(blob["data"]))
                written.append(str(target))
            elif part.get("text"):
                notes.append(part["text"].strip())

    if not written:
        reason = (data.get("promptFeedback") or {}).get("blockReason") \
            or next((c.get("finishReason") for c in data.get("candidates", []) if c.get("finishReason")), "")
        fail(2, f"Gemini returned no image (model {used}). {reason} {' '.join(notes)}".strip())

    print(json.dumps({"model": used, "files": written, "note": " ".join(notes)[:500]}))


if __name__ == "__main__":
    main()
