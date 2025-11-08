import os
import cloudscraper
from bs4 import BeautifulSoup
import csv
import time
import random

# --- small helper config ---
MAX_RETRIES = 5
INITIAL_BACKOFF = 1.0
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Optional proxy support (set environment variable FBREF_PROXY="http://user:pass@host:port")
FBREF_PROXY = os.environ.get("FBREF_PROXY")

# --- create scraper ---
scraper = cloudscraper.create_scraper()

def is_challenge_page(text, status_code):
    """Return True when response looks like a Cloudflare challenge or rate-limit."""
    if status_code in (403, 429):
        return True
    if not text:
        return True
    lower = text[:1000].lower()
    # Common challenge indicators
    if "just a moment" in lower or "checking your browser" in lower or "cf-chl-bypass" in lower:
        return True
    return False

def safe_get(url, max_retries=MAX_RETRIES):
    """
    Wrapper around scraper.get with retries, backoff, rotating UA, optional proxy.
    Returns response or None on failure.
    """
    backoff = INITIAL_BACKOFF
    for attempt in range(1, max_retries + 1):
        # rotate UA a bit
        ua = random.choice(USER_AGENTS)
        scraper.headers.update({"User-Agent": ua})
        try:
            if FBREF_PROXY:
                resp = scraper.get(url, timeout=20, proxies={"http": FBREF_PROXY, "https": FBREF_PROXY})
            else:
                resp = scraper.get(url, timeout=20)
        except Exception as e:
            print(f"[attempt {attempt}] network error for {url}: {e} — backing off {backoff:.1f}s")
            time.sleep(backoff + random.uniform(0, 1.0))
            backoff *= 2
            continue

        # quick cloudflare / rate-limit detection
        if is_challenge_page(resp.text, resp.status_code):
            print(f"[attempt {attempt}] Cloudflare / rate-limited on {url} (status {resp.status_code}). backoff {backoff:.1f}s")
            # small randomization to avoid synchronized retries
            time.sleep(backoff + random.uniform(0.5, 1.5))
            backoff *= 2
            continue

        # success-ish
        return resp

    # exhausted
    print(f"❌ Failed to fetch {url} after {max_retries} attempts.")
    return None

# --------------------- your original structure, minimal edits ---------------------

main_url = "https://fbref.com/en/comps/9/history/Premier-League-Seasons"
resp = safe_get(main_url)
if resp is None:
    raise SystemExit("Could not fetch the seasons index (blocked or network issue).")

print(f"Status Code: {resp.status_code}")
soup = BeautifulSoup(resp.text, "html.parser")

# STEP 1: Find the table DIRECTLY (not inside comments)
# We can find it by:
# 1. Looking for a table with a caption "Premier League Table"
caption = soup.find('caption', string='Premier League Seasons Table')
if caption:
    table = caption.find_parent('table')
else:
    # 2. Or find by ID pattern (starts with "results" and ends with "_overall")
    table = soup.find('table', {'id': lambda x: x and x.startswith('results') and x.endswith('_overall')})

if not table:
    # instead of exiting hard, warn and continue (you might still get season links below)
    print("⚠️ Premier League table not found on index page (may be inside comments or blocked). Proceeding to extract links anyway.")
    table = None

season_links = []
for link in soup.select('a[href*="Premier-League-Stats"]'):
    href = link.get('href')
    print(href)
    full_url = f"https://fbref.com{href}" if href.startswith('/') else href
    # avoid duplicates
    if full_url not in season_links:
        season_links.append(full_url)

season_scraper = cloudscraper.create_scraper()  # you can still keep this if you want separate instance

for link in season_links:
    season_url = link
    # use safe_get here
    resp = safe_get(link)
    if resp is None:
        print(f"Skipping {link} due to repeated blocking.")
        continue

    print(f"Status Code: {resp.status_code}")
    soup = BeautifulSoup(resp.text, "html.parser")

    # STEP 1: Find the table DIRECTLY (not inside comments)
    # We can find it by:
    # 1. Looking for a table with a caption "Premier League Table"
    caption = soup.find('caption', string='Premier League Seasons Table')
    if caption:
        table = caption.find_parent('table')
    else:
        # 2. Or find by ID pattern (starts with "results" and ends with "_overall")
        table = soup.find('table', {'id': lambda x: x and x.startswith('results') and x.endswith('_overall')})

    if not table:
        # do not crash: warn and continue to next season
        print(f"⚠️ Premier League table not found on {season_url} — possibly hidden/inside comments or page structure differs. Skipping.")
        time.sleep(random.uniform(2, 4))
        continue

    # STEP 2: Extract data from the table
    rows = []
    tbody = table.find('tbody')
    if tbody is None:
        print(f"⚠️ No tbody on table for {season_url}. Skipping.")
        time.sleep(random.uniform(2, 4))
        continue

    for tr in tbody.find_all('tr'):
        # Skip header rows (marked with 'thead' class)
        if tr.get('class') and 'thead' in tr.get('class'):
            continue

        # Get rank (from <th> element with data-stat="rank")
        rank_th = tr.find('th', {'data-stat': 'rank'})
        rank = rank_th.text.strip() if rank_th else ""

        # Get team name (from <a> tag inside <td data-stat="team">)
        team_td = tr.find('td', {'data-stat': 'team'})
        team = team_td.find('a').text.strip() if team_td and team_td.find('a') else (team_td.text.strip() if team_td else "")

        # Get all other stats
        played = tr.find('td', {'data-stat': 'games'}).text.strip() if tr.find('td', {'data-stat': 'games'}) else ""
        wins = tr.find('td', {'data-stat': 'wins'}).text.strip() if tr.find('td', {'data-stat': 'wins'}) else ""
        draws = tr.find('td', {'data-stat': 'ties'}).text.strip() if tr.find('td', {'data-stat': 'ties'}) else ""
        losses = tr.find('td', {'data-stat': 'losses'}).text.strip() if tr.find('td', {'data-stat': 'losses'}) else ""
        gf = tr.find('td', {'data-stat': 'goals_for'}).text.strip() if tr.find('td', {'data-stat': 'goals_for'}) else ""
        ga = tr.find('td', {'data-stat': 'goals_against'}).text.strip() if tr.find('td', {'data-stat': 'goals_against'}) else ""
        gd = tr.find('td', {'data-stat': 'goal_diff'}).text.strip() if tr.find('td', {'data-stat': 'goal_diff'}) else ""
        points = tr.find('td', {'data-stat': 'points'}).text.strip() if tr.find('td', {'data-stat': 'points'}) else ""
        points_avg = tr.find('td', {'data-stat': 'points_avg'}).text.strip() if tr.find('td', {'data-stat': 'points_avg'}) else ""

        rows.append({
            "rank": rank,
            "team": team,
            "played": played,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "gf": gf,
            "ga": ga,
            "gd": gd,
            "points": points,
            "points_avg": points_avg
        })

    # STEP 3: Save to CSV (keeps same file-per-run behavior but overwrites each season in your original)
    with open("pl_tableGG.csv", "w", newline="", encoding="utf-8") as f:
        fieldnames = ["rank", "team", "played", "wins", "draws", "losses", "gf", "ga", "gd", "points", "points_avg"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Successfully saved {len(rows)} teams to pl_tableGG.csv")
    time.sleep(random.uniform(2, 4))   # polite gap
