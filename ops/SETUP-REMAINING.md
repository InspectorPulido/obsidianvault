# Remaining Setup (30 minutes total)

## 1. Resend SMTP (10 min)
Replace SES sandbox. Free tier: 100 emails/day. Permanent.

1. Go to resend.com, sign up (Google or GitHub)
2. Add domain: obsidianvault.vip
3. It gives you DNS records -- add them via Porkbun dashboard
4. Once verified, get API key
5. Update /var/www/zerodrop/.env:
```
SMTP_HOST=smtp.resend.com
SMTP_PORT=587
SMTP_USER=resend
SMTP_PASS=re_xxxxxxxxxxxx
```
6. Run: sudo systemctl restart zerodrop

## 2. Twitter/X API (10 min)
Free tier: 1,500 tweets/month. Permanent posting.

1. Go to developer.twitter.com, sign in with @BlckOfficial
2. Sign up for Free tier
3. Create an app, get 4 keys
4. Add to /home/ubuntu/bot/.env:
```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx
```
5. Run post-launcher to post thread from /var/www/zerodrop/launch/twitter-thread.md

## 3. LinkedIn (2 min)
No free API. Copy-paste once.
Content: /var/www/zerodrop/launch/linkedin.md

## 4. Product Hunt (3 min)
Manual submission at producthunt.com/posts/new
Content: /var/www/zerodrop/launch/producthunt.md
