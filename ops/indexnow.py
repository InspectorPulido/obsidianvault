#!/home/ubuntu/bot/venv/bin/python3
"""Submit new/changed URLs to IndexNow (Bing, Yandex, etc.)
Run after any content change. Idempotent -- safe to call repeatedly."""

import json
import os
import sys
import urllib.request
import urllib.error

DOMAIN = "obsidianvault.vip"
KEY = "a448dd66768a21b9289d326502bdfc8c"
BLOG_DIR = "/var/www/zerodrop/blog"


def get_all_urls():
    """Build list of all indexable URLs."""
    urls = [
        f"https://{DOMAIN}/",
        f"https://{DOMAIN}/create",
        f"https://{DOMAIN}/blog",
    ]
    if os.path.exists(BLOG_DIR):
        for fname in sorted(os.listdir(BLOG_DIR)):
            if fname.endswith(".md"):
                slug = fname.replace(".md", "")
                urls.append(f"https://{DOMAIN}/blog/{slug}")
    return urls


def submit(urls):
    """Submit URLs to IndexNow API."""
    payload = json.dumps({
        "host": DOMAIN,
        "key": KEY,
        "keyLocation": f"https://{DOMAIN}/{KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.indexnow.org/IndexNow",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print(f"[indexnow] Submitted {len(urls)} URLs: HTTP {resp.status}")
            return True
    except urllib.error.HTTPError as e:
        if e.code == 202:
            print(f"[indexnow] Submitted {len(urls)} URLs: HTTP 202 (accepted)")
            return True
        print(f"[indexnow] HTTP {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[indexnow] Error: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    urls = get_all_urls()
    print(f"[indexnow] {len(urls)} URLs to submit")
    submit(urls)
