import requests
from bs4 import BeautifulSoup

url = "https://fbref.com/en/comps/9/Premier-League-Stats"
r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
print("Status code:", r.status_code)
html = r.text
print("Downloaded HTML length:", len(html))
print("HTML head preview:\n", html[:1000])   # first 1000 chars
soup = BeautifulSoup(html, 'lxml')
print("Tables found with class='stats_table':", len(soup.find_all('table', class_='stats_table')))
