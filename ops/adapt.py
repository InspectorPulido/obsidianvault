#!/home/ubuntu/bot/venv/bin/python3
"""ObsidianVault adaptive layer. Runs daily at 11pm AEST (13:00 UTC).
Reads operational data. When thresholds are breached, rewrites copy,
commits, pushes, restarts the service. One change per day max.

the jungle adapts or it dies. this is the adaptation engine."""

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notify import send_tg

OPS_DIR = "/var/www/zerodrop/ops"
APP_PY = "/var/www/zerodrop/app.py"
COLD_EMAIL = "/var/www/zerodrop/launch/cold-email.md"
EMAILS_FILE = os.path.join(OPS_DIR, "emails.json")
PAYMENTS_FILE = os.path.join(OPS_DIR, "payments.json")
OUTREACH_LOG = os.path.join(OPS_DIR, "outreach-log.json")
DECISIONS_LOG = os.path.join(OPS_DIR, "decisions.log")
ADAPT_STATE = os.path.join(OPS_DIR, ".adapt_state.json")
LAUNCH_DIR = "/var/www/zerodrop/launch"
REPO_DIR = "/var/www/zerodrop"

# CTA variants for email capture section -- rotated on failure
EMAIL_CTA_VARIANTS = [
    {
        "heading": "Get notified when Pro launches",
        "sub": "Lock in beta pricing. One email. No spam.",
        "placeholder": "you@practice.com.au",
        "button": "Notify me",
    },
    {
        "heading": "Your practice is one breach away from an OAIC complaint",
        "sub": "Get the fix before the fine. Free tier available now.",
        "placeholder": "practice@email.com.au",
        "button": "Get started",
    },
    {
        "heading": "50,000 medical records were breached in Australia last year",
        "sub": "Yours don't have to be next. Join practices already protecting patient files.",
        "placeholder": "reception@yourpractice.com.au",
        "button": "Protect my practice",
    },
    {
        "heading": "Every email attachment is a liability",
        "sub": "Practice managers across Australia are switching to encrypted transfer. See why.",
        "placeholder": "manager@clinic.com.au",
        "button": "Show me how",
    },
]

# Pricing copy variants -- rotated on failure
PRICING_SUB_VARIANTS = [
    "A compliance breach costs $500,000. This costs less than lunch.",
    "One OAIC complaint costs more than a decade of Pro. Do the math.",
    "Your medical indemnity insurer would approve. Your patients would too.",
    "Practices pay $9/mo. The alternative is a Privacy Act investigation.",
]


def load_json(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_state():
    try:
        with open(ADAPT_STATE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_run": "",
            "last_change_date": "",
            "email_cta_variant": 0,
            "pricing_variant": 0,
            "cold_email_rewrites": 0,
            "changes_today": 0,
        }


def save_state(state):
    with open(ADAPT_STATE, "w") as f:
        json.dump(state, f, indent=2)


def log_decision(tag, message):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{ts} | {tag} | {message}\n"
    try:
        with open(DECISIONS_LOG, "a") as f:
            f.write(line)
    except Exception as e:
        print(f"[adapt] Failed to write decisions.log: {e}", file=sys.stderr)


def parse_timestamp(entry):
    ts = entry.get("timestamp") or entry.get("created") or entry.get("date")
    if not ts:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.fromtimestamp(ts, tz=timezone.utc)
        ts_clean = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_clean)
    except (ValueError, TypeError):
        return None


def file_age_hours(path):
    try:
        mtime = os.path.getmtime(path)
        return (time.time() - mtime) / 3600
    except (FileNotFoundError, OSError):
        return None


