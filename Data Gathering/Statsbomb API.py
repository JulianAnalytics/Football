#STATSBOMB - All Competitions

from statsbombpy import sb

# Find competitions id
competitions = sb.competitions()

competitions = competitions[
    (competitions['country_name'] == 'Europe') & (competitions['competition_gender'] == 'female')]

competitions.head()

# STATSBOMB - UEFA Women's Euro 2022

sb.matches(competition_id=53, season_id=106)

# STATSBOMB - UEFA Women's Euro 2022 - All Matches

all_matches = []
for match_id in sb.matches(competition_id=53, season_id=106).match_id:
    temp_match = sb.events(match_id=match_id)
    all_matches.append(temp_match)

df = pd.concat(all_matches)

# STATSBOMB - UEFA Women's Euro 2022 - Aitana Bonmati

Bonmati = df[df['player'] == 'Aitana Bonmati Conca']

Bonmati.head()


#Summary of StatsBomb functions:
#load() or load_data(): Loads the primary match, event, and team data.
#competitions(): Retrieves competition data.
#matches(): Retrieves match-level details.
#events(): Retrieves event data for matches.
#teams(): Retrieves team-level data.
#players(): Retrieves player-related data for matches.
#games(): Retrieves match data for a specific competition and season.
#event_types(): Retrieves available event types.
#players_per_match(): Retrieves player data for a specific match.
#get_match_data(): Retrieves comprehensive match data.
