
import cloudscraper
from bs4 import BeautifulSoup
import csv

scraper = cloudscraper.create_scraper()
main_url = "https://fbref.com/en/comps/9/history/Premier-League-Seasons"
resp = scraper.get(main_url)
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
    raise SystemExit("❌ Premier League table not found!")

season_links = []
for link in soup.select('a[href*="Premier-League-Stats"]'):
    href = link.get('href')
    print(href)

    full_url = f"https://fbref.com{href}" if href.startswith('/') else href
    print(full_url)
