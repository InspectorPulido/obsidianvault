# Contributing

Built by one person so far. Could use the help.

## Running Locally

```bash
cp .env.example .env
python3 app.py
```

Open http://localhost:5060. That is it.

## Code Structure

It is one file. `app.py`. The whole server. HTTP handler, encryption demo, drop management, blog engine, email capture, Stripe webhook -- all in one file. No framework. No ORM. No build step.

This is intentional. One file means one thing to audit. One thing to deploy. One thing to understand.

## How to Contribute

1. Open an issue describing what you want to change and why
2. Fork the repo
3. Make your change
4. Test it locally
5. Submit a PR

## What We Need

- Security review of the Web Crypto API usage
- Browser compatibility testing
- Accessibility improvements
- Documentation for self-hosting

## What We Do Not Need

- Framework migrations
- Database backends
- Microservice architecture
- Enterprise features nobody asked for
