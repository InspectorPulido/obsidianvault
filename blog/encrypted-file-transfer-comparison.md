---
title: "Encrypted File Transfer Tools Compared: WeTransfer vs Dropbox vs OneDrive vs ObsidianVault"
slug: encrypted-file-transfer-comparison
date: 2026-03-28
description: "Honest comparison of encrypted file transfer tools for sensitive data. WeTransfer, Dropbox, OneDrive, ProtonDrive, and ObsidianVault assessed on real security."
---

# Encrypted File Transfer Tools Compared: WeTransfer vs Dropbox vs OneDrive vs ObsidianVault

"We use Dropbox, so we're encrypted" is something I hear constantly. It's not wrong, exactly. It's just incomplete in a way that matters.

Every major file transfer platform uses some form of encryption. The question isn't whether your files are encrypted -- it's who holds the keys, what's protected at which stage, and what happens when (not if) something goes wrong.

Here's an honest comparison. I'll include the tool I built (ObsidianVault) because I believe it solves a real problem, but I'll also be straightforward about its limitations.

## The Encryption Spectrum

Before comparing tools, you need to understand three distinct levels of encryption:

**Encryption in transit (TLS):** Your data is encrypted while moving between your device and the server. This prevents interception during transmission. Nearly every web service uses this. It's the baseline, not a feature.

**Encryption at rest:** Your data is encrypted while stored on the server's disk. This protects against physical theft of server hardware or certain types of server breach. The service provider typically holds the encryption keys.

**End-to-end encryption (E2E):** Your data is encrypted on your device before it leaves, and only the intended recipient can decrypt it. The service provider never has access to the unencrypted content or the decryption keys. This is the gold standard.

The gap between "encrypted at rest" and "end-to-end encrypted" is enormous. With encryption at rest, the provider can access your files, can be compelled to hand them over by legal process, and a breach of their systems exposes your content. With E2E, none of those are true.

## WeTransfer

**What it offers:**
- TLS encryption in transit
- Files stored on servers (AWS infrastructure)
- Files expire after 7 days (free) or customisable (paid)
- No recipient account required

**What it doesn't offer:**
- End-to-end encryption
- Zero-knowledge architecture
- Granular access controls

**The reality:** WeTransfer is designed for convenience, not security. It excels at sending large files quickly. But WeTransfer has access to every file on its platform -- they hold the encryption keys. A server breach, a rogue employee, or a legal request would expose file contents. WeTransfer Pro adds password protection but doesn't change the fundamental architecture.

**Best for:** Large creative files, non-sensitive transfers.

## Dropbox

**What it offers:**
- TLS encryption in transit
- AES-256 encryption at rest
- Granular sharing permissions
- Version history and audit logs
- Extensive third-party integrations

**What it doesn't offer:**
- End-to-end encryption (standard plans)
- Zero-knowledge architecture

**The reality:** Dropbox is well-engineered with strong security practices and SOC 2 compliance. But Dropbox holds the encryption keys -- they can access file contents and will comply with valid legal process. The 2012 breach (68 million credentials, disclosed in 2016) is worth noting, though their security has improved substantially since. Dropbox Advanced offers customer-managed keys, but it's priced for enterprise.

**Best for:** Team collaboration, file syncing, document management.

## OneDrive (Microsoft 365)

**What it offers:**
- TLS encryption in transit
- BitLocker encryption at rest (at the disk level) plus per-file encryption
- Deep integration with Microsoft 365 ecosystem
- Compliance tools (DLP, retention policies) on business plans
- Personal Vault with additional verification

**What it doesn't offer:**
- End-to-end encryption for standard files
- Zero-knowledge architecture

**The reality:** OneDrive benefits from Microsoft's security infrastructure and compliance certifications. The compliance tools on business plans (E3/E5) -- data loss prevention, retention labels, audit logging -- are genuinely useful for regulated industries. Personal Vault adds an extra identity verification layer.

But Microsoft holds the encryption keys and will respond to legal process. For Australian organisations, you've delegated custody of sensitive information to a US-based entity subject to different legal frameworks. Customer Key (E5 add-on) lets organisations manage their own keys, but it's enterprise-priced.

