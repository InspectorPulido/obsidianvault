# r/sysadmin Post

**Subreddit:** r/sysadmin
**Title:** Anyone else dealing with medical offices that refuse to stop emailing unencrypted patient files?
**Flair:** Discussion

---

I'll keep this short because I know you're all dealing with the same thing.

My GP's receptionist needed to send me my medical records. File was too big for one email. Her solution: split the PDF into 5 parts and email them as unencrypted attachments. Shared practice inbox. No password protection. No encryption. Nothing.

That's 5 separate Privacy Act breaches in one afternoon.

I talked to the practice manager. She said "that's how we've always done it." I asked what system they use for secure file transfer. She didn't understand the question.

This is not a technology problem. The technology has existed for decades. This is a workflow problem. These offices won't adopt anything that requires:

- Creating accounts
- Remembering passwords
- Installing software
- Paying money
- Training staff

So I built something that requires none of those things.

**ObsidianVault** -- zero-knowledge encrypted file transfer.

For the practice:
1. Go to the site
2. Drop the file
3. Send the link to the patient

For the patient:
1. Click the link
2. Download the file

That's it. Encryption is AES-256-GCM, happens in the browser. The server stores ciphertext only. The decryption key is in the URL fragment and never touches the server. Files auto-delete after a configurable TTL. There's a hash-chained audit log for compliance.

No accounts. No software. No training. Free.

It's also a single Python file you can self-host if you don't trust my server: `python3 app.py`.

Live: https://obsidianvault.vip
GitHub: https://github.com/8889-coder/obsidianvault

I know this won't fix the root cause, which is that medical practices have zero security culture and regulators don't enforce. But if even one receptionist uses this instead of emailing a raw PDF, that's one fewer breach.

Anyone here actually managed to get a medical or dental office to adopt encrypted file transfer? What worked?
