#!/home/ubuntu/bot/venv/bin/python3
"""ObsidianVault cold outreach. Reads template, sends to practices.csv, max 20/day."""

import csv
import json
import os
import smtplib
import sys
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notify import send_tg

OPS_DIR = "/var/www/zerodrop/ops"
LAUNCH_DIR = "/var/www/zerodrop/launch"
TEMPLATE_PATH = os.path.join(LAUNCH_DIR, "cold-email.md")
TEMPLATE_LEGAL = os.path.join(LAUNCH_DIR, "cold-email-legal.md")
TEMPLATE_ACCOUNTING = os.path.join(LAUNCH_DIR, "cold-email-accounting.md")
PRACTICES_CSV = os.path.join(OPS_DIR, "practices.csv")
OUTREACH_LOG = os.path.join(OPS_DIR, "outreach-log.json")
FROM_EMAIL = "hello@obsidianvault.vip"
MAX_PER_DAY = 20

# keywords in practice name that select template variant
LEGAL_KEYWORDS = ["lawyer", "legal", "solicitor", "law", "barrister", "counsel"]
ACCOUNTING_KEYWORDS = ["account", "tax", "audit", "bookkeep", "cpa", "chartered"]


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


def _parse_template(path):
    """Parse a template file into (subject, body). Returns None if missing."""
    try:
        with open(path, "r") as f:
            content = f.read().strip()
    except FileNotFoundError:
        return None

    lines = content.split("\n")
    subject = "Secure file transfer for your practice"
    body = content
    for i, line in enumerate(lines):
        if line.startswith("# "):
            subject = line[2:].strip()
            body = "\n".join(lines[i + 1:]).strip()
            break
        elif line.startswith("Subject:"):
            subject = line[len("Subject:"):].strip()
            body = "\n".join(lines[i + 1:]).strip()
            break

    return subject, body


def select_template(practice_name):
    """Pick the right template based on practice name keywords."""
    name_lower = practice_name.lower()
    for kw in LEGAL_KEYWORDS:
        if kw in name_lower:
            t = _parse_template(TEMPLATE_LEGAL)
            if t:
                return t
            break
    for kw in ACCOUNTING_KEYWORDS:
        if kw in name_lower:
            t = _parse_template(TEMPLATE_ACCOUNTING)
            if t:
                return t
            break
    return _parse_template(TEMPLATE_PATH)


def load_practices():
    """Load practices CSV. Returns list of (name, email) tuples."""
    practices = []
    try:
        with open(PRACTICES_CSV, "r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get("name", "").strip()
                email = row.get("email", "").strip()
                if email:
                    practices.append((name, email))
    except FileNotFoundError:
        print(f"[outreach] Practices CSV not found: {PRACTICES_CSV}", file=sys.stderr)
    return practices


def get_already_sent(log):
    """Return set of emails actually sent to (excludes dry_run and failed)."""
    return {entry["email"] for entry in log if entry.get("email") and entry.get("status") == "sent"}


def get_smtp_config():
    """Return SMTP config from env vars, or None if not configured."""
    host = os.environ.get("SMTP_HOST")
    port = os.environ.get("SMTP_PORT", "587")
    user = os.environ.get("SMTP_USER")
    password = os.environ.get("SMTP_PASS")
    if not host or not user or not password:
        return None
    return {"host": host, "port": int(port), "user": user, "password": password}


def send_email(smtp_config, to_email, to_name, subject, body_template):
    """Send a single email via SMTP. Returns True on success."""
    body = body_template.replace("{{name}}", to_name or "there")

    msg = MIMEMultipart("alternative")
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_config["user"], smtp_config["password"])
            server.sendmail(FROM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[outreach] SMTP error sending to {to_email}: {e}", file=sys.stderr)
        return False


def main():
    now = datetime.now(timezone.utc).isoformat()
    log = load_json(OUTREACH_LOG)
    already_sent = get_already_sent(log)
    practices = load_practices()
    smtp_config = get_smtp_config()

    if not practices:
        print("[outreach] No practices to contact.")
        return

    sent_count = 0
    skipped_count = 0
    failed_count = 0
    dry_run = smtp_config is None

    if dry_run:
        print("[outreach] SMTP not configured. Dry-run mode.")

    for name, email in practices:
        if sent_count >= MAX_PER_DAY:
            break

        if email in already_sent:
            skipped_count += 1
            continue

        template = select_template(name)
        if template is None:
            print(f"[outreach] No template available, skipping {name}", file=sys.stderr)
            continue
        subject, body = template

        if dry_run:
            print(f"[DRY RUN] Would send to: {name} <{email}>")
            print(f"  Subject: {subject}")
            print(f"  Body preview: {body[:100]}...")
            print()
            log.append({
                "email": email,
                "name": name,
                "timestamp": now,
                "status": "dry_run",
                "note": "SMTP not configured",
            })
            sent_count += 1
        else:
            ok = send_email(smtp_config, email, name, subject, body)
            if ok:
                log.append({
                    "email": email,
                    "name": name,
                    "timestamp": now,
                    "status": "sent",
                })
                sent_count += 1
                time.sleep(2)  # rate limit
            else:
                log.append({
                    "email": email,
                    "name": name,
                    "timestamp": now,
                    "status": "failed",
                })
                failed_count += 1

    save_json(OUTREACH_LOG, log)

    mode = "DRY RUN" if dry_run else ""
    summary = f"OUTREACH{' (' + mode + ')' if mode else ''}: {sent_count} sent, {skipped_count} skipped (already sent), {failed_count} failed"
    print(summary)
    send_tg(summary)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[outreach] Fatal: {e}", file=sys.stderr)
        sys.exit(1)
