#FBREF Scraping - Big 5 Leagues

import pandas as pd

df = pd.read_html('https://fbref.com/en/comps/Big5/stats/players/Big-5-European-Leagues-Stats', attrs={'id': 'stats_standard'})[0]

df.columns = ['_'.join(col).strip() for col in df.columns.values]

df.head()


# FBREF Scraping - Champions League

df = pd.read_html('https://fbref.com/en/comps/8/2023-2024/2023-2024-Champions-League-Stats', attrs={'id': 'results2023-202480_overall'})[0]

df = df.dropna(subset=['Rk'])

df.head()


# FBREF Scraping - Premier League - Arsenal 
df = pd.read_html('https://fbref.com/en/squads/18bb7c10/2022-2023/Arsenal-Stats', attrs={'id': 'stats_standard_9'})[0]

df.columns = ['_'.join(col).strip() for col in df.columns.values]

df.head()

# FBREF Scraping - La Liga - FC Barcelona 
df = pd.read_html('https://fbref.com/en/squads/206d90db/2023-2024/Barcelona-Stats', attrs={'id': 'stats_standard_12'})[0]

df.columns = ['_'.join(col).strip() for col in df.columns.values]

df.head()


# FBREF Scraping - Primeira Liga

import requests
import bs4
from io import StringIO

response = requests.get('https://fbref.com/en/comps/32/stats/Primeira-Liga-Stats')
soup = bs4.BeautifulSoup(response.content)

comments = soup.find_all(string=lambda text: isinstance(text, bs4.Comment))

commented_out_tables = [bs4.BeautifulSoup(cmt).find_all('table') for cmt in comments]

commented_out_tables = [tab[0] for tab in commented_out_tables if len(tab) == 1]

df = pd.read_html(StringIO(str(commented_out_tables[0])))[0]

df.head()
