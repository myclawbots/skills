#!/usr/bin/env python3
"""
scripts/post_social.py
======================
Publishes single image or multi-image carousel posts to Instagram, Facebook,
Threads, LinkedIn or (when connected) Pinterest via the MyClawBots Social API proxy.

Usage via CLI:
    # Post carousel to Instagram (2-10 image URLs)
    python3 post_social.py --platform instagram \
      --caption "Check out today's top AI news! 🚀 #AI #myclawbots" \
      --images https://res.cloudinary.com/.../slide1.png https://res.cloudinary.com/.../slide2.png

    # Post single image
    python3 post_social.py --platform facebook \
      --caption "New update is live!" \
      --image https://res.cloudinary.com/.../cover.png

    # Post to Threads (text-only is allowed here; Instagram requires media)
    python3 post_social.py --platform threads --caption "Shipping today."

    # Post to LinkedIn (text or images only — no video)
    python3 post_social.py --platform linkedin \
      --caption "We just shipped multi-platform publishing." \
      --image https://res.cloudinary.com/.../cover.png

    # Post to a connected LinkedIn company Page instead of the profile
    python3 post_social.py --platform linkedin --account-type page \
      --caption "We just shipped multi-platform publishing." \
      --image https://res.cloudinary.com/.../cover.png

    # Pin to a Pinterest board (image required; 2-5 images for a carousel;
    # JPEG/PNG only; no video). --board-id comes from GET /social/accounts.
    python3 post_social.py --platform pinterest --board-id 123456789 \
      --title "Autumn table ideas" --link https://example.com/autumn \
      --alt-text "A wooden table set for dinner" \
      --caption "Five ways to set an autumn table." \
      --image https://mcp.myclawbots.ai/media/<id>

The same hosted image URL can be reused across platforms — post once per
platform with the same --images/--image values rather than re-uploading.

Environment variables:
    SOCIAL_POST_PROXY_URL (e.g. https://api.myclawbots.ai)
    PROXY_API_KEY
    MYCLAWBOTS_IG_ACCOUNT_ID (optional: auto-discovered from GET /social/accounts if omitted)
    MYCLAWBOTS_FB_ACCOUNT_ID (optional: auto-discovered if omitted)
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional


def load_env():
    """Load .env.local if present in current or parent directories."""
    cwd = Path.cwd()
    for search_dir in [cwd, cwd.parent, cwd.parent.parent]:
        env_file = search_dir / ".env.local"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        os.environ.setdefault(k.strip(), v.strip())
            break


load_env()


def get_proxy_config():
    return {
        "proxy_url": os.environ.get("SOCIAL_POST_PROXY_URL", "").rstrip("/"),
        "api_key": os.environ.get("PROXY_API_KEY", ""),
        "ig_account_id": os.environ.get("MYCLAWBOTS_IG_ACCOUNT_ID", ""),
        "fb_account_id": os.environ.get("MYCLAWBOTS_FB_ACCOUNT_ID", ""),
    }


def get_connected_accounts() -> List[dict]:
    """Fetch list of connected social accounts from the MyClawBots proxy."""
    cfg = get_proxy_config()
    if not cfg["proxy_url"] or not cfg["api_key"]:
        return []

    cmd = [
        "curl", "-s", f"{cfg['proxy_url']}/social/accounts",
        "-H", f"x-api-key: {cfg['api_key']}",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if res.returncode == 0:
            data = json.loads(res.stdout)
            if isinstance(data, dict) and "accounts" in data:
                return data.get("accounts") or []
            if isinstance(data, list):
                return data
    except Exception as e:
        print(f"⚠️ Failed to fetch accounts: {e}", file=sys.stderr)
    return []


def resolve_account_id(platform: str, target_account_id: Optional[str] = None, target_username: Optional[str] = None, account_type: Optional[str] = None) -> Optional[str]:
    """Resolve account ID from explicit arg, env var, or auto-discover from proxy."""
    # 1. Direct argument
    if target_account_id:
        return target_account_id

    cfg = get_proxy_config()
    # Env-var pinning exists only for the two original platforms; threads and
    # linkedin always auto-discover from /social/accounts below.
    target_env_id = (
        cfg["ig_account_id"] if platform == "instagram"
        else cfg["fb_account_id"] if platform == "facebook"
        else None
    )
    if target_env_id:
        return target_env_id

    username_to_match = (
        target_username
        or os.environ.get("MYCLAWBOTS_IG_USERNAME")
        or os.environ.get("BRAND_HANDLE", "@myclawbots.ai")
    ).lstrip("@").lower()

    accounts = get_connected_accounts()
    platform_accounts = [a for a in accounts if a.get("platform") == platform]

    # A LinkedIn company Page shares platform 'linkedin' with the person's
    # profile (added 2026-09-24), so an unqualified post must not silently land
    # on the company feed: it goes to the profile unless --account-type page,
    # even when a Page is the only LinkedIn account. Posting as the wrong one
    # is worse than failing. Only an older proxy that sends no account_type at
    # all keeps the unfiltered list (it can only return profiles).
    if platform == "linkedin":
        typed = [a for a in platform_accounts if a.get("account_type") == (account_type or "profile")]
        legacy = all(a.get("account_type") is None for a in platform_accounts)
        if account_type or not legacy:
            platform_accounts = typed

    if not platform_accounts:
        return None

    # Try matching by username if specified or by brand handle
    for acct in platform_accounts:
        u = (acct.get("username") or "").lstrip("@").lower()
        if u and (u == username_to_match or username_to_match in u or u in username_to_match):
            return acct.get("id")

    # If only 1 account exists for platform, use it
    if len(platform_accounts) == 1:
        return platform_accounts[0].get("id")

    # Fallback to first, with a warning
    chosen = platform_accounts[0]
    print(f"ℹ️ Multiple {platform} accounts detected. Using {chosen.get('username') or chosen.get('id')}. Set MYCLAWBOTS_IG_ACCOUNT_ID to lock it.", file=sys.stderr)
    return chosen.get("id")


def post_to_social(
    platform: str,
    caption: str,
    media_urls: Optional[List[str]] = None,
    media_url: Optional[str] = None,
    account_type: Optional[str] = None,
    pinterest: Optional[dict] = None,
) -> bool:
    """Submit post to MyClawBots Social Proxy."""
    cfg = get_proxy_config()
    if not cfg["proxy_url"]:
        print("❌ SOCIAL_POST_PROXY_URL is not set", file=sys.stderr)
        return False
    if not cfg["api_key"]:
        print("❌ PROXY_API_KEY is not set", file=sys.stderr)
        return False

    account_id = resolve_account_id(platform, account_type=account_type)
    if not account_id:
        print(f"❌ No active {platform} account found. Connect via MyClawBots Settings → Social.", file=sys.stderr)
        return False

    payload = {
        "platform": platform,
        "account_id": account_id,
        "content": caption,
    }

    if media_urls:
        # Pinterest takes 2-5 images, not 10 (2026-09-25): send the list as
        # given and let the proxy refuse an oversized one with a clear message,
        # rather than silently publishing a Pin missing slides 6+.
        payload["media_urls"] = media_urls if platform == "pinterest" else media_urls[:10]
    elif media_url:
        payload["media_url"] = media_url

    # Pinterest-only fields; only the ones actually given are sent.
    for key, value in (pinterest or {}).items():
        if value:
            payload[key] = value

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(payload, f)
        tmp_name = f.name

    cmd = [
        "curl", "-s", "-X", "POST", f"{cfg['proxy_url']}/social/post",
        "-H", "Content-Type: application/json",
        "-H", f"x-api-key: {cfg['api_key']}",
        "-d", f"@{tmp_name}",
        "-w", "\n%{http_code}",
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        lines = res.stdout.strip().split("\n")
        status_code = lines[-1] if lines else "000"
        body = "\n".join(lines[:-1]).strip()

        if status_code.startswith("2"):
            print(f"✅ Successfully published to {platform} (HTTP {status_code})")
            # A notice is something true about the post the user cannot see
            # (e.g. a Pinterest Trial Pin is visible only to them) — print it
            # so the agent can relay it verbatim.
            try:
                notice = json.loads(body).get("notice")
            except Exception:
                notice = None
            if notice:
                print(f"NOTICE (tell the user verbatim): {notice}")
            return True
        else:
            print(f"❌ Failed to publish to {platform} (HTTP {status_code}): {body}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"❌ Error submitting post: {e}", file=sys.stderr)
        return False
    finally:
        Path(tmp_name).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Publish posts to social media via MyClawBots proxy")
    parser.add_argument("--platform", choices=["instagram", "facebook", "threads", "linkedin", "youtube", "tiktok", "pinterest"], default="instagram", help="Target platform")
    parser.add_argument("--caption", required=True, help="Post caption / copy")
    parser.add_argument("--images", nargs="+", help="Image URLs for carousel (2-10 URLs)")
    parser.add_argument("--image", help="Single image URL")
    parser.add_argument("--account-type", choices=["profile", "page"], help="linkedin only: post as the person's profile (default) or a connected company Page")
    # Pinterest only. The caption becomes the Pin description (<=800 chars).
    parser.add_argument("--board-id", help="pinterest only: the board to pin to (an id from the account's `boards`); may be omitted when the account has exactly one board")
    parser.add_argument("--title", help="pinterest only: Pin title (<=100 chars)")
    parser.add_argument("--link", help="pinterest only: destination URL the Pin opens (http/https)")
    parser.add_argument("--alt-text", help="pinterest only: image description for screen readers (<=500 chars)")
    parser.add_argument("--ai-disclosure", action="append", choices=["AI_MODIFIED", "SYNTHETIC_PERFORMER"], help="pinterest only: label the Pin as AI content; repeat for both")

    args = parser.parse_args()

    pinterest = {
        "board_id": args.board_id,
        "title": args.title,
        "link": args.link,
        "alt_text": args.alt_text,
        "ai_disclosures": args.ai_disclosure,
    }
    if args.platform != "pinterest" and any(pinterest.values()):
        print("❌ --board-id, --title, --link, --alt-text and --ai-disclosure are for --platform pinterest only", file=sys.stderr)
        sys.exit(1)

    if not args.images and not args.image:
        print("❌ Either --images (for carousel) or --image (single post) must be provided", file=sys.stderr)
        sys.exit(1)

    success = post_to_social(
        platform=args.platform,
        caption=args.caption,
        media_urls=args.images,
        media_url=args.image,
        account_type=args.account_type,
        pinterest=pinterest if args.platform == "pinterest" else None,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
