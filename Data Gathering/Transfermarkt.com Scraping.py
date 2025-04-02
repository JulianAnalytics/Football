{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 70,
   "id": "0ff472f2-1247-4489-9fa7-4150c014077b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests\n",
    "from bs4 import BeautifulSoup\n",
    "import pandas as pd\n",
    "import time"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "5d93af89-b2d9-4608-9ec1-28209111f7aa",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b8b341c7-15fc-4714-bb36-81a0e5a67e88",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": 112,
   "id": "5b5866f1-993f-41da-a8a7-b945cf53d571",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a list of players\n",
    "player_list = ['Rodri', 'Vinicius Junior', 'Jude Bellingham', 'Dani Carvajal', 'Erling Haaland']"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 114,
   "id": "ad19ae8f-6538-4660-9ecd-03f5d1eb6a41",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Base URL for player search\n",
    "base_url = \"https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query=\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 116,
   "id": "6d84a5d1-dd57-4883-bfe3-1479f14172e2",
   "metadata": {},
   "outputs": [],
   "source": [
    "# DataFrame to store results\n",
    "results = []"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 118,
   "id": "90d205b0-b8a6-453a-9691-70161bedc275",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "1/5: Rodri\n",
      "2/5: Vinicius Junior\n",
      "3/5: Jude Bellingham\n",
      "4/5: Dani Carvajal\n",
      "5/5: Erling Haaland\n"
     ]
    }
   ],
   "source": [
    "\n",
    "# Iterate through the player list with a counter\n",
    "for i, player in enumerate(player_list, start=1):\n",
    "    # Format the player name for the URL\n",
    "    search_url = base_url + player.replace(\" \", \"+\")\n",
    "    # Print the stage of the scraping process and the players which have been scraped\n",
    "    print(f\"{i}/{len(player_list)}: {player}\")\n",
    "\n",
    "    try:\n",
    "        # Fetch the page\n",
    "        response = requests.get(search_url, headers={\"User-Agent\": \"Mozilla/5.0\"})\n",
    "        response.raise_for_status()\n",
    "        soup = BeautifulSoup(response.text, \"html.parser\")\n",
    "\n",
    "        # Extract the market value\n",
    "        market_value_tag = soup.find(\"td\", class_=\"rechts hauptlink\")  # Target the specific class\n",
    "        if market_value_tag:\n",
    "            market_value = market_value_tag.text.strip()\n",
    "        else:\n",
    "            market_value = \"Not Found\"\n",
    "\n",
    "        # Append the result\n",
    "        results.append({\"Player\": player, \"Market Value\": market_value})\n",
    "    except Exception as e:\n",
    "        results.append({\"Player\": player, \"Market Value\": \"Error: \" + str(e)})\n",
    "\n",
    "    # Pause to avoid being blocked by the website\n",
    "    time.sleep(2)\n",
    "\n",
    "# Convert results to DataFrame\n",
    "df_results = pd.DataFrame(results)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 120,
   "id": "601deed0-4206-4bb5-9045-1229ed4b40c5",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "            Player Market Value\n",
      "0            Rodri     €130.00m\n",
      "1  Vinicius Junior     €200.00m\n",
      "2  Jude Bellingham     €180.00m\n",
      "3    Dani Carvajal    Not Found\n",
      "4   Erling Haaland     €200.00m\n"
     ]
    }
   ],
   "source": [
    "# Display results\n",
    "print(df_results)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "aed43221-3253-415a-9238-ef8840dab778",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Save to csv\n",
    "df_results.to_csv(\"player_market_values.csv\", index=False)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "9ad7a277-7955-440e-b6d0-1192e6b2c295",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