def git_commit_and_push(message):
    """Commit changes and push. Returns True on success."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=REPO_DIR, capture_output=True, timeout=30)
        result = subprocess.run(
            ["git", "commit", "-m", message],
            cwd=REPO_DIR, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            print(f"[adapt] git commit failed: {result.stderr}", file=sys.stderr)
            return False
        push = subprocess.run(
            ["git", "push"], cwd=REPO_DIR, capture_output=True, text=True, timeout=60
        )
        if push.returncode != 0:
            print(f"[adapt] git push failed: {push.stderr}", file=sys.stderr)
            # commit succeeded even if push failed, that's ok
        return True
    except Exception as e:
        print(f"[adapt] git error: {e}", file=sys.stderr)
        return False


def restart_service():
    """Restart zerodrop service."""
    try:
        subprocess.run(
            ["sudo", "systemctl", "restart", "zerodrop"],
            capture_output=True, timeout=15
        )
    except Exception as e:
        print(f"[adapt] restart failed: {e}", file=sys.stderr)


def rewrite_email_cta(variant_idx):
    """Rewrite the email capture CTA in app.py. Returns True if changed."""
    variant = EMAIL_CTA_VARIANTS[variant_idx % len(EMAIL_CTA_VARIANTS)]

    try:
        with open(APP_PY, "r") as f:
            code = f.read()
    except Exception as e:
        print(f"[adapt] Failed to read app.py: {e}", file=sys.stderr)
        return False

    # Find and replace the email capture section
    # Pattern: the capture div with heading, sub, placeholder, button
    old_pattern = re.compile(
        r'(<div class="capture">.*?<h3>)(.*?)(</h3>.*?<p>)(.*?)(</p>.*?placeholder=")(.*?)(".*?<button.*?>)(.*?)(</button>)',
        re.DOTALL
    )
    match = old_pattern.search(code)
    if not match:
        print("[adapt] Could not find email capture section in app.py", file=sys.stderr)
        return False

    new_code = old_pattern.sub(
        lambda m: (
            m.group(1) + variant["heading"] + m.group(3) +
            variant["sub"] + m.group(5) + variant["placeholder"] +
            m.group(7) + variant["button"] + m.group(9)
        ),
        code,
        count=1
    )

    if new_code == code:
        return False

    with open(APP_PY, "w") as f:
        f.write(new_code)
    return True


def rewrite_pricing_sub(variant_idx):
    """Rewrite the pricing subtitle in app.py. Returns True if changed."""
    variant = PRICING_SUB_VARIANTS[variant_idx % len(PRICING_SUB_VARIANTS)]

    try:
        with open(APP_PY, "r") as f:
            code = f.read()
    except Exception as e:
        print(f"[adapt] Failed to read app.py: {e}", file=sys.stderr)
        return False

    # Find the pricing sub line
    old_pattern = re.compile(
        r'(<div class="sub">)(A compliance breach costs.*?|One OAIC complaint.*?|Your medical indemnity.*?|Practices pay \$9.*?)(</div>\s*<div class="tiers">)',
        re.DOTALL
    )
    match = old_pattern.search(code)
    if not match:
        print("[adapt] Could not find pricing sub in app.py", file=sys.stderr)
        return False

    new_code = old_pattern.sub(
        lambda m: m.group(1) + variant + m.group(3),
        code,
        count=1
    )

    if new_code == code:
        return False

    with open(APP_PY, "w") as f:
        f.write(new_code)
    return True


def rewrite_cold_email():
    """Rewrite cold-email.md with next variant. Returns True if changed."""
    templates = [
        {
            "subject": "Your practice is emailing patient records unencrypted",
            "body": """Hi {{name}},

Quick question: how does your practice send patient records to specialists?

If the answer is email, those files are sitting in cleartext on Microsoft or Google servers right now. Every one is technically a Privacy Act breach.

I built ObsidianVault after my own GP's receptionist split my medical records across 5 unencrypted emails. It encrypts files in the browser before they leave. The server never sees the data. Takes 30 seconds. Free tier available.

https://obsidianvault.vip

Happy to show you a 2-minute demo if useful.

Patrick
ObsidianVault""",
        },
        {
            "subject": "The OAIC received 1,111 health data breach reports last year",
            "body": """Hi {{name}},

Healthcare is the #1 sector for data breaches reported to the OAIC. Most of them are exactly what you'd expect: patient records sent via unencrypted email.

ObsidianVault is a zero-knowledge file transfer tool built specifically for practices like yours. Files are encrypted in the browser before upload. The server stores only ciphertext. Decryption key never touches our infrastructure.

Free for personal use. $9/mo for practice features (audit logs, compliance certificates, custom TTL).

https://obsidianvault.vip

Takes 30 seconds to try. No account needed.

Patrick
ObsidianVault""",
        },
        {
            "subject": "Encrypted file transfer for {{name}} -- 30 second setup",
            "body": """Hi {{name}},

I noticed your practice is listed on HealthDirect. I'm reaching out because most practices I talk to are still emailing patient records as PDF attachments.

That's a problem. Every unencrypted email is a Privacy Act liability. The OAIC fined a medical practice $500K last year for exactly this.

I built a fix: ObsidianVault. Drop a file, it encrypts in your browser, you share a link. Recipient clicks and downloads. No app, no account, no training.

The server mathematically cannot read the files.

https://obsidianvault.vip

Free to try. Want me to walk your practice manager through it?

