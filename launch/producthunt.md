# Product Hunt Listing

## Product Name
ObsidianVault

## Tagline
Zero-knowledge encrypted file transfer. Server never sees your files.

## Description

ObsidianVault encrypts files in your browser before they touch the server. AES-256-GCM via the Web Crypto API. The decryption key lives in the URL fragment -- the part browsers never send to servers. The server stores ciphertext only. It cannot read your files.

No accounts. No sign-up. No cookies. No tracking.

Drop a file. Get a link. Send the link. Recipient clicks, browser decrypts, file downloads. Done.

**Built because:** A GP receptionist emailed unencrypted medical records across 5 separate emails because the file was "too big." Each one was a Privacy Act breach. The tools that exist cost thousands or require enterprise IT. This one is a single Python file.

## Features

- **Zero-knowledge encryption** -- AES-256-GCM, client-side only. Server stores ciphertext.
- **No accounts** -- No sign-up, no email, no phone number. Ever.
- **No tracking** -- No cookies, no analytics, no fingerprinting, no third-party scripts.
- **Self-hostable** -- One Python file, stdlib only. `git clone && python3 app.py`.
- **Auto-expiry** -- Configurable TTL. Files delete themselves.
- **Audit log** -- Hash-chained, append-only. Every action logged with cryptographic link to previous entry.
- **Open source** -- MIT licensed. Read every line.
- **Works now** -- No beta, no waitlist, no "request access."

## Pricing

**Free** -- Unlimited drops, up to 100MB per file. No account needed.

**Pro ($9/month)** -- 1GB files, custom expiry, branded drop pages, priority support.

## Links

- Website: https://obsidianvault.vip
- GitHub: https://github.com/8889-coder/obsidianvault

## Topics
Privacy, Security, Developer Tools, Open Source, Healthcare

## Maker Comment

I built this on my birthday in a motel room. I was on the disability support pension with 5 cents in my bank account. My GP's receptionist had just emailed my medical records -- unencrypted, split across 5 emails -- because "the file was too big."

I'm a developer. I knew exactly how bad that was. I also knew she wasn't trying to be negligent. She was using the only tools her practice gave her: email and hope.

The enterprise encrypted transfer solutions cost more than my annual income. The consumer ones require accounts, which means someone knows who's sending what to whom. I needed something that was free, required zero technical knowledge, and that I could verify end-to-end because I wrote it.

So I built it. One Python file. AES-256-GCM in the browser. Server never sees plaintext. No accounts, no tracking, no BS.

Healthcare is the most-breached sector in Australia. Not because encryption is hard. Because nobody made it easy enough for a receptionist to use without training.

I did.

It's free. It's open source. Go encrypt something.
