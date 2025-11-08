
import cloudscraper
from bs4 import BeautifulSoup
import csv

url = "https://fbref.com/en/comps/9/Premier-League-Stats"
scraper = cloudscraper.create_scraper()
resp = scraper.get(url)
print(f"Status Code: {resp.status_code}")

soup = BeautifulSoup(resp.text, "html.parser")

# STEP 1: Find the table DIRECTLY (not inside comments)
# We can find it by:
# 1. Looking for a table with a caption "Premier League Table"
caption = soup.find('caption', string='Premier League Table')
if caption:
    table = caption.find_parent('table')
else:
    # 2. Or find by ID pattern (starts with "results" and ends with "_overall")
    table = soup.find('table', {'id': lambda x: x and x.startswith('results') and x.endswith('_overall')})

if not table:
    raise SystemExit("❌ Premier League table not found!")

# STEP 2: Extract data from the table
rows = []
tbody = table.find('tbody')

for tr in tbody.find_all('tr'):
    # Skip header rows (marked with 'thead' class)
    if tr.get('class') and 'thead' in tr.get('class'):
        continue
    
    # Get rank (from <th> element with data-stat="rank")
    rank_th = tr.find('th', {'data-stat': 'rank'})
    rank = rank_th.text.strip() if rank_th else ""
    
    # Get team name (from <a> tag inside <td data-stat="team">)
    team_td = tr.find('td', {'data-stat': 'team'})
    team = team_td.find('a').text.strip() if team_td and team_td.find('a') else ""
    
    # Get all other stats
    played = tr.find('td', {'data-stat': 'games'}).text.strip() if tr.find('td', {'data-stat': 'games'}) else ""
    wins = tr.find('td', {'data-stat': 'wins'}).text.strip() if tr.find('td', {'data-stat': 'wins'}) else ""
    draws = tr.find('td', {'data-stat': 'ties'}).text.strip() if tr.find('td', {'data-stat': 'ties'}) else ""
    losses = tr.find('td', {'data-stat': 'losses'}).text.strip() if tr.find('td', {'data-stat': 'losses'}) else ""
    gf = tr.find('td', {'data-stat': 'goals_for'}).text.strip() if tr.find('td', {'data-stat': 'goals_for'}) else ""
    ga = tr.find('td', {'data-stat': 'goals_against'}).text.strip() if tr.find('td', {'data-stat': 'goals_against'}) else ""
    gd = tr.find('td', {'data-stat': 'goal_diff'}).text.strip() if tr.find('td', {'data-stat': 'goal_diff'}) else ""
    points = tr.find('td', {'data-stat': 'points'}).text.strip() if tr.find('td', {'data-stat': 'points'}) else ""
    
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
        "points": points
    })

# STEP 3: Save to CSV
with open("pl_table.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["rank", "team", "played", "wins", "draws", "losses", "gf", "ga", "gd", "points"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Successfully saved {len(rows)} teams to pl_table.csv")