# r/netsec Post

**Subreddit:** r/netsec
**Title:** Threat model review request: browser-based zero-knowledge file transfer using AES-256-GCM via Web Crypto API
**Flair:** Hiring/Review (or whichever mod-approved flair fits)

---

I built a zero-knowledge encrypted file transfer tool and I'm looking for critique, not validation. The architecture is simple enough that the threat model should be reviewable in 10 minutes.

**How it works:**

1. Browser generates 256-bit random key via `crypto.getRandomValues()`
2. Files encrypted with AES-256-GCM via `crypto.subtle.encrypt()`
3. Ciphertext uploaded to server over TLS
4. Server returns drop URL. Key appended as URL fragment (`#key=...`)
5. Recipient opens URL, browser fetches ciphertext, decrypts with key from fragment
6. Server never receives the key (browsers don't send URI fragments in HTTP requests)

**Threat model:**

| Threat | Mitigation | Residual Risk |
|---|---|---|
| Server compromise | Server stores only ciphertext + encrypted filenames | None beyond metadata (sizes, timestamps, IPs) |
| Network eavesdropping | TLS for transport + client-side AES-256-GCM for payload | Standard TLS caveats |
| Link interception | Key in URL fragment, not query string | If full URL is intercepted (clipboard, screen share, logs), key is exposed |
| Malicious server-served JS | **Open source. CSP headers.** | **This is the big one.** Server operator can serve modified JS that exfiltrates keys. No current mitigation beyond code audit and trust. SRI planned but not yet implemented. |
| Brute force on ciphertext | 256-bit key space | Not feasible |
| Replay attacks | Each drop has unique ID + TTL | Within TTL window, ciphertext is replayable but still encrypted |
| Metadata analysis | Minimal metadata stored. No accounts. No cookies. | Ciphertext sizes, timestamps, IPs are visible to server operator |
| Browser-level compromise | Out of scope | Keylogger/malicious extension defeats any browser-based crypto |
| Key in browser history | Fragment is stored in browser history | Local device compromise exposes past keys |

**Known weaknesses I want to discuss:**

1. **Server-served JS trust problem.** This is the elephant in the room for any browser-based E2E system. I know about it. I don't have a good solution beyond "read the source." Interested in practical mitigations beyond "use a native app."

2. **No key derivation.** The raw AES key is base64-encoded in the URL. No password-based key derivation layer. A password-protected mode where the URL key wraps a derived key would add defense-in-depth for link interception.

3. **IV/nonce handling.** Using random 96-bit IV per encryption operation via `crypto.getRandomValues()`. Standard GCM nonce. No nonce reuse risk in practice because each drop generates a fresh key, but worth verifying my implementation.

4. **No authentication of sender.** Anyone with the upload endpoint can create drops. This is by design (no accounts) but means no sender verification.

**Implementation:**

- Single Python file (~800 lines including inline HTML/JS)
- Python stdlib only (`http.server`)
- Web Crypto API for all cryptographic operations
- Hash-chained append-only audit log

Source: https://github.com/8889-coder/obsidianvault
Live: https://obsidianvault.vip
License: MIT

What am I missing? What would you attack first?
