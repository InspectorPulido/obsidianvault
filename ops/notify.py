#!/home/ubuntu/bot/venv/bin/python3
"""Telegram notification helper for ObsidianVault ops."""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse

BOT_TOKEN = os.environ.get("BOT_TOKEN_BLCKOFFICIAL", "")
CHAT_ID = os.environ.get("TG_CHAT_ID", "")


def send_tg(message):
    """Send a Telegram message. Returns True on success, False on failure."""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("ok", False)
    except Exception as e:
        print(f"[notify] TG send failed: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = " ".join(sys.argv[1:])
    else:
        msg = "ObsidianVault ops: notify.py test"
    ok = send_tg(msg)
    print(f"Sent: {ok}")
