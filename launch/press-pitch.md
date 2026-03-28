# Press Pitch

**Target outlets:** The Age, ABC News, Guardian Australia, Crikey, The Saturday Paper
**Angle:** Healthcare privacy + human interest + tech
**Format:** Email pitch to journalist

---

**Subject:** Melbourne man on disability pension builds encryption tool in motel room after GP breaches his medical privacy

**To:** [journalist name]

Hi [name],

A Melbourne man on the disability support pension built a free encryption tool in a motel room on his birthday -- after his GP's receptionist emailed his complete medical records unencrypted across five separate emails because "the file was too big."

Each email was a breach of the Australian Privacy Act 1988.

**The story:**

Patrick Verhoeven is a software developer who fell on hard times. On his birthday, staying in a motel with 5 cents in his bank account, he received five unencrypted emails containing his full medical history -- sent through a shared practice inbox over plain SMTP. No password protection. No encryption. Standard practice for most GP offices in Australia.

Instead of filing a complaint, he built ObsidianVault -- a free, open-source tool that encrypts files in the browser before they ever touch a server. The server mathematically cannot read the files it stores. It requires no accounts, no training, no IT department. A receptionist can use it in 30 seconds.

**Why it matters now:**

- Healthcare has been Australia's most-breached sector for 14 consecutive OAIC reporting periods
- Penalties for serious Privacy Act breaches start at $2.5 million
- The Privacy Act Review recommendations (released 2023) flagged healthcare data handling as a critical gap
- Most GP practices still use email attachments as their primary method for transferring patient files
- No affordable, easy-to-use alternative existed until now

**Key facts:**

- Tool: ObsidianVault (https://obsidianvault.vip)
- Encryption: AES-256-GCM, browser-side via Web Crypto API
- Server role: Stores only ciphertext. Cannot decrypt.
- Cost: Free. Open source (MIT license).
- Technical: Single Python file, no dependencies. Self-hostable.
- GitHub: https://github.com/8889-coder/obsidianvault

**Suggested headline options:**

- "He had 5 cents in the bank. His GP emailed his records unencrypted. So he built the fix."
- "A Melbourne developer built a free encryption tool in a motel room. His GP's privacy breach was the catalyst."
- "Healthcare is Australia's most-breached sector. A developer on disability support built the solution for free."

**What makes this different from a tech press release:**

This isn't a startup launch. There's no funding round, no board, no growth strategy. It's a guy who got angry about a real problem, had the skills to fix it, and did -- from the worst possible starting position. The tool is genuinely free, genuinely open source, and solves a problem that costs the healthcare sector millions in breach penalties every year.

**Available for interview:**

Patrick Verhoeven
Developer, Blacktrace
Melbourne, Australia
Email: x@8889.quest
Web: https://obsidianvault.vip

Happy to do phone, video, or in-person in Melbourne. Can provide a live demo of the encryption process, the technical architecture, and the original breach emails (redacted).
