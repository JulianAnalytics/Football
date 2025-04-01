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
df_combined2 = df_combined.drop(columns=["Rk", "Age", "year"])
df_combined3 = df_combined2.drop_duplicates()

# Defines the function to get players in two given squads
def get_players_in_squads(df, squad1, squad2):
    # Filters players in squad1 and squad2
    players_squad1 = set(df_combined3[df_combined3['Squad'] == squad1]['Player'])
    players_squad2 = set(df_combined3[df_combined3['Squad'] == squad2]['Player'])
    
    # Finds the intersection of both sets (players who appear in both squads)
    common_players = players_squad1.intersection(players_squad2)
    
    return list(common_players)

squad1 = input("Enter the first squad name: ")
squad2 = input("Enter the second squad name: ")

players_in_both = get_players_in_squads(df_combined3, squad1, squad2)

#Prints the number of players which appear in both lists as a clue
print(len(players_in_both))

#Prints the players which appear in both lists as the answer
print("Players in both squads:", players_in_both)
