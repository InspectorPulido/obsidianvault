# r/privacy Post

**Subreddit:** r/privacy
**Title:** I built a free, zero-knowledge encrypted file transfer after my GP's office emailed my medical records unencrypted -- 5 times
**Flair:** Software

---

My GP's receptionist needed to send me my medical records. The file was too big. Her solution: split it into 5 unencrypted PDF attachments across 5 emails. Shared practice inbox. Plain SMTP.

Each email was a breach of the Australian Privacy Act. Five breaches in one afternoon.

I'm a developer on a disability pension. I couldn't afford any of the existing encrypted transfer services. The free ones all want you to create an account, which means they know who's sending what to whom. That metadata is often more sensitive than the files themselves.

So I built ObsidianVault. It's free. Here's what it does and doesn't do:

**Privacy model:**

- AES-256-GCM encryption happens in your browser before anything touches the server
- The decryption key lives in the URL fragment (the part after #). Browsers don't send fragments to servers. The key never leaves the client side.
- No accounts. No sign-up. No email. No phone number.
- No cookies. No analytics. No tracking pixels. No fingerprinting.
- No third-party scripts. No CDN dependencies. Everything served from one origin.
- Server stores ciphertext only. Compromise the server and you get encrypted noise.

**What it can't protect against:**

- If someone intercepts the full link (including the fragment), they can decrypt the files. Send links through a secure channel.
- Server-served JavaScript is a trust point. I could theoretically serve malicious JS that exfiltrates keys before encryption. This is the fundamental limitation of browser-based E2E encryption. The code is open source so you can verify, but realistically most people won't audit it.
- I can see ciphertext sizes and timestamps. If you need to hide the fact that a transfer happened at all, this isn't the tool.

**What it replaces:**

- Emailing sensitive documents as attachments (the thing that 90% of medical/legal/financial offices still do)
- WeTransfer, Google Drive links, Dropbox links -- all of which can read your files
- Enterprise DLP solutions that cost more than my annual income

**Details:**

- Single Python file, stdlib only
- MIT licensed
- Self-hostable: `python3 app.py`
- Configurable TTL (files auto-delete)
- Hash-chained audit log for compliance

Live: https://obsidianvault.vip
Source: https://github.com/8889-coder/obsidianvault

No accounts. No tracking. No cookies. Free.

I built this because I was angry. I stayed because it's useful.
