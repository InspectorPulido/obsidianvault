#!/home/ubuntu/bot/venv/bin/python3
"""ObsidianVault followup. Checks for signups >48hrs old without payment, sends nudge."""

import json
import os
import smtplib
import sys
import time
from datetime import datetime, timezone, timedelta
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notify import send_tg

OPS_DIR = "/var/www/zerodrop/ops"
EMAILS_FILE = os.path.join(OPS_DIR, "emails.json")
PAYMENTS_FILE = os.path.join(OPS_DIR, "payments.json")
FOLLOWUP_LOG = os.path.join(OPS_DIR, "followup-log.json")
FROM_EMAIL = "hello@obsidianvault.vip"
MAX_PER_DAY = 10
FOLLOWUP_BODY = "Hey -- noticed you signed up for ObsidianVault but haven't gone Pro yet. Need anything? Reply here."
FOLLOWUP_SUBJECT = "Quick check-in from ObsidianVault"


def load_json(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_smtp_config():
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT", "587")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    if not host or not user or not password:
        return None
    return {"host": host, "port": int(port), "user": user, "password": password}


def send_followup_email(smtp_config, to_email):
    """Send followup email. Returns True on success."""
    msg = MIMEText(FOLLOWUP_BODY, "plain", "utf-8")
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = FOLLOWUP_SUBJECT

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_config["user"], smtp_config["password"])
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[followup] SMTP error sending to {to_email}: {e}", file=sys.stderr)
        return False


def parse_timestamp(entry):
    """Extract timestamp from an entry, handling multiple formats."""
    ts = entry.get("timestamp") or entry.get("created") or entry.get("date")
    if not ts:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        # Try ISO format
        ts_clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_clean)
    except (ValueError, TypeError):
        return None


def get_email_address(entry):
    """Extract email from an entry."""
    return entry.get("email") or entry.get("address") or entry.get("Email")


def main():
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    cutoff = now - timedelta(hours=48)

    emails = load_json(EMAILS_FILE)
    payments = load_json(PAYMENTS_FILE)
    followup_log = load_json(FOLLOWUP_LOG)
    smtp_config = get_smtp_config()

    # Emails that have paid
    paid_emails = set()
    for p in payments:
        addr = get_email_address(p)
        if addr:
            paid_emails.add(addr.lower())

    # Emails actually followed up (excludes dry_run and failed)
    already_followed = {e.get("email", "").lower() for e in followup_log if e.get("email") and e.get("status") == "sent"}

    # Find signups >48hrs old without payment
    candidates = []
    for entry in emails:
        addr = get_email_address(entry)
        if not addr:
            continue
        addr_lower = addr.lower()
        if addr_lower in paid_emails:
            continue
        if addr_lower in already_followed:
            continue
        ts = parse_timestamp(entry)
        if ts is None:
            continue
        if ts < cutoff:
            candidates.append(addr)

    sent_count = 0
    skipped_count = len(already_followed)
    failed_count = 0
    dry_run = smtp_config is None

    if dry_run and candidates:
        print("[followup] SMTP not configured. Dry-run mode.")

    for email_addr in candidates[:MAX_PER_DAY]:
        if dry_run:
            print(f"[DRY RUN] Would follow up: {email_addr}")
            followup_log.append({
                "email": email_addr,
                "timestamp": now_iso,
                "status": "dry_run",
            })
            sent_count += 1
        else:
            ok = send_followup_email(smtp_config, email_addr)
            if ok:
                followup_log.append({
                    "email": email_addr,
                    "timestamp": now_iso,
                    "status": "sent",
                })
                sent_count += 1
                time.sleep(2)
            else:
                followup_log.append({
                    "email": email_addr,
                    "timestamp": now_iso,
                    "status": "failed",
                })
                failed_count += 1

    save_json(FOLLOWUP_LOG, followup_log)

    mode = " (DRY RUN)" if dry_run and candidates else ""
    summary = f"FOLLOWUP{mode}: {sent_count} sent, {skipped_count} already done, {failed_count} failed, {len(candidates)} eligible"
    print(summary)
    if sent_count > 0 or failed_count > 0:
        send_tg(summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[followup] Fatal: {e}", file=sys.stderr)
        sys.exit(1)