Patrick
ObsidianVault""",
        },
    ]

    try:
        with open(COLD_EMAIL, "r") as f:
            current = f.read()
    except FileNotFoundError:
        current = ""

    # Pick next template based on what's NOT currently in the file
    for i, tmpl in enumerate(templates):
        if tmpl["subject"] not in current:
            new_content = f"# {tmpl['subject']}\n\n{tmpl['body']}\n"
            with open(COLD_EMAIL, "w") as f:
                f.write(new_content)
            return True

    # All tried, cycle back to first
    tmpl = templates[0]
    new_content = f"# {tmpl['subject']}\n\n{tmpl['body']}\n"
    with open(COLD_EMAIL, "w") as f:
        f.write(new_content)
    return True


def main():
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    state = load_state()

    # One change per day max
    if state.get("last_change_date") == today:
        print(f"[adapt] Already made a change today ({today}). Skipping.")
        return

    emails = load_json(EMAILS_FILE)
    payments = load_json(PAYMENTS_FILE)
    outreach_log = load_json(OUTREACH_LOG)

    changed = False

    # Rule 1: 0 email signups in 48hrs -- rewrite CTA
    emails_age = file_age_hours(EMAILS_FILE)
    if not changed and emails_age is not None and emails_age > 48:
        cutoff = now - timedelta(hours=48)
        recent = sum(1 for e in emails if (parse_timestamp(e) or datetime.min.replace(tzinfo=timezone.utc)) > cutoff)
        # Exclude test entries
        real_emails = [e for e in emails if e.get("source") != "verification"]
        real_recent = sum(1 for e in real_emails if (parse_timestamp(e) or datetime.min.replace(tzinfo=timezone.utc)) > cutoff)

        if real_recent == 0:
            next_variant = (state.get("email_cta_variant", 0) + 1) % len(EMAIL_CTA_VARIANTS)
            if rewrite_email_cta(next_variant):
                msg = f"0 real signups in 48hrs. Rotated email CTA to variant {next_variant}: '{EMAIL_CTA_VARIANTS[next_variant]['heading']}'"
                log_decision("ADAPT_CTA", msg)
                send_tg(f"ADAPT: {msg}")
                state["email_cta_variant"] = next_variant
                changed = True
                print(f"[adapt] {msg}")

    # Rule 2: 0 payments in 7 days (only if we have historical payments)
    if not changed and len(payments) > 0:
        cutoff_7d = now - timedelta(days=7)
        recent_payments = sum(1 for p in payments if (parse_timestamp(p) or datetime.min.replace(tzinfo=timezone.utc)) > cutoff_7d)
        if recent_payments == 0:
            next_variant = (state.get("pricing_variant", 0) + 1) % len(PRICING_SUB_VARIANTS)
            if rewrite_pricing_sub(next_variant):
                msg = f"0 payments in 7 days. Rotated pricing copy to variant {next_variant}: '{PRICING_SUB_VARIANTS[next_variant][:60]}...'"
                log_decision("ADAPT_PRICING", msg)
                send_tg(f"ADAPT: {msg}")
                state["pricing_variant"] = next_variant
                changed = True
                print(f"[adapt] {msg}")

    # Rule 3: 0% conversion from outreach after 50 sends
    sent_count = sum(1 for e in outreach_log if e.get("status") == "sent")
    if not changed and sent_count >= 50:
        outreach_addrs = {e.get("email", "").lower() for e in outreach_log if e.get("status") == "sent"}
        signup_addrs = set()
        for entry in emails:
            addr = entry.get("email") or entry.get("address") or ""
            if addr:
                signup_addrs.add(addr.lower())
        conversions = outreach_addrs & signup_addrs
        if len(conversions) == 0:
            if rewrite_cold_email():
                state["cold_email_rewrites"] = state.get("cold_email_rewrites", 0) + 1
                msg = f"0 conversions from {sent_count} outreach emails. Rewrote cold-email.md (rewrite #{state['cold_email_rewrites']})"
                log_decision("ADAPT_OUTREACH", msg)
                send_tg(f"ADAPT: {msg}")
                changed = True
                print(f"[adapt] {msg}")

    # If we made a change, commit, push, restart
    if changed:
        state["last_change_date"] = today
        state["changes_today"] = state.get("changes_today", 0) + 1
        save_state(state)

        commit_msg = f"adapt: automated copy rotation {today}"
        if git_commit_and_push(commit_msg):
            print(f"[adapt] Committed and pushed: {commit_msg}")
        restart_service()
        print("[adapt] Service restarted.")
    else:
        state["last_run"] = now.isoformat()
        save_state(state)
        status = f"[adapt] No changes needed. emails={len(emails)} payments={len(payments)} outreach={sent_count}"
        print(status)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[adapt] Fatal: {e}", file=sys.stderr)
        log_decision("ADAPT_ERROR", str(e))
        sys.exit(1)
