import os
import time
import logging
from dataclasses import dataclass
from typing import Iterable, Dict, Any, List, Optional

import praw

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str
    sleep_seconds: float = 1.0  # gentle pacing; keep it conservative


def load_config_from_env() -> RedditConfig:
    client_id = os.getenv("REDDIT_CLIENT_ID", "").strip()
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "").strip()
    user_agent = os.getenv("REDDIT_USER_AGENT", "academic-automotive-cyber-research").strip()

    if not client_id or not client_secret:
        raise RuntimeError(
            "Missing Reddit credentials. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET."
        )

    return RedditConfig(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def make_reddit_client(cfg: RedditConfig) -> praw.Reddit:
    # Read-only client (no username/password, no refresh token)
    reddit = praw.Reddit(
        client_id=cfg.client_id,
        client_secret=cfg.client_secret,
        user_agent=cfg.user_agent,
        check_for_async=False,
    )
    # Optional: explicitly keep it read-only
    reddit.read_only = True
    return reddit


def fetch_posts(
    reddit: praw.Reddit,
    subreddits: Iterable[str],
    limit_per_subreddit: int = 500,
    listing: str = "new",
    sleep_seconds: float = 1.0,
) -> List[Dict[str, Any]]:
    """
    Fetch public post metadata (read-only).
    Stores only: title, created_utc, subreddit, id, permalink.
    """
    results: List[Dict[str, Any]] = []

    for sub in subreddits:
        sub = sub.strip()
        if not sub:
            continue

        log.info("Fetching r/%s (%s, limit=%d)", sub, listing, limit_per_subreddit)
        sr = reddit.subreddit(sub)

        if listing == "hot":
            iterator = sr.hot(limit=limit_per_subreddit)
        elif listing == "top":
            iterator = sr.top(limit=limit_per_subreddit)
        else:
            iterator = sr.new(limit=limit_per_subreddit)

        for post in iterator:
            # Minimal, non-personal metadata
            results.append(
                {
                    "id": post.id,
                    "subreddit": post.subreddit.display_name,
                    "created_utc": float(post.created_utc),
                    "title": post.title or "",
                    "permalink": f"https://www.reddit.com{post.permalink}",
                }
            )

        # Gentle pacing between subreddits
        time.sleep(max(0.0, float(sleep_seconds)))

    return results
