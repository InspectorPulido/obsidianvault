---
title: "FERPA and HIPAA Equivalents in Australia: What the Privacy Act Actually Covers"
slug: ferpa-hipaa-equivalent-australia-privacy-act
date: 2026-03-28
description: "Australia doesn't have FERPA or HIPAA. It has the Privacy Act 1988 and APPs, which cover education and health data differently. Here's the actual mapping."
---

# FERPA and HIPAA Equivalents in Australia: What the Privacy Act Actually Covers

If you've googled "Australian equivalent of FERPA" or "HIPAA equivalent Australia," you've probably found a mix of vague references to the Privacy Act and US-centric compliance guides that mention Australia as an afterthought. Here's the actual picture.

The short version: Australia doesn't have sector-specific privacy statutes equivalent to FERPA (education) or HIPAA (health). Instead, it has a general-purpose privacy framework -- the Privacy Act 1988 (Cth) and the Australian Privacy Principles (APPs) -- that covers both sectors (and everything else) under a single regime, supplemented by state and territory legislation.

This is a fundamentally different approach. Understanding how it maps to the US framework is essential if you're operating across both jurisdictions, adopting US-built compliance tools, or trying to explain Australian privacy obligations to an American parent company.

## HIPAA vs. the Privacy Act: Health Data

### What HIPAA Does

HIPAA (the Health Insurance Portability and Accountability Act of 1996) creates specific rules for "covered entities" -- health plans, healthcare clearinghouses, and healthcare providers who transmit health information electronically. HIPAA's Privacy Rule governs uses and disclosures. The Security Rule mandates administrative, physical, and technical safeguards. The Breach Notification Rule requires notification within 60 days.

HIPAA is prescriptive. It specifies encryption standards (AES-128 or AES-256), requires risk assessments, mandates access controls, and defines exactly who is a covered entity and what constitutes protected health information (PHI).

### What Australia Does Instead

The Privacy Act 1988 doesn't have a separate health data statute. Instead, health information is classified as "sensitive information" under section 6 of the Act. Sensitive information triggers stricter requirements throughout the APPs:

- **APP 3 (Collection):** Sensitive information generally requires consent for collection, whereas non-sensitive personal information can be collected without consent if reasonably necessary.
- **APP 6 (Use and Disclosure):** Sensitive information has narrower permitted uses and disclosures.
- **APP 11 (Security):** The "reasonable steps" obligation applies to all personal information, but the sensitivity of health data raises the bar for what counts as reasonable.

There is no Australian equivalent of HIPAA's specific encryption mandates. APP 11 requires "technical and organisational measures" (strengthened by the 2024 amendments), and the OAIC identifies encryption as an example of a reasonable technical measure. But the standard is principle-based -- "reasonable steps" -- rather than prescriptive.

### State and Territory Health Records Acts

Several states and territories have their own health records legislation that sits alongside the federal Privacy Act:

- **Victoria:** Health Records Act 2001 (Vic) -- establishes Health Privacy Principles (HPPs) governing health information handled by Victorian public and private sector organisations.
- **NSW:** Health Records and Information Privacy Act 2002 (NSW) -- creates Health Privacy Principles for NSW health organisations.
- **ACT:** Health Records (Privacy and Access) Act 1997 (ACT).

These state Acts can impose additional obligations beyond the federal Privacy Act. If you're operating in healthcare, you need to comply with both.

### The Notifiable Data Breaches Scheme

Australia's equivalent of HIPAA's Breach Notification Rule is the Notifiable Data Breaches (NDB) scheme, which commenced in February 2018. Under Part IIIC of the Privacy Act, APP entities must notify the OAIC and affected individuals of eligible data breaches -- those likely to result in serious harm.

The health sector consistently reports the highest number of breaches: 20% of all notifications in July-December 2024, and 18% in January-June 2025, according to OAIC reporting.

## FERPA vs. the Privacy Act: Education Data

### What FERPA Does

