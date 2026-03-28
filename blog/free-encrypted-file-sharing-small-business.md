---
title: "Free Encrypted File Sharing for Small Business in Australia"
slug: free-encrypted-file-sharing-small-business
date: 2026-03-28
description: "Small businesses need encrypted file transfer but can't justify enterprise pricing. Here are the genuinely free options, what they actually encrypt, and where the catches are."
---

# Free Encrypted File Sharing for Small Business in Australia

You run a small business. You need to send sensitive files to clients, suppliers, or your accountant. You know you should be encrypting them. You also know that the "enterprise-grade security solutions" you keep seeing advertised start at $15/user/month and require a sales call with someone named Chad.

Here's the good news: genuinely secure, end-to-end encrypted file sharing is available for free. Here's the less good news: most of what claims to be "encrypted file sharing" isn't what you think it is, and the free tier of most platforms has catches that matter.

Let me save you some time.

## Why You Need This (The 60-Second Version)

If your business has annual turnover exceeding $3 million, you're covered by the Privacy Act 1988 (Cth) and must comply with the Australian Privacy Principles (APPs). Even if you're under $3 million, you may be covered if you're a health service provider, trade in personal information, or are related to an entity that's covered.

APP 11 requires you to take "reasonable steps" to protect personal information. Following the 2024 amendments, this explicitly includes "technical and organisational measures," with encryption identified as a standard technical measure.

The penalty for a serious interference with privacy: up to $50 million for a body corporate, or three times the benefit, or 30% of turnover. The mid-tier penalty for non-serious interference: up to $3.3 million per contravention.

For a small business, even the lower-tier penalties are existential. The cost of encrypted file transfer: zero dollars. The maths is straightforward.

## What "Encrypted" Actually Means

This is where most comparisons go wrong. There are three levels, and only one of them protects you from everything including the service provider itself:

**Encryption in transit (TLS).** Your file is encrypted while travelling between your device and the server. This is the baseline. Every reputable service does this. It's like a sealed envelope -- it protects against interception during delivery, but the postal service can still open it.

**Encryption at rest.** Your file is encrypted while stored on the server. The service provider holds the encryption keys. If they're breached, hacked, or served with a legal request, your files can be decrypted. It's a locked filing cabinet where the building manager has a master key.

**End-to-end encryption (E2E) / zero-knowledge.** Your file is encrypted on your device before it leaves. The service provider stores only encrypted data and never has the decryption key. A breach of the provider doesn't expose your content. A legal request to the provider yields only encrypted blobs. This is the only model where you're genuinely protected.

When a service says "encrypted" without qualification, they almost always mean the first two. The third is what you actually need.

## The Free Options, Honestly Assessed

### Google Drive (15 GB free)

**Encryption level:** In transit (TLS) + at rest (AES-256). Google holds the keys.

**The catch:** Google can access your files. Google's terms of service grant them certain rights to process your content. A breach of Google exposes your content. A government request to Google can yield your files. For a small business sending invoices and marketing materials, this is fine. For sensitive client data, financial records, or anything covered by the Privacy Act's "sensitive information" category, it's not end-to-end encrypted and Google is an additional attack surface.

**Verdict:** Good for general business files. Insufficient for sensitive data under APP 11.

### Dropbox Basic (2 GB free)

**Encryption level:** In transit (TLS) + at rest (AES-256). Dropbox holds the keys.

**The catch:** Same fundamental issue as Google Drive. Dropbox has SOC 2 compliance and strong security practices, but they hold the encryption keys. Their 2012 breach (disclosed 2016, 68 million credentials) is historical, and their security has improved substantially. But the architecture means a sufficiently serious breach would expose file contents.

**Verdict:** Good collaboration tool. Not zero-knowledge. 2 GB is too small for most business use.

### OneDrive (5 GB free)

**Encryption level:** In transit (TLS) + at rest (BitLocker + per-file encryption). Microsoft holds the keys.

**The catch:** Same pattern. Microsoft's infrastructure is robust, their compliance certifications are extensive, and Personal Vault adds an extra authentication layer. But it's not end-to-end encrypted. Microsoft can access file contents.

