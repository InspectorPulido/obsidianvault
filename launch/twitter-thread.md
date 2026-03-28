# Twitter/X Thread

**Post as:** @blacktrace_io (or personal account)
**Format:** Thread, 7 tweets

---

1/ I built a file transfer tool where the server literally cannot read your files.

Not "we promise we won't." Cannot. Mathematically.

AES-256-GCM encryption happens in your browser. The key stays in the URL fragment. Server only ever touches ciphertext.

2/ Why I built it:

My GP's receptionist split my medical records into 5 unencrypted email attachments because "the file was too big."

Shared inbox. Plain SMTP. Five Privacy Act breaches before lunch.

3/ The entire thing is one Python file. No frameworks. No dependencies. No npm install.

git clone, python3 app.py, done.

Open source. MIT licensed. Self-host it if you don't trust me (you shouldn't trust me -- that's the point).

4/ Threat model, honestly:

What it stops: server compromise, network MITM, nosy hosting providers

What it doesn't stop: if someone gets the full URL, they have the key. And yes, server-served JS is a trust point. I know. It's open source so you can verify.

5/ No accounts. No cookies. No tracking. No analytics. No sign-up.

Drop a file. Get a link. Send the link.

That's the whole product.

6/ Healthcare is the most-breached sector in Australia for the 14th consecutive reporting period.

Not because encryption is hard. Because the tools that exist require enterprise contracts, training budgets, and IT departments that GP practices don't have.

This requires none of that.

7/ Live: https://obsidianvault.vip
Source: https://github.com/8889-coder/obsidianvault

Free. No account needed. Works right now.

Go encrypt something.
