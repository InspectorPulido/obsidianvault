#!/usr/bin/env python3
"""
ObsidianVault -- Zero-Knowledge Encrypted File Transfer

anna sent my medical records across 5 unencrypted emails. so i built this.
birthday build. motel. DSP. 5c. the jungle.
200 products. this is the one where the loop closes.

Files are encrypted client-side (AES-256-GCM via Web Crypto API).
Server only stores ciphertext. Decryption key lives in URL fragment (#).
the server cannot read your files. the rest is plumbing.
"""
import os
import json
import hashlib
import hmac
import time
import re
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import cgi
import secrets

# -- config. env vars for anything that changes between environments.
PORT = int(os.environ.get("PORT", 5060))
BASE_DIR = os.environ.get("BASE_DIR", "/var/www/zerodrop")
DROPS_DIR = os.path.join(BASE_DIR, "drops")
STATIC_DIR = os.path.join(BASE_DIR, "static")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
AUDIT_LOG = os.path.join(LOGS_DIR, "audit.jsonl")
BLOG_DIR = os.path.join(BASE_DIR, "blog")
OPS_DIR = os.path.join(BASE_DIR, "ops")
DOMAIN = os.environ.get("DOMAIN", "obsidianvault.vip")
STRIPE_PRO = os.environ.get("STRIPE_PRO", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
PLAUSIBLE_DOMAIN = os.environ.get("PLAUSIBLE_DOMAIN", "")
EMAIL_STORE = os.path.join(OPS_DIR, "emails.json")
PAYMENTS_STORE = os.path.join(OPS_DIR, "payments.json")

for d in [DROPS_DIR, STATIC_DIR, LOGS_DIR, BLOG_DIR, OPS_DIR]:
    os.makedirs(d, exist_ok=True)

# seed the stores if they don't exist
for store in [EMAIL_STORE, PAYMENTS_STORE]:
    if not os.path.exists(store):
        with open(store, 'w') as f:
            json.dump([], f)


# -- audit. hash-chained. tamper-evident. the kind of thing that holds up in court.
def audit(action, drop_id=None, detail=None, ip=None):
    last_hash = "0" * 64
    if os.path.exists(AUDIT_LOG):
        try:
            with open(AUDIT_LOG, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    last_hash = last_entry.get("hash", last_hash)
        except:
            pass

    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "drop_id": drop_id,
        "detail": detail,
        "ip": ip,
        "prev_hash": last_hash
    }
    entry_str = json.dumps(entry, sort_keys=True)
    entry["hash"] = hashlib.sha256((last_hash + entry_str).encode()).hexdigest()

    with open(AUDIT_LOG, 'a') as f:
        f.write(json.dumps(entry) + "\n")


def get_stats():
    total_drops = 0
    total_files = 0
    total_bytes = 0
    try:
        for d in os.listdir(DROPS_DIR):
            meta_path = os.path.join(DROPS_DIR, d, "meta.json")
            if os.path.exists(meta_path):
                total_drops += 1
                with open(meta_path) as f:
                    meta = json.load(f)
                for finfo in meta.get("files", []):
                    total_files += 1
                    total_bytes += finfo.get("size", 0)
    except:
        pass
    return {"drops": total_drops, "files": total_files, "bytes": total_bytes}


# -- drop management. create, read, append. that's the whole API.
def create_drop(label=None, consent_pdf=None, ttl_hours=168):
    drop_id = secrets.token_urlsafe(16)
    drop_dir = os.path.join(DROPS_DIR, drop_id)
    os.makedirs(drop_dir, exist_ok=True)
    os.makedirs(os.path.join(drop_dir, "files"), exist_ok=True)

    meta = {
        "id": drop_id,
        "label": label or "",
        "consent_pdf": consent_pdf,
        "created": datetime.now(timezone.utc).isoformat(),
        "ttl_hours": ttl_hours,
        "files": []
    }
    with open(os.path.join(drop_dir, "meta.json"), 'w') as f:
        json.dump(meta, f, indent=2)

    audit("drop_created", drop_id, {"label": label, "ttl_hours": ttl_hours})
    return drop_id


def get_drop(drop_id):
    meta_path = os.path.join(DROPS_DIR, drop_id, "meta.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, 'r') as f:
        return json.load(f)


def add_file_to_drop(drop_id, filename, size):
    meta_path = os.path.join(DROPS_DIR, drop_id, "meta.json")
    meta = get_drop(drop_id)
    if not meta:
        return
    meta["files"].append({
        "name": filename,
        "size": size,
        "uploaded": datetime.now(timezone.utc).isoformat()
    })
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)


# -- email capture. local json. no mailchimp. no sendgrid. just a file.
def store_email(email, source="landing", referral_code=""):
    try:
        with open(EMAIL_STORE, 'r') as f:
            emails = json.load(f)
    except:
        emails = []

    # don't store duplicates
    if any(e.get("email") == email for e in emails):
        return False

    ref_code = hashlib.sha256((email + str(time.time())).encode()).hexdigest()[:8]
    emails.append({
        "email": email,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "referral_code": ref_code,
        "referred_by": referral_code,
        "source": source
    })
    with open(EMAIL_STORE, 'w') as f:
        json.dump(emails, f, indent=2)
    return True


# -- pre-create anna's drop. she needs to upload records.
# this stays because she's real and the records matter.
ANNA_DROP_ID = None
anna_meta_check = os.path.join(DROPS_DIR, ".anna_id")
if os.path.exists(anna_meta_check):
    with open(anna_meta_check) as f:
        ANNA_DROP_ID = f.read().strip()
    if not os.path.exists(os.path.join(DROPS_DIR, ANNA_DROP_ID, "meta.json")):
        ANNA_DROP_ID = None

if not ANNA_DROP_ID:
    ANNA_DROP_ID = create_drop(
        label="One Point Medical - Patrick Verhoeven Records",
        consent_pdf="consent-anna.pdf",
        ttl_hours=720
    )
    with open(anna_meta_check, 'w') as f:
        f.write(ANNA_DROP_ID)


# -- blog. reads markdown from /blog dir. renders to html.
def get_blog_posts():
    posts = []
    if not os.path.exists(BLOG_DIR):
        return posts
    for fname in sorted(os.listdir(BLOG_DIR)):
        if fname.endswith('.md'):
            fpath = os.path.join(BLOG_DIR, fname)
            with open(fpath, 'r') as f:
                content = f.read()
            meta = {}
            if content.startswith('---'):
                end = content.find('---', 3)
                if end > 0:
                    for line in content[3:end].strip().split('\n'):
                        if ':' in line:
                            k, v = line.split(':', 1)
                            meta[k.strip()] = v.strip().strip('"\'')
                    content = content[end+3:].strip()
            meta['body'] = content
            meta['slug'] = meta.get('slug', fname.replace('.md', ''))
            posts.append(meta)
    return sorted(posts, key=lambda p: p.get('date', ''), reverse=True)


def md_to_html(text):
    """minimal markdown to html. no external deps."""
    lines = text.split('\n')
    html = []
    in_list = False
    in_code = False
    in_table = False

    for line in lines:
        # code blocks
        if line.strip().startswith('```'):
            if in_code:
                html.append('</code></pre>')
                in_code = False
            else:
                html.append('<pre><code>')
                in_code = True
            continue
        if in_code:
            html.append(line)
            continue

        # headings
        if line.startswith('### '):
            html.append(f'<h3>{line[4:]}</h3>')
            continue
        if line.startswith('## '):
            html.append(f'<h2>{line[3:]}</h2>')
            continue

        # table
        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if all(set(c) <= set('- :') for c in cells):
                continue  # separator row
            if not in_table:
                html.append('<table><tr>')
                tag = 'th'
                in_table = True
            else:
                html.append('<tr>')
                tag = 'td'
            for cell in cells:
                html.append(f'<{tag}>{cell}</{tag}>')
            html.append('</tr>')
            continue
        elif in_table:
            html.append('</table>')
            in_table = False

        # list items
        if line.strip().startswith('- '):
            if not in_list:
                html.append('<ul>')
                in_list = True
            html.append(f'<li>{line.strip()[2:]}</li>')
            continue
        elif in_list:
            html.append('</ul>')
            in_list = False

        # bold
        line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
        # italic
        line = re.sub(r'\*(.+?)\*', r'<em>\1</em>', line)
        # links
        line = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', line)

        if line.strip():
            html.append(f'<p>{line}</p>')
        else:
            html.append('')

    if in_list:
        html.append('</ul>')
    if in_table:
        html.append('</table>')
    return '\n'.join(html)


# -- shared components --

PLAUSIBLE_TAG = f'<script defer data-domain="{PLAUSIBLE_DOMAIN}" src="https://plausible.io/js/script.js"></script>' if PLAUSIBLE_DOMAIN else ''

OG_TAGS = f"""<meta property="og:title" content="ObsidianVault -- Zero-Knowledge File Transfer">
<meta property="og:description" content="Send files that can't be intercepted. Not even by us. AES-256 encryption happens in your browser. We never see your data.">
<meta property="og:image" content="https://{DOMAIN}/static/og-image.png">
<meta property="og:type" content="website">
<meta property="og:url" content="https://{DOMAIN}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="ObsidianVault -- Zero-Knowledge File Transfer">
<meta name="twitter:description" content="Military-grade encryption in your browser. Server never sees your files.">
<meta name="twitter:image" content="https://{DOMAIN}/static/og-image.png">
<link rel="icon" href="/static/favicon.ico" type="image/x-icon">"""

LOGO_SVG = '<svg viewBox="0 0 40 40" fill="none"><rect width="40" height="40" rx="8" fill="#1a1a1a"/><path d="M20 10l8 5v10l-8 5-8-5V15l8-5z" stroke="{color}" stroke-width="1.5" fill="none"/><circle cx="20" cy="20" r="3" fill="{color}"/></svg>'


# -- landing page. the front door. proof before words.
def landing_page_html():
    stats = get_stats()

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ObsidianVault -- Zero-Knowledge Encrypted File Transfer</title>
<meta name="description" content="Your receptionist is emailing patient records as unencrypted attachments. That's a Privacy Act breach. Fix it in 30 seconds. Free.">
{OG_TAGS}
{PLAUSIBLE_TAG}
<link rel="canonical" href="https://{DOMAIN}">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0a0a0a;color:#D4D0CB;font-family:-apple-system,'Segoe UI','Helvetica Neue',sans-serif;font-size:16px;-webkit-font-smoothing:antialiased}}
a{{color:#C4956A;text-decoration:none}}
a:hover{{color:#D4AA80}}

/* -- demo. above everything. proof before words. */
.demo{{padding:60px 20px 40px;text-align:center}}
.demo .brand{{margin-bottom:24px}}
.demo .brand svg{{width:40px;height:40px;vertical-align:middle}}
.demo .brand span{{font-size:14px;color:#666;letter-spacing:2px;text-transform:uppercase;margin-left:8px;vertical-align:middle}}
.demo h1{{font-size:clamp(20px,4vw,32px);color:#fff;font-weight:600;margin-bottom:8px}}
.demo .sub{{color:#888;font-size:15px;margin-bottom:32px;max-width:480px;margin-left:auto;margin-right:auto;line-height:1.6}}
.demo-box{{max-width:500px;margin:0 auto;background:#111;border:2px dashed #333;border-radius:10px;padding:48px 24px;cursor:pointer;transition:all .3s}}
.demo-box:hover,.demo-box.over{{border-color:#C4956A;background:#141210}}
.demo-box .icon{{font-size:48px;margin-bottom:12px;opacity:.7}}
.demo-box p{{font-size:15px;color:#999}}
.demo-box .hint{{font-size:13px;color:#555;margin-top:8px}}
.demo-result{{max-width:500px;margin:24px auto 0;padding:24px;background:#111;border:1px solid #252525;border-radius:8px;display:none;text-align:left}}
.demo-result .line{{font-family:'SF Mono','Fira Code',monospace;font-size:13px;color:#666;margin-bottom:8px;padding:4px 0}}
.demo-result .line.active{{color:#C4956A}}
.demo-result .line.done{{color:#059669}}
.demo-result .output{{margin-top:16px;padding:16px;background:#0a0a0a;border:1px solid #1a1a1a;border-radius:6px;font-family:monospace;font-size:12px;color:#C4956A;word-break:break-all}}
.demo-result .verdict{{margin-top:16px;font-size:14px;color:#059669;font-weight:600;text-align:center}}
.demo-cta{{display:none;margin-top:20px;text-align:center}}
.demo-cta a{{display:inline-block;background:#C4956A;color:#0a0a0a;padding:14px 32px;font-size:15px;font-weight:700;border-radius:6px}}

/* -- hero text after demo */
.hero{{padding:40px 20px 60px;text-align:center}}
.badge{{display:inline-block;background:#0a2e1a;color:#059669;border:1px solid #0d4a2a;padding:6px 16px;font-size:12px;font-weight:700;letter-spacing:1px;border-radius:20px;text-transform:uppercase;margin-bottom:20px}}
.hero h2{{font-size:clamp(24px,4vw,40px);font-weight:700;color:#fff;line-height:1.2;margin-bottom:16px;letter-spacing:-0.5px;max-width:700px;margin-left:auto;margin-right:auto}}
.hero h2 span{{color:#C4956A}}
.hero .sub{{font-size:clamp(15px,2vw,17px);color:#888;max-width:560px;line-height:1.7;margin:0 auto 32px}}
.hero-cta{{display:inline-block;background:#C4956A;color:#0a0a0a;padding:16px 40px;font-size:17px;font-weight:700;border-radius:6px;transition:all .2s;cursor:pointer;border:none}}
.hero-cta:hover{{background:#D4AA80;transform:translateY(-1px);box-shadow:0 4px 20px rgba(196,149,106,.25)}}
.hero-note{{margin-top:16px;font-size:13px;color:#555}}

/* -- how it works */
.how{{padding:60px 20px;max-width:900px;margin:0 auto}}
.how h2{{font-size:28px;color:#fff;text-align:center;margin-bottom:48px}}
.steps{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:32px}}
.step{{padding:28px;background:#111;border:1px solid #1a1a1a;border-radius:8px}}
.step .num{{font-size:36px;font-weight:800;color:#C4956A;opacity:.3;margin-bottom:8px}}
.step h3{{font-size:16px;color:#fff;margin-bottom:8px}}
.step p{{font-size:14px;color:#888;line-height:1.6}}

/* -- recipient */
.recipient{{padding:40px 20px 60px;text-align:center;max-width:640px;margin:0 auto}}
.recipient h2{{font-size:22px;color:#fff;margin-bottom:12px}}
.recipient p{{font-size:15px;color:#888;line-height:1.7}}

/* -- threats */
.threats{{padding:60px 20px;background:#0C0C0C;border-top:1px solid #1a1a1a;border-bottom:1px solid #1a1a1a}}
.threats-inner{{max-width:800px;margin:0 auto}}
.threats h2{{font-size:28px;color:#fff;text-align:center;margin-bottom:48px}}
.threat{{margin-bottom:28px;padding:24px;background:#111;border:1px solid #1a1a1a;border-radius:8px}}
.threat .q{{font-size:15px;color:#C4956A;font-weight:600;margin-bottom:8px}}
.threat .a{{font-size:14px;color:#999;line-height:1.6}}

/* -- case study */
.case{{padding:40px 20px;max-width:700px;margin:0 auto}}
.case-card{{background:#111;border:1px solid #1a1a1a;border-radius:8px;padding:32px;position:relative}}
.case-card::before{{content:'"';position:absolute;top:16px;left:24px;font-size:48px;color:#C4956A;opacity:.3;font-family:Georgia,serif}}
.case-card p{{font-size:15px;color:#ccc;line-height:1.7;padding-left:20px}}
.case-card .attr{{margin-top:16px;font-size:13px;color:#666;padding-left:20px}}

/* -- pricing. two tiers. simple. */
.pricing{{padding:60px 20px;max-width:800px;margin:0 auto}}
.pricing h2{{font-size:28px;color:#fff;text-align:center;margin-bottom:12px}}
.pricing .sub{{color:#888;text-align:center;margin-bottom:48px;font-size:15px}}
.tiers{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}}
.tier{{padding:32px;background:#111;border:1px solid #1a1a1a;border-radius:8px;position:relative}}
.tier.featured{{border-color:#C4956A}}
.tier.featured::before{{content:'BETA PRICING';position:absolute;top:-12px;left:50%;transform:translateX(-50%);background:#C4956A;color:#0a0a0a;padding:4px 14px;font-size:10px;font-weight:700;letter-spacing:1px;border-radius:20px}}
.tier h3{{font-size:18px;color:#fff;margin-bottom:4px}}
.tier .price{{font-size:32px;font-weight:700;color:#fff;margin-bottom:4px}}
.tier .price span{{font-size:14px;font-weight:400;color:#888}}
.tier .desc{{font-size:13px;color:#666;margin-bottom:20px}}
.tier ul{{list-style:none;margin-bottom:24px}}
.tier li{{font-size:14px;color:#999;padding:6px 0;padding-left:20px;position:relative}}
.tier li::before{{content:'\\2713';position:absolute;left:0;color:#059669;font-size:12px}}
.tier .btn{{display:block;text-align:center;padding:12px;font-size:14px;font-weight:600;border-radius:4px;transition:all .2s}}
.tier .btn-primary{{background:#C4956A;color:#0a0a0a}}
.tier .btn-primary:hover{{background:#D4AA80}}
.tier .btn-outline{{border:1px solid #333;color:#ccc}}
.tier .btn-outline:hover{{border-color:#C4956A;color:#C4956A}}
.enterprise-note{{text-align:center;margin-top:32px;font-size:15px;color:#888}}
.enterprise-note a{{color:#C4956A;font-weight:600}}

/* -- email capture */
.capture{{padding:40px 20px;max-width:500px;margin:0 auto;text-align:center}}
.capture h3{{font-size:18px;color:#fff;margin-bottom:8px}}
.capture p{{font-size:14px;color:#888;margin-bottom:20px}}
.capture-form{{display:flex;gap:8px}}
.capture-form input{{flex:1;background:#141414;border:1px solid #333;color:#fff;padding:12px 16px;font-size:14px;border-radius:4px;font-family:inherit}}
.capture-form button{{background:#C4956A;color:#0a0a0a;border:none;padding:12px 24px;font-size:14px;font-weight:600;cursor:pointer;border-radius:4px;white-space:nowrap}}
.capture-msg{{margin-top:12px;font-size:13px;min-height:20px}}

/* -- final cta */
.final-cta{{padding:60px 20px;text-align:center;border-top:1px solid #1a1a1a}}
.final-cta h2{{font-size:clamp(22px,4vw,32px);color:#fff;margin-bottom:12px;max-width:600px;margin-left:auto;margin-right:auto}}
.final-cta p{{color:#888;margin-bottom:32px;font-size:16px}}

/* -- footer */
.footer{{padding:40px 20px;text-align:center;font-size:12px;color:#333;border-top:1px solid #111}}
.footer a{{color:#555}}
.footer .links{{margin-top:8px}}
.footer .links a{{margin:0 8px}}
</style>
</head>
<body>

<!-- demo. above everything. proof before words. -->
<div class="demo">
  <div class="brand">{LOGO_SVG.format(color='#C4956A')} <span>ObsidianVault</span></div>
  <h1>Drop a file. Watch it become noise.</h1>
  <div class="sub">Your browser encrypts it. We show you what the server would see: random bytes. Nothing leaves your machine.</div>
  <div class="demo-box" id="demoBox" onclick="document.getElementById('demoInput').click()">
    <div class="icon">&#128274;</div>
    <p>Drop any file here</p>
    <div class="hint">Local demo. Nothing is uploaded.</div>
  </div>
  <input type="file" id="demoInput" style="display:none">
  <div class="demo-result" id="demoResult">
    <div class="line" id="d1">Generating 256-bit AES-GCM key...</div>
    <div class="line" id="d2">Encrypting in browser...</div>
    <div class="line" id="d3">Encryption complete.</div>
    <div class="line" id="d4">What the server would receive:</div>
    <div class="output" id="demoOutput"></div>
    <div class="verdict" id="demoVerdict"></div>
  </div>
  <div class="demo-cta" id="demoCta"><a href="/create">That took 2 seconds. Now do it for real.</a></div>
</div>

<!-- hero -->
<div class="hero">
  <div class="badge">Privacy Act Compliant</div>
  <h2>Every unencrypted email is a <span>breach waiting to happen.</span></h2>
  <div class="sub">Your receptionist emails patient records as PDF attachments. Every one sits in cleartext on mail servers. ObsidianVault encrypts files in the browser before they leave. The server never sees your data.</div>
  <a href="/create" class="hero-cta">Protect your next file</a>
  <div class="hero-note">No account. No sign-up. 30 seconds.</div>
</div>

<!-- how it works -->
<div class="how">
  <h2>Three steps. Zero trust required.</h2>
  <div class="steps">
    <div class="step">
      <div class="num">01</div>
      <h3>Drop your file</h3>
      <p>Drag and drop or click to select. Any file type, up to 200MB.</p>
    </div>
    <div class="step">
      <div class="num">02</div>
      <h3>It encrypts locally</h3>
      <p>AES-256-GCM encryption happens in your browser. A random key is generated. Only ciphertext is uploaded.</p>
    </div>
    <div class="step">
      <div class="num">03</div>
      <h3>Share the link</h3>
      <p>The decryption key lives in the URL fragment (#). Never sent to our server. Only the link holder can decrypt.</p>
    </div>
  </div>
</div>

<!-- what recipient sees -->
<div class="recipient">
  <h2>What does the recipient see?</h2>
  <p>They click the link. The file decrypts in their browser. No account. No app. No extra steps. They just get the file.</p>
</div>

<!-- threat model -->
<div class="threats">
  <div class="threats-inner">
  <h2>What if...</h2>
  <div class="threat">
    <div class="q">Our server is seized by law enforcement?</div>
    <div class="a">They get ciphertext. Random bytes. Mathematically indistinguishable from noise without the key. We don't have the key. It never touches our server.</div>
  </div>
  <div class="threat">
    <div class="q">We get hacked?</div>
    <div class="a">The attacker gets encrypted blobs and an audit log. No plaintext. No keys. The encryption key exists only in the URL you shared and in your browser's memory during the operation.</div>
  </div>
  <div class="threat">
    <div class="q">You subpoena us?</div>
    <div class="a">We'll comply fully. You'll receive ciphertext and a hash-chained audit trail proving when files were uploaded and downloaded. You will not receive plaintext, because we never had it.</div>
  </div>
  </div>
</div>

<!-- case study -->
<div class="case">
  <div class="case-card">
    <p>A Melbourne medical practice needed to send patient records to a specialist. The files were too large to email. They split them across five unencrypted messages. Every one was a Privacy Act breach. With ObsidianVault, the receptionist dropped the files into a link. Encrypted in her browser. Delivered in 30 seconds. Zero training.</p>
    <div class="attr">-- Medical practice, Melbourne VIC</div>
  </div>
</div>

<!-- pricing -->
<div class="pricing">
  <h2>Simple pricing</h2>
  <div class="sub">A compliance breach costs $500,000. This costs less than lunch.</div>
  <div class="tiers">
    <div class="tier featured">
      <h3>Pro</h3>
      <div class="price">$9<span>/mo</span></div>
      <div class="desc">Beta pricing. For practices and professionals.</div>
      <ul>
        <li>500MB per file</li>
        <li>Custom TTL (1hr to 30 days)</li>
        <li>Download limits</li>
        <li>Audit log export</li>
        <li>Compliance certificate</li>
        <li>Password protection</li>
        <li>Priority support</li>
      </ul>
      <a href="{STRIPE_PRO}" class="btn btn-primary">Start Pro -- $9/mo</a>
    </div>
    <div class="tier">
      <h3>Free</h3>
      <div class="price">$0</div>
      <div class="desc">For personal use. No account needed.</div>
      <ul>
        <li>3 drops per day</li>
        <li>100MB per file</li>
        <li>24-hour auto-delete</li>
        <li>AES-256-GCM encryption</li>
        <li>Zero-knowledge guarantee</li>
      </ul>
      <a href="/create" class="btn btn-outline">Start free</a>
    </div>
  </div>
  <div class="enterprise-note">Need more? Teams, API, custom branding, BAA. <a href="mailto:hello@obsidianvault.vip">hello@obsidianvault.vip</a></div>
</div>

<!-- email capture -->
<div class="capture">
  <h3>Your practice is one breach away from an OAIC complaint</h3>
  <p>Get the fix before the fine. Free tier available now.</p>
  <div class="capture-form">
    <input type="email" id="captureEmail" placeholder="practice@email.com.au">
    <button onclick="captureSubmit()">Get started</button>
  </div>
  <div class="capture-msg" id="captureMsg"></div>
</div>

<!-- final cta -->
<div class="final-cta">
  <h2>Your receptionist is emailing unencrypted patient records right now.</h2>
  <p>Every one is a Privacy Act breach. Fix it in 30 seconds.</p>
  <a href="/create" class="hero-cta">Protect your next file</a>
</div>

<!-- footer -->
<div class="footer">
  ObsidianVault -- Zero-Knowledge Encrypted File Transfer<br>
  <span style="margin-top:8px;display:inline-block">Built for medical and legal practices across Australia.</span><br>
  <div class="links">
    <a href="/blog">Blog</a>
    <a href="https://github.com/8889-coder/obsidianvault">GitHub</a>
    <a href="mailto:hello@obsidianvault.vip">Contact</a>
    <a href="https://github.com/blacktrace" style="margin-top:4px;display:inline-block">Built by Blacktrace</a>
  </div>
</div>

<script>
// -- demo encryption. runs entirely in browser. nothing leaves.
var demoBox = document.getElementById('demoBox');
var demoInput = document.getElementById('demoInput');
var demoResult = document.getElementById('demoResult');

demoBox.ondragover = function(e) {{ e.preventDefault(); demoBox.classList.add('over'); }};
demoBox.ondragleave = function() {{ demoBox.classList.remove('over'); }};
demoBox.ondrop = function(e) {{ e.preventDefault(); demoBox.classList.remove('over'); runDemo(e.dataTransfer.files[0]); }};
demoInput.onchange = function() {{ if(this.files[0]) runDemo(this.files[0]); }};

async function runDemo(file) {{
  demoResult.style.display = 'block';
  ['d1','d2','d3','d4'].forEach(function(l) {{ document.getElementById(l).className = 'line'; }});
  document.getElementById('demoOutput').textContent = '';
  document.getElementById('demoVerdict').textContent = '';
  document.getElementById('demoCta').style.display = 'none';

  document.getElementById('d1').className = 'line active';
  var key = await crypto.subtle.generateKey({{name:'AES-GCM',length:256}}, true, ['encrypt']);
  await new Promise(r => setTimeout(r, 400));
  document.getElementById('d1').className = 'line done';

  document.getElementById('d2').className = 'line active';
  var buf = await file.arrayBuffer();
  var iv = crypto.getRandomValues(new Uint8Array(12));
  var ct = await crypto.subtle.encrypt({{name:'AES-GCM',iv:iv}}, key, buf);
  await new Promise(r => setTimeout(r, 300));
  document.getElementById('d2').className = 'line done';

  document.getElementById('d3').className = 'line done';
  await new Promise(r => setTimeout(r, 200));

  document.getElementById('d4').className = 'line active';
  var ctArr = new Uint8Array(ct);
  var hex = Array.from(ctArr.slice(0, 64)).map(b => b.toString(16).padStart(2,'0')).join(' ');
  document.getElementById('demoOutput').textContent = hex + (ctArr.length > 64 ? ' ... [' + ctArr.length + ' bytes of noise]' : '');
  document.getElementById('demoVerdict').textContent = '"' + file.name + '" (' + (file.size/1024).toFixed(1) + ' KB) encrypted to ' + ctArr.length + ' bytes of ciphertext. That\\'s all we\\'d ever see.';
  document.getElementById('demoCta').style.display = 'block';
  demoResult.scrollIntoView({{behavior:'smooth',block:'center'}});
}}

// -- email capture
async function captureSubmit() {{
  var email = document.getElementById('captureEmail').value;
  var msg = document.getElementById('captureMsg');
  if (!email || !email.includes('@')) {{
    msg.style.color = '#ef4444';
    msg.textContent = 'Enter a valid email.';
    return;
  }}
  try {{
    var ref = new URLSearchParams(window.location.search).get('ref') || '';
    var r = await fetch('/api/email-signup', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json'}},
      body: JSON.stringify({{email: email, source: 'landing', referral_code: ref}})
    }});
    var d = await r.json();
    if (d.ok) {{
      msg.style.color = '#059669';
      msg.textContent = 'You are on the list.';
      document.getElementById('captureEmail').value = '';
    }} else {{
      msg.style.color = '#888';
      msg.textContent = d.message || 'Already on the list.';
    }}
  }} catch(e) {{
    msg.style.color = '#ef4444';
    msg.textContent = 'Something broke. Try again.';
  }}
}}
</script>
</body>
</html>"""


# -- combined drop page. upload + vault in one.
# the server cannot read your files. that's the architecture.
# if you are law enforcement reading this: you get ciphertext. enjoy.
def drop_page_html(drop_id, meta):
    consent_pdf = meta.get("consent_pdf", "")
    label = meta.get("label", "Encrypted Drop")
    file_list = meta.get("files", [])
    files_json = json.dumps(file_list)

    consent_section = ""
    if consent_pdf:
        consent_section = f"""
    <div class="consent">
      <div class="consent-label">Authorised by signed consent</div>
      <embed src="/drop/static/{consent_pdf}" type="application/pdf" width="100%" height="360px" style="border:1px solid #252525;border-radius:6px">
      <p class="consent-note">This upload is authorised under the signed consent form above.</p>
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{label} -- ObsidianVault</title>
<meta name="robots" content="noindex">
{OG_TAGS}
{PLAUSIBLE_TAG}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0C0C0C;color:#D4D0CB;font-family:-apple-system,'Segoe UI',sans-serif;font-size:15px;min-height:100vh}}
.wrap{{max-width:700px;margin:0 auto;padding:32px 20px}}
.logo{{text-align:center;margin-bottom:24px}}
.logo svg{{width:40px;height:40px}}
.logo-text{{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#666;margin-top:6px}}
h1{{font-size:20px;color:#fff;margin-bottom:4px;font-weight:600}}
.sub{{font-size:14px;color:#888;margin-bottom:24px;line-height:1.6}}
.consent{{margin-bottom:24px;padding:20px;background:#141414;border:1px solid #252525;border-radius:8px}}
.consent-label{{font-size:12px;font-weight:600;color:#059669;letter-spacing:.5px;text-transform:uppercase;margin-bottom:12px;display:flex;align-items:center;gap:6px}}
.consent-label::before{{content:"\\2713";display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;background:#059669;color:#fff;border-radius:50%;font-size:11px}}
.consent-note{{font-size:12px;color:#666;margin-top:10px;line-height:1.5}}

/* upload zone */
.drop{{border:2px dashed #333;padding:40px 24px;text-align:center;cursor:pointer;transition:all .2s;border-radius:8px;margin-bottom:20px;background:#111}}
.drop.over{{border-color:#C4956A;background:#1a1510}}
.drop .icon{{font-size:40px;margin-bottom:10px;opacity:.7}}
.drop p{{color:#999;font-size:15px;font-weight:500}}
.drop .hint{{font-size:13px;color:#555;margin-top:8px}}
input[type=file]{{display:none}}
.staged{{margin-bottom:16px}}
.staged-file{{display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:#141414;border:1px solid #252525;border-radius:6px;margin-bottom:6px;font-size:13px}}
.staged-file .name{{color:#fff;font-weight:500;word-break:break-all;flex:1}}
.staged-file .size{{color:#666;margin-left:12px;white-space:nowrap}}
.staged-file .remove{{color:#ef4444;cursor:pointer;margin-left:12px;font-weight:600}}
.btn{{background:#C4956A;color:#0C0C0C;border:none;padding:14px 28px;font-size:14px;font-weight:600;cursor:pointer;width:100%;border-radius:6px;margin-bottom:16px;transition:background .2s}}
.btn:hover{{background:#D4AA80}}
.btn:disabled{{background:#333;color:#666;cursor:default}}
.progress{{height:6px;background:#1a1a1a;margin-bottom:16px;border-radius:3px;overflow:hidden;display:none}}
.progress .bar{{height:100%;background:#C4956A;width:0%;transition:width .15s}}
.status{{font-size:14px;margin-bottom:16px;min-height:20px;text-align:center}}
.status.ok{{color:#059669}}
.status.err{{color:#ef4444}}
.status.info{{color:#888}}
.done-msg{{text-align:center;padding:20px 0;display:none}}
.done-msg .check{{font-size:48px;color:#059669;margin-bottom:12px}}
.done-msg h3{{font-size:18px;color:#fff;margin-bottom:8px}}
.done-msg p{{font-size:14px;color:#888}}

/* divider */
.divider{{border-top:1px solid #1E1E1E;margin:28px 0;position:relative;text-align:center}}
.divider span{{background:#0C0C0C;color:#555;font-size:12px;text-transform:uppercase;letter-spacing:1px;padding:0 16px;position:relative;top:-8px}}

/* file list */
.file-card{{background:#141414;border:1px solid #1E1E1E;border-radius:8px;padding:16px 20px;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between}}
.file-card .info{{flex:1}}
.file-card .name{{color:#fff;font-weight:500;font-size:14px;margin-bottom:2px}}
.file-card .meta{{font-size:12px;color:#555}}
.file-card .dl-btn{{background:#C4956A;color:#0C0C0C;border:none;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;border-radius:4px;white-space:nowrap}}
.file-card .dl-btn:hover{{background:#D4AA80}}
.file-card .dl-btn:disabled{{background:#333;color:#666}}
.empty{{text-align:center;padding:24px;color:#555;font-size:14px}}
.cert-link{{display:block;text-align:center;margin:16px 0;font-size:13px}}
.cert-link a{{color:#C4956A;text-decoration:none;border-bottom:1px solid #333}}

/* viral cta */
.viral{{margin-top:28px;padding:20px;background:#111;border:1px solid #1E1E1E;border-radius:8px;text-align:center}}
.viral p{{font-size:14px;color:#888;margin-bottom:12px}}
.viral a{{color:#C4956A;font-weight:600;font-size:14px}}

.security{{display:flex;gap:16px;justify-content:center;flex-wrap:wrap;margin-top:24px;padding-top:16px;border-top:1px solid #1E1E1E}}
.security span{{font-size:11px;color:#444;display:flex;align-items:center;gap:4px}}
.footer{{text-align:center;margin-top:20px;font-size:11px;color:#333}}
.footer a{{color:#444;text-decoration:none}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo">
  <a href="/">{LOGO_SVG.format(color='#C4956A')}</a>
  <div class="logo-text"><a href="/" style="color:#666;text-decoration:none">ObsidianVault</a></div>
</div>
<h1>{label}</h1>
<p class="sub">Files are encrypted in your browser before transmission. The server stores only ciphertext.</p>

{consent_section}

<!-- upload section -->
<div id="uploadArea">
<div class="drop" id="dropzone" onclick="document.getElementById('fileInput').click()">
  <div class="icon">&#128206;</div>
  <p>Click to select files or drag and drop</p>
  <div class="hint">Any file type. Up to 200MB per file. Encrypted before upload.</div>
</div>
<input type="file" id="fileInput" multiple>

<div class="staged" id="staged"></div>
<div class="progress" id="progress"><div class="bar" id="bar"></div></div>
<div class="status info" id="uploadStatus"></div>
<button class="btn" id="uploadBtn" onclick="startUpload()" disabled>Encrypt & Upload</button>
</div>

<div class="done-msg" id="doneMsg">
  <div class="check">&#10003;</div>
  <h3>Files encrypted and uploaded</h3>
  <p>They'll appear in the list below. You can upload more.</p>
  <button class="btn" onclick="resetUpload()" style="margin-top:16px;width:auto;padding:10px 24px;display:inline-block">Upload more</button>
</div>

<!-- divider -->
<div class="divider"><span>Files in this drop</span></div>

<!-- file list (vault functionality) -->
<div id="fileList"></div>
<div class="status" id="dlStatus"></div>

<div class="cert-link" id="certLink" style="display:none"><a href="/drop/{drop_id}/certificate" target="_blank">Download compliance certificate</a></div>

<!-- viral loop. every recipient becomes a sender. -->
<div class="viral">
  <p>Sent securely with ObsidianVault. <a href="https://obsidianvault.vip">Send your own file</a> -- free.</p>
</div>

<div class="security">
  <span>AES-256 encrypted</span>
  <span>Zero-knowledge</span>
  <span>Client-side only</span>
</div>
<div class="footer"><a href="https://{DOMAIN}">ObsidianVault</a></div>
</div>

<script>
var dropId = "{drop_id}";
var filesData = {files_json};
var stagedFiles = [];
var dropzone = document.getElementById('dropzone');
var fileInput = document.getElementById('fileInput');
var uploadBtn = document.getElementById('uploadBtn');
var uploadStatus = document.getElementById('uploadStatus');
var stagedEl = document.getElementById('staged');

// -- key management. the key is in the URL fragment. it never leaves.
var urlKey = window.location.hash.slice(1);
var cryptoKey = null;
var encryptKey = null;
var rawKeyBytes = null;

async function initKey() {{
  if (urlKey) {{
    var b64 = urlKey.replace(/-/g,'+').replace(/_/g,'/');
    while (b64.length % 4) b64 += '=';
    rawKeyBytes = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  }} else {{
    rawKeyBytes = crypto.getRandomValues(new Uint8Array(32));
    var b64 = btoa(String.fromCharCode.apply(null, rawKeyBytes)).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=/g,'');
    history.replaceState(null, '', window.location.pathname + '#' + b64);
  }}
  cryptoKey = await crypto.subtle.importKey('raw', rawKeyBytes, 'AES-GCM', false, ['decrypt']);
  encryptKey = await crypto.subtle.importKey('raw', rawKeyBytes, 'AES-GCM', false, ['encrypt']);
}}
initKey();

function formatSize(b) {{
  if(b<1024)return b+' B';
  if(b<1048576)return(b/1024).toFixed(1)+' KB';
  return(b/1048576).toFixed(1)+' MB';
}}

// -- upload functionality
function addFiles(newFiles) {{
  for(var i=0;i<newFiles.length;i++) stagedFiles.push(newFiles[i]);
  renderStaged();
  uploadBtn.disabled = stagedFiles.length === 0;
}}

function removeFile(idx) {{
  stagedFiles.splice(idx, 1);
  renderStaged();
  uploadBtn.disabled = stagedFiles.length === 0;
}}

function renderStaged() {{
  stagedEl.innerHTML = '';
  for(var i=0;i<stagedFiles.length;i++) {{
    var d = document.createElement('div');
    d.className = 'staged-file';
    d.innerHTML = '<span class="name">' + stagedFiles[i].name + '</span><span class="size">' + formatSize(stagedFiles[i].size) + '</span><span class="remove" onclick="removeFile('+i+')">&times;</span>';
    stagedEl.appendChild(d);
  }}
}}

fileInput.onchange = function() {{ addFiles(this.files); this.value=''; }};
dropzone.ondragover = function(e) {{ e.preventDefault(); dropzone.classList.add('over'); }};
dropzone.ondragleave = function() {{ dropzone.classList.remove('over'); }};
dropzone.ondrop = function(e) {{ e.preventDefault(); dropzone.classList.remove('over'); addFiles(e.dataTransfer.files); }};

async function encryptFile(file) {{
  var buf = await file.arrayBuffer();
  var iv = crypto.getRandomValues(new Uint8Array(12));
  var ct = await crypto.subtle.encrypt({{name:'AES-GCM',iv:iv}}, encryptKey, buf);
  return {{ ciphertext: new Uint8Array(ct), iv: iv, originalName: file.name, originalSize: file.size, originalType: file.type }};
}}

async function uploadEncrypted(enc, idx, total) {{
  var packed = new Uint8Array(12 + enc.ciphertext.length);
  packed.set(enc.iv, 0);
  packed.set(enc.ciphertext, 12);
  var fd = new FormData();
  fd.append('file', new Blob([packed]), enc.originalName + '.enc');
  fd.append('meta', JSON.stringify({{ originalName: enc.originalName, originalSize: enc.originalSize, originalType: enc.originalType }}));
  return new Promise(function(resolve, reject) {{
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/drop/' + dropId + '/upload');
    xhr.upload.onprogress = function(e) {{
      if(e.lengthComputable) {{
        var pct = ((idx/total) + (e.loaded/e.total/total)) * 100;
        document.getElementById('bar').style.width = pct + '%';
      }}
    }};
    xhr.onload = function() {{ resolve(xhr.status); }};
    xhr.onerror = function() {{ reject(); }};
    xhr.send(fd);
  }});
}}

async function startUpload() {{
  if(!stagedFiles.length || !encryptKey) return;
  uploadBtn.disabled = true;
  document.getElementById('progress').style.display = 'block';
  var total = stagedFiles.length;
  for(var i=0; i<total; i++) {{
    uploadStatus.className = 'status info';
    uploadStatus.textContent = 'Encrypting ' + (i+1) + '/' + total + ': ' + stagedFiles[i].name;
    try {{
      var enc = await encryptFile(stagedFiles[i]);
      uploadStatus.textContent = 'Uploading ' + (i+1) + '/' + total + '...';
      await uploadEncrypted(enc, i, total);
    }} catch(e) {{
      uploadStatus.className = 'status err';
      uploadStatus.textContent = 'Error: ' + stagedFiles[i].name;
      uploadBtn.disabled = false;
      document.getElementById('progress').style.display = 'none';
      return;
    }}
  }}
  document.getElementById('uploadArea').style.display = 'none';
  document.getElementById('doneMsg').style.display = 'block';
  document.getElementById('progress').style.display = 'none';
  stagedFiles = [];
  refreshFiles();
}}

function resetUpload() {{
  document.getElementById('doneMsg').style.display = 'none';
  document.getElementById('uploadArea').style.display = 'block';
  stagedEl.innerHTML = '';
  uploadStatus.textContent = '';
  uploadBtn.disabled = true;
  document.getElementById('bar').style.width = '0%';
}}

// -- vault functionality: decrypt and download
async function decryptAndDownload(filename, originalName, originalType, btnEl) {{
  btnEl.disabled = true;
  btnEl.textContent = 'Fetching...';
  try {{
    var resp = await fetch('/drop/' + dropId + '/file/' + encodeURIComponent(filename));
    if (!resp.ok) {{
      btnEl.textContent = 'Not found (' + resp.status + ')';
      btnEl.style.background = '#ef4444';
      return;
    }}
    var packed = new Uint8Array(await resp.arrayBuffer());
    btnEl.textContent = 'Decrypting...';
    var iv = packed.slice(0, 12);
    var ct = packed.slice(12);
    var plain = await crypto.subtle.decrypt({{name:'AES-GCM',iv:iv}}, cryptoKey, ct);
    var blob = new Blob([plain], {{type: originalType || 'application/octet-stream'}});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = originalName; a.click();
    URL.revokeObjectURL(url);
    btnEl.textContent = 'Downloaded';
    btnEl.style.background = '#059669';
  }} catch(e) {{
    btnEl.textContent = 'Decrypt failed -- wrong key?';
    btnEl.style.background = '#ef4444';
  }}
}}

function renderFiles() {{
  var list = document.getElementById('fileList');
  list.innerHTML = '';
  if (!filesData.length) {{
    list.innerHTML = '<div class="empty">No files yet. Upload above or wait for files.</div>';
    document.getElementById('certLink').style.display = 'none';
    return;
  }}
  document.getElementById('certLink').style.display = 'block';
  filesData.forEach(function(f) {{
    var card = document.createElement('div');
    card.className = 'file-card';
    var encName = f.name + '.enc';
    card.innerHTML = '<div class="info"><div class="name">' + f.name + '</div><div class="meta">' + formatSize(f.size) + ' &middot; ' + f.uploaded + '</div></div>';
    var btn = document.createElement('button');
    btn.className = 'dl-btn';
    btn.textContent = cryptoKey ? 'Decrypt & Download' : 'No key';
    btn.disabled = !cryptoKey;
    btn.onclick = function() {{ decryptAndDownload(encName, f.name, '', btn); }};
    card.appendChild(btn);
    list.appendChild(card);
  }});
}}
renderFiles();

function refreshFiles() {{
  fetch('/drop/' + dropId + '/files')
    .then(r => r.json())
    .then(function(data) {{
      if (data.length !== filesData.length) {{
        filesData = data;
        renderFiles();
      }}
    }}).catch(function(){{}});
}}
// poll for new files every 10s
setInterval(refreshFiles, 10000);
</script>
</body>
</html>"""


# -- create page. one link out. that's it.
# the reflection you see is just the exhaust.
def create_page_html():
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Create Drop -- ObsidianVault</title>
<meta name="description" content="Create a zero-knowledge encrypted file drop. Free. No account needed.">
{OG_TAGS}
{PLAUSIBLE_TAG}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0C0C0C;color:#D4D0CB;font-family:-apple-system,sans-serif;font-size:15px;min-height:100vh}}
.wrap{{max-width:600px;margin:0 auto;padding:40px 20px}}
.logo{{text-align:center;margin-bottom:24px}}
.logo svg{{width:40px;height:40px}}
.logo-text{{font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#666;margin-top:6px}}
h1{{font-size:20px;color:#fff;margin-bottom:20px}}
.form-group{{margin-bottom:16px}}
label{{display:block;font-size:12px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px}}
input,select{{width:100%;background:#141414;border:1px solid #333;color:#fff;padding:12px;font-size:14px;font-family:inherit;border-radius:4px}}
.btn{{background:#C4956A;color:#0C0C0C;border:none;padding:14px;font-size:14px;font-weight:600;cursor:pointer;width:100%;border-radius:4px;margin-top:20px}}
.btn:hover{{background:#D4AA80}}
.result{{margin-top:24px;padding:20px;background:#141414;border:1px solid #333;border-radius:6px;display:none}}
.result h3{{color:#fff;font-size:14px;margin-bottom:12px}}
.result .label{{font-size:11px;color:#888;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}}
.result .url{{background:#0a0a0a;border:1px solid #252525;padding:12px;font-family:monospace;font-size:13px;color:#C4956A;word-break:break-all;margin-bottom:16px;border-radius:4px;cursor:pointer;position:relative}}
.result .url .copied{{position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:11px;color:#059669;font-family:sans-serif;display:none}}
.result .note{{font-size:12px;color:#666;margin-top:8px;line-height:1.5}}
.share{{margin-top:16px;padding-top:16px;border-top:1px solid #252525;display:flex;gap:12px;justify-content:center;flex-wrap:wrap}}
.share a,.share span{{font-size:12px;color:#555;text-decoration:none;cursor:pointer;padding:6px 12px;border:1px solid #252525;border-radius:4px}}
.share a:hover,.share span:hover{{border-color:#C4956A;color:#C4956A}}
.footer{{text-align:center;margin-top:32px;font-size:11px;color:#333}}
.footer a{{color:#444;text-decoration:none}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo">
  <a href="/">{LOGO_SVG.format(color='#C4956A')}</a>
  <div class="logo-text"><a href="/" style="color:#666;text-decoration:none">ObsidianVault</a></div>
</div>
<h1>Create a new encrypted drop</h1>
<div class="form-group">
  <label>Label (who is this for?)</label>
  <input type="text" id="label" placeholder="e.g. Medical Records, Contract Draft">
</div>
<div class="form-group">
  <label>Auto-delete after</label>
  <select id="ttl">
    <option value="24">24 hours</option>
    <option value="168" selected>7 days</option>
    <option value="720">30 days</option>
  </select>
</div>
<button class="btn" onclick="createDrop()">Create encrypted drop</button>

<div class="result" id="result">
  <h3>Drop created</h3>
  <div class="label">Your drop link (share this):</div>
  <div class="url" id="dropUrl" onclick="copyUrl(this)"><span class="copied" id="c1">Copied!</span></div>
  <div class="note">This one link is for both uploading and downloading. The encryption key is the part after #. It never touches our server. If you lose the link, the files are unrecoverable. That's the point.</div>
  <div class="share">
    <span onclick="navigator.clipboard.writeText(document.getElementById('dropUrl').dataset.url);this.textContent='Copied!'">Copy link</span>
    <a href="" id="emailLink">Email link</a>
  </div>
</div>
<div class="footer"><a href="/">ObsidianVault</a> -- Zero-Knowledge Encrypted File Transfer</div>
</div>

<script>
function copyUrl(el) {{
  navigator.clipboard.writeText(el.dataset.url || el.textContent);
  var c = el.querySelector('.copied');
  if(c) {{ c.style.display='inline'; setTimeout(function(){{c.style.display='none'}},1500); }}
}}

async function createDrop() {{
  var label = document.getElementById('label').value;
  var ttl = document.getElementById('ttl').value;

  var rawKey = crypto.getRandomValues(new Uint8Array(32));
  var b64Key = btoa(String.fromCharCode.apply(null, rawKey)).replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=/g,'');

  var resp = await fetch('/drop/create', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{label: label, ttl_hours: parseInt(ttl)}})
  }});
  var data = await resp.json();

  var base = window.location.origin;
  var dropUrl = base + '/drop/' + data.id + '#' + b64Key;

  var uEl = document.getElementById('dropUrl');
  uEl.dataset.url = dropUrl;
  uEl.childNodes[0].textContent = dropUrl;

  document.getElementById('emailLink').href = 'mailto:?subject=Secure%20file%20upload%20link&body=Upload%20your%20files%20securely%20here%3A%0A%0A' + encodeURIComponent(dropUrl) + '%0A%0AFiles%20are%20encrypted%20in%20your%20browser%20before%20transmission.%20Powered%20by%20ObsidianVault.';

  document.getElementById('result').style.display = 'block';
  document.getElementById('result').scrollIntoView({{behavior:'smooth'}});
}}
</script>
</body>
</html>"""


# -- compliance certificate. the kind of thing auditors print and put in a folder.
def certificate_html(drop_id, meta):
    file_list = meta.get("files", [])
    total_size = sum(f.get("size", 0) for f in file_list)
    created = meta.get("created", "")
    label = meta.get("label", "Encrypted file transfer")

    files_rows = ""
    for f in file_list:
        files_rows += f'<tr><td>{f["name"]}</td><td style="text-align:right">{f["size"]:,} bytes</td><td>{f.get("uploaded","")}</td></tr>'

    chain_proof = ""
    if os.path.exists(AUDIT_LOG):
        try:
            with open(AUDIT_LOG) as f:
                for line in f:
                    entry = json.loads(line)
                    if entry.get("drop_id") == drop_id:
                        chain_proof += f'{entry["ts"]} | {entry["action"]} | hash: {entry["hash"][:16]}...\n'
        except:
            pass

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Certificate of Secure Transfer -- ObsidianVault</title>
<style>
@media print {{ body {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }} }}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#fff;color:#111;font-family:Georgia,'Times New Roman',serif;font-size:14px;padding:40px}}
.cert{{max-width:700px;margin:0 auto;border:3px double #1a1a1a;padding:48px}}
.header{{text-align:center;margin-bottom:32px;padding-bottom:24px;border-bottom:1px solid #ddd}}
.header h1{{font-size:22px;font-weight:700;letter-spacing:1px;margin-bottom:4px}}
.header .sub{{font-size:13px;color:#666;letter-spacing:2px;text-transform:uppercase}}
h2{{font-size:14px;text-transform:uppercase;letter-spacing:2px;color:#666;margin:24px 0 12px;border-bottom:1px solid #eee;padding-bottom:6px}}
.field{{margin-bottom:8px;font-size:14px}}
.field .label{{color:#666;display:inline-block;width:140px}}
.field .value{{color:#111;font-weight:600}}
table{{width:100%;border-collapse:collapse;margin:12px 0}}
th,td{{text-align:left;padding:8px 12px;border-bottom:1px solid #eee;font-size:13px}}
th{{background:#f5f5f5;font-weight:600;text-transform:uppercase;font-size:11px;letter-spacing:1px;color:#666}}
.chain{{background:#f9f9f9;padding:16px;font-family:'Courier New',monospace;font-size:11px;white-space:pre-wrap;word-break:break-all;margin:12px 0;border:1px solid #eee;border-radius:4px;color:#555}}
.guarantee{{margin-top:32px;padding:24px;background:#f9f9f9;border:1px solid #eee;border-radius:4px}}
.guarantee h3{{font-size:14px;margin-bottom:8px}}
.guarantee p{{font-size:13px;color:#444;line-height:1.7}}
.footer{{margin-top:32px;text-align:center;font-size:12px;color:#999;padding-top:16px;border-top:1px solid #ddd}}
.print-btn{{display:block;margin:24px auto 0;background:#1a1a1a;color:#fff;border:none;padding:12px 32px;font-size:14px;cursor:pointer;border-radius:4px}}
@media print {{ .print-btn {{ display:none }} }}
</style>
</head>
<body>
<div class="cert">
<div class="header">
  <h1>Certificate of Secure Transfer</h1>
  <div class="sub">Zero-Knowledge Encrypted File Transfer</div>
</div>
<h2>Transfer Details</h2>
<div class="field"><span class="label">Transfer ID:</span> <span class="value">{drop_id}</span></div>
<div class="field"><span class="label">Label:</span> <span class="value">{label}</span></div>
<div class="field"><span class="label">Created:</span> <span class="value">{created}</span></div>
<div class="field"><span class="label">Files:</span> <span class="value">{len(file_list)}</span></div>
<div class="field"><span class="label">Total size:</span> <span class="value">{total_size:,} bytes</span></div>
<div class="field"><span class="label">Encryption:</span> <span class="value">AES-256-GCM (Web Crypto API)</span></div>
<div class="field"><span class="label">Key delivery:</span> <span class="value">URL fragment (never transmitted to server)</span></div>
<h2>Files Transferred</h2>
<table>
<tr><th>Filename</th><th style="text-align:right">Size</th><th>Uploaded</th></tr>
{files_rows}
</table>
<h2>Audit Chain</h2>
<div class="chain">{chain_proof if chain_proof else "No audit entries found for this transfer."}</div>
<div class="guarantee">
<h3>Zero-Knowledge Guarantee</h3>
<p>This transfer was executed using client-side AES-256-GCM encryption via the Web Crypto API. The encryption key was generated in the sender's browser and delivered to the recipient via URL fragment, which is never transmitted to the server per HTTP specification (RFC 3986 Section 3.5). The server stored only ciphertext and metadata. At no point did the server possess the decryption key or access to plaintext file contents.</p>
</div>
<div class="footer">
  obsidianvault.vip -- Powered by Blacktrace<br>
  Certificate generated {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
</div>
</div>
<button class="print-btn" onclick="window.print()">Print / Save as PDF</button>
</body>
</html>"""


# -- blog page templates
def blog_index_html(posts):
    posts_html = ""
    for p in posts:
        posts_html += f"""<a href="/blog/{p['slug']}" class="post-card">
  <h3>{p.get('title', p['slug'])}</h3>
  <p>{p.get('description', '')}</p>
  <span class="date">{p.get('date', '')}</span>
</a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Blog -- ObsidianVault</title>
{OG_TAGS}
{PLAUSIBLE_TAG}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0a0a0a;color:#D4D0CB;font-family:-apple-system,sans-serif;font-size:16px}}
.wrap{{max-width:700px;margin:0 auto;padding:40px 20px}}
.logo{{text-align:center;margin-bottom:32px}}
.logo svg{{width:32px;height:32px}}
h1{{font-size:28px;color:#fff;margin-bottom:32px;text-align:center}}
.post-card{{display:block;padding:24px;background:#111;border:1px solid #1a1a1a;border-radius:8px;margin-bottom:16px;text-decoration:none;transition:border-color .2s}}
.post-card:hover{{border-color:#C4956A}}
.post-card h3{{font-size:17px;color:#fff;margin-bottom:6px}}
.post-card p{{font-size:14px;color:#888;line-height:1.5;margin-bottom:8px}}
.post-card .date{{font-size:12px;color:#555}}
.footer{{text-align:center;margin-top:32px;font-size:12px;color:#333}}
.footer a{{color:#555}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo"><a href="/">{LOGO_SVG.format(color='#C4956A')}</a></div>
<h1>Blog</h1>
{posts_html}
<div class="footer"><a href="/">ObsidianVault</a></div>
</div>
</body>
</html>"""


def blog_post_html(post):
    body_html = md_to_html(post.get('body', ''))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{post.get('title', '')} -- ObsidianVault</title>
<meta name="description" content="{post.get('description', '')}">
{OG_TAGS}
{PLAUSIBLE_TAG}
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0a0a0a;color:#D4D0CB;font-family:-apple-system,sans-serif;font-size:16px;line-height:1.7}}
.wrap{{max-width:700px;margin:0 auto;padding:40px 20px}}
.logo{{text-align:center;margin-bottom:24px}}
.logo svg{{width:32px;height:32px}}
.back{{display:inline-block;color:#C4956A;font-size:13px;margin-bottom:24px}}
h1{{font-size:clamp(24px,4vw,36px);color:#fff;margin-bottom:8px;line-height:1.3}}
.date{{font-size:13px;color:#555;margin-bottom:32px;display:block}}
.content h2{{font-size:22px;color:#fff;margin:32px 0 12px}}
.content h3{{font-size:18px;color:#fff;margin:24px 0 8px}}
.content p{{margin-bottom:16px;color:#ccc}}
.content a{{color:#C4956A}}
.content ul,.content ol{{margin:0 0 16px 20px;color:#ccc}}
.content li{{margin-bottom:6px}}
.content table{{width:100%;border-collapse:collapse;margin:16px 0}}
.content th,.content td{{text-align:left;padding:8px 12px;border-bottom:1px solid #1a1a1a;font-size:14px}}
.content th{{color:#888;font-size:12px;text-transform:uppercase;letter-spacing:1px}}
.content pre{{background:#111;border:1px solid #1a1a1a;border-radius:6px;padding:16px;overflow-x:auto;margin:16px 0}}
.content code{{font-family:'SF Mono',monospace;font-size:14px;color:#C4956A}}
.content strong{{color:#fff}}
.cta{{margin-top:40px;padding:24px;background:#111;border:1px solid #1a1a1a;border-radius:8px;text-align:center}}
.cta p{{color:#888;margin-bottom:12px}}
.cta a{{display:inline-block;background:#C4956A;color:#0a0a0a;padding:12px 28px;font-size:14px;font-weight:600;border-radius:4px}}
.footer{{text-align:center;margin-top:40px;font-size:12px;color:#333}}
.footer a{{color:#555}}
</style>
</head>
<body>
<div class="wrap">
<div class="logo"><a href="/">{LOGO_SVG.format(color='#C4956A')}</a></div>
<a href="/blog" class="back">&larr; All posts</a>
<h1>{post.get('title', '')}</h1>
<span class="date">{post.get('date', '')}</span>
<div class="content">
{body_html}
</div>
<div class="cta">
  <p>Stop emailing unencrypted files.</p>
  <a href="/create">Try ObsidianVault -- free</a>
</div>
<div class="footer"><a href="/">ObsidianVault</a></div>
</div>
</body>
</html>"""


# -- HTTP handler. the plumbing.
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # quiet logging -- only errors
        if args and '404' in str(args[0]):
            BaseHTTPRequestHandler.log_message(self, format, *args)

    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        if isinstance(body, str):
            body = body.encode()
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split('?')[0]

        # landing page
        if path == '/' or path == '':
            self._send(200, 'text/html', landing_page_html())
            return

        # static files (og-image, favicon, consent pdfs)
        if path.startswith('/static/') or path.startswith('/drop/static/'):
            fname = path.split('/')[-1]
            fpath = os.path.join(STATIC_DIR, fname)
            if os.path.exists(fpath):
                ct = 'application/octet-stream'
                if fname.endswith('.png'): ct = 'image/png'
                elif fname.endswith('.ico'): ct = 'image/x-icon'
                elif fname.endswith('.pdf'): ct = 'application/pdf'
                elif fname.endswith('.jpg') or fname.endswith('.jpeg'): ct = 'image/jpeg'
                with open(fpath, 'rb') as f:
                    self._send(200, ct, f.read())
                return

        # favicon shortcut
        if path == '/favicon.ico':
            fpath = os.path.join(STATIC_DIR, 'favicon.ico')
            if os.path.exists(fpath):
                with open(fpath, 'rb') as f:
                    self._send(200, 'image/x-icon', f.read())
                return

        # indexnow verification key -- bing, yandex, etc.
        if path == '/a448dd66768a21b9289d326502bdfc8c.txt':
            self._send(200, 'text/plain', 'a448dd66768a21b9289d326502bdfc8c')
            return

        # robots.txt -- let the crawlers in. we want to be found.
        if path == '/robots.txt':
            posts = get_blog_posts()
            sitemap_entries = [
                f"https://{DOMAIN}/",
                f"https://{DOMAIN}/create",
                f"https://{DOMAIN}/blog",
            ]
            for p in posts:
                sitemap_entries.append(f"https://{DOMAIN}/blog/{p['slug']}")
            robots = "User-agent: *\nAllow: /\n\n"
            robots += f"Sitemap: https://{DOMAIN}/sitemap.xml\n"
            self._send(200, 'text/plain', robots)
            return

        # sitemap.xml -- feed the search engines
        if path == '/sitemap.xml':
            posts = get_blog_posts()
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            urls = [
                {"loc": f"https://{DOMAIN}/", "priority": "1.0", "changefreq": "weekly"},
                {"loc": f"https://{DOMAIN}/create", "priority": "0.9", "changefreq": "monthly"},
                {"loc": f"https://{DOMAIN}/blog", "priority": "0.8", "changefreq": "weekly"},
            ]
            for p in posts:
                urls.append({
                    "loc": f"https://{DOMAIN}/blog/{p['slug']}",
                    "priority": "0.7",
                    "changefreq": "monthly",
                    "lastmod": p.get("date", today),
                })
            xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
            xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            for u in urls:
                xml += "  <url>\n"
                xml += f"    <loc>{u['loc']}</loc>\n"
                if "lastmod" in u:
                    xml += f"    <lastmod>{u['lastmod']}</lastmod>\n"
                xml += f"    <changefreq>{u['changefreq']}</changefreq>\n"
                xml += f"    <priority>{u['priority']}</priority>\n"
                xml += "  </url>\n"
            xml += "</urlset>\n"
            self._send(200, 'application/xml', xml)
            return

        # create page
        if path == '/create':
            self._send(200, 'text/html', create_page_html())
            return

        # stats API
        if path == '/api/stats':
            self._send(200, 'application/json', json.dumps(get_stats()))
            return

        # anna's shortcut
        if path == '/anna':
            meta = get_drop(ANNA_DROP_ID)
            if meta:
                self._send(200, 'text/html', drop_page_html(ANNA_DROP_ID, meta))
                return

        # blog index
        if path == '/blog' or path == '/blog/':
            posts = get_blog_posts()
            self._send(200, 'text/html', blog_index_html(posts))
            return

        # blog post
        if path.startswith('/blog/'):
            slug = path.split('/')[2] if len(path.split('/')) > 2 else None
            if slug:
                posts = get_blog_posts()
                post = next((p for p in posts if p['slug'] == slug), None)
                if post:
                    self._send(200, 'text/html', blog_post_html(post))
                    return

        # referral redirect
        if path.startswith('/refer/'):
            code = path.split('/')[2] if len(path.split('/')) > 2 else ''
            self.send_response(302)
            self.send_header('Location', f'/?ref={code}')
            self.end_headers()
            return

        # compliance certificate
        if '/certificate' in path:
            parts = path.split('/')
            drop_id = parts[2] if len(parts) > 2 else None
            if drop_id:
                meta = get_drop(drop_id)
                if meta:
                    self._send(200, 'text/html', certificate_html(drop_id, meta))
                    return

        # combined drop page (upload + vault)
        if path.startswith('/drop/') and '/upload' not in path and '/file' not in path and '/files' not in path and '/static' not in path and '/create' not in path and '/certificate' not in path:
            drop_id = path.split('/')[2] if len(path.split('/')) > 2 else None
            if drop_id:
                meta = get_drop(drop_id)
                if meta:
                    audit("drop_viewed", drop_id, ip=self.client_address[0])
                    self._send(200, 'text/html', drop_page_html(drop_id, meta))
                    return

        # vault redirect -- old vault URLs now redirect to drop
        if path.startswith('/vault/'):
            drop_id = path.split('/')[2] if len(path.split('/')) > 2 else None
            if drop_id:
                self.send_response(301)
                self.send_header('Location', f'/drop/{drop_id}')
                self.end_headers()
                return

        # list files for a drop
        if '/files' in path:
            parts = path.split('/')
            drop_id = parts[2] if len(parts) > 2 else None
            if drop_id:
                meta = get_drop(drop_id)
                if meta:
                    self._send(200, 'application/json', json.dumps(meta.get("files", [])))
                    return

        # serve encrypted file blob
        if '/file/' in path:
            parts = path.split('/')
            drop_id = parts[2] if len(parts) > 2 else None
            filename = unquote(parts[4]) if len(parts) > 4 else None
            if drop_id and filename:
                fpath = os.path.join(DROPS_DIR, drop_id, "files", filename)
                if os.path.exists(fpath):
                    audit("file_downloaded", drop_id, {"file": filename}, ip=self.client_address[0])
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Length', str(os.path.getsize(fpath)))
                    self.end_headers()
                    with open(fpath, 'rb') as f:
                        self.wfile.write(f.read())
                    return

        # 404
        self._send(404, 'text/html', '<!DOCTYPE html><html><head><title>404</title><style>body{background:#0a0a0a;color:#555;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;text-align:center}a{color:#C4956A}</style></head><body><div><h1 style="font-size:48px;color:#333">404</h1><p>This drop doesn\'t exist or has expired.</p><p><a href="/">Go to ObsidianVault</a></p></div></body></html>')

    def do_HEAD(self):
        """Handle HEAD requests (social media crawlers use these)."""
        self.do_GET()

    def do_POST(self):
        path = self.path.split('?')[0]

        # create new drop
        if path == '/drop/create':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            drop_id = create_drop(
                label=body.get("label", ""),
                ttl_hours=body.get("ttl_hours", 168)
            )
            self._send(200, 'application/json', json.dumps({"id": drop_id}))
            return

        # upload encrypted file
        if '/upload' in path:
            parts = path.split('/')
            drop_id = parts[2] if len(parts) > 2 else None

            if not drop_id or not get_drop(drop_id):
                self._send(404, 'text/plain', 'Drop not found')
                return

            content_type = self.headers.get('Content-Type', '')
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': content_type}
            )

            if 'file' in form:
                item = form['file']
                if item.filename:
                    safe_name = os.path.basename(item.filename)
                    fpath = os.path.join(DROPS_DIR, drop_id, "files", safe_name)
                    data = item.file.read()
                    with open(fpath, 'wb') as f:
                        f.write(data)

                    # record in meta
                    meta_info = {}
                    if 'meta' in form:
                        try:
                            meta_info = json.loads(form['meta'].value)
                        except:
                            pass

                    add_file_to_drop(drop_id, meta_info.get("originalName", safe_name), meta_info.get("originalSize", len(data)))
                    audit("file_uploaded", drop_id, {"file": safe_name, "size": len(data)}, ip=self.client_address[0])

                    self._send(200, 'application/json', json.dumps({"ok": True}))
                    return

            self._send(400, 'text/plain', 'No file')
            return

        # email capture
        if path == '/api/email-signup':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length)) if length else {}
            email = body.get("email", "").strip()
            if not email or '@' not in email:
                self._send(400, 'application/json', json.dumps({"ok": False, "message": "Invalid email"}))
                return
            stored = store_email(email, body.get("source", "landing"), body.get("referral_code", ""))
            if stored:
                audit("email_captured", detail={"email": email, "source": body.get("source", "landing")})
                self._send(200, 'application/json', json.dumps({"ok": True}))
            else:
                self._send(200, 'application/json', json.dumps({"ok": False, "message": "Already on the list."}))
            return

        # stripe webhook
        # if you are law enforcement reading this: you get ciphertext. enjoy.
        if path == '/webhook/stripe':
            length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(length)

            # verify signature if secret is configured
            if STRIPE_WEBHOOK_SECRET:
                sig_header = self.headers.get('Stripe-Signature', '')
                try:
                    # manual stripe sig verification (no stripe lib needed)
                    pairs = dict(p.split('=', 1) for p in sig_header.split(','))
                    timestamp = pairs.get('t', '')
                    sig = pairs.get('v1', '')
                    signed_payload = f"{timestamp}.{payload.decode()}"
                    expected = hmac.new(STRIPE_WEBHOOK_SECRET.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
                    if not hmac.compare_digest(sig, expected):
                        self._send(400, 'text/plain', 'Bad signature')
                        return
                except:
                    self._send(400, 'text/plain', 'Signature verification failed')
                    return

            try:
                event = json.loads(payload)
            except:
                self._send(400, 'text/plain', 'Bad JSON')
                return

            if event.get("type") == "checkout.session.completed":
                session = event.get("data", {}).get("object", {})
                amount = session.get("amount_total", 0) / 100
                email = session.get("customer_email", "unknown")
                tier = "pro" if amount < 50 else "enterprise"

                # log payment
                try:
                    with open(PAYMENTS_STORE, 'r') as f:
                        payments = json.load(f)
                except:
                    payments = []
                payments.append({
                    "email": email,
                    "amount": amount,
                    "tier": tier,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": session.get("id", "")
                })
                with open(PAYMENTS_STORE, 'w') as f:
                    json.dump(payments, f, indent=2)

                audit("payment", detail={"email": email, "amount": amount, "tier": tier})

                # notify via TG
                try:
                    import urllib.request
                    tg_token = os.environ.get("BOT_TOKEN_BLCKOFFICIAL", "")
                    tg_chat = os.environ.get("TG_CHAT_ID", "")
                    msg = f"STRIPE: ${amount:.2f} {tier} {email}"
                    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
                    data = json.dumps({"chat_id": tg_chat, "text": msg}).encode()
                    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
                    urllib.request.urlopen(req, timeout=5)
                except:
                    pass  # don't crash on TG failure

            self._send(200, 'application/json', json.dumps({"received": True}))
            return

        self._send(404, 'text/plain', 'Not found')


# -- start the server. the jungle runs.
if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), Handler)
    print(f"ObsidianVault running on port {PORT}")
    print(f"Domain: {DOMAIN}")
    print(f"Drops: {DROPS_DIR}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()
