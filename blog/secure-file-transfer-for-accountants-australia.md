---
title: "Secure File Transfer for Accountants in Australia: What the TPB Expects"
slug: secure-file-transfer-for-accountants-australia
date: 2026-03-28
description: "Australian accountants and tax agents have confidentiality obligations under the Tax Agent Services Act and Privacy Act. Here's what the TPB actually requires for transferring client data."
---

# Secure File Transfer for Accountants in Australia: What the TPB Expects

Tax season in Australia runs on email. Tax returns, financial statements, payroll summaries, BAS lodgements, trust distributions, SMSF audits -- all of it shuttled back and forth between accountants and clients as PDF attachments in plain email.

Every one of those documents contains the kind of information that identity thieves dream about. Tax file numbers, bank account details, ABNs, full financial histories. And every one of those emails sits unencrypted in at least two mailboxes, forever, until someone compromises one of them.

The regulatory framework governing how tax practitioners handle client data has tightened significantly. If you're an accountant still emailing unencrypted client files in 2026, you should understand what you're risking.

## The TPB Confidentiality Obligation

Section 30-10 of the Tax Agent Services Act 2009 (TASA) establishes the Code of Professional Conduct for registered tax agents and BAS agents. Item 6 of the Code requires practitioners to maintain the confidentiality of client information:

> Unless you have a legal duty to do so, you must not disclose any information relating to a client's affairs to a third party without your client's permission.

The Tax Practitioners Board (TPB) has published extensive guidance on this obligation, including TPB(I) 21/2014, which makes clear that confidentiality extends beyond simply not telling people things. It encompasses how you store, transmit, and protect client data.

The TPB's guidance specifically addresses outsourcing and data handling: practitioners must consider their confidentiality obligations when client data is sent to or stored by third-party services. That includes your email provider.

## The 2024-2025 Code Reforms

The Tax Agent Services (Code of Professional Conduct) Determination 2024 introduced strengthened obligations that took effect on 1 July 2025 for practices with 100 or fewer employees. These reforms expanded the Code to include explicit requirements around:

- Information security measures for client data
- Transparency about data handling practices
- Adequate systems and processes for protecting client information

The direction of travel is clear: the TPB expects practitioners to have actual systems for protecting client data, not just a vague intention to be careful.

## The Privacy Act Layer

If your practice has annual turnover exceeding $3 million, you're also an APP entity under the Privacy Act 1988 (Cth). Tax file numbers receive additional protection under the Privacy (Tax File Number) Rule 2015, which restricts how TFNs can be collected, used, stored, and disclosed.

APP 11, as amended by the Privacy and Other Legislation Amendment Act 2024, now explicitly requires "technical and organisational measures" to protect personal information. The OAIC identifies encryption as a standard technical measure.

The penalty framework for serious privacy breaches is severe: up to $50 million, three times the benefit obtained, or 30% of adjusted turnover -- whichever is greatest.

The finance sector (which includes accounting practices) reported 14% of all notifiable data breaches to the OAIC in the January-June 2025 reporting period, making it the second most-breached sector after health. These aren't hypothetical risks.

## What You're Actually Emailing

Consider what a typical email exchange during tax season contains:

**Individual clients:** Full name, date of birth, residential address, tax file number, employer details, salary and wage information, bank account numbers, investment holdings, rental property income, capital gains records, private health insurance details, spouse and dependent information.

**Business clients:** ABN, director details, profit and loss statements, balance sheets, aged receivables, payroll records (including employee TFNs and bank details), BAS worksheets, trust distribution statements.

**SMSF clients:** Member details, contribution records, pension payment schedules, investment portfolio details, actuarial certificates, auditor reports.

Each of these documents, sitting in an unencrypted email, is a single phishing attack away from exposure. And unlike a credit card number that can be cancelled, a tax file number is permanent. Once it's compromised, it's compromised for life.

## Common Practices That Don't Actually Work

**Password-protected ZIP files.** Better than nothing, marginally. The password invariably gets sent in the next email. The encryption strength of standard ZIP passwords is poor. And most clients will call you asking how to open it, costing you more in support time than you saved in breach risk.

**Client portals (practice management software).** If you're using Xero Practice Manager, MYOB Practice, or similar, their built-in portals are reasonable for ongoing document exchange with clients who have accounts. The limitation is ad hoc transfers -- new clients, one-off requests, sending documents to third parties like solicitors or financial advisers who aren't in your portal ecosystem.

**"Can you just text me the PDF?"** I've heard this from more practitioners than I'd like to admit. SMS and messaging apps like WhatsApp provide encryption in transit, but the document persists unencrypted on both devices, in cloud backups, and is accessible to anyone who picks up an unlocked phone.

**Dropbox or Google Drive links.** Encrypted at rest and in transit, but the provider holds the keys. A Dropbox breach, a compromised Google account, or a valid legal request would expose the contents. Not zero-knowledge. Not end-to-end encrypted.

## What the TPB Will Ask After a Breach

If client data is exposed and a complaint reaches the TPB, they'll want to know:

1. What systems did you have in place to protect client information?
2. Were those systems reasonable given the sensitivity of the data?
3. Did you comply with your obligations under Code item 6?
4. What technical measures were implemented for data in transit?

"We emailed it as a PDF attachment" is not an answer that demonstrates reasonable systems. The TPB has the power to impose sanctions ranging from written cautions to suspension or termination of registration. For a sole practitioner, termination of registration is termination of livelihood.

## What Secure Transfer Actually Looks Like

The requirements for accounting practices aren't different from any other profession handling sensitive data:

1. **End-to-end encryption.** The file is encrypted on your device before upload. Only the intended recipient can decrypt it. The transfer service never has access to the unencrypted content.
2. **Zero knowledge.** The service provider cannot read your files. This means a breach of the service provider doesn't expose your client data.
3. **No recipient account required.** Your clients range from tech-savvy business owners to retirees who struggle with email. Any solution that requires them to create an account or install software will fail.
4. **Automatic expiry.** Tax documents shouldn't persist on a third-party server indefinitely. Transfer it, confirm receipt, it's gone.
5. **Audit trail.** You need to be able to demonstrate that you used a secure method. A record of the transfer, without exposing the content, satisfies this.

The technology to do this properly exists now. The question is whether you implement it before or after a breach forces the decision.

## The Business Case

Beyond compliance, there's a straightforward business argument. Clients are increasingly aware of data security. An accounting practice that can demonstrate it takes data protection seriously -- "we use end-to-end encrypted file transfer for all client documents" -- has a genuine differentiator. It costs almost nothing to implement and signals professionalism to exactly the kind of clients who are worth retaining.

The firms that will struggle are the ones that wait until a breach forces a reactive, expensive, reputation-damaging scramble to implement what they could have done proactively for almost no cost.

---

*ObsidianVault provides zero-knowledge encrypted file transfer built for professional compliance. No accounts required for clients. No training. Upload, share a link, done. [Try it at obsidianvault.vip](https://obsidianvault.vip)*