**Best for:** Organisations already in the Microsoft ecosystem.

## ProtonDrive

**What it offers:**
- End-to-end encryption (genuinely zero-knowledge)
- Swiss jurisdiction and privacy law
- Open-source clients (audited)
- Strong privacy credentials

**What it doesn't offer:**
- Recipient access without a Proton account (for most sharing features)
- Deep enterprise integration
- Extensive third-party app ecosystem

**The reality:** ProtonDrive is the strongest option from a pure privacy perspective among established cloud platforms. Genuinely zero-knowledge, open-source, credible track record. The limitation is practical: sharing files with someone outside the Proton ecosystem creates friction. Password-protected links help, but the workflow for ad hoc external transfers is less seamless than mainstream platforms.

**Best for:** Privacy-conscious users. Excellent when both parties are in the Proton ecosystem.

## ObsidianVault

**What it offers:**
- End-to-end encryption (zero-knowledge)
- No account required for recipients
- Encryption key embedded in the URL fragment (never sent to the server)
- Files encrypted in the browser before upload
- Configurable expiry and access limits

**What it doesn't offer:**
- A native desktop or mobile app
- Integration with practice management systems
- Long-term file storage (it's a transfer tool, not a drive)
- Independence from server-served JavaScript (see below)

**The reality, honestly:** ObsidianVault is designed for one thing: transferring sensitive files securely with minimal friction. Upload, get a link, share it. Files are encrypted client-side using AES-256-GCM; the encryption key lives in the URL fragment (which browsers never send to the server); the server only stores encrypted blobs.

**The tradeoffs:**

**Server-served JavaScript.** The encryption code is served by the same server that stores files. A compromised server could theoretically serve malicious JS that exfiltrates keys. This is a known limitation of all browser-based E2E systems. Mitigations exist (subresource integrity, open-source audits) but don't fully eliminate the risk.

**No native app.** A native app would solve the JS trust problem. ObsidianVault doesn't have one yet.

**Link security.** The share link contains the decryption key. Share it over an insecure channel and you've reduced your security to that channel's level.

**Not a storage solution.** Files expire by design. It doesn't replace Dropbox or OneDrive for file management.

**Best for:** Ad hoc transfers of sensitive files where the recipient shouldn't need an account. Healthcare referrals, legal documents, financial records, anything where the priority is security and simplicity for the recipient.

## The Comparison Table

| Feature | WeTransfer | Dropbox | OneDrive | ProtonDrive | ObsidianVault |
|---|---|---|---|---|---|
| Encryption in transit | Yes (TLS) | Yes (TLS) | Yes (TLS) | Yes (TLS) | Yes (TLS) |
| Encryption at rest | Yes | Yes (AES-256) | Yes (BitLocker + per-file) | Yes (E2E) | Yes (E2E, AES-256-GCM) |
| End-to-end encryption | No | No | No | Yes | Yes |
| Zero-knowledge | No | No | No | Yes | Yes |
| Recipient needs account | No | No (for links) | No (for links) | Partially | No |
| Provider can access files | Yes | Yes | Yes | No | No |
| Native apps | Yes | Yes | Yes | Yes | No |
| File size limit (free) | 2GB | 2GB storage | 5GB storage | 1GB storage | Varies |
| Jurisdiction | Netherlands | US | US | Switzerland | AU |

## Choosing the Right Tool

There is no single correct answer. The right tool depends on what you're sending, who you're sending it to, and what regulatory obligations apply.

If you're transferring files that would cause harm if exposed -- patient records, legal documents, financial data, anything classified as sensitive under the Privacy Act -- you should be using a tool with genuine end-to-end encryption and zero-knowledge architecture.

If you're sharing marketing materials or public documents, use whatever's convenient.

The mistake is using the convenient tool for both categories.

---

*ObsidianVault is purpose-built for sensitive file transfer. End-to-end encrypted, zero-knowledge, no accounts required. [Try it at obsidianvault.vip](https://obsidianvault.vip)*
