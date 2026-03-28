---
title: "AES-256-GCM Encryption with the Web Crypto API: A Practical Guide"
slug: aes-256-gcm-web-crypto-api-tutorial
date: 2026-03-28
description: "How to implement AES-256-GCM encryption in the browser using the Web Crypto API. Working code, real security considerations, and why most tutorials skip the hard parts."
---

# AES-256-GCM Encryption with the Web Crypto API: A Practical Guide

Most AES-256-GCM tutorials give you a code snippet, tell you it's secure, and move on. That's fine if you're encrypting a TODO app. It's insufficient if you're building something that handles data people actually care about.

This guide covers the Web Crypto API's AES-256-GCM implementation with the context that matters: why GCM, what the IV requirements actually are, how key management works in a browser context, and where the security model breaks down. Working code included. No npm packages required -- the Web Crypto API is built into every modern browser.

## Why AES-256-GCM

AES (Advanced Encryption Standard) with a 256-bit key is the standard symmetric encryption algorithm used by governments, military, and financial institutions worldwide. GCM (Galois/Counter Mode) adds authenticated encryption -- it encrypts the data and simultaneously produces an authentication tag that detects any tampering.

This matters. Encryption without authentication (like AES-CBC without a separate HMAC) is vulnerable to padding oracle attacks and other manipulation. GCM gives you confidentiality and integrity in a single operation. It's also fast -- GCM is designed for hardware acceleration, and modern CPUs with AES-NI instructions can encrypt at multiple GB/s.

The Web Crypto API exposes AES-256-GCM through the `SubtleCrypto` interface. It runs in a secure context (HTTPS only), operates on `ArrayBuffer` objects, and is fully asynchronous. The "subtle" in `SubtleCrypto` is a reminder that cryptographic APIs are easy to misuse -- the API is correct, but the code around it might not be.

## Generating a Key

```
async function generateKey() {
  return await crypto.subtle.generateKey(
    { name: "AES-GCM", length: 256 },
    true,    // extractable -- set to true if you need to export it
    ["encrypt", "decrypt"]
  );
}
```

The `extractable` parameter controls whether the key can be exported from the CryptoKey object. Set it to `true` if you need to share the key (e.g., embed it in a URL or store it). Set it to `false` for keys that should never leave the browser's crypto subsystem.

The key is generated using the browser's cryptographically secure random number generator (`crypto.getRandomValues` under the hood). You don't need to seed it. You don't need an external entropy source. The browser handles this correctly.

## Encryption

```
async function encrypt(key, plaintext) {
  const encoder = new TextEncoder();
  const data = encoder.encode(plaintext);

  // 96-bit IV, as recommended by NIST SP 800-38D
  const iv = crypto.getRandomValues(new Uint8Array(12));

  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    key,
    data
  );

  return { iv, ciphertext };
}
```

### The IV: What You Must Not Get Wrong

The initialisation vector (IV) for AES-GCM must be 96 bits (12 bytes) and must be unique for every encryption operation with a given key. The NIST specification (SP 800-38D) is explicit about this.

If you reuse an IV with the same key, the security of GCM collapses catastrophically. An attacker can recover the authentication key and forge ciphertexts. This isn't a theoretical weakness -- it's a complete break of both confidentiality and authenticity.

For random IVs, the birthday bound gives you roughly 2^48 encryptions before a collision becomes probable. That's about 281 trillion operations. If you're encrypting fewer than a few billion items with the same key, random IVs are safe. If you're building a system that might exceed that, use a counter-based IV scheme.

The IV is not secret. It's sent alongside the ciphertext. The security of GCM depends on IV uniqueness, not IV secrecy.

## Decryption

```
async function decrypt(key, iv, ciphertext) {
  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: iv },
    key,
    ciphertext
  );

  const decoder = new TextDecoder();
  return decoder.decode(plaintext);
}
```

If the ciphertext has been tampered with, `decrypt()` will throw a `DOMException` with the name `OperationError`. This is the authentication tag doing its job. Do not catch this error and try to proceed -- if decryption fails, the data has been modified and should be discarded entirely.

## Exporting and Importing Keys

To share a key (e.g., embed it in a URL fragment), you need to export it:

