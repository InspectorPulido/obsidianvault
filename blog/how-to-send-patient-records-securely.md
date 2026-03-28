---
title: "How to Send Patient Records Securely (Without Making Your Staff Hate You)"
slug: how-to-send-patient-records-securely
date: 2026-03-28
description: "A practical guide to secure patient record transfer in Australia. Compares encrypted email, portals, USB drives, and zero-knowledge transfer."
---

# How to Send Patient Records Securely (Without Making Your Staff Hate You)

Every practice manager has had this conversation. The one where IT says "we need to encrypt patient records in transit" and the reception staff say "we barely have time to answer the phone." Both sides are right. And that tension -- between what security demands and what humans will actually do -- is where most compliance efforts go to die.

Let me walk through the real options, honestly, including what breaks in practice.

## Option 1: Encrypted Email

**The theory:** Use S/MIME certificates or PGP keys to encrypt email end-to-end. Only the intended recipient can decrypt the message.

**The reality:** S/MIME requires both sender and recipient to have digital certificates. Someone has to procure, install, renew, and troubleshoot those certificates. PGP is even worse from a usability perspective -- it was designed by cryptographers for cryptographers, and it shows.

Microsoft 365 does offer message encryption that's somewhat easier to deploy. The sender can mark a message as encrypted, and the recipient receives a link to view the message through a web portal. It works, technically.

**What actually happens:** Staff forget to click the encrypt button. Recipients can't figure out the portal and call the practice asking for the records "just as an attachment." The practice manager, drowning in admin, tells reception to "just send it normally this one time." That one time becomes every time.

**Verdict:** Technically sound. Practically fragile. The system's security depends on the most rushed, least technical person in the office remembering an extra step every single time.

## Option 2: Secure Patient Portals

**The theory:** Upload records to a secure portal. Patient logs in and downloads them. Audit trail. Access controls. Everything encrypted.

**The reality:** My Health Record exists. Practice management systems like Best Practice and Medical Director have their own secure messaging features. Hospital systems run their own portals. In theory, this is solved.

**What actually happens:** Patients don't log in. As of 2023, over 23 million Australians had a My Health Record (most created by default under the opt-out model), but active patient-initiated usage has remained low relative to the registered base. The portal exists. The records are there. But getting a 74-year-old to set up an account, remember a password, navigate the interface, and download a PDF is a support burden that clinics can't absorb.

Specialist-to-specialist transfers are marginally better because both sides have IT support. But even there, the number of different portal systems creates interoperability problems. Specialist A uses one system, Specialist B uses another, the GP uses a third. Nobody has accounts on everyone else's system.

**Verdict:** Good for structured, ongoing relationships. Poor for ad hoc transfers, referrals, or anything involving a patient who doesn't live online.

## Option 3: USB Drives and Physical Media

**The theory:** Put the files on an encrypted USB drive. Hand it to the patient or courier it.

**The reality:** This works from a security perspective if the drive is properly encrypted. BitLocker, VeraCrypt, or hardware-encrypted drives all do the job.

**What actually happens:** Staff don't encrypt the drive. Or they encrypt it and write the password on a sticky note attached to the drive. Or the drive gets lost in transit. Or the patient can't figure out how to access an encrypted volume because they're running a Chromebook.

Also, this is 2026. Physical media transfer for digital files is a workflow from a different era. It requires someone to be physically present, which defeats the purpose of digital records.

**Verdict:** Appropriate for specific high-security scenarios. Absurd as a general-purpose solution.

## Option 4: Consumer Cloud Storage (Dropbox, Google Drive, OneDrive)

**The theory:** Upload the file to a shared folder or generate a share link. Recipient clicks and downloads.

**The reality:** These platforms encrypt data in transit (TLS) and at rest (AES-256 typically). They have access controls. They're familiar to most people. They're also the most common "shadow IT" solution -- staff already using them even if the practice hasn't sanctioned it.

**The problem:** None of these platforms offer zero-knowledge encryption in their standard tiers. The provider holds the encryption keys. This means:

- The provider can technically access the files.
- A breach of the provider's systems exposes the content.
- Government or legal requests to the provider can compel access to the files.
- From a Privacy Act perspective, you've handed control of sensitive health information to a third party whose data governance is outside your control.

For non-sensitive files, this is fine. For patient health records -- classified as sensitive information under the Privacy Act -- the risk profile is harder to justify.

**Verdict:** Convenient. Familiar. Not designed for health data compliance. The ease of use is real, but it comes with a governance gap that a regulator would notice.

## Option 5: Zero-Knowledge Encrypted Transfer

**The theory:** Files are encrypted in the sender's browser before upload. The encryption key is embedded in the share link (in the URL fragment, which is never sent to the server). The server only ever sees encrypted data. The recipient clicks the link and the file decrypts in their browser.

**The reality:** This is the model used by tools like ObsidianVault. The design eliminates the "provider holds the keys" problem entirely. Even if the server is breached, the attacker gets encrypted blobs with no way to decrypt them.

**What actually happens:** The sender uploads a file and gets a link. The recipient clicks the link and downloads the file. That's it. No accounts. No certificates. No portals. No passwords to communicate separately (the key is in the link itself).

**The tradeoffs (being honest):**

- **Server-served JavaScript:** The encryption runs in the browser, and the JavaScript is served by the same server that stores the encrypted files. In theory, a compromised server could serve malicious JavaScript that exfiltrates the key. This is a real limitation of any browser-based E2E encryption system. The mitigation is subresource integrity checks, reproducible builds, and open-source code that can be audited.
- **No native app:** Browser-based means no offline access, no integration with practice management software, and performance limits on very large files.
- **Link security:** The share link contains the decryption key. If the link is intercepted (e.g., sent over an insecure channel), the file is compromised. The link itself needs to be shared through a reasonably secure channel.

Despite these tradeoffs, the usability profile is unmatched. The cognitive load on clinical staff is close to zero -- upload, copy link, send link. That simplicity is not a marketing advantage. It's a compliance advantage. A tool that staff actually use is infinitely more secure than a tool that staff circumvent.

## The Real Problem Is Adoption, Not Technology

The technology to send patient records securely has existed for years. The reason most practices still email unencrypted PDFs isn't ignorance -- it's that every "secure" alternative adds friction, and healthcare workers are already at capacity.

When a new tool requires accounts, passwords, multi-step processes, training, and IT support, clinical staff will solve the problem by going back to email.

The only way to improve security in practice is to make the secure option **easier** than the insecure one. Not "about the same" -- easier. "About the same" loses to the incumbent every time.

The right question for evaluating any tool isn't "is it technically encrypted?" It's "will my staff actually use it on a Tuesday afternoon when they're running behind and the specialist needs the records now?"

If the answer isn't a confident yes, you've just added a line item to your compliance documentation that doesn't reflect reality.

---

*ObsidianVault was built for exactly this problem -- end-to-end encrypted file transfer that's simpler than email attachments. No accounts. No training. No excuses. [See how it works at obsidianvault.vip](https://obsidianvault.vip)*
