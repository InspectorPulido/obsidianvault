#!/home/ubuntu/bot/venv/bin/python3
"""ObsidianVault monitor. Runs every 6 hours via cron.
At 11:00 UTC (9pm AEST) sends daily summary."""

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notify import send_tg

OPS_DIR = "/var/www/zerodrop/ops"
STATE_FILE = os.path.join(OPS_DIR, ".monitor_state.json")
EMAILS_FILE = os.path.join(OPS_DIR, "emails.json")
PAYMENTS_FILE = os.path.join(OPS_DIR, "payments.json")
OUTREACH_LOG = os.path.join(OPS_DIR, "outreach-log.json")

AEST = timezone(timedelta(hours=11))


def load_json(path):
    """Load a JSON file, return empty list if missing or corrupt."""
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, PermissionError):
        return []


def load_state():
    """Load monitor state, return defaults if missing."""
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_check": 0,
            "last_email_count": 0,
            "last_payment_count": 0,
            "last_daily_summary": "",
        }


def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"[monitor] Failed to save state: {e}", file=sys.stderr)


def count_new_since(entries, last_count):
    """Count new entries since last check based on total count."""
    current = len(entries)
    new = max(0, current - last_count)
    return current, new


def get_plausible_visitors():
    """Stub: Plausible API key needed. Returns None until configured.

    To enable: set PLAUSIBLE_API_KEY and PLAUSIBLE_SITE_ID env vars.
    API: GET https://plausible.io/api/v1/stats/aggregate
         ?site_id={site_id}&period=day&metrics=visitors
         Authorization: Bearer {api_key}
    """
    api_key = os.environ.get("PLAUSIBLE_API_KEY")
    site_id = os.environ.get("PLAUSIBLE_SITE_ID")
    if not api_key or not site_id:
        return None
    # TODO: implement when API key is available
    return None


def count_outreach_sent():
    """Count total outreach emails sent."""
    log = load_json(OUTREACH_LOG)
    sent = sum(1 for e in log if e.get("status") == "sent")
    return sent


def count_posts_live():
    """Count .md files in launch directory as proxy for posts."""
    launch_dir = "/var/www/zerodrop/launch"
    try:
        return len([f for f in os.listdir(launch_dir) if f.endswith(".md")])
    except (FileNotFoundError, PermissionError):
        return 0


def is_daily_summary_time():
    """Check if current hour is 11 UTC (9pm AEST)."""
    now = datetime.now(timezone.utc)
    return now.hour == 11


def main():
    now_ts = time.time()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    state = load_state()

    emails = load_json(EMAILS_FILE)
    payments = load_json(PAYMENTS_FILE)

    email_total, new_emails = count_new_since(emails, state.get("last_email_count", 0))
    payment_total, new_payments = count_new_since(payments, state.get("last_payment_count", 0))

    visitors = get_plausible_visitors()
    visitors_str = str(visitors) if visitors is not None else "N/A"
    outreach_sent = count_outreach_sent()
    posts_live = count_posts_live()

    print(f"[{now_str}] emails={email_total} (+{new_emails}) payments={payment_total} (+{new_payments}) visitors={visitors_str} outreach={outreach_sent} posts={posts_live}")

    # Daily summary at 9pm AEST (11:00 UTC)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if is_daily_summary_time() and state.get("last_daily_summary") != today:
        summary = (
            f"<b>ObsidianVault Daily</b> {today}\n"
            f"Emails: {email_total} (+{new_emails} new)\n"
            f"Payments: {payment_total} (+{new_payments} new)\n"
            f"Visitors: {visitors_str}\n"
            f"Outreach sent: {outreach_sent}\n"
            f"Posts live: {posts_live}"
        )
        send_tg(summary)
        state["last_daily_summary"] = today

    state["last_check"] = now_ts
    state["last_email_count"] = email_total
    state["last_payment_count"] = payment_total
    save_state(state)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[monitor] Fatal: {e}", file=sys.stderr)
        sys.exit(1)
