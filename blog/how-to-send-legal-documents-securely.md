---
title: "How to Send Legal Documents Securely in Australia"
slug: how-to-send-legal-documents-securely
date: 2026-03-28
description: "Australian solicitors have strict confidentiality obligations under the ASCR. Emailing unencrypted client documents is a professional conduct risk. Here's what the rules actually require."
---

# How to Send Legal Documents Securely in Australia

Every law firm in Australia emails client documents. Affidavits, settlement deeds, financial disclosures, medical reports, immigration files. Most of those emails are unencrypted. Most solicitors know this is a problem. Almost none of them have fixed it.

The reason is always the same: the secure alternatives are too annoying. So the profession collectively pretends that standard email is fine and hopes nothing goes wrong. This is a terrible strategy, and the regulatory framework is increasingly designed to punish it.

## The Confidentiality Obligation

Rule 9.1 of the Australian Solicitors' Conduct Rules (ASCR) is unambiguous:

> A solicitor must not disclose any information which is confidential to a client and acquired by the solicitor during the client's engagement to any person who is not [within the practice or otherwise authorised].

This isn't aspirational. It's a professional conduct obligation enforceable by state and territory legal services regulators. Breach it and you're looking at a complaint to the Legal Services Commissioner, a potential finding of unsatisfactory professional conduct or professional misconduct, and in serious cases, suspension or cancellation of your practising certificate.

Rule 9 doesn't say "try not to disclose." It says "must not disclose." The obligation extends to taking reasonable steps to prevent inadvertent disclosure -- which is where email becomes a problem.

## Why Standard Email Fails the Test

When you attach a settlement deed to a Gmail or Outlook email and hit send, here's what actually happens:

1. The email travels from your mail server to the recipient's mail server. If both support TLS (most do in 2026), it's encrypted in transit. Good.
2. The email sits on your mail server, unencrypted. It sits on their mail server, unencrypted. It sits in both your sent folder and their inbox, unencrypted, indefinitely.
3. Anyone who compromises either mailbox -- phishing, credential stuffing, a disgruntled employee, a misconfigured server -- gets the document in plain text.
4. You've also just created a permanent copy you can't delete. If your client later asks you to destroy all copies of a document, good luck reaching into opposing counsel's Exchange server.

The legal sector reported 5% of all notifiable data breaches to the OAIC in the July-December 2024 reporting period. Email remains one of the top vectors. These aren't theoretical risks.

## The Privacy Act Layer

Beyond professional conduct rules, law firms are also APP entities under the Privacy Act 1988 (Cth) if they have annual turnover exceeding $3 million -- which covers most firms beyond sole practitioners.

Australian Privacy Principle 11 (APP 11) requires entities to take reasonable steps to protect personal information from misuse, interference, loss, and unauthorised access, modification, or disclosure.

Following the Privacy and Other Legislation Amendment Act 2024, APP 11 now explicitly references "technical and organisational measures." Encryption is called out as an example of a technical measure. The OAIC's guidance has moved from treating encryption as nice-to-have to treating it as a baseline expectation for sensitive information.

The penalty regime backs this up. For a body corporate, the maximum civil penalty for a serious interference with privacy is the greater of:

- $50 million
- Three times the value of any benefit obtained
- 30% of adjusted turnover in the relevant period

For a mid-tier firm, even the lower-tier penalties ($3.3 million per contravention for non-serious interference) are enough to be career-ending.

## Legal Professional Privilege and Encryption

Here's an angle most firms don't consider: legal professional privilege protects confidential communications made for the dominant purpose of obtaining or providing legal advice. But privilege can be waived if confidentiality is lost.

If a client's privileged document is exposed because you emailed it unencrypted and someone intercepted it, you may have inadvertently waived privilege over that communication. The consequences for the client could dwarf any penalty you'd personally face.

This isn't a common scenario. But it's a scenario where the downside is so catastrophic that any reasonable risk management framework would account for it.

## What Doesn't Work

**Password-protected PDFs.** The encryption in standard PDF password protection is weak enough that free tools can crack it in minutes. It creates the appearance of security without the substance. Also, you inevitably end up emailing the password in a follow-up email to the same address, which achieves nothing.

**Encrypted email (S/MIME or PGP).** Technically excellent. Practically impossible. You'd need every opposing solicitor, every client, every barrister, and every expert witness to manage cryptographic certificates. This will never happen in the legal profession. The number of Australian solicitors with a functioning PGP key is in the low hundreds, and that's being generous.

**Microsoft 365 Message Encryption.** Better than nothing. But it requires recipients to authenticate through a Microsoft portal, which creates friction and confusion. Client-facing: "Please click this link, create a Microsoft account, verify your identity, then you can read my email" is not a workflow that survives first contact with a 70-year-old client.

**Secure client portals.** Large firms have them. They work well within the firm's ecosystem. They're useless for ad hoc document transfers to external parties who aren't going to create an account on your portal to receive a single document.

## What Actually Works

The requirements are straightforward:

1. **End-to-end encryption.** The document must be encrypted before it leaves your device, and only the intended recipient should be able to decrypt it.
2. **Zero knowledge.** The service facilitating the transfer should not be able to access the document contents. This eliminates the service provider as an attack surface.
3. **No account required for the recipient.** If opposing counsel or a client needs to create an account, install software, or manage certificates, adoption will be zero.
4. **Expiry.** The document should not persist indefinitely on any server. Transfer it, then it's gone.

These aren't exotic requirements. The technology exists. The problem has always been that the tools implementing it properly were designed by security engineers for security engineers, not by anyone who has ever tried to get a family law client to follow a three-step process.

## The Cost of Inaction

Every unencrypted email containing client documents is a liability sitting in at least two mailboxes. The expected cost of any individual email being breached is low. The expected cost across thousands of emails over years of practice is not low. And the tail risk -- a high-profile breach involving privileged documents in active litigation -- is the kind of event that ends careers and firms.

The profession is in a transitional period. Five years ago, emailing unencrypted documents was standard practice and regulators largely looked the other way. The combination of the strengthened Privacy Act penalties, explicit references to encryption as a reasonable technical measure, and rising community expectations has shifted the standard. Firms that adapt now are managing risk. Firms that wait are accumulating it.

---

*ObsidianVault provides zero-knowledge encrypted file transfer designed for legal confidentiality obligations. No accounts. No training sessions. Upload, share a link, done. [Try it at obsidianvault.vip](https://obsidianvault.vip)*
