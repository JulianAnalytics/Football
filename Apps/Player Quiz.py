import pandas as pd
import os
os.chdir('/Users/julian/Downloads/FBREF')

# Loops through each file and create a dataframe with the same name as the CSV file (without the extension)
files = [f for f in os.listdir() if f.endswith('.csv')]

for file in files:

    filename_without_extension = os.path.splitext(file)[0]
    
    df = pd.read_csv(file)
    
    # Creates a dataframe with the same name as the CSV file
    globals()[filename_without_extension] = df

# Assigns the 'year' column to the corresponding dataframe
years = list(range(1992, 2025))

for year in years:
    df_name = f"PL{year}"  
    globals()[df_name]['year'] = year 

# Concatenates all PL dataframes (from PL1992 to PL2024)
pl_dfs = [globals()[f"PL{year}"] for year in range(1992, 2025)]

df_combined = pd.concat(pl_dfs, ignore_index=True)

#Cleans data by dropping unwanted columns
df_combined5 = df_combined.drop(columns=["Rk", "Age"])

#Given a player, returns all (Squad, Year) combinations where they featured.
def find_squads_and_years_for_player(df_combined5, player):
 
    player_data = df_combined5[df_combined5['Player'] == player][['Squad', 'year']].drop_duplicates()

    return [tuple(x) for x in player_data.values]

#Given a list of (Squad, Year) combinations, returns all players who featured in these squads and years.
def find_players_in_squads_and_years(df_combined5, squad_years):

    filtered_df = df_combined5[df_combined5[['Squad', 'year']].apply(tuple, axis=1).isin(squad_years)]
    
    return filtered_df['Player'].unique().tolist()
    
#Finds common players between two lists.
def find_common_players(players1, players2):
    
    return list(set(players1) & set(players2))

#Inputs the two players
player1 = input("Enter the first player: ")
player2 = input("Enter the second player: ")

#Finds the (Squad, Year) combinations for each player
player_squads_years1 = find_squads_and_years_for_player(df_combined5, player1)
player_squads_years2 = find_squads_and_years_for_player(df_combined5, player2)

#Finds players who appeared in those squads during those years
players1 = find_players_in_squads_and_years(df_combined5, player_squads_years1)
players2 = find_players_in_squads_and_years(df_combined5, player_squads_years2)

#Finds players which appear in both lists
common_players = find_common_players(players1, players2)

#Prints the number of players which appear in both lists as a clue
print(len(common_players))

#Prints the players which appear in both lists as the answer
print(common_players)