FERPA (the Family Educational Rights and Privacy Act of 1974) protects the privacy of student education records. It applies to educational institutions that receive federal funding (which is virtually all of them in the US). FERPA gives parents rights over their children's records until the student turns 18 or enters postsecondary education, at which point rights transfer to the student.

FERPA prohibits disclosure of education records without consent, with defined exceptions (directory information, legitimate educational interest, health/safety emergencies, etc.).

### What Australia Does Instead

Australia has no equivalent of FERPA as a standalone education privacy statute. Student records are governed by the general Privacy Act framework, with the following key distinctions:

**Private schools:** Most private schools are APP entities and must comply with the full set of Australian Privacy Principles. They must have privacy policies, obtain consent for collection of sensitive information, and take reasonable steps to secure personal information.

**Public schools:** Government schools are generally exempt from the federal Privacy Act (as they're part of state/territory government agencies), but they're covered by state and territory privacy legislation:

- **Victoria:** Privacy and Data Protection Act 2014 (Vic) and the Information Privacy Principles.
- **NSW:** Privacy and Personal Information Protection Act 1998 (NSW).
- **Queensland:** Information Privacy Act 2009 (Qld).
- **Other states/territories:** Each has its own framework.

**Universities:** Public universities are generally exempt from the federal Privacy Act but covered by state/territory legislation. Private universities are APP entities.

The practical effect: there's no single "FERPA equivalent" in Australia. Instead, there's a patchwork of federal and state/territory legislation that varies by institution type and jurisdiction.

### Student Records in Practice

The rights that FERPA provides -- access to records, right to request amendment, control over disclosure -- exist in Australian law, but they're distributed across multiple instruments:

- **Access:** APP 12 gives individuals the right to access personal information held about them. Parents can access children's records under the APPs.
- **Correction:** APP 13 gives individuals the right to request correction of personal information.
- **Disclosure:** APP 6 restricts use and disclosure of personal information. Sensitive information (which may include health records collected by schools) has additional restrictions.

## The Key Differences

| Feature | US (HIPAA/FERPA) | Australia (Privacy Act + APPs) |
|---|---|---|
| Approach | Sector-specific statutes | General-purpose framework |
| Encryption | HIPAA specifies standards | APP 11 requires "reasonable steps" |
| Penalties | HIPAA: up to $2.13M per violation category per year | Privacy Act: up to $50M / 3x benefit / 30% turnover |
| Breach notification | HIPAA: 60 days | NDB scheme: "as soon as practicable" after assessment |
| Education data | FERPA (standalone statute) | Privacy Act + state/territory legislation |
| Health data | HIPAA (standalone statute) | Privacy Act (sensitive information) + state Health Records Acts |
| Regulator | HHS (HIPAA), Dept of Education (FERPA) | OAIC (federal) + state commissioners |

## Why This Matters Practically

If you're an Australian organisation evaluating US-built compliance tools, understanding this mapping prevents two common mistakes:

**Over-compliance.** Adopting HIPAA's specific technical requirements verbatim when the Privacy Act's principle-based approach may require different (sometimes more, sometimes less) measures. HIPAA's prescriptive rules don't map 1:1 to Australian obligations.

**Under-compliance.** Assuming that because Australia lacks a FERPA equivalent, student data privacy obligations are weaker. They're not -- they're just distributed differently across federal and state/territory legislation.

If you're handling sensitive data -- health records, student records, financial data -- the practical requirement in Australia is the same regardless of sector: take reasonable technical and organisational measures to protect it, including during transmission.

Emailing unencrypted sensitive records -- whether they're patient files, student reports, or tax returns -- is increasingly difficult to defend as "reasonable" under any of these frameworks.

---

*ObsidianVault provides zero-knowledge encrypted file transfer that meets the "reasonable steps" standard under Australia's Privacy Act. No sector-specific certification required -- just genuine end-to-end encryption. [Try it at obsidianvault.vip](https://obsidianvault.vip)*
