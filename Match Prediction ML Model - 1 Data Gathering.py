import pandas as pd

# Define dates for data set 
dates = pd.date_range(start='1/1/2018', end='5/31/2024', freq='YS')

# Scrape La Liga and Premier League match data over the predefined date range
all_dfs = []
for date in dates:
    season_start = date.year
    season_end = date.year + 1
    season = f'{season_start}-{season_end}'
    print(season)
    df = pd.read_html(f'https://fbref.com/en/comps/12/{season}/schedule/{season}-La-Liga-Scores-and-Fixtures', attrs={"id": f"sched_{season}_12_1"})[0]
    all_dfs.append(df)
    
    df2 = pd.read_html(f'https://fbref.com/en/comps/9/{season}/schedule/{season}-Premier-League-Scores-and-Fixtures', attrs={"id": f"sched_{season}_9_1"})[0]
    all_dfs.append(df2)

# Concatenate all dfs together
df = pd.concat(all_dfs)

# Drop rows with missing values in Wk column and drop irrelevant fields (Match Report and Notes) from df
df = df.dropna(subset=['Wk'])
df.drop(columns=['Match Report', 'Notes'], inplace=True)

# Save dataframe locally to a csv 
df.to_csv('~/Documents/GitHub/Football/MLMatchPrediction.csv', index=False)
