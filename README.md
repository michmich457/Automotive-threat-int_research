# Automotive Cybersecurity Topic Trends (Reddit Research)

This repository contains a research and educational tool that analyzes **public Reddit discussions** to identify **topic trends** related to **automotive cybersecurity** (e.g., ECU security, CAN bus attacks, OTA risks).

The project uses **read-only** access to the official Reddit API and does **not** interact with users or influence discussions.

## Goals

- Track how automotive cybersecurity topics evolve over time on Reddit
- Identify recurring vulnerability themes and emerging discussions
- Produce aggregated indicators for research, learning, and awareness

## What the app does

- Collects **public post metadata** from selected subreddits (e.g., title, timestamp, subreddit name)
- Computes **aggregated** statistics (e.g., keyword frequency, weekly/monthly trends)
- Exports results to CSV/JSON for further analysis

## What the app does NOT do

- No posting, commenting, voting, or messaging
- No user tracking or profiling
- No collection of personal user data (usernames, user IDs, private info)
- No scraping outside the official Reddit API
- No attempts to bypass rate limits

## Data processed

Only high-level public metadata is processed:
- Post title
- Post creation timestamp
- Subreddit name
- Post ID/permalink (optional, for deduplication and transparency)

## Intended subreddits (initial scope)

Examples (may evolve depending on research needs):
- r/cybersecurity
- r/netsec
- r/CarHacking
- r/ReverseEngineering
- r/embedded
- r/IOTSecurity
- r/automotive

## Setup

### Requirements
- Python 3.10+
- Reddit API credentials (OAuth)

### Install
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Automotive-threat-int_research
Research tool for analyzing public Reddit discussions to identify trends in automotive cybersecurity topics using read-only API access.
