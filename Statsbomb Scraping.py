#STATSBOMB - All Competitions

from statsbombpy import sb

sb.competitions()

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
