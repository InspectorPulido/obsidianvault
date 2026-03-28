# ObsidianVault

I built this in a motel room on my birthday because a receptionist named Anna split my medical records across 5 unencrypted emails. Each one was a Privacy Act breach. So I wrote something that makes it impossible.

**Zero-knowledge encrypted file transfer.** Your browser encrypts files with AES-256-GCM before they leave your machine. The server stores ciphertext. The decryption key lives in the URL fragment (`#`). It never touches the server. We cannot read your files. That is the whole product.

https://obsidianvault.vip

## Architecture

```
  You (sender)                    Server                     Recipient
  +-----------+                +-----------+              +-----------+
  | Browser   |  ciphertext   | Stores    |  ciphertext  | Browser   |
  | encrypts  | ----------->  | encrypted | -----------> | decrypts  |
  | AES-256   |               | blobs     |              | AES-256   |
  +-----------+                +-----------+              +-----------+
       |                            |                          |
       |  key in URL fragment (#)   |  never sees the key     |  key from URL
       +----------------------------+--------------------------+
```

The server is a single Python file. No framework. No dependencies beyond stdlib. No database. Files go in a directory. Metadata is JSON. That is the entire stack.

## Quick Start

```bash
python3 app.py
```

Listens on port 5060. Put Caddy or nginx in front for TLS.

## Docker

```bash
docker build -t obsidianvault . && docker run -p 5060:5060 obsidianvault
```

## How It Works

1. You drop a file on the page
2. Your browser generates a random 256-bit AES-GCM key
3. The file is encrypted entirely in the browser using the Web Crypto API
4. Only ciphertext is uploaded to the server
5. You get a link. The decryption key is in the URL fragment (`#key`)
6. The recipient clicks the link. Their browser downloads the ciphertext and decrypts it locally
7. The server never sees the key. The server never sees the plaintext.

## What If

- **You get hacked?** They get encrypted blobs. Indistinguishable from random noise.
- **Law enforcement seizes your servers?** They get ciphertext. We cannot produce plaintext because we never had it.
- **The link leaks?** Yes, then the file is accessible. Links are the credential. Treat them like passwords.

## Privacy Act 1988 Compliance

The 2024 Privacy Act amendments explicitly name encryption as a "reasonable technical measure" under APP 11. ObsidianVault implements client-side encryption so that the server operator (us) has zero access to plaintext data. This is the strongest possible compliance posture -- you cannot breach what you cannot read.

Built for medical practices, law firms, and accounting firms across Australia.

## License

MIT
