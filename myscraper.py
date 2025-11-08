import cloudscraper
from bs4 import BeautifulSoup, Comment
import csv

url = "https://fbref.com/en/comps/9/Premier-League-Stats"
scraper = cloudscraper.create_scraper()
resp = scraper.get(url)
print(resp.status_code)  # should be 200

soup = BeautifulSoup(resp.text, "lxml")

# fbref wraps tables in HTML comments
comments = soup.find_all(string=lambda text: isinstance(text, Comment))
table = None
for c in comments:
    if '<table' in c and 'stats' in c:  # pick a keyword in the table you want
        comment_soup = BeautifulSoup(c, "lxml")
        table = comment_soup.find("table")
        if table:
            break

if not table:
    raise SystemExit("Table not found inside comments!")

tbody = table.find("tbody")
rows = []

for tr in tbody.find_all("tr"):
    # ignore header/empty rows
    if tr.get('class') and 'thead' in tr.get('class'):
        continue
    def cell(stat):
        td = tr.find("td", {"data-stat": stat})
        return td.get_text(strip=True) if td else ""
    
    rank = tr.find("th").get_text(strip=True)
    rows.append({
        "rank": rank,
        "team": cell("team"),
        "played": cell("games"),
        "wins": cell("wins"),
        "draws": cell("ties"),
        "losses": cell("losses"),
        "gf": cell("goals_for"),
        "ga": cell("goals_against"),
        "gd": cell("goal_diff"),
        "points": cell("points")
    })

with open("pl_table.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {len(rows)} rows to pl_table.csv")
