# 🏆 Premier League Historical Table Scraper

A Python web scraper that extracts **Premier League season tables** from [FBref.com](https://fbref.com) using `cloudscraper` to bypass Cloudflare, and supports **rotating proxies** for stable long-run scraping.

---

## ⚙️ Features

- Scrapes **all Premier League seasons** automatically  
- Extracts per-team stats:
  - Rank  
  - Team name  
  - Matches played, wins, draws, losses  
  - Goals For / Against / Difference  
  - Points and Points Per Game  
- Saves all data neatly into `pl_tableGG.csv`
- Handles **Cloudflare protection** using `cloudscraper`
- Supports **rotating proxies** (premium or free)
- Adds polite random delays between requests to avoid bans

---

## 🧰 Requirements

| Library | Purpose |
|----------|----------|
| `cloudscraper` | Handles Cloudflare challenge pages |
| `beautifulsoup4` | Parses the HTML |
| `requests` | (Optional) for testing proxies |
| `csv` | Writes extracted data |
| `time`, `random`, `os` | Utility modules |

Install dependencies:

```bash
pip install cloudscraper beautifulsoup4
