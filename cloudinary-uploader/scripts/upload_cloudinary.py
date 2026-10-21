#!/usr/bin/env python3
"""
scripts/upload_cloudinary.py
============================
Uploads one or more local image files to Cloudinary using signed REST uploads.

Usage via CLI:
    python3 upload_cloudinary.py slide1.png slide2.png slide3.png slide4.png
    python3 upload_cloudinary.py --folder "myclawbots/carousel" /path/to/image.png

Environment variables:
    CLOUDINARY_CLOUD_NAME
    CLOUDINARY_API_KEY
    CLOUDINARY_API_SECRET
    CLOUDINARY_FOLDER (optional, default: 'myclawbots/carousel')
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
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


def get_config():
    return {
        "cloud_name": os.environ.get("CLOUDINARY_CLOUD_NAME", ""),
        "api_key": os.environ.get("CLOUDINARY_API_KEY", ""),
        "api_secret": os.environ.get("CLOUDINARY_API_SECRET", ""),
        "folder": os.environ.get("CLOUDINARY_FOLDER", "myclawbots/carousel"),
    }


def _sign(params: dict, api_secret: str) -> str:
    """Generate SHA-1 signature of sorted params + api_secret."""
    exclude = {"api_key", "file", "resource_type"}
    pairs = sorted(f"{k}={v}" for k, v in params.items() if k not in exclude)
    to_sign = "&".join(pairs) + api_secret
    return hashlib.sha1(to_sign.encode("utf-8")).hexdigest()


def upload_image(local_path: str, folder: Optional[str] = None) -> Optional[str]:
    """Upload a single local image to Cloudinary and return its HTTPS URL."""
    cfg = get_config()
    cloud_name = cfg["cloud_name"]
    api_key = cfg["api_key"]
    api_secret = cfg["api_secret"]
    target_folder = folder or cfg["folder"]

    if not os.path.exists(local_path):
        print(f"❌ File not found: {local_path}", file=sys.stderr)
        return None

    if not cloud_name or not api_key or not api_secret:
        print("❌ Cloudinary credentials missing (CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET)", file=sys.stderr)
        return None

    upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
    timestamp = str(int(time.time()))
    filename = Path(local_path).stem

    params = {
        "folder": target_folder,
        "public_id": filename,
        "timestamp": timestamp,
        "overwrite": "true",
    }
    signature = _sign(params, api_secret)

    cmd = [
        "curl", "-s", "-X", "POST", upload_url,
        "-F", f"file=@{local_path}",
        "-F", f"api_key={api_key}",
        "-F", f"timestamp={timestamp}",
        "-F", f"signature={signature}",
        "-F", f"folder={target_folder}",
        "-F", f"public_id={filename}",
        "-F", "overwrite=true",
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode != 0:
            print(f"❌ Curl error: {res.stderr[:200]}", file=sys.stderr)
            return None

        data = json.loads(res.stdout)
        if "error" in data:
            print(f"❌ Cloudinary error: {data['error'].get('message', data['error'])}", file=sys.stderr)
            return None

        secure_url = data.get("secure_url")
        return secure_url
    except Exception as e:
        print(f"❌ Upload exception: {e}", file=sys.stderr)
        return None


def upload_batch(file_paths: List[str], folder: Optional[str] = None) -> List[str]:
    """Upload multiple files and return list of secure URLs."""
    urls = []
    for p in file_paths:
        url = upload_image(p, folder)
        if url:
            urls.append(url)
        else:
            print(f"⚠️ Failed to upload: {p}", file=sys.stderr)
    return urls


def main():
    parser = argparse.ArgumentParser(description="Upload images to Cloudinary")
    parser.add_argument("files", nargs="+", help="Local image file paths to upload")
    parser.add_argument("--folder", default=None, help="Cloudinary target folder")
    parser.add_argument("--json", action="store_true", help="Output result as JSON array")
    args = parser.parse_args()

    urls = upload_batch(args.files, args.folder)
    if args.json:
        print(json.dumps(urls))
    else:
        for u in urls:
            print(u)

    if len(urls) != len(args.files):
        sys.exit(1)


if __name__ == "__main__":
    main()
