# Show HN: I built a zero-knowledge file transfer in a motel room because my GP breached my privacy

**Post as: Text post on Hacker News**
**URL: (leave blank -- text post)**

---

I'm on the disability support pension. I had 5 cents in my bank account on my birthday. I was staying in a motel because I had nowhere else to go.

My GP's receptionist needed to send me my medical records. The file was too big to email. So she split it into 5 unencrypted PDF attachments and emailed them across 5 separate messages. Through a shared practice inbox. Over plain SMTP.

Each one was a breach of the Australian Privacy Act.

I'm a developer. I knew exactly how bad this was. I also knew nobody was going to fix it for her. The tools that exist are either enterprise garbage that costs $50k/year, or consumer apps that require accounts and collect metadata.

So I built ObsidianVault.

**What it does:**

- AES-256-GCM encryption happens entirely in the browser via the Web Crypto API
- The encryption key never leaves the client. It lives in the URL fragment (after the #), which browsers don't send to servers
- The server stores and serves ciphertext. It literally cannot decrypt your files. Not "we promise we won't." Cannot.
- No accounts. No cookies. No tracking. No JavaScript frameworks.
- Single Python file. stdlib only. `python3 app.py` and you're running.

**Architecture:**

1. Sender drops file(s) into the browser
2. Browser generates a random 256-bit AES-GCM key
3. Files encrypted client-side, ciphertext uploaded to server
4. Server returns a link. Key is appended as URL fragment
5. Recipient opens link, browser fetches ciphertext, decrypts locally
6. Server sees: ciphertext in, ciphertext out. That's it.

**What the server knows:**

- Ciphertext blob size
- Upload timestamp
- Download timestamp
- IP addresses (unless you use Tor/VPN)

**What the server does NOT know:**

- File contents
- File names (encrypted)
- Who sent it
- Who received it

**Threat model (honest version):**

| Threat | Status |
|---|---|
| Server compromise | Protected -- server only has ciphertext |
| Network MITM | Protected -- TLS + client-side encryption |
| Recipient link interception | Key in fragment, not sent to server. But if someone has the full URL, they have the key. |
| Server-served JavaScript | **Known weakness.** If I serve malicious JS, I could exfiltrate keys. This is the fundamental limitation of any browser-based E2E system. Mitigations: open source, CSP headers, subresource integrity planned. |
| Brute force on encryption key | 256-bit AES. Heat death of the universe. |

**Stack:**

- Python 3. stdlib only. No Flask, no Django, no npm.
- Web Crypto API for AES-256-GCM
- Hash-chained append-only audit log (each entry includes SHA-256 of previous)
- Configurable TTL with auto-expiry
- MIT licensed

GitHub: https://github.com/8889-coder/obsidianvault
Live: https://obsidianvault.vip

The whole thing is one Python file. About 800 lines including the HTML. I know that's ugly. I also know it works, and I can read every line of it.

I built this because a receptionist shouldn't need a security clearance to send a medical file. And a patient shouldn't have to hope nobody's reading their records in transit.

Tear it apart. I'd rather find the holes here than in production.
