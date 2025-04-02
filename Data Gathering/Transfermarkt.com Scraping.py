import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Create a list of players e.g. 2024 Ballon d'Or finalists
player_list = ['Rodri', 'Vinicius Junior', 'Jude Bellingham', 'Dani Carvajal', 'Erling Haaland']

# Base URL for player search
base_url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query="

# DataFrame to store results
results = []


# Iterate through the player list with a counter
for i, player in enumerate(player_list, start=1):
    # Format the player name for the URL
    search_url = base_url + player.replace(" ", "+")
    # Print the stage of the scraping process and the players which have been scraped
    print(f"{i}/{len(player_list)}: {player}")

    try:
        # Fetch the page
        response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract the market value
        market_value_tag = soup.find("td", class_="rechts hauptlink")  # Target the specific class
        if market_value_tag:
            market_value = market_value_tag.text.strip()
        else:
            market_value = "Not Found"

        # Append the result
        results.append({"Player": player, "Market Value": market_value})
    except Exception as e:
        results.append({"Player": player, "Market Value": "Error: " + str(e)})

    # Pause to avoid being blocked by the website
    time.sleep(2)

# Convert results to DataFrame
df_results = pd.DataFrame(results)

# Display results
print(df_results)
