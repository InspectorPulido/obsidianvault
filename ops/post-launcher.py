#!/home/ubuntu/bot/venv/bin/python3
"""ObsidianVault post launcher. Reads .md files from launch/, posts or prints for copy-paste."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from notify import send_tg

LAUNCH_DIR = "/var/www/zerodrop/launch"
CREDS_PATH = "/home/ubuntu/bot/__PJ/poster/cookies/creds.json"

# Platform keywords in filenames
PLATFORMS = ["twitter", "reddit", "linkedin", "instagram", "facebook", "hackernews", "producthunt", "medium", "substack"]


def load_creds():
    """Load credentials from creds.json or env vars."""
    creds = {}
    try:
        with open(CREDS_PATH, "r") as f:
            creds = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Override/supplement with env vars
    for platform in PLATFORMS:
        prefix = platform.upper()
        for key in ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_SECRET", "CLIENT_ID", "CLIENT_SECRET", "USERNAME", "PASSWORD"]:
            env_key = f"{prefix}_{key}"
            val = os.environ.get(env_key)
            if val:
                creds.setdefault(platform, {})[key.lower()] = val

    return creds


def detect_platform(filename):
    """Detect platform from filename."""
    name_lower = filename.lower()
    for p in PLATFORMS:
        if p in name_lower:
            return p
    return None


def extract_content(filepath):
    """Read markdown file and extract title + body."""
    with open(filepath, "r") as f:
        content = f.read().strip()

    lines = content.split("\n")
    title = ""
    body = content
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            body = "\n".join(lines[i + 1:]).strip()
            break

    return title, body, content


def post_twitter(title, body, creds):
    """Post to Twitter/X using tweepy if available."""
    twitter_creds = creds.get("twitter", {})
    api_key = twitter_creds.get("api_key")
    api_secret = twitter_creds.get("api_secret")
    access_token = twitter_creds.get("access_token")
    access_secret = twitter_creds.get("access_secret")

    if not all([api_key, api_secret, access_token, access_secret]):
        return "no_creds"

    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret,
        )
        # Twitter: use title + truncated body, max 280 chars
        tweet = title if title else body[:270]
        if len(tweet) > 280:
            tweet = tweet[:277] + "..."
        client.create_tweet(text=tweet)
        return "posted"
    except ImportError:
        return "tweepy_missing"
    except Exception as e:
        print(f"[post-launcher] Twitter error: {e}", file=sys.stderr)
        return "failed"


def post_reddit(title, body, creds):
    """Post to Reddit using praw if available."""
    reddit_creds = creds.get("reddit", {})
    client_id = reddit_creds.get("client_id")
    client_secret = reddit_creds.get("client_secret")
    username = reddit_creds.get("username")
    password = reddit_creds.get("password")
    subreddit_name = reddit_creds.get("subreddit", "test")

    if not all([client_id, client_secret, username, password]):
        return "no_creds"

    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent="ObsidianVault/1.0",
        )
        subreddit = reddit.subreddit(subreddit_name)
        subreddit.submit(title or "ObsidianVault", selftext=body)
        return "posted"
    except ImportError:
        return "praw_missing"
    except Exception as e:
        print(f"[post-launcher] Reddit error: {e}", file=sys.stderr)
        return "failed"


def print_copy_paste(platform, title, body, content):
    """Print content formatted for manual copy-paste."""
    print(f"\n{'='*60}")
    print(f"PLATFORM: {platform.upper()}")
    print(f"{'='*60}")
    if title:
        print(f"TITLE: {title}")
        print(f"---")
    print(content)
    print(f"{'='*60}\n")


def main():
    creds = load_creds()
    results = []

    try:
        md_files = sorted(Path(LAUNCH_DIR).glob("*.md"))
    except (FileNotFoundError, PermissionError):
        print("[post-launcher] Launch directory not found or not accessible.")
        return

    if not md_files:
        print("[post-launcher] No .md files in launch directory.")
        return

    for filepath in md_files:
        filename = filepath.name
        platform = detect_platform(filename)

        try:
            title, body, content = extract_content(str(filepath))
        except Exception as e:
            print(f"[post-launcher] Error reading {filename}: {e}", file=sys.stderr)
            results.append((filename, platform or "unknown", "read_error"))
            continue

        if platform is None:
            # Generic content -- print for manual use
            print_copy_paste("unknown", title, body, content)
            results.append((filename, "unknown", "manual"))
            continue

        status = "manual"

        if platform == "twitter":
            result = post_twitter(title, body, creds)
            if result == "posted":
                status = "posted"
            elif result in ("no_creds", "tweepy_missing"):
                print_copy_paste(platform, title, body, content)
                status = f"manual ({result})"
            else:
                print_copy_paste(platform, title, body, content)
                status = "failed"

        elif platform == "reddit":
            result = post_reddit(title, body, creds)
            if result == "posted":
                status = "posted"
            elif result in ("no_creds", "praw_missing"):
                print_copy_paste(platform, title, body, content)
                status = f"manual ({result})"
            else:
                print_copy_paste(platform, title, body, content)
                status = "failed"

        else:
            print_copy_paste(platform, title, body, content)
            status = "manual"

        results.append((filename, platform, status))

    # TG notifications per platform
    for filename, platform, status in results:
        tg_status = "posted" if "posted" in status else "manual needed"
        send_tg(f"POST: {platform} -- {tg_status} ({filename})")
        print(f"[{platform}] {status} -- {filename}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[post-launcher] Fatal: {e}", file=sys.stderr)
        sys.exit(1)
