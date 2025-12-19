import argparse
import csv
import logging
import math
from datetime import datetime, timezone
from collections import Counter, defaultdict
from typing import List, Dict, Any

from dotenv import load_dotenv

from reddit_client import load_config_from_env, make_reddit_client, fetch_posts

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("analysis")


DEFAULT_KEYWORDS = [
    "can", "can bus", "canfd", "uds", "xcp", "ecu", "bootloader",
    "ota", "telematics", "gateway", "immobilizer", "keyless",
    "reverse engineering", "firmware", "diagnostics", "autosar",
    "secoc", "vulnerability", "exploit", "malware"
]


def to_week_bucket(created_utc: float) -> str:
    dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def keyword_hits(title: str, keywords: List[str]) -> Counter:
    t = normalize(title)
    c = Counter()
    for kw in keywords:
        k = normalize(kw)
        if k and k in t:
            c[k] += 1
    return c


def main():
    parser = argparse.ArgumentParser(description="Read-only Reddit topic trend analysis (automotive cybersecurity).")
    parser.add_argument("--subreddits", default="cybersecurity,netsec,CarHacking,ReverseEngineering,embedded,IOTSecurity,automotive")
    parser.add_argument("--limit", type=int, default=300, help="Posts per subreddit")
    parser.add_argument("--listing", choices=["new", "hot", "top"], default="new")
    parser.add_argument("--out", default="out.csv")
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS))
    args = parser.parse_args()

    load_dotenv()

    cfg = load_config_from_env()
    reddit = make_reddit_client(cfg)

    subreddits = [s.strip() for s in args.subreddits.split(",") if s.strip()]
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]

    posts = fetch_posts(
        reddit,
        subreddits=subreddits,
        limit_per_subreddit=args.limit,
        listing=args.listing,
        sleep_seconds=cfg.sleep_seconds,
    )

    # Aggregate counts by ISO week bucket
    bucket_counts = defaultdict(Counter)  # bucket -> Counter(keyword -> count)
    bucket_total_posts = Counter()        # bucket -> total posts

    for p in posts:
        bucket = to_week_bucket(p["created_utc"])
        bucket_total_posts[bucket] += 1
        bucket_counts[bucket] += keyword_hits(p["title"], keywords)

    # Write a flat CSV: one row per (bucket, keyword)
    rows = []
    for bucket in sorted(bucket_counts.keys()):
        total = bucket_total_posts[bucket]
        for kw in keywords:
            k = normalize(kw)
            hits = bucket_counts[bucket][k]
            # simple normalized rate: hits per 100 posts
            rate = (hits / total * 100.0) if total else 0.0
            rows.append({
                "week": bucket,
                "subreddits": ";".join(subreddits),
                "keyword": k,
                "hits": hits,
                "total_posts": total,
                "hits_per_100_posts": round(rate, 4),
            })

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [
            "week", "subreddits", "keyword", "hits", "total_posts", "hits_per_100_posts"
        ])
        writer.writeheader()
        writer.writerows(rows)

    log.info("Done. Wrote %d rows to %s", len(rows), args.out)


if __name__ == "__main__":
    main()