**Verdict:** Best free option if you're already in the Microsoft ecosystem. Not zero-knowledge.

### ProtonDrive (1 GB free / 5 GB with free Proton account)

**Encryption level:** End-to-end encrypted. Zero-knowledge. Proton cannot access your files.

**The catch:** This is genuinely E2E encrypted, which is the right architecture. The limitations are practical: 1-5 GB free storage is tight for business use. Sharing files with people outside Proton's ecosystem has friction -- they need to access files through a web interface. Swiss jurisdiction is a privacy advantage but means your data is outside Australia, which may matter for some regulatory contexts.

**Verdict:** The strongest privacy option among mainstream cloud storage providers. Limited free tier. Some friction for external sharing.

### Signal (free, unlimited)

**Encryption level:** End-to-end encrypted. Signal cannot access file contents.

**The catch:** Signal is a messaging app, not a file transfer service. File size limit is 100 MB. No web interface -- both parties need Signal installed. No file management, no expiry controls, no audit trail. Files persist in both users' chat histories and device backups unless manually deleted.

**Verdict:** Excellent for ad hoc secure messaging. Not designed for business file transfer workflows.

### ObsidianVault (free tier available)

**Encryption level:** End-to-end encrypted (AES-256-GCM). Zero-knowledge. Encryption key in URL fragment -- never sent to server.

**The catch:** I built this, so take my assessment with appropriate scepticism. It's a transfer tool, not a storage solution. Files expire by design. No native app (browser-based). Server-served JavaScript means you're trusting the server to serve the correct encryption code at page load -- the standard limitation of all browser-based E2E systems. No desktop sync, no collaboration features, no file management.

**Verdict:** Purpose-built for the specific use case of "I need to send this sensitive file to someone securely, right now, and they shouldn't need to create an account." If that's your workflow, it's the simplest zero-knowledge option available. If you need ongoing file storage and collaboration, it's the wrong tool.

## The Honest Comparison

| Feature | Google Drive | Dropbox | OneDrive | ProtonDrive | ObsidianVault |
|---|---|---|---|---|---|
| Free storage | 15 GB | 2 GB | 5 GB | 1-5 GB | Transfer only |
| End-to-end encrypted | No | No | No | Yes | Yes |
| Zero-knowledge | No | No | No | Yes | Yes |
| Recipient needs account | No (links) | No (links) | No (links) | Partially | No |
| File size limit (free) | 5 TB upload | 2 GB storage | 250 GB upload | 1 GB storage | Varies |
| Collaboration features | Extensive | Extensive | Extensive | Limited | None |
| Australian data residency | No | No | No | No (Switzerland) | Yes |

## What Should Small Businesses Actually Do?

The pragmatic approach is to use different tools for different sensitivity levels:

**General business files** (marketing materials, public documents, non-sensitive correspondence): Use whatever's convenient. Google Drive, Dropbox, OneDrive -- all fine. The encryption they provide is sufficient for data that wouldn't cause harm if exposed.

**Sensitive files** (client personal information, financial records, health data, anything covered by Privacy Act sensitive information categories, anything you'd be embarrassed to see on the front page of the paper): Use a tool with genuine end-to-end encryption and zero-knowledge architecture. ProtonDrive for storage, ObsidianVault for transfers.

**The one thing you should stop doing immediately:** Emailing sensitive files as unencrypted PDF attachments. This is the single highest-risk practice in most small businesses, and it's the easiest to fix. Replace "attach the PDF and hit send" with "upload to an encrypted transfer service and send the link." Same number of steps. Fundamentally different security posture.

The Privacy Act doesn't require perfection. It requires reasonable steps. Using free, zero-knowledge encrypted file transfer for sensitive data is a reasonable step that costs nothing and takes about 30 seconds longer than an email attachment.

You don't need Chad. You don't need a sales call. You need to stop emailing tax returns as PDF attachments.

---

*ObsidianVault is free, zero-knowledge encrypted file transfer. No accounts. No sales calls. No Chad. Upload a file, share a link, the server can't read your data. [Try it at obsidianvault.vip](https://obsidianvault.vip)*
