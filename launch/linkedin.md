# LinkedIn Post

**Post as:** Patrick Verhoeven
**Format:** Long-form post with line breaks for readability

---

Your receptionist emailed a patient's medical records as an unencrypted PDF attachment today.

I know because mine did. Five times. In one afternoon. Because the file was "too big."

Each email was a breach of the Australian Privacy Act 1988. Penalties start at $2.5 million per serious breach. The OAIC investigated 1,133 data breach notifications last financial year. Healthcare was the most-breached sector for the 14th consecutive reporting period.

And the tool most practices use for transferring sensitive patient files? Gmail. With a PDF attached. To a shared inbox.

This isn't a security awareness problem. It's a workflow problem. The secure alternatives require enterprise contracts, IT departments, training budgets, and staff who care. Most GP practices have none of those things.

I'm a developer. I was also the patient in this story. I built a tool to fix it.

ObsidianVault encrypts files in the browser before they touch the server. AES-256-GCM. The server only ever sees ciphertext. It cannot decrypt your files. Not "we choose not to." Cannot. The key never leaves the client.

No accounts. No passwords. No training. Drop a file, get a link, send the link. The recipient clicks and downloads. That's it.

It's free. Open source. Self-hostable. A single Python file.

If you run a practice, manage compliance for a health service, or you're just tired of watching sensitive data fly across the internet in plaintext -- try it.

https://obsidianvault.vip

It won't fix the culture. But it removes the excuse.

Patrick Verhoeven
Blacktrace