```
async function exportKey(key) {
  const raw = await crypto.subtle.exportKey("raw", key);
  return btoa(String.fromCharCode(...new Uint8Array(raw)));
}

async function importKey(base64Key) {
  const raw = Uint8Array.from(atob(base64Key), c => c.charCodeAt(0));
  return await crypto.subtle.importKey(
    "raw",
    raw,
    { name: "AES-GCM", length: 256 },
    true,
    ["encrypt", "decrypt"]
  );
}
```

The exported key is 32 bytes (256 bits). Base64-encoded, that's 44 characters. Short enough to embed in a URL fragment.

## The URL Fragment Trick

This is the pattern ObsidianVault uses, and it's worth understanding why it works.

When you create a URL like `https://example.com/file/abc123#decryptionKeyHere`, the browser sends a request for `/file/abc123` to the server. The fragment (`#decryptionKeyHere`) is never sent. It stays in the browser. This is defined in RFC 3986 and is fundamental to how URLs work -- it's not a hack, it's the specification.

This means you can embed a decryption key in a URL and share it, and the server hosting the encrypted file never sees the key. The server stores ciphertext. The key lives in the URL. The decryption happens entirely in the browser.

The security model is: anyone with the full URL can decrypt the file. Anyone without the fragment (including the server) cannot. The link is the key.

## Putting It Together: File Encryption

For files (as opposed to text strings), you work with `ArrayBuffer` objects directly:

```
async function encryptFile(key, fileArrayBuffer) {
  const iv = crypto.getRandomValues(new Uint8Array(12));

  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: iv },
    key,
    fileArrayBuffer
  );

  // Prepend IV to ciphertext for storage
  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(ciphertext), iv.length);

  return combined.buffer;
}

async function decryptFile(key, combinedBuffer) {
  const combined = new Uint8Array(combinedBuffer);
  const iv = combined.slice(0, 12);
  const ciphertext = combined.slice(12);

  return await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: iv },
    key,
    ciphertext
  );
}
```

Prepending the IV to the ciphertext is a common pattern. The IV is not secret, so storing it alongside the encrypted data is standard practice.

## Where the Security Model Breaks

The Web Crypto API is cryptographically sound. The problems are in the surrounding architecture.

**Server-served JavaScript.** The encryption code runs in the browser, but the browser loads that code from a server. If the server is compromised, it could serve malicious JavaScript that exfiltrates keys before encryption or after decryption. This is the fundamental limitation of all browser-based E2E encryption. Mitigations include subresource integrity (SRI) hashes, open-source code audits, and reproducible builds. None of these fully eliminate the risk. A native application would, because the code is verified at install time, not at every page load.

**Key distribution.** The URL fragment pattern is elegant, but the key's security is only as good as the channel you share the URL through. Share it over unencrypted email and you've reduced your security to the security of email. Share it over Signal and you're in better shape. This is a usage problem, not a crypto problem, but it's the one most users will get wrong.

**Memory safety.** JavaScript doesn't give you control over memory. Decrypted data in a JavaScript variable will persist in memory until garbage collected, and you can't zero it. For most threat models this is acceptable. For adversaries with memory access (e.g., Spectre-class attacks, malicious browser extensions), it's a consideration.

**Browser trust.** You're trusting the browser's implementation of the Web Crypto API. In practice, major browsers (Chrome, Firefox, Safari) use well-audited cryptographic libraries (BoringSSL, NSS, CommonCrypto). This is a reasonable trust assumption for almost all use cases.

## Self-Hosting vs. Using a Service

If you're a developer considering self-hosting an encrypted file transfer service, the code above gives you the client-side crypto. The server-side is straightforward: accept an encrypted blob, store it, serve it back. The server never needs to know anything about the content.

The hard part isn't the crypto -- it's everything else. Rate limiting, abuse prevention, storage management, expiry, access logging, uptime, TLS configuration, CSP headers, and the ongoing maintenance burden of a public-facing service.

ObsidianVault is open-source. You can inspect the implementation, fork it, or self-host it. The repo is at [github.com/8889-coder/obsidianvault](https://github.com/8889-coder/obsidianvault). If you want to understand how a production implementation handles the edge cases that tutorials skip, that's a reasonable starting point.

---

*ObsidianVault implements exactly this pattern -- AES-256-GCM via the Web Crypto API, key in the URL fragment, zero-knowledge server. Open-source and free. [Try it at obsidianvault.vip](https://obsidianvault.vip) or [read the code on GitHub](https://github.com/8889-coder/obsidianvault).*
