# r/selfhosted Post

**Subreddit:** r/selfhosted
**Title:** ObsidianVault -- zero-knowledge encrypted file transfer. Single Python file, stdlib only, no dependencies.
**Flair:** Share Your Creation

---

I built a zero-knowledge encrypted file transfer that's a single Python file with no dependencies beyond stdlib.

**Setup:**

```bash
git clone https://github.com/8889-coder/obsidianvault.git
cd obsidianvault
python3 app.py
```

That's it. No pip install. No requirements.txt. No node_modules. No Docker required (though you can obviously containerize it).

**What it does:**

- Browser encrypts files with AES-256-GCM (Web Crypto API) before upload
- Server only stores/serves ciphertext
- Decryption key stays in URL fragment -- never hits the server
- Configurable TTL with auto-expiry
- Hash-chained audit log (append-only, each entry SHA-256 linked to previous)
- Serves its own HTML/JS/CSS -- no build step

**Stack:**

- Python 3 `http.server`
- Web Crypto API
- That's the whole stack

**What it doesn't have (yet):**

- Docker Compose file (pull request welcome)
- Reverse proxy config examples
- Password-protected drops
- Upload size is currently limited by available RAM during the crypto operation

I built this because my GP's receptionist emailed my medical records unencrypted and I needed something that a non-technical person could use but that I'd actually trust with sensitive files.

Currently running behind nginx with Let's Encrypt on a $5 VPS. Uses about 30MB of RAM idle.

**Links:**

- GitHub: https://github.com/8889-coder/obsidianvault
- Live instance: https://obsidianvault.vip
- License: MIT

Any feature requests before I clean up the repo? Specifically interested in what would make this useful for your homelab setup.
