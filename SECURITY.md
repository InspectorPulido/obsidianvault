# Security

The whole product is security. If you find something, tell us.

## Contact

security@obsidianvault.vip

## Responsible Disclosure

- Report vulnerabilities via email. PGP key available on request.
- We will acknowledge receipt within 48 hours.
- We will provide a fix timeline within 7 days.
- No bounty program yet. We will credit you in this file unless you prefer anonymity.
- Do not publicly disclose until we have shipped a fix.

## Threat Model

### In Scope

- Client-side encryption implementation (AES-256-GCM via Web Crypto API)
- Key generation and derivation
- URL fragment handling (key must never be sent to server)
- Server-side file storage and access controls
- Drop expiry and deletion
- XSS, CSRF, injection attacks against the web interface

### Out of Scope

- Attacks requiring physical access to the user's device
- Social engineering attacks against end users
- Link sharing -- if a user shares the link, the recipient can decrypt. This is by design.
- Browser vulnerabilities in the Web Crypto API itself
- Denial of service against the server (mitigate at the network layer)

## Architecture Guarantees

1. The server never receives the decryption key. It lives in the URL fragment, which browsers do not send in HTTP requests.
2. All encryption happens in the browser before upload. The server receives and stores only ciphertext.
3. The server cannot distinguish between encrypted files. All stored data is indistinguishable from random bytes.
4. Drop metadata (label, timestamp, file count) is stored in plaintext. File contents are not.

## Known Limitations

- No end-to-end authentication. The link IS the credential. Anyone with the link can decrypt.
- No forward secrecy. If the key is compromised, all files encrypted with it are compromised.
- File metadata (filename, size) is visible to the server. Only file contents are encrypted.
- Single-server architecture. No redundancy.

## Hall of Fame

Nobody yet. Be the first.
