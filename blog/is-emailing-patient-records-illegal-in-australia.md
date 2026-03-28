---
title: "Is Emailing Patient Records Illegal in Australia?"
slug: is-emailing-patient-records-illegal-in-australia
date: 2026-03-28
description: "Emailing patient records isn't explicitly illegal in Australia, but unencrypted email likely breaches Privacy Act obligations. Here's what the law actually says."
---

# Is Emailing Patient Records Illegal in Australia?

Short answer: no. Longer answer: it depends on how you do it, and if you're emailing unencrypted patient records in 2026, you're going to have a very hard time arguing you've met your legal obligations.

Let me explain.

## What the Law Actually Says

The Privacy Act 1988 (Cth) is the primary federal legislation governing how organisations handle personal information in Australia. Health information gets extra protection under the Act because it's classified as "sensitive information" -- a category that triggers stricter rules around collection, use, and disclosure.

The relevant obligation sits in Australian Privacy Principle 11 (APP 11), which states:

> An APP entity must take such steps as are reasonable in the circumstances to protect personal information from misuse, interference and loss, as well as unauthorised access, modification or disclosure.

Note the language. The law doesn't say "you must encrypt." It doesn't say "email is prohibited." It says you must take **reasonable steps** to protect the information.

That word -- reasonable -- is doing a lot of heavy lifting. And what counts as "reasonable" shifts over time as technology, threats, and community expectations evolve.

## The "Reasonable Steps" Standard in 2026

In 2003, emailing a patient referral as a plain-text PDF attachment might have been defensible. The threat landscape was different. Encryption was expensive and complicated. Most medical practices were still transitioning from fax machines.

In 2026, that argument has collapsed. Here's why:

**The Medibank breach of 2022** exposed the sensitive health information of approximately 9.7 million current and former customers. The data included mental health records, pregnancy termination records, and HIV status. The breach was a turning point in how Australia thinks about health data security.

In the aftermath, the Australian Government passed the Privacy Legislation Amendment (Enforcement and Other Measures) Act 2022, which dramatically increased penalties (more on that below) and signalled that the era of treating privacy obligations as soft guidelines was over.

**The Office of the Australian Information Commissioner (OAIC)** has published guidance making clear that organisations should implement technical measures to protect personal information during transmission. Their guide to securing personal information specifically references encryption as a standard protective measure.

**Community expectations have shifted.** Patients increasingly understand that their health data is valuable and vulnerable. A practice that emails unencrypted records is out of step with what a reasonable person would expect in 2026.

Put these together, and the "reasonable steps" standard has effectively moved. What was arguable in 2010 is indefensible now.

## The Penalty Regime

Prior to the 2022 amendments, maximum penalties for serious or repeated privacy breaches were capped at around $2.2 million for bodies corporate (the exact figure depended on the applicable penalty unit value at the time). That was low enough that some organisations treated compliance as a cost-benefit analysis -- the fine was cheaper than fixing the systems.

Post-amendment, the maximum civil penalty for a body corporate is the greater of:

- $50 million
- Three times the value of any benefit obtained from the breach
- 30% of the organisation's adjusted turnover in the relevant period

For individuals, the maximum penalty is $2.5 million.

These aren't theoretical numbers. The OAIC commenced Federal Court proceedings against Medibank in 2023 seeking penalties under this framework. The message was clear: the regulator has teeth now and intends to use them.

For a small medical practice, the $50 million cap is academic -- you'd hit financial ruin well before that. The point is that the penalty regime was redesigned to remove any economic incentive to deprioritise privacy.

## What About Encryption?

Email encryption exists, but it's worth being honest about the landscape.

**S/MIME and PGP** are the two established standards for end-to-end email encryption. Both require certificate management on both the sender's and recipient's side. In practice, almost nobody outside of government and defence uses them. Asking a GP clinic to manage S/MIME certificates is not realistic.

**TLS (Transport Layer Security)** encrypts email in transit between mail servers, and most major email providers now support it. But TLS only protects the connection, not the message. The email sits unencrypted on both the sending and receiving mail servers. If either server is compromised, the data is exposed.

**Microsoft 365 Message Encryption** and similar services exist, but they introduce friction -- recipients need to authenticate through a portal, which creates workflow disruption that most clinical staff will work around rather than through.

This is the core problem. The technically correct solutions are either impractical to deploy or so annoying that staff circumvent them. The result is that most practices default to plain email because nothing else is simple enough.

## So Is It Illegal or Not?

Sending patient records by email is not, per se, illegal. There is no provision in the Privacy Act that says "thou shalt not email health records."

But here's the practical reality:

1. APP 11.1 requires you to take reasonable steps to protect personal information.
2. Sending unencrypted patient records over standard email in 2026 is increasingly difficult to characterise as "reasonable."
3. The OAIC has signalled through guidance and enforcement actions that it expects organisations to implement appropriate technical safeguards.
4. The penalty regime has been deliberately calibrated to make non-compliance economically irrational.

You're not breaking a specific prohibition. You're failing to meet a standard of care that has been rising steadily for years. And if something goes wrong -- a misdirected email, a compromised mailbox, a disgruntled employee -- you'll be asked to explain what reasonable steps you took. "We just emailed it" is not an answer that ages well.

## What Should Practices Actually Do?

The ideal solution has three properties:

1. **End-to-end encryption** -- the data is protected in transit and at rest, and only the intended recipient can access it.
2. **Zero knowledge** -- the service provider cannot access the content, removing them as an attack vector.
3. **Simplicity** -- it has to be easier than attaching a PDF to an email, or staff will route around it.

That third point is the one most security products ignore. Compliance tools that require training sessions, IT support, and 12-step workflows don't get used. They get avoided. And an avoided compliance tool is worse than no tool at all, because it creates the illusion of compliance while achieving nothing.

The technology to solve this problem properly exists now. The question for practices is whether they implement it before or after something goes wrong.

---

*ObsidianVault provides zero-knowledge encrypted file transfer designed for healthcare compliance. No accounts required for recipients. No training sessions. No excuses. [Try it at obsidianvault.vip](https://obsidianvault.vip)*
