import pandas as pd

import warnings
warnings.filterwarnings('ignore')

#Load six PL and La Liga match data since 2018
df = pd.read_csv('~/Documents/GitHub/Football/MLMatchPrediction.csv')

# Drop rows where there are missing values in 'Score', 'xG', 'xG.1', and 'Referee'
df = df.dropna(subset=['Score', 'xG', 'xG.1', 'Referee'])

# Drop 'Attendance' and 'Time' columns as they are irrelevant to the model
df = df.drop(columns=['Attendance', 'Time'])

# Split the 'Score' column into 'HomeGoals' and 'AwayGoals' columns
df[['home_goals', 'away_goals']] = df['Score'].str.split('–', expand=True).astype(float)

# Create a season_start column so that we can fit dates into football seasons
df['Date'] = pd.to_datetime(df['Date'])
df['season_start'] = df['Date'].apply(lambda x: x.year - 1 if x.month < 8 else x.year)

# Create a match result as the target variable which returns whether a match was a home win, away win or draw
def determine_result(row):
    if row['home_goals'] > row['away_goals']:
        return 'Home win'
    elif row['home_goals'] < row['away_goals']:
        return 'Away win'
    else:
        return 'Draw'

df['result'] = df.apply(determine_result, axis=1)

# Encode 'Day' as seven categorical variables by using pd.get_dummies
df['Day'] = df['Date'].dt.day_name()
df = pd.get_dummies(df, columns=['Day'])

# Reset the index to avoid misalignments in temporary dfs 
df.reset_index(drop=True, inplace=True)
df.sort_values(['Date'], inplace=True)

# Create a temporary df with all matches for a certain team (either at home or away)
for x in df.Home.unique():
    temp_df = df[(df['Home'] == x) | (df['Away'] == x)]
    temp_df = temp_df.sort_values(['Date'])
# Ensure the correct goal value is being calculated depending whether a team is at home or away    
    temp_df['goal_value_to_calculate'] = temp_df.apply(lambda y: y['home_goals'] if y['Home'] == x else y['away_goals'], axis=1)
# Calculate the rolling average of goals of the last five matches  
    temp_df['rolling_avg_goals'] = temp_df['goal_value_to_calculate'].rolling(window=5, closed="left", min_periods=1).mean()
# Apply the rolling average of goals to the original df    
    for index, row in temp_df.iterrows():
        if row['Home'] == x:
            df.at[index, 'home_rolling_avg_goals'] = row['rolling_avg_goals']
        else:
            df.at[index, 'away_rolling_avg_goals'] = row['rolling_avg_goals']

#Check the rolling goal average variable using Chelsea as an example
df[(df['Home'] == 'Chelsea') | (df['Away'] == 'Chelsea')][['Wk', 'Date', 'Home', 'Away', 'home_goals', 'away_goals','home_rolling_avg_goals', 'away_rolling_avg_goals']]

#Replicate the same model but for xG
for x in df.Home.unique():
    temp_df = df[(df['Home'] == x) | (df['Away'] == x)]
    temp_df = temp_df.sort_values(['Date'])
    
    temp_df['xG_value_to_calculate'] = temp_df.apply(lambda y: y['xG'] if y['Home'] == x else y['xG.1'], axis=1)
    temp_df['rolling_avg_xG'] = temp_df['xG_value_to_calculate'].rolling(window=5, closed="left", min_periods=1).mean()
    
    for index, row in temp_df.iterrows():
        if row['Home'] == x:
            df.at[index, 'home_rolling_avg_xG'] = row['rolling_avg_xG']
        else:
            df.at[index, 'away_rolling_avg_xG'] = row['rolling_avg_xG']

# Drop the rows where the rolling averages are null because a lack of historic data
df = df.dropna(subset=['home_rolling_avg_goals', 'away_rolling_avg_goals', 'home_rolling_avg_xG', 'away_rolling_avg_xG'])

#Check the rolling xG again using Chelsea as an example
df[(df['Home'] == 'Chelsea') | (df['Away'] == 'Chelsea')][['Date', 'Home', 'Away', 'xG', 'xG.1','home_rolling_avg_xG', 'away_rolling_avg_xG']]



